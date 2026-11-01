import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { WelcomePage } from "../pages/WelcomePage";
import i18n from "../i18n";

describe("Language Switching", () => {
  it("toggles between English and Hindi", async () => {
    i18n.changeLanguage("en");

    render(
      <BrowserRouter>
        <div>
          <LanguageSwitcher />
          <WelcomePage />
        </div>
      </BrowserRouter>
    );

    // Initial English check
    expect(screen.getByText("Start Finding Internships")).toBeInTheDocument();

    // Click language switcher button to switch to Hindi
    const switchBtn = screen.getByRole("button", { name: /Toggle language/i });
    fireEvent.click(switchBtn);

    // Should now show Hindi text
    expect(screen.getByText("इंटर्नशिप खोजना शुरू करें")).toBeInTheDocument();

    // Switch back to English
    fireEvent.click(switchBtn);
    expect(screen.getByText("Start Finding Internships")).toBeInTheDocument();
  });
});
