import React, { useState, useEffect } from "react";
import { useParams, useLocation, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  MapPin,
  Calendar,
  IndianRupee,
  Building2,
  Sparkles,
  Bookmark,
  BookmarkCheck,
  AlertTriangle,
  ArrowLeft,
} from "lucide-react";
import { fetchInternshipDetail } from "../services/api";
import type { Internship, RecommendedInternship } from "../types";
import { useSavedInternships } from "../hooks/useSavedInternships";
import { ScoreBadge } from "../components/ScoreBadge";
import { ReasonBadge } from "../components/ReasonBadge";

export const InternshipDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const isHindi = i18n.language.startsWith("hi");
  const { isSaved, toggleSave } = useSavedInternships();

  const stateRec = (location.state as { recommendation?: RecommendedInternship })?.recommendation;

  const [internship, setInternship] = useState<Internship | null>(stateRec?.internship || null);
  const [loading, setLoading] = useState(!stateRec?.internship);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!internship && id) {
      setLoading(true);
      fetchInternshipDetail(id)
        .then((data) => {
          setInternship(data);
          setLoading(false);
        })
        .catch((err) => {
          setErrorMsg(err.message || "Failed to load internship details.");
          setLoading(false);
        });
    }
  }, [id, internship]);

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <div className="w-10 h-10 border-4 border-saathi-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-civic-700">Loading opportunity details...</p>
      </div>
    );
  }

  if (errorMsg || !internship) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-civic-900">Internship Not Found</h2>
        <p className="text-sm text-civic-700">{errorMsg || "The requested listing could not be found."}</p>
        <Link
          to="/wizard"
          className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-saathi-600 text-white text-xs font-semibold"
        >
          <span>Find Other Opportunities</span>
        </Link>
      </div>
    );
  }

  const sectorName = isHindi ? internship.sector.name_hi : internship.sector.name_en;

  return (
    <div className="max-w-3xl mx-auto py-2 sm:py-6 space-y-6">
      {/* Navigation Breadcrumb */}
      <div>
        <Link
          to="/recommendations"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-civic-700 hover:text-civic-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t("detail.back_to_results")}</span>
        </Link>
      </div>

      {/* Main Card */}
      <div className="bg-white rounded-2xl border border-civic-200 shadow-sm p-6 sm:p-8 space-y-6">
        {/* Title & Organization Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-civic-100">
          <div>
            <span className="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-civic-100 text-civic-700 mb-2">
              {sectorName}
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-civic-900 leading-tight">
              {internship.title}
            </h1>
            <div className="flex items-center gap-2 text-sm text-civic-700 mt-1 font-semibold">
              <Building2 className="w-4 h-4 text-civic-700" />
              <span>{internship.organization_name}</span>
              <span className="text-civic-700">•</span>
              <span className="text-xs text-civic-700 font-normal">ID: {internship.id}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => toggleSave(internship.id)}
            aria-label={isSaved(internship.id) ? t("recommendations.saved") : t("recommendations.save")}
            className={`p-2.5 rounded-xl border transition touch-target ${
              isSaved(internship.id)
                ? "bg-saathi-50 border-saathi-500 text-saathi-700"
                : "bg-civic-50 border-civic-200 text-civic-700 hover:text-civic-900"
            }`}
          >
            {isSaved(internship.id) ? (
              <BookmarkCheck className="w-5 h-5 text-saathi-600" />
            ) : (
              <Bookmark className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Key Attributes Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-civic-50 border border-civic-200 text-xs">
          <div className="space-y-1">
            <span className="text-civic-700 font-medium block">{t("detail.location")}</span>
            <div className="flex items-center gap-1 font-bold text-civic-900">
              <MapPin className="w-3.5 h-3.5 text-civic-700" />
              <span>{internship.district}, {internship.state}</span>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-civic-700 font-medium block">{t("detail.work_mode")}</span>
            <span className="font-bold text-civic-900 capitalize block">
              {internship.work_mode}
            </span>
          </div>

          <div className="space-y-1">
            <span className="text-civic-700 font-medium block">{t("detail.duration")}</span>
            <div className="flex items-center gap-1 font-bold text-civic-900">
              <Calendar className="w-3.5 h-3.5 text-civic-700" />
              <span>{internship.duration_months} Months</span>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-civic-700 font-medium block">{t("detail.stipend")}</span>
            <div className="flex items-center gap-1 font-extrabold text-civic-900">
              <IndianRupee className="w-3.5 h-3.5 text-saathi-600" />
              <span>₹{internship.stipend_inr.toLocaleString("en-IN")} / mo</span>
            </div>
          </div>
        </div>

        {/* If Navigated from Recommendation: Show Profile Match Analysis */}
        {stateRec && (
          <div className="p-4 rounded-xl bg-saathi-50/60 border border-saathi-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-saathi-600" />
                <span className="text-xs font-bold text-saathi-900 uppercase tracking-wider">
                  {t("detail.match_analysis")}
                </span>
              </div>
              <ScoreBadge score={stateRec.relative_score} tier={stateRec.match_tier} />
            </div>

            {stateRec.reasons && stateRec.reasons.length > 0 && (
              <div className="space-y-1.5 pt-1">
                {stateRec.reasons.map((r, idx) => (
                  <ReasonBadge key={idx} reason={r} />
                ))}
              </div>
            )}

            {/* Score Component Breakdown */}
            <div className="pt-2 border-t border-saathi-200/60 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-saathi-900">
              <div>
                <span className="text-saathi-700 block">{t("detail.skill_comp")}:</span>
                <span className="font-bold">
                  {stateRec.component_scores.skill_score !== null
                    ? `${Math.round((stateRec.component_scores.skill_score || 0) * 100)}%`
                    : t("detail.not_applicable")}
                </span>
              </div>
              <div>
                <span className="text-saathi-700 block">{t("detail.sector_comp")}:</span>
                <span className="font-bold">
                  {stateRec.component_scores.sector_score !== null
                    ? `${Math.round((stateRec.component_scores.sector_score || 0) * 100)}%`
                    : t("detail.not_applicable")}
                </span>
              </div>
              <div>
                <span className="text-saathi-700 block">{t("detail.location_comp")}:</span>
                <span className="font-bold">
                  {stateRec.component_scores.location_score !== null
                    ? `${Math.round((stateRec.component_scores.location_score || 0) * 100)}%`
                    : t("detail.not_applicable")}
                </span>
              </div>
              <div>
                <span className="text-saathi-700 block">{t("detail.text_comp")}:</span>
                <span className="font-bold">
                  {stateRec.component_scores.text_score !== null
                    ? `${Math.round((stateRec.component_scores.text_score || 0) * 100)}%`
                    : t("detail.not_applicable")}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Description Section */}
        <div className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-civic-700">
            {t("detail.description")}
          </h2>
          <p className="text-sm text-civic-800 leading-relaxed">
            {internship.description}
          </p>
        </div>

        {/* Requirements Section */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
          {/* Required Skills */}
          <div className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-civic-700">
              {t("detail.skills_required")}
            </h2>
            {internship.required_skills && internship.required_skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {internship.required_skills.map((sk) => (
                  <span
                    key={sk.id}
                    className="px-2.5 py-1 rounded-md bg-civic-100 text-civic-800 text-xs font-medium"
                  >
                    {isHindi ? sk.name_hi : sk.name_en}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-saathi-700 font-semibold bg-saathi-50 p-2 rounded-lg border border-saathi-200">
                {t("detail.skills_none")}
              </p>
            )}
          </div>

          {/* Accepted Education */}
          <div className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-civic-700">
              {t("detail.accepted_education")}
            </h2>
            <div className="flex flex-wrap gap-1.5">
              {internship.accepted_educations && internship.accepted_educations.length > 0 ? (
                internship.accepted_educations.map((edu) => (
                  <span
                    key={edu.id}
                    className="px-2.5 py-1 rounded-md bg-civic-100 text-civic-800 text-xs font-medium"
                  >
                    {isHindi ? edu.label_hi : edu.label_en}
                  </span>
                ))
              ) : (
                <span className="text-xs text-civic-700">Any education</span>
              )}
            </div>
          </div>
        </div>

        {/* Sample Notice Box (NO fake apply button!) */}
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">Prototype Demonstration Listing</p>
            <p>{t("detail.sample_notice")}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
