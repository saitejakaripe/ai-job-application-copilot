import type { JobRecommendationResponse, Preferences, ResumeProfile } from "./types";

export async function analyzeResumeText(
  resumeText: string,
  candidateName?: string
): Promise<ResumeProfile> {
  const response = await fetch("/v1/resumes/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      candidate_name: candidateName || undefined
    })
  });
  return parseJsonResponse<ResumeProfile>(response);
}

export async function analyzeResumeFile(
  file: File,
  candidateName?: string
): Promise<ResumeProfile> {
  const formData = new FormData();
  formData.set("resume_file", file);
  if (candidateName) {
    formData.set("candidate_name", candidateName);
  }

  const response = await fetch("/v1/resumes/analyze-file", {
    method: "POST",
    body: formData
  });
  return parseJsonResponse<ResumeProfile>(response);
}

export async function recommendJobs(
  profile: ResumeProfile,
  preferences: Preferences
): Promise<JobRecommendationResponse> {
  const response = await fetch("/v1/jobs/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, preferences })
  });
  return parseJsonResponse<JobRecommendationResponse>(response);
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => undefined);
  if (!response.ok) {
    const message =
      typeof payload?.detail === "string"
        ? payload.detail
        : "The request could not be completed.";
    throw new Error(message);
  }
  return payload as T;
}
