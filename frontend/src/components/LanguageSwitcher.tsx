import React from "react";
import { useTranslation } from "react-i18next";
import { Languages } from "lucide-react";

export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const nextLang = i18n.language.startsWith("hi") ? "en" : "hi";
    i18n.changeLanguage(nextLang);
    localStorage.setItem("saathi_language", nextLang);
  };

  const isHindi = i18n.language.startsWith("hi");

  return (
    <button
      type="button"
      onClick={toggleLanguage}
      aria-label="Toggle language between English and Hindi"
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-civic-200 bg-white text-civic-700 hover:bg-civic-50 text-sm font-semibold transition shadow-sm touch-target"
    >
      <Languages className="w-4 h-4 text-saathi-600" aria-hidden="true" />
      <span>{isHindi ? "English" : "हिन्दी"}</span>
    </button>
  );
};
