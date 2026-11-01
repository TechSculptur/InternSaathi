import React from "react";
import { useTranslation } from "react-i18next";
import { Check, MapPin, Briefcase, Sparkles, UserCheck } from "lucide-react";
import type { ReasonCode } from "../types";

interface ReasonBadgeProps {
  reason: ReasonCode;
}

export const ReasonBadge: React.FC<ReasonBadgeProps> = ({ reason }) => {
  const { i18n } = useTranslation();
  const isHindi = i18n.language.startsWith("hi");
  const text = isHindi ? reason.text_hi : reason.text_en;

  let Icon = Check;
  if (reason.code.includes("DISTRICT") || reason.code.includes("STATE") || reason.code.includes("LOCATION")) {
    Icon = MapPin;
  } else if (reason.code.includes("SECTOR")) {
    Icon = Briefcase;
  } else if (reason.code.includes("NO_PRIOR_SKILLS") || reason.code.includes("BEGINNER")) {
    Icon = UserCheck;
  } else if (reason.code.includes("REMOTE")) {
    Icon = Sparkles;
  }

  return (
    <div className="flex items-start gap-2 text-xs text-civic-800 bg-civic-50 rounded-lg p-2 border border-civic-200">
      <Icon className="w-4 h-4 text-saathi-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
      <span className="leading-snug">{text}</span>
    </div>
  );
};
