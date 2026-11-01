import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Bookmark,
  Trash2,
  MapPin,
  Calendar,
  IndianRupee,
  Building2,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { useSavedInternships } from "../hooks/useSavedInternships";
import { fetchInternshipDetail } from "../services/api";
import type { Internship } from "../types";

export const SavedPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isHindi = i18n.language.startsWith("hi");
  const { savedIds, clearSaved, toggleSave } = useSavedInternships();

  const [savedItems, setSavedItems] = useState<Internship[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (savedIds.length === 0) {
      setSavedItems([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    // Fetch details in parallel, gracefully filtering out deleted/missing IDs
    Promise.allSettled(savedIds.map((id) => fetchInternshipDetail(id))).then(
      (results) => {
        const loaded: Internship[] = [];
        results.forEach((r) => {
          if (r.status === "fulfilled") {
            loaded.push(r.value);
          }
        });
        setSavedItems(loaded);
        setLoading(false);
      }
    );
  }, [savedIds]);

  return (
    <div className="max-w-4xl mx-auto py-2 sm:py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-civic-200">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700 mb-1">
            <Bookmark className="w-3.5 h-3.5 text-saathi-600" />
            <span>{t("saved.title")}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-civic-900">
            {t("saved.title")}
          </h1>
          <p className="text-xs sm:text-sm text-civic-700 mt-1">
            {t("saved.subtitle")}
          </p>
        </div>

        {savedItems.length > 0 && (
          <button
            type="button"
            onClick={clearSaved}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold shadow-xs transition self-start sm:self-auto touch-target"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{t("saved.clear_all")}</span>
          </button>
        )}
      </div>

      {loading ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-saathi-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold text-civic-700">Loading saved opportunities...</p>
        </div>
      ) : savedItems.length === 0 ? (
        <div className="bg-white rounded-2xl border border-civic-200 p-8 sm:p-12 text-center space-y-4 max-w-md mx-auto my-8">
          <div className="w-12 h-12 rounded-full bg-saathi-50 text-saathi-600 flex items-center justify-center mx-auto">
            <Bookmark className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-civic-900">{t("saved.empty_title")}</h2>
          <p className="text-sm text-civic-700">{t("saved.empty_desc")}</p>
          <Link
            to="/wizard"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-saathi-600 hover:bg-saathi-700 text-white font-bold text-sm shadow-sm transition touch-target"
          >
            <Sparkles className="w-4 h-4" />
            <span>{t("saved.find_btn")}</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {savedItems.map((item) => {
            const sectorName = isHindi ? item.sector.name_hi : item.sector.name_en;
            return (
              <div
                key={item.id}
                className="bg-white rounded-xl border border-civic-200 shadow-sm p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <span className="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-civic-100 text-civic-700 mb-1.5">
                        {sectorName}
                      </span>
                      <h2 className="text-lg font-bold text-civic-900 leading-tight">
                        {item.title}
                      </h2>
                      <div className="flex items-center gap-1.5 text-sm text-civic-700 mt-1 font-medium">
                        <Building2 className="w-4 h-4" />
                        <span>{item.organization_name}</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => toggleSave(item.id)}
                      className="p-2 rounded-lg border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 text-xs font-medium flex items-center gap-1 touch-target"
                      aria-label="Remove from saved"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 my-3 py-2.5 border-y border-civic-100 text-xs text-civic-700">
                    <div className="flex items-center gap-1.5 font-medium">
                      <MapPin className="w-4 h-4" />
                      <span>{item.district}, {item.state} ({item.work_mode})</span>
                    </div>
                    <div className="flex items-center gap-1.5 font-medium">
                      <Calendar className="w-4 h-4" />
                      <span>{item.duration_months} Months</span>
                    </div>
                    <div className="flex items-center gap-1.5 font-bold text-civic-900">
                      <IndianRupee className="w-4 h-4 text-saathi-600" />
                      <span>₹{item.stipend_inr.toLocaleString("en-IN")} / mo</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-civic-100 flex items-center justify-between">
                  <span className="text-[10px] text-civic-700 italic">
                    ID: {item.id} • Sample Data
                  </span>
                  <Link
                    to={`/internships/${item.id}`}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-saathi-600 hover:bg-saathi-700 text-white text-xs font-semibold shadow-sm transition touch-target"
                  >
                    <span>View Full Details</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
