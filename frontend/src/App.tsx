import {
  Bookmark,
  BookmarkCheck,
  BriefcaseBusiness,
  CheckCircle2,
  ExternalLink,
  FileText,
  Filter,
  MapPin,
  RotateCcw,
  Search,
  Sparkles,
  Upload
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { analyzeResumeFile, analyzeResumeText, recommendJobs } from "./api";
import type {
  ApplicationLink,
  CandidateLevel,
  JobRecommendation,
  JobRecommendationResponse,
  JobType,
  MarketScope,
  Preferences,
  ResumeProfile
} from "./types";

const JOB_TYPES: JobType[] = ["Internship", "Full-time", "Part-time", "Contract", "Remote"];
const LOCATIONS = [
  "Remote",
  "Hyderabad",
  "Bengaluru",
  "Chennai",
  "Pune",
  "Mumbai",
  "Delhi NCR",
  "Anywhere in India"
];
const STORAGE_KEY = "jobmatch-saved-jobs";

const DEFAULT_PREFERENCES: Preferences = {
  candidate_level: "fresher",
  years_experience: null,
  job_types: ["Full-time", "Remote"],
  locations: ["Remote"],
  custom_location: "",
  interested_roles: [],
  open_to_relocation: false,
  expected_salary_min_lpa: null,
  expected_salary_max_lpa: null,
  market_scope: "both",
  min_match_percentage: 40,
  skill_filters: [],
  source_filters: []
};

interface DashboardFilters {
  location: string;
  jobType: string;
  source: string;
  skill: string;
  minMatch: number;
  maxSalary: number;
  savedOnly: boolean;
}

const DEFAULT_DASHBOARD_FILTERS: DashboardFilters = {
  location: "all",
  jobType: "all",
  source: "all",
  skill: "all",
  minMatch: 40,
  maxSalary: 0,
  savedOnly: false
};

export function App() {
  const [resumeText, setResumeText] = useState("");
  const [candidateName, setCandidateName] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(DEFAULT_PREFERENCES);
  const [roleInput, setRoleInput] = useState("");
  const [skillInput, setSkillInput] = useState("");
  const [response, setResponse] = useState<JobRecommendationResponse | null>(null);
  const [filters, setFilters] = useState<DashboardFilters>(DEFAULT_DASHBOARD_FILTERS);
  const [savedJobs, setSavedJobs] = useState<string[]>(loadSavedJobs);
  const [status, setStatus] = useState("Paste or upload your resume to begin.");
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRecommending, setIsRecommending] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(savedJobs));
  }, [savedJobs]);

  const jobs = response?.jobs ?? [];
  const sourceOptions = useMemo(() => unique(jobs.map((job) => job.source_website)), [jobs]);
  const skillOptions = useMemo(
    () => unique(jobs.flatMap((job) => job.required_skills)).slice(0, 18),
    [jobs]
  );
  const locationOptions = useMemo(() => unique(jobs.map((job) => job.location)), [jobs]);

  const filteredJobs = useMemo(
    () =>
      jobs.filter((job) => {
        if (filters.savedOnly && !savedJobs.includes(job.id)) {
          return false;
        }
        if (job.resume_match_percentage < filters.minMatch) {
          return false;
        }
        if (filters.location !== "all" && job.location !== filters.location) {
          return false;
        }
        if (filters.jobType !== "all" && job.job_type !== filters.jobType) {
          return false;
        }
        if (filters.source !== "all" && job.source_website !== filters.source) {
          return false;
        }
        if (filters.skill !== "all" && !job.required_skills.includes(filters.skill)) {
          return false;
        }
        if (filters.maxSalary > 0 && salaryFloor(job.salary_range) > filters.maxSalary) {
          return false;
        }
        return true;
      }),
    [filters, jobs, savedJobs]
  );

  async function handleAnalyze() {
    setError("");
    setIsAnalyzing(true);
    try {
      const nextProfile = resumeFile
        ? await analyzeResumeFile(resumeFile, candidateName)
        : await analyzeResumeText(resumeText, candidateName);
      setProfile(nextProfile);
      setRoleInput(nextProfile.suitable_roles.join(", "));
      setSkillInput("");
      setStatus(`Analyzed ${nextProfile.candidate_name}'s resume.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Resume analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleRecommend() {
    if (!profile) {
      setError("Analyze a resume before requesting job matches.");
      return;
    }
    setError("");
    setIsRecommending(true);
    try {
      const requestPreferences = {
        ...preferences,
        interested_roles: parseList(roleInput),
        skill_filters: parseList(skillInput),
        years_experience:
          preferences.candidate_level === "experienced"
            ? preferences.years_experience ?? profile.years_experience ?? 0
            : preferences.years_experience,
        expected_salary_min_lpa: preferences.expected_salary_min_lpa || null,
        expected_salary_max_lpa: preferences.expected_salary_max_lpa || null,
        custom_location: preferences.custom_location || null
      };
      const nextResponse = await recommendJobs(profile, requestPreferences);
      setResponse(nextResponse);
      setFilters((current) => ({
        ...current,
        minMatch: nextResponse.preferences.min_match_percentage
      }));
      setStatus(
        `${nextResponse.returned_matches} job matches and ` +
          `${nextResponse.generated_application_links_count} unique apply links found.`
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Job recommendation failed.");
    } finally {
      setIsRecommending(false);
    }
  }

  function updatePreference<K extends keyof Preferences>(key: K, value: Preferences[K]) {
    setPreferences((current) => ({ ...current, [key]: value }));
  }

  function toggleSaved(jobId: string) {
    setSavedJobs((current) =>
      current.includes(jobId) ? current.filter((id) => id !== jobId) : [...current, jobId]
    );
  }

  const canAnalyze = Boolean(resumeFile || resumeText.trim().length >= 50);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">JobMatch India</p>
          <h1>Resume-aware remote job recommendations</h1>
        </div>
        <div className="status-strip">
          <Metric label="Resume skills" value={String(profile?.skills.length ?? 0)} />
          <Metric label="Matches" value={String(response?.returned_matches ?? jobs.length)} />
          <Metric
            label="Unique apply links"
            value={String(response?.generated_application_links_count ?? 0)}
          />
          <Metric label="Saved" value={String(savedJobs.length)} />
        </div>
      </header>

      <main className="workspace">
        <section className="input-column" aria-label="Resume and preferences">
          <ResumePanel
            resumeText={resumeText}
            candidateName={candidateName}
            resumeFile={resumeFile}
            isAnalyzing={isAnalyzing}
            canAnalyze={canAnalyze}
            profile={profile}
            onCandidateNameChange={setCandidateName}
            onResumeTextChange={setResumeText}
            onResumeFileChange={setResumeFile}
            onAnalyze={handleAnalyze}
          />

          <PreferencePanel
            preferences={preferences}
            roleInput={roleInput}
            skillInput={skillInput}
            isRecommending={isRecommending}
            hasProfile={Boolean(profile)}
            onPreferenceChange={updatePreference}
            onRoleInputChange={setRoleInput}
            onSkillInputChange={setSkillInput}
            onRecommend={handleRecommend}
          />
        </section>

        <section className="dashboard-column" aria-label="Job dashboard">
          <div className="dashboard-head">
            <div>
              <p className="eyebrow">Dashboard</p>
              <h2>Recommended opportunities</h2>
            </div>
            <div className="message-stack">
              <span className="status-message">{status}</span>
              {error ? <span className="error-message">{error}</span> : null}
            </div>
          </div>

          <ProfileSummary profile={profile} />
          <ResultsSummary response={response} visibleJobs={filteredJobs.length} />

          <DashboardFilters
            filters={filters}
            locationOptions={locationOptions}
            sourceOptions={sourceOptions}
            skillOptions={skillOptions}
            onChange={setFilters}
          />

          <div className="job-list">
            {filteredJobs.length ? (
              filteredJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  saved={savedJobs.includes(job.id)}
                  onToggleSaved={toggleSaved}
                />
              ))
            ) : (
              <EmptyState hasJobs={Boolean(response)} />
            )}
          </div>

          <ImprovementSection response={response} />
        </section>
      </main>
    </div>
  );
}

function ResumePanel(props: {
  resumeText: string;
  candidateName: string;
  resumeFile: File | null;
  isAnalyzing: boolean;
  canAnalyze: boolean;
  profile: ResumeProfile | null;
  onCandidateNameChange: (value: string) => void;
  onResumeTextChange: (value: string) => void;
  onResumeFileChange: (file: File | null) => void;
  onAnalyze: () => void;
}) {
  return (
    <div className="tool-panel">
      <div className="panel-title">
        <FileText size={20} />
        <h2>Resume</h2>
      </div>
      <label>
        Candidate name
        <input
          value={props.candidateName}
          onChange={(event) => props.onCandidateNameChange(event.target.value)}
          placeholder="Optional"
        />
      </label>
      <label className="file-input">
        <Upload size={18} />
        <span>{props.resumeFile ? props.resumeFile.name : "Upload TXT, MD, PDF, or DOCX"}</span>
        <input
          type="file"
          accept=".txt,.md,.pdf,.docx"
          onChange={(event) => props.onResumeFileChange(event.target.files?.[0] ?? null)}
        />
      </label>
      <label>
        Resume text
        <textarea
          value={props.resumeText}
          onChange={(event) => props.onResumeTextChange(event.target.value)}
          placeholder="Paste your resume text here..."
          rows={8}
        />
      </label>
      <button
        className="primary-button"
        type="button"
        disabled={!props.canAnalyze || props.isAnalyzing}
        onClick={props.onAnalyze}
      >
        <Sparkles size={18} />
        {props.isAnalyzing ? "Analyzing" : "Analyze resume"}
      </button>

      {props.profile ? (
        <div className="profile-pills">
          <ChipList title="Skills" items={props.profile.skills.slice(0, 10)} />
          <ChipList title="Roles" items={props.profile.suitable_roles.slice(0, 6)} />
        </div>
      ) : null}
    </div>
  );
}

function PreferencePanel(props: {
  preferences: Preferences;
  roleInput: string;
  skillInput: string;
  isRecommending: boolean;
  hasProfile: boolean;
  onPreferenceChange: <K extends keyof Preferences>(key: K, value: Preferences[K]) => void;
  onRoleInputChange: (value: string) => void;
  onSkillInputChange: (value: string) => void;
  onRecommend: () => void;
}) {
  const preferences = props.preferences;

  return (
    <div className="tool-panel">
      <div className="panel-title">
        <BriefcaseBusiness size={20} />
        <h2>Preferences</h2>
      </div>

      <div className="segmented">
        {(["fresher", "intern", "experienced"] as CandidateLevel[]).map((level) => (
          <button
            key={level}
            type="button"
            className={preferences.candidate_level === level ? "active" : ""}
            onClick={() => props.onPreferenceChange("candidate_level", level)}
          >
            {titleCase(level)}
          </button>
        ))}
      </div>

      {preferences.candidate_level === "experienced" ? (
        <label>
          Years of experience
          <input
            type="number"
            min={0}
            max={50}
            value={preferences.years_experience ?? ""}
            onChange={(event) =>
              props.onPreferenceChange("years_experience", numberOrNull(event.target.value))
            }
          />
        </label>
      ) : null}

      <fieldset>
        <legend>Job type</legend>
        <CheckGrid
          values={JOB_TYPES}
          selected={preferences.job_types}
          onToggle={(next) => props.onPreferenceChange("job_types", next as JobType[])}
        />
      </fieldset>

      <fieldset>
        <legend>Location</legend>
        <CheckGrid
          values={LOCATIONS}
          selected={preferences.locations}
          onToggle={(next) => props.onPreferenceChange("locations", next)}
        />
      </fieldset>

      <label>
        Custom location
        <input
          value={preferences.custom_location ?? ""}
          onChange={(event) => props.onPreferenceChange("custom_location", event.target.value)}
          placeholder="Country, city, or time zone"
        />
      </label>

      <label>
        Interested roles
        <input
          value={props.roleInput}
          onChange={(event) => props.onRoleInputChange(event.target.value)}
          placeholder="AI Engineer, Frontend Developer"
        />
      </label>

      <label>
        Skill filters
        <input
          value={props.skillInput}
          onChange={(event) => props.onSkillInputChange(event.target.value)}
          placeholder="python, react, llm"
        />
      </label>

      <div className="split-fields">
        <label>
          Min salary LPA
          <input
            type="number"
            min={0}
            value={preferences.expected_salary_min_lpa ?? ""}
            onChange={(event) =>
              props.onPreferenceChange(
                "expected_salary_min_lpa",
                numberOrNull(event.target.value)
              )
            }
          />
        </label>
        <label>
          Max salary LPA
          <input
            type="number"
            min={0}
            value={preferences.expected_salary_max_lpa ?? ""}
            onChange={(event) =>
              props.onPreferenceChange(
                "expected_salary_max_lpa",
                numberOrNull(event.target.value)
              )
            }
          />
        </label>
      </div>

      <label>
        Job market
        <select
          value={preferences.market_scope}
          onChange={(event) =>
            props.onPreferenceChange("market_scope", event.target.value as MarketScope)
          }
        >
          <option value="india">India jobs</option>
          <option value="abroad">Abroad remote jobs</option>
          <option value="both">Both</option>
        </select>
      </label>

      <label>
        Minimum match: {preferences.min_match_percentage}%
        <input
          type="range"
          min={0}
          max={95}
          step={5}
          value={preferences.min_match_percentage}
          onChange={(event) =>
            props.onPreferenceChange("min_match_percentage", Number(event.target.value))
          }
        />
      </label>

      <label className="toggle-row">
        <input
          type="checkbox"
          checked={preferences.open_to_relocation}
          onChange={(event) =>
            props.onPreferenceChange("open_to_relocation", event.target.checked)
          }
        />
        Open to relocation
      </label>

      <button
        className="primary-button"
        type="button"
        disabled={!props.hasProfile || props.isRecommending}
        onClick={props.onRecommend}
      >
        <Search size={18} />
        {props.isRecommending ? "Finding matches" : "Find matching jobs"}
      </button>
    </div>
  );
}

function ProfileSummary({ profile }: { profile: ResumeProfile | null }) {
  if (!profile) {
    return (
      <div className="summary-band empty-summary">
        <FileText size={20} />
        <span>Resume profile appears here after analysis.</span>
      </div>
    );
  }

  return (
    <div className="summary-band">
      <Metric label="Candidate" value={profile.candidate_name} />
      <Metric label="Experience" value={profile.years_experience ?? "Not found"} />
      <Metric label="Tools" value={profile.technical_tools.length} />
      <Metric label="Projects" value={profile.projects.length} />
    </div>
  );
}

function ResultsSummary({
  response,
  visibleJobs
}: {
  response: JobRecommendationResponse | null;
  visibleJobs: number;
}) {
  if (!response) {
    return null;
  }

  return (
    <div className="results-summary">
      <Metric label="All eligible matches" value={response.total_matches} />
      <Metric label="Displayed after filters" value={visibleJobs} />
      <Metric label="Unique apply links" value={response.generated_application_links_count} />
    </div>
  );
}

function DashboardFilters(props: {
  filters: DashboardFilters;
  locationOptions: string[];
  sourceOptions: string[];
  skillOptions: string[];
  onChange: (filters: DashboardFilters) => void;
}) {
  const filters = props.filters;
  const update = <K extends keyof DashboardFilters>(key: K, value: DashboardFilters[K]) => {
    props.onChange({ ...filters, [key]: value });
  };

  return (
    <div className="filter-panel">
      <div className="panel-title compact">
        <Filter size={18} />
        <h3>Filters</h3>
      </div>
      <select value={filters.location} onChange={(event) => update("location", event.target.value)}>
        <option value="all">All locations</option>
        {props.locationOptions.map((location) => (
          <option key={location} value={location}>
            {location}
          </option>
        ))}
      </select>
      <select value={filters.jobType} onChange={(event) => update("jobType", event.target.value)}>
        <option value="all">All job types</option>
        {JOB_TYPES.map((jobType) => (
          <option key={jobType} value={jobType}>
            {jobType}
          </option>
        ))}
      </select>
      <select value={filters.source} onChange={(event) => update("source", event.target.value)}>
        <option value="all">All sources</option>
        {props.sourceOptions.map((source) => (
          <option key={source} value={source}>
            {source}
          </option>
        ))}
      </select>
      <select value={filters.skill} onChange={(event) => update("skill", event.target.value)}>
        <option value="all">All skills</option>
        {props.skillOptions.map((skill) => (
          <option key={skill} value={skill}>
            {skill}
          </option>
        ))}
      </select>
      <label>
        Match {filters.minMatch}%+
        <input
          type="range"
          min={0}
          max={95}
          step={5}
          value={filters.minMatch}
          onChange={(event) => update("minMatch", Number(event.target.value))}
        />
      </label>
      <label>
        Salary floor
        <input
          type="number"
          min={0}
          value={filters.maxSalary || ""}
          onChange={(event) => update("maxSalary", Number(event.target.value) || 0)}
          placeholder="Max starting LPA"
        />
      </label>
      <label className="toggle-row">
        <input
          type="checkbox"
          checked={filters.savedOnly}
          onChange={(event) => update("savedOnly", event.target.checked)}
        />
        Saved only
      </label>
      <button
        className="secondary-button"
        type="button"
        onClick={() => props.onChange(DEFAULT_DASHBOARD_FILTERS)}
      >
        <RotateCcw size={16} />
        Reset
      </button>
    </div>
  );
}

function JobCard(props: {
  job: JobRecommendation;
  saved: boolean;
  onToggleSaved: (jobId: string) => void;
}) {
  const job = props.job;

  return (
    <article className="job-card">
      <div className="job-card-head">
        <div>
          <p className="source-line">{job.source_website}</p>
          <h3>{job.job_title}</h3>
          <p className="company">{job.company_name}</p>
        </div>
        <div className="match-badge">{job.resume_match_percentage}%</div>
      </div>

      <div className="job-meta">
        <span>
          <MapPin size={15} />
          {job.location}
        </span>
        <span>
          <BriefcaseBusiness size={15} />
          {job.job_type}
        </span>
        <span>{job.required_experience}</span>
        {job.salary_range ? <span>{job.salary_range}</span> : null}
      </div>

      <p className="reason">{job.match_reason}</p>
      <ChipList title="Required skills" items={job.required_skills} />
      <ChipList title="Matched" items={job.matched_skills} tone="success" />

      <div className="job-actions">
        <button className="secondary-button" type="button" onClick={() => props.onToggleSaved(job.id)}>
          {props.saved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
          {props.saved ? "Saved" : "Save"}
        </button>
        <a className="apply-button" href={job.direct_apply_link} target="_blank" rel="noreferrer">
          <ExternalLink size={16} />
          Apply
        </a>
      </div>
    </article>
  );
}

function ImprovementSection({ response }: { response: JobRecommendationResponse | null }) {
  if (!response) {
    return null;
  }

  const improvements = response.resume_improvements;

  return (
    <section className="improvement-section">
      <div className="panel-title">
        <CheckCircle2 size={20} />
        <h2>Resume improvements</h2>
      </div>
      <div className="improvement-grid">
        <ImprovementBlock title="Missing skills" items={improvements.missing_skills} />
        <ImprovementBlock title="Keywords" items={improvements.keywords_to_add} />
        <ImprovementBlock title="Projects" items={improvements.project_suggestions} />
        <ImprovementBlock title="Certifications" items={improvements.certification_suggestions} />
        <ImprovementBlock title="ATS" items={improvements.ats_suggestions} />
      </div>

      <div className="source-links">
        <h3>Remote job sources</h3>
        {response.source_links.map((source) => (
          <a key={source.url} href={source.url} target="_blank" rel="noreferrer">
            <ExternalLink size={15} />
            {source.label}
          </a>
        ))}
      </div>

      <ApplicationLinksSection links={response.application_links} />
    </section>
  );
}

function ApplicationLinksSection({ links }: { links: ApplicationLink[] }) {
  if (!links.length) {
    return null;
  }

  const grouped = groupApplicationLinks(links);

  return (
    <div className="application-links">
      <h3>Unique apply links</h3>
      <div className="application-link-grid">
        {grouped.map((group) => (
          <div className="application-link-group" key={group.source}>
            <h4>{group.source}</h4>
            <div>
              {group.links.map((link) => (
                <a key={`${link.url}-${link.label}`} href={link.url} target="_blank" rel="noreferrer">
                  <ExternalLink size={14} />
                  <span>{link.role}</span>
                  <small>
                    {link.job_type} · {link.location}
                  </small>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImprovementBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="improvement-block">
      <h3>{title}</h3>
      {items.length ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>No major gaps detected.</p>
      )}
    </div>
  );
}

function EmptyState({ hasJobs }: { hasJobs: boolean }) {
  return (
    <div className="empty-state">
      <Search size={28} />
      <h3>{hasJobs ? "No jobs match these filters" : "No recommendations yet"}</h3>
      <p>
        {hasJobs
          ? "Adjust the dashboard filters or lower the match threshold."
          : "Analyze a resume, set preferences, and run the matcher."}
      </p>
    </div>
  );
}

function CheckGrid(props: {
  values: string[];
  selected: string[];
  onToggle: (values: string[]) => void;
}) {
  return (
    <div className="check-grid">
      {props.values.map((value) => (
        <label key={value} className="checkbox-pill">
          <input
            type="checkbox"
            checked={props.selected.includes(value)}
            onChange={(event) => {
              const next = event.target.checked
                ? [...props.selected, value]
                : props.selected.filter((item) => item !== value);
              props.onToggle(unique(next));
            }}
          />
          {value}
        </label>
      ))}
    </div>
  );
}

function ChipList({
  title,
  items,
  tone = "default"
}: {
  title: string;
  items: string[];
  tone?: "default" | "success";
}) {
  if (!items.length) {
    return null;
  }
  return (
    <div className="chip-group">
      <span>{title}</span>
      <div>
        {items.map((item) => (
          <span key={item} className={`chip ${tone}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function parseList(value: string): string[] {
  return unique(
    value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
  );
}

function groupApplicationLinks(links: ApplicationLink[]) {
  const groups = new Map<string, ApplicationLink[]>();
  for (const link of links) {
    const group = groups.get(link.source_website) ?? [];
    group.push(link);
    groups.set(link.source_website, group);
  }
  return Array.from(groups, ([source, groupLinks]) => ({
    source,
    links: groupLinks
  }));
}

function unique(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean)));
}

function numberOrNull(value: string): number | null {
  return value === "" ? null : Number(value);
}

function salaryFloor(label: string | null): number {
  if (!label) {
    return 0;
  }
  const match = label.match(/^(\d+(?:\.\d+)?)/);
  return match ? Number(match[1]) : 0;
}

function titleCase(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function loadSavedJobs(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}
