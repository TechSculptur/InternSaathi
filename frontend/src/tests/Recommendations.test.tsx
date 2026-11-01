import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { RecommendationsPage } from "../pages/RecommendationsPage";
import { fetchRecommendations } from "../services/api";
import "../i18n";

const mockRecommendationResponse = {
  results: [
    {
      internship: {
        id: "TEST-REC-1",
        title: "Digital Assistant Intern",
        organization_name: "Gramin Digital Labs",
        sector: { id: 1, code: "it_software", name_en: "IT & Digital", name_hi: "आईटी" },
        state: "Maharashtra",
        district: "Pune",
        work_mode: "onsite",
        duration_months: 6,
        stipend_inr: 8500,
        deadline: "2026-11-01",
        is_active: true,
        allows_no_skills: false,
        is_sample: true,
      },
      relative_score: 0.88,
      match_tier: "strong",
      component_scores: {
        skill_score: 0.9,
        sector_score: 1.0,
        location_score: 0.8,
        text_score: 0.75,
      },
      effective_weights: {
        skill_weight: 0.4,
        sector_weight: 0.3,
        location_weight: 0.2,
        text_weight: 0.1,
      },
      missing_skills: ["Advanced Excel"],
      reasons: [
        {
          code: "SAME_DISTRICT",
          params: {},
          text_en: "Located in your home district: Pune.",
          text_hi: "आपके गृह जिले में स्थित है: Pune.",
        },
      ],
      is_sample: true,
    },
  ],
  total_eligible: 1,
  has_limited_profile: false,
  profile_summary_en: "Evaluated 1 eligible opportunity.",
  profile_summary_hi: "1 पात्र अवसर का मूल्यांकन किया गया।",
  disclaimer: "Demonstration prototype.",
};

describe("RecommendationsPage", () => {
  it("renders recommendations cards with score badges and match reasons", () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: "/recommendations",
            state: { recommendations: mockRecommendationResponse },
          },
        ]}
      >
        <RecommendationsPage />
      </MemoryRouter>
    );

    expect(screen.getByText("Digital Assistant Intern")).toBeInTheDocument();
    expect(screen.getByText("Gramin Digital Labs")).toBeInTheDocument();
    expect(screen.getByText(/Pune, Maharashtra/i)).toBeInTheDocument();
    expect(screen.getByText(/Strong Match/i)).toBeInTheDocument();
    expect(screen.getByText(/Located in your home district/i)).toBeInTheDocument();
    expect(screen.getByText("+Advanced Excel")).toBeInTheDocument();
  });

  it("normalizes recommendation API validation-detail objects into a readable error string", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [{ type: "json_invalid", msg: "JSON decode error" }],
        }),
      })
    );

    await expect(
      fetchRecommendations(
        {
          education: "tenth_pass",
          skills: [],
          sectors: [],
          state: "Delhi",
          district: "",
          preferred_work_mode: "any",
          is_work_mode_mandatory: false,
          is_location_mandatory: false,
          willing_to_relocate: true,
        },
        5
      )
    ).rejects.toThrow("JSON decode error");
  });
});
