import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WizardPage } from "../pages/WizardPage";
import * as api from "../services/api";
import "../i18n";

vi.mock("../services/api", () => ({
  fetchOptions: vi.fn(),
  fetchRecommendations: vi.fn(),
}));

const mockOptions = {
  education_categories: [
    { code: "tenth_pass", label_en: "10th Pass", label_hi: "10वीं पास" },
    { code: "twelfth_pass", label_en: "12th Pass", label_hi: "12वीं पास" },
  ],
  sectors: [
    { code: "it_software", name_en: "IT & Digital", name_hi: "आईटी" },
  ],
  skills: [
    { code: "python", name_en: "Python", name_hi: "पायथन", sector_code: "it_software" },
  ],
  states_and_districts: [
    {
      state_en: "Maharashtra",
      state_hi: "महाराष्ट्र",
      districts: [{ name_en: "Pune", name_hi: "पुणे" }],
    },
  ],
  work_modes: [
    { code: "any", label_en: "Any Mode", label_hi: "कोई भी" },
    { code: "remote", label_en: "Remote", label_hi: "रिमोट" },
  ],
};

describe("WizardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (api.fetchOptions as any).mockResolvedValue(mockOptions);
  });

  it("renders options and blocks advancing without selecting education", async () => {
    render(
      <BrowserRouter>
        <WizardPage />
      </BrowserRouter>
    );

    // Wait for options to load
    await waitFor(() => {
      expect(screen.getByText("10th Pass")).toBeInTheDocument();
    });

    // Try clicking Continue without selecting education
    const nextBtn = screen.getByText("Continue");
    fireEvent.click(nextBtn);

    // Expect validation error message
    expect(screen.getByText(/Please select your education to continue/i)).toBeInTheDocument();
  });

  it("allows advancing after selecting education", async () => {
    render(
      <BrowserRouter>
        <WizardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("10th Pass")).toBeInTheDocument();
    });

    // Select 10th Pass
    fireEvent.click(screen.getByText("10th Pass"));

    // Click Continue
    const nextBtn = screen.getByText("Continue");
    fireEvent.click(nextBtn);

    // Should now be on Step 2 (Skills)
    await waitFor(() => {
      expect(screen.getByText(/What skills do you have/i)).toBeInTheDocument();
    });
  });
});
