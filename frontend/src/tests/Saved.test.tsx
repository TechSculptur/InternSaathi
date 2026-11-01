import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { SavedPage } from "../pages/SavedPage";
import * as api from "../services/api";
import "../i18n";

vi.mock("../services/api", () => ({
  fetchInternshipDetail: vi.fn(),
}));

const mockDetail = {
  id: "INT-001",
  title: "Junior Web Development Intern",
  organization_name: "Pragati Tech Solutions",
  description: "Web assistant position.",
  sector: { id: 1, code: "it_software", name_en: "IT", name_hi: "आईटी" },
  state: "Maharashtra",
  district: "Mumbai",
  work_mode: "onsite",
  duration_months: 6,
  stipend_inr: 8500,
  deadline: "2026-12-01",
  is_active: true,
  allows_no_skills: false,
  is_sample: true,
};

describe("SavedPage", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("shows empty state when no internships are bookmarked", () => {
    render(
      <BrowserRouter>
        <SavedPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/No Saved Internships Yet/i)).toBeInTheDocument();
  });

  it("loads and displays saved internships when present in localStorage", async () => {
    localStorage.setItem("saathi_saved_ids", JSON.stringify(["INT-001"]));
    (api.fetchInternshipDetail as any).mockResolvedValue(mockDetail);

    render(
      <BrowserRouter>
        <SavedPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Junior Web Development Intern")).toBeInTheDocument();
      expect(screen.getByText("Pragati Tech Solutions")).toBeInTheDocument();
    });

    // Test clear all button
    const clearBtn = screen.getByText("Clear All Saved");
    fireEvent.click(clearBtn);

    await waitFor(() => {
      expect(screen.getByText(/No Saved Internships Yet/i)).toBeInTheDocument();
    });
  });
});
