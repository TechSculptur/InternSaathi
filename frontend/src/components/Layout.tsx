import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Compass, Bookmark, WifiOff, FileText } from "lucide-react";
import { DisclaimerBanner } from "./DisclaimerBanner";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useSavedInternships } from "../hooks/useSavedInternships";

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { t } = useTranslation();
  const location = useLocation();
  const { savedIds } = useSavedInternships();
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-civic-50 text-civic-900">
      {/* Top Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Offline Alert if connection lost */}
      {!isOnline && (
        <div
          role="alert"
          className="bg-amber-600 text-white px-4 py-2 text-xs font-semibold flex items-center justify-center gap-2"
        >
          <WifiOff className="w-4 h-4" aria-hidden="true" />
          <span>{t("app.offline_notice")}</span>
        </div>
      )}

      {/* Main Header */}
      <header className="bg-white border-b border-civic-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2.5 group focus:outline-none focus-visible:ring-2 focus-visible:ring-saathi-500 rounded-lg p-1"
          >
            <div className="w-9 h-9 rounded-lg bg-saathi-600 text-white flex items-center justify-center font-bold text-lg shadow-sm group-hover:bg-saathi-700 transition">
              IS
            </div>
            <div>
              <span className="text-lg font-extrabold text-civic-900 tracking-tight block leading-tight">
                {t("app.title")}
              </span>
              <span className="text-[10px] text-civic-700 font-medium block">
                {t("welcome.hero_badge")}
              </span>
            </div>
          </Link>

          {/* Nav Controls */}
          <div className="flex items-center gap-2 sm:gap-4">
            <nav className="flex items-center gap-1 sm:gap-2">
              <Link
                to="/wizard"
                className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition touch-target inline-flex items-center gap-1.5 ${
                  location.pathname === "/wizard"
                    ? "bg-saathi-50 text-saathi-700 border border-saathi-200"
                    : "text-civic-700 hover:bg-civic-100"
                }`}
              >
                <Compass className="w-4 h-4" aria-hidden="true" />
                <span className="hidden sm:inline">{t("nav.find")}</span>
              </Link>
              <Link
                to="/tailor-resume"
                className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition touch-target inline-flex items-center gap-1.5 ${
                  location.pathname === "/tailor-resume"
                    ? "bg-saathi-50 text-saathi-700 border border-saathi-200"
                    : "text-civic-700 hover:bg-civic-100"
                }`}
              >
                <FileText className="w-4 h-4" aria-hidden="true" />
                <span className="hidden sm:inline">Tailor Resume</span>
              </Link>
              <Link
                to="/saved"
                className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition touch-target inline-flex items-center gap-1.5 ${
                  location.pathname === "/saved"
                    ? "bg-saathi-50 text-saathi-700 border border-saathi-200"
                    : "text-civic-700 hover:bg-civic-100"
                }`}
              >
                <Bookmark className="w-4 h-4" aria-hidden="true" />
                <span>{t("nav.saved", { count: savedIds.length })}</span>
              </Link>
            </nav>

            <div className="h-6 w-[1px] bg-civic-200" aria-hidden="true" />

            {/* Language Switcher */}
            <LanguageSwitcher />
          </div>
        </div>
      </header>

      {/* Main App Body */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-6 md:py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-civic-200 py-6 mt-12 text-center text-xs text-civic-700">
        <div className="max-w-5xl mx-auto px-4 space-y-2">
          <p className="font-medium text-civic-800">
            {t("app.title")} — {t("app.tagline")}
          </p>
          <p>{t("app.footer_note")}</p>
          <p className="text-[11px] text-civic-700">
            Demonstration prototype inspired by the PM Internship Scheme problem statement.
            All listings, company names, and data are strictly synthetic.
          </p>
        </div>
      </footer>
    </div>
  );
};
