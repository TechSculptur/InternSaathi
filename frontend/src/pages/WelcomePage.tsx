import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  GraduationCap,
  ShieldCheck,
  Compass,
  ArrowRight,
  Sparkles,
  BookOpen,
} from "lucide-react";

export const WelcomePage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto py-4 sm:py-8 space-y-10">
      {/* Hero Section */}
      <section className="text-center space-y-5 px-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-saathi-50 border border-saathi-200 text-saathi-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-saathi-600" aria-hidden="true" />
          <span>{t("welcome.hero_badge")}</span>
        </div>

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-civic-900 tracking-tight leading-tight">
          {t("welcome.hero_title")}
        </h1>

        <p className="text-base sm:text-lg text-civic-700 max-w-2xl mx-auto leading-relaxed">
          {t("welcome.hero_desc")}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-3">
          <Link
            to="/wizard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-saathi-600 hover:bg-saathi-700 text-white font-bold text-base shadow-md transition touch-target"
          >
            <span>{t("welcome.start_btn")}</span>
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </Link>
          <Link
            to="/saved"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-civic-50 border border-civic-200 text-civic-700 font-semibold text-base transition touch-target"
          >
            <span>{t("welcome.browse_btn")}</span>
          </Link>
        </div>
      </section>

      {/* 3 Core Principles Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="bg-white rounded-xl p-6 border border-civic-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-saathi-50 text-saathi-600 flex items-center justify-center">
            <GraduationCap className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-base font-bold text-civic-900">
            {t("welcome.key_feat_1_title")}
          </h2>
          <p className="text-sm text-civic-700 leading-relaxed">
            {t("welcome.key_feat_1_desc")}
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-civic-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Compass className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-base font-bold text-civic-900">
            {t("welcome.key_feat_2_title")}
          </h2>
          <p className="text-sm text-civic-700 leading-relaxed">
            {t("welcome.key_feat_2_desc")}
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-civic-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" aria-hidden="true" />
          </div>
          <h2 className="text-base font-bold text-civic-900">
            {t("welcome.key_feat_3_title")}
          </h2>
          <p className="text-sm text-civic-700 leading-relaxed">
            {t("welcome.key_feat_3_desc")}
          </p>
        </div>
      </section>

      {/* Clear Demonstration Notice Box */}
      <section className="bg-civic-100 rounded-xl p-5 border border-civic-200 text-xs sm:text-sm text-civic-700 space-y-2">
        <div className="flex items-center gap-2 font-bold text-civic-900">
          <BookOpen className="w-4 h-4 text-saathi-600" aria-hidden="true" />
          <span>About This Demonstration Prototype</span>
        </div>
        <p>
          This is an educational prototype built to demonstrate accessible recommendation logic
          for first-time applicants under simulated requirements. It contains 120 synthetic
          opportunities and does not submit real applications to government portals.
        </p>
      </section>
    </div>
  );
};
