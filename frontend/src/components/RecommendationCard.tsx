import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  MapPin,
  Calendar,
  IndianRupee,
  Bookmark,
  BookmarkCheck,
  Building2,
  ArrowRight,
} from "lucide-react";
import type { RecommendedInternship } from "../types";
import { ScoreBadge } from "./ScoreBadge";
import { ReasonBadge } from "./ReasonBadge";

interface RecommendationCardProps {
  item: RecommendedInternship;
  isSaved: boolean;
  onToggleSave: (id: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  item,
  isSaved,
  onToggleSave,
}) => {
  const { t, i18n } = useTranslation();
  const isHindi = i18n.language.startsWith("hi");
  const { internship, relative_score, match_tier, reasons, missing_skills } = item;

  const sectorName = isHindi ? internship.sector.name_hi : internship.sector.name_en;

  const formatWorkMode = (mode: string) => {
    switch (mode.toLowerCase()) {
      case "remote":
        return isHindi ? "रिमोट (घर से)" : "Remote";
      case "hybrid":
        return isHindi ? "हाइब्रिड" : "Hybrid";
      default:
        return isHindi ? "ऑन-साइट" : "On-site";
    }
  };

  return (
    <div className="bg-white rounded-xl border border-civic-200 shadow-sm hover:shadow-md transition-shadow p-5 flex flex-col justify-between">
      <div>
        {/* Top Header: Organization & Bookmark */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1">
            <span className="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-civic-100 text-civic-700 mb-1.5">
              {sectorName}
            </span>
            <h2 className="text-lg font-bold text-civic-900 leading-tight">
              {internship.title}
            </h2>
            <div className="flex items-center gap-1.5 text-sm text-civic-700 mt-1 font-medium">
              <Building2 className="w-4 h-4 text-civic-700 flex-shrink-0" aria-hidden="true" />
              <span>{internship.organization_name}</span>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onToggleSave(internship.id)}
            aria-label={isSaved ? t("recommendations.saved") : t("recommendations.save")}
            className={`p-2 rounded-lg border transition touch-target ${
              isSaved
                ? "bg-saathi-50 border-saathi-500 text-saathi-700"
                : "bg-civic-50 border-civic-200 text-civic-700 hover:text-civic-900"
            }`}
          >
            {isSaved ? (
              <BookmarkCheck className="w-5 h-5 text-saathi-600" aria-hidden="true" />
            ) : (
              <Bookmark className="w-5 h-5" aria-hidden="true" />
            )}
          </button>
        </div>

        {/* Quick Info Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 my-3 py-2.5 border-y border-civic-100 text-xs text-civic-700">
          <div className="flex items-center gap-1.5 font-medium">
            <MapPin className="w-4 h-4 text-civic-700 flex-shrink-0" aria-hidden="true" />
            <span>
              {internship.district}, {internship.state}
              <span className="ml-1 px-1.5 py-0.5 rounded bg-civic-100 text-civic-700 text-[10px] font-semibold">
                {formatWorkMode(internship.work_mode)}
              </span>
            </span>
          </div>
          <div className="flex items-center gap-1.5 font-medium">
            <Calendar className="w-4 h-4 text-civic-700 flex-shrink-0" aria-hidden="true" />
            <span>{t("recommendations.duration", { months: internship.duration_months })}</span>
          </div>
          <div className="flex items-center gap-1.5 font-bold text-civic-900">
            <IndianRupee className="w-4 h-4 text-saathi-600 flex-shrink-0" aria-hidden="true" />
            <span>{t("recommendations.stipend", { amount: internship.stipend_inr.toLocaleString("en-IN") })}</span>
          </div>
        </div>

        {/* Match Score Badge */}
        <div className="mb-3">
          <ScoreBadge score={relative_score} tier={match_tier} />
        </div>

        {/* Match Reasons */}
        {reasons && reasons.length > 0 && (
          <div className="space-y-1.5 mb-3">
            <p className="text-[11px] font-bold uppercase tracking-wider text-civic-700">
              {t("recommendations.match_reasons")}
            </p>
            {reasons.slice(0, 3).map((r, idx) => (
              <ReasonBadge key={idx} reason={r} />
            ))}
          </div>
        )}

        {/* Missing Skills Pills */}
        {missing_skills && missing_skills.length > 0 && (
          <div className="mb-4">
            <p className="text-[11px] font-bold uppercase tracking-wider text-civic-700 mb-1">
              {t("recommendations.missing_skills")}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {missing_skills.slice(0, 3).map((skillName, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200 text-[11px] font-medium"
                >
                  +{skillName}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-civic-100 flex items-center justify-between">
        <span className="text-[10px] text-civic-700 italic">
          {internship.id} • Sample Data
        </span>
        <Link
          to={`/internships/${internship.id}`}
          state={{ recommendation: item }}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-saathi-600 hover:bg-saathi-700 text-white text-xs font-semibold shadow-sm transition touch-target"
        >
          <span>{t("recommendations.view_details")}</span>
          <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
        </Link>
      </div>
    </div>
  );
};
