import React from "react";
import { useTranslation } from "react-i18next";
import { AlertTriangle } from "lucide-react";

export const DisclaimerBanner: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div
      role="alert"
      className="bg-saffron-50 border-b border-saffron-500/30 px-4 py-2 text-xs md:text-sm text-saffron-800 font-medium flex items-center justify-center gap-2"
    >
      <AlertTriangle className="w-4 h-4 text-saffron-600 flex-shrink-0" aria-hidden="true" />
      <span>{t("app.disclaimer")}</span>
    </div>
  );
};
