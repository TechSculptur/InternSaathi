import React from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Sparkles,
  SlidersHorizontal,
  ArrowLeft,
  AlertCircle,
  HelpCircle,
} from "lucide-react";
import { RecommendationCard } from "../components/RecommendationCard";
import { useSavedInternships } from "../hooks/useSavedInternships";
import type { RecommendationResponse, CandidateProfile } from "../types";

export const RecommendationsPage: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();

  const { isSaved, toggleSave } = useSavedInternships();

  const stateData = location.state as {
    recommendations?: RecommendationResponse;
    submittedProfile?: CandidateProfile;
  } | null;

  const recommendations = stateData?.recommendations;

  if (!recommendations || !recommendations.results) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-civic-100 text-civic-700 flex items-center justify-center mx-auto">
          <HelpCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-civic-900">
          {t("recommendations.no_results_title")}
        </h2>
        <p className="text-sm text-civic-700">
          {t("recommendations.no_results_desc")}
        </p>
        <Link
          to="/wizard"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-saathi-600 hover:bg-saathi-700 text-white font-bold text-sm shadow-sm transition touch-target"
        >
          <span>{t("recommendations.try_again")}</span>
        </Link>
      </div>
    );
  }

  const { results, total_eligible, has_limited_profile } = recommendations;

  return (
    <div className="max-w-4xl mx-auto py-2 sm:py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-civic-200">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-saathi-600" />
            <span>{t("recommendations.title")}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-civic-900">
            {t("recommendations.title")}
          </h1>
          <p className="text-xs sm:text-sm text-civic-700 mt-1">
            {t("recommendations.subtitle", { total: total_eligible })}
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate("/wizard")}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-civic-200 bg-white hover:bg-civic-50 text-civic-800 text-xs font-semibold shadow-xs transition self-start sm:self-auto touch-target"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>{t("recommendations.edit_profile")}</span>
        </button>
      </div>

      {/* Limited Profile Warning Banner */}
      {has_limited_profile && (
        <div
          role="note"
          className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs sm:text-sm flex items-start gap-2.5"
        >
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <span>{t("recommendations.limited_profile_notice")}</span>
        </div>
      )}

      {/* Recommendations List (Up to 5 cards) */}
      {results.length === 0 ? (
        <div className="py-12 text-center space-y-3 bg-white rounded-2xl border border-civic-200 p-8">
          <h3 className="text-lg font-bold text-civic-900">
            {t("recommendations.no_results_title")}
          </h3>
          <p className="text-sm text-civic-700">
            {t("recommendations.no_results_desc")}
          </p>
          <Link
            to="/wizard"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-saathi-600 text-white text-xs font-semibold"
          >
            <span>{t("recommendations.try_again")}</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((rec) => (
            <RecommendationCard
              key={rec.internship.id}
              item={rec}
              isSaved={isSaved(rec.internship.id)}
              onToggleSave={toggleSave}
            />
          ))}
        </div>
      )}

      {/* Bottom Back Button */}
      <div className="pt-4 flex items-center justify-between">
        <Link
          to="/wizard"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-civic-700 hover:text-civic-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t("wizard.back")}</span>
        </Link>
        <span className="text-[11px] text-civic-700">
          Showing {results.length} of {total_eligible} eligible listings
        </span>
      </div>
    </div>
  );
};
