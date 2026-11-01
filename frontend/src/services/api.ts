import type {
  OptionsResponse,
  Internship,
  CandidateProfile,
  RecommendationResponse,
  ParsedResumeResponse,
} from "../types";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, "")
  : "/api/v1";

function normalizeApiError(errorData: any, fallback: string): string {
  if (!errorData || typeof errorData !== "object") {
    return fallback;
  }

  const detail = errorData.detail;
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const parts = detail.map((item: any) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") {
        return item.msg || item.message || item.type || JSON.stringify(item);
      }
      return String(item);
    });
    const readable = parts.join(". ");
    return readable || fallback;
  }

  if (detail && typeof detail === "object") {
    if (typeof detail.message === "string") return detail.message;
    if (typeof detail.msg === "string") return detail.msg;
    if (typeof detail.error === "string") return detail.error;
    return JSON.stringify(detail);
  }

  return fallback;
}

async function throwApiError(res: Response, fallback: string): Promise<never> {
  const errorData = await res.json().catch(() => ({}));
  const message = normalizeApiError(errorData, fallback);
  throw new Error(message);
}

export async function fetchHealth(): Promise<{ status: string; sample_data_count: number }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchOptions(): Promise<OptionsResponse> {
  const res = await fetch(`${API_BASE_URL}/options`);
  if (!res.ok) {
    await throwApiError(res, `Failed to fetch options: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchInternshipDetail(id: string): Promise<Internship> {
  const res = await fetch(`${API_BASE_URL}/internships/${encodeURIComponent(id)}`);
  if (!res.ok) {
    await throwApiError(res, `Failed to load internship: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchRecommendations(
  profile: CandidateProfile,
  limit: number = 5
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE_URL}/recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ profile, limit }),
  });

  if (!res.ok) {
    await throwApiError(res, `Server returned error (${res.status})`);
  }

  return res.json();
}

export async function parseResume(file: File): Promise<ParsedResumeResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/resume/parse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    await throwApiError(res, `Failed to parse resume (${res.status})`);
  }

  return res.json();
}


export interface ResumeTailoringResult {
  professional_summary?: string;
  skills?: string[];
  experience_bullets?: string[];
  projects?: string[];
  education?: string[];
  other_sections?: string[];
  matched_requirements?: string[];
  missing_requirements?: string[];
  change_notes?: string[];
  detected_resume_skills?: string[];
  docx_base64: string;
  filename: string;
  disclaimer: string;
}

export async function tailorResume(file: File, jobDescription: string): Promise<ResumeTailoringResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);
  const res = await fetch(`${API_BASE_URL}/resume/tailor`, { method: "POST", body: formData });
  if (!res.ok) await throwApiError(res, `Resume tailoring failed (${res.status})`);
  return res.json();
}


export async function exportTailoredResume(result: ResumeTailoringResult): Promise<Blob> {
  const { docx_base64: _docx, filename: _filename, disclaimer: _disclaimer, ...content } = result;
  const res = await fetch(`${API_BASE_URL}/resume/export-tailored`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(content),
  });
  if (!res.ok) await throwApiError(res, `Resume export failed (${res.status})`);
  return res.blob();
}


export async function fetchInternshipsForTailoring(): Promise<Array<{ id: string; title: string; organization_name: string }>> {
  const res = await fetch(`${API_BASE_URL}/internships?page=1&page_size=50`);
  if (!res.ok) await throwApiError(res, `Failed to fetch internships: ${res.statusText}`);
  const data = await res.json();
  return data.items || [];
}
