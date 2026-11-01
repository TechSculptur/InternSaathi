import React from "react";
import { useTranslation } from "react-i18next";
import { Sparkles, CheckCircle2, Compass, AlertCircle } from "lucide-react";

interface ScoreBadgeProps {
  score: number;
  tier: "strong" | "good" | "moderate" | "exploratory";
}

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score, tier }) => {
  const { t } = useTranslation();
  const percentage = Math.round(score * 100);

  let badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-300";
  let Icon = CheckCircle2;
  let tierLabel = t("recommendations.match_tier_good");

  if (tier === "strong") {
    badgeColor = "bg-saathi-100 text-saathi-700 border-saathi-500";
    Icon = Sparkles;
    tierLabel = t("recommendations.match_tier_strong");
  } else if (tier === "good") {
    badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-300";
    Icon = CheckCircle2;
    tierLabel = t("recommendations.match_tier_good");
  } else if (tier === "moderate") {
    badgeColor = "bg-blue-50 text-blue-800 border-blue-300";
    Icon = Compass;
    tierLabel = t("recommendations.match_tier_moderate");
  } else {
    badgeColor = "bg-slate-100 text-slate-700 border-slate-300";
    Icon = AlertCircle;
    tierLabel = t("recommendations.match_tier_exploratory");
  }

  return (
    <div className="inline-flex items-center gap-2">
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}`}
      >
        <Icon className="w-3.5 h-3.5" aria-hidden="true" />
        <span>{tierLabel}</span>
      </span>
      <span className="text-xs text-civic-700 font-medium">
        {t("recommendations.relative_score", { score: percentage })}
      </span>
    </div>
  );
};
