import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  GraduationCap,
  Sparkles,
  Briefcase,
  MapPin,
  ArrowLeft,
  ArrowRight,
  Check,
  Search,
  AlertCircle,
  HelpCircle,
  Upload,
  FileText,
  X,
  Loader2,
} from "lucide-react";
import { ProgressBar } from "../components/ProgressBar";
import { fetchOptions, fetchRecommendations, parseResume } from "../services/api";
import type { OptionsResponse, CandidateProfile, ParsedResumeResponse } from "../types";

const MAX_SKILLS = 20;
const MAX_SECTORS = 10;

export const WizardPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isHindi = i18n.language.startsWith("hi");

  const [step, setStep] = useState(1);
  const [options, setOptions] = useState<OptionsResponse | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // In-memory candidate profile state (No persistent tracking without consent)
  const [education, setEducation] = useState<string>("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [skillSearch, setSkillSearch] = useState<string>("");
  const [isBeginnerSkills, setIsBeginnerSkills] = useState<boolean>(false);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [stateName, setStateName] = useState<string>("");
  const [districtName, setDistrictName] = useState<string>("");
  const [workMode, setWorkMode] = useState<string>("any");
  const [isWorkModeMandatory, setIsWorkModeMandatory] = useState<boolean>(false);
  const [isLocationMandatory, setIsLocationMandatory] = useState<boolean>(false);
  const [willingToRelocate, setWillingToRelocate] = useState<boolean>(true);

  // Resume upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState<string>("");
  const [resumeDetectedSkills, setResumeDetectedSkills] = useState<string[]>([]);
  const [resumeUploading, setResumeUploading] = useState<boolean>(false);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchOptions()
      .then((data) => {
        setOptions(data);
        setLoadingOptions(false);
      })
      .catch((err) => {
        console.error(err);
        const message = err instanceof Error ? err.message : typeof err === "string" ? err : t("wizard.error_loading_options");
        setErrorMsg(message || t("wizard.error_loading_options"));
        setLoadingOptions(false);
      });
  }, []);

  const handleNext = () => {
    setErrorMsg(null);
    if (step === 1 && !education) {
      setErrorMsg(t("wizard.error_education"));
      return;
    }
    setStep((prev) => Math.min(prev + 1, 4));
  };

  const handleBack = () => {
    setErrorMsg(null);
    setStep((prev) => Math.max(prev - 1, 1));
  };

  const toggleSkill = (code: string) => {
    setIsBeginnerSkills(false);
    setSelectedSkills((prev) => {
      if (prev.includes(code)) {
        return prev.filter((s) => s !== code);
      }
      if (prev.length >= MAX_SKILLS) {
        setErrorMsg(`You can select at most ${MAX_SKILLS} skills.`);
        return prev;
      }
      return [...prev, code];
    });
  };

  const setBeginner = () => {
    setIsBeginnerSkills(true);
    setSelectedSkills([]);
  };

  const toggleSector = (code: string) => {
    setSelectedSectors((prev) => {
      if (prev.includes(code)) {
        return prev.filter((s) => s !== code);
      }
      if (prev.length >= MAX_SECTORS) {
        setErrorMsg(`You can select at most ${MAX_SECTORS} sectors.`);
        return prev;
      }
      return [...prev, code];
    });
  };

  const handleResumeUpload = async (file: File) => {
    setResumeError(null);
    setResumeUploading(true);

    try {
      const response: ParsedResumeResponse = await parseResume(file);
      const detectedSkills = response.detected_skills.slice(0, MAX_SKILLS);

      // Set detected skills from resume (user can deselect)
      setResumeDetectedSkills(detectedSkills);
      setSelectedSkills(detectedSkills);
      setIsBeginnerSkills(false);

      // Store resume text for semantic matching
      setResumeText(response.resume_text);

      setResumeFile(file);
    } catch (err: any) {
      const message = err.message || t("wizard.resume_upload_failed");
      setResumeError(message);
      setResumeFile(null);
      setResumeText("");
      setResumeDetectedSkills([]);
    } finally {
      setResumeUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleResumeUpload(file);
    }
  };

  const removeResume = () => {
    setResumeFile(null);
    setResumeText("");
    setResumeDetectedSkills([]);
    setResumeError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!education) {
      setStep(1);
      setErrorMsg(t("wizard.error_education"));
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    const payloadSkills = selectedSkills.slice(0, MAX_SKILLS);
    const payloadSectors = selectedSectors.slice(0, MAX_SECTORS);

    const profilePayload: CandidateProfile = {
      education,
      skills: payloadSkills,
      sectors: payloadSectors,
      state: stateName || undefined,
      district: districtName || undefined,
      preferred_work_mode: workMode,
      is_work_mode_mandatory: isWorkModeMandatory,
      is_location_mandatory: isLocationMandatory,
      willing_to_relocate: willingToRelocate,
      resume_text: resumeText || undefined,
    };

    try {
      const response = await fetchRecommendations(profilePayload, 5);
      navigate("/recommendations", {
        state: { recommendations: response, submittedProfile: profilePayload },
      });
    } catch (err: any) {
      console.error(err);
      const message = err instanceof Error ? err.message : typeof err === "string" ? err : t("wizard.error_fetching_recommendations");
      setErrorMsg(message || t("wizard.error_fetching_recommendations"));
    } finally {
      setSubmitting(false);
    }
  };

  // Districts for currently selected state
  const selectedStateObj = options?.states_and_districts.find(
    (s) => s.state_en === stateName
  );

  const filteredSkills = (options?.skills || []).filter((s) => {
    const term = skillSearch.toLowerCase();
    const name = isHindi ? s.name_hi.toLowerCase() : s.name_en.toLowerCase();
    return name.includes(term) || s.code.toLowerCase().includes(term);
  });

  if (loadingOptions) {
    return (
      <div className="py-16 text-center space-y-3">
        <div className="w-10 h-10 border-4 border-saathi-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-civic-700">
          {t("wizard.loading")}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-2 sm:py-6">
      <ProgressBar currentStep={step} totalSteps={4} />

      <div className="bg-white rounded-2xl border border-civic-200 shadow-sm p-6 sm:p-8">
        {errorMsg && (
          <div
            role="alert"
            className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center gap-2"
          >
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* STEP 1: EDUCATION */}
          {step === 1 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700">
                  <GraduationCap className="w-4 h-4" />
                  <span>{t("wizard.step_1")}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-civic-900">
                  {t("wizard.step_1_title")}
                </h2>
                <p className="text-sm text-civic-700">
                  {t("wizard.step_1_sub")}
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                {options?.education_categories.map((edu) => {
                  const isSelected = education === edu.code;
                  return (
                    <button
                      key={edu.code}
                      type="button"
                      onClick={() => setEducation(edu.code)}
                      className={`p-4 rounded-xl border text-left flex items-center justify-between transition touch-target ${
                        isSelected
                          ? "bg-saathi-50 border-saathi-600 ring-2 ring-saathi-600 text-saathi-900 font-bold"
                          : "bg-white border-civic-200 hover:border-civic-300 text-civic-800 font-medium"
                      }`}
                    >
                      <span className="text-sm sm:text-base">
                        {isHindi ? edu.label_hi : edu.label_en}
                      </span>
                      {isSelected && (
                        <div className="w-6 h-6 rounded-full bg-saathi-600 text-white flex items-center justify-center flex-shrink-0">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 2: SKILLS */}
          {step === 2 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700">
                  <Sparkles className="w-4 h-4" />
                  <span>{t("wizard.step_2")}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-civic-900">
                  {t("wizard.step_2_title")}
                </h2>
                <p className="text-sm text-civic-700">
                  {t("wizard.step_2_sub")}
                </p>
              </div>

              {/* Beginner option */}
              <button
                type="button"
                onClick={setBeginner}
                className={`w-full p-3.5 rounded-xl border text-sm font-semibold flex items-center justify-center gap-2 transition touch-target ${
                  isBeginnerSkills
                    ? "bg-emerald-100 border-emerald-600 text-emerald-900 ring-2 ring-emerald-600"
                    : "bg-civic-50 border-civic-200 text-civic-800 hover:bg-civic-100"
                }`}
              >
                <HelpCircle className="w-4 h-4 text-saathi-600" />
                <span>{t("wizard.not_sure_skills")}</span>
              </button>

              {/* Resume Upload */}
              <div className="space-y-3">
                <label className="block text-xs font-bold text-civic-800">
                  {t("wizard.upload_resume")}
                </label>
                <div className="relative">
                  <input
                    ref={fileInputRef}
                    id="resume-upload"
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleFileSelect}
                    disabled={resumeUploading}
                    className="sr-only"
                  />
                  <label
                    htmlFor="resume-upload"
                    className={`w-full p-4 rounded-xl border-2 border-dashed text-center cursor-pointer transition touch-target ${
                      resumeUploading
                        ? "border-civic-300 bg-civic-50 cursor-not-allowed"
                        : "border-saathi-300 hover:border-saathi-500 hover:bg-saathi-50"
                    }`}
                  >
                    {resumeUploading ? (
                      <div className="flex flex-col items-center gap-2">
                        <Loader2 className="w-6 h-6 text-saathi-600 animate-spin" />
                        <span className="text-sm text-civic-700">{t("wizard.uploading")}</span>
                      </div>
                    ) : resumeFile ? (
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <FileText className="w-6 h-6 text-saathi-600 flex-shrink-0" />
                          <div>
                            <p className="text-sm font-medium text-civic-900 truncate max-w-[200px]">
                              {resumeFile.name}
                            </p>
                            <p className="text-xs text-civic-600">
                              {(resumeFile.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={removeResume}
                          className="p-1.5 rounded-lg text-civic-500 hover:text-red-600 hover:bg-red-50 transition touch-target"
                          aria-label={t("wizard.remove_resume")}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-2">
                        <Upload className="w-8 h-8 text-saathi-400" />
                        <span className="text-sm font-medium text-civic-700">
                          {t("wizard.drop_resume")}
                        </span>
                        <span className="text-xs text-civic-500">
                          {t("wizard.resume_formats")}
                        </span>
                      </div>
                    )}
                  </label>
                </div>
                {resumeError && (
                  <p className="text-sm text-red-600 flex items-center gap-1.5" role="alert">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {resumeError}
                  </p>
                )}
                {resumeDetectedSkills.length > 0 && !resumeUploading && (
                  <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                    <p className="text-xs font-medium text-emerald-800 mb-2 flex items-center gap-1.5">
                      <Check className="w-3.5 h-3.5" />
                      {t("wizard.resume_skills_detected")}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {resumeDetectedSkills.map((code) => {
                        const skill = options?.skills.find((s) => s.code === code);
                        const name = skill ? (isHindi ? skill.name_hi : skill.name_en) : code;
                        return (
                          <span
                            key={code}
                            className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-300"
                          >
                            {name}
                          </span>
                        );
                      })}
                    </div>
                    <p className="text-xs text-emerald-700 mt-2">
                      {t("wizard.resume_skills_note")}
                    </p>
                  </div>
                )}
                {/* Privacy note */}
                <p className="text-xs text-civic-600 flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5 text-saathi-500 flex-shrink-0" />
                  <span>{t("wizard.privacy_note")}</span>
                </p>
              </div>

              {/* Skill Search Box */}
              <div className="relative">
                <Search className="w-4 h-4 text-civic-700 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={skillSearch}
                  onChange={(e) => setSkillSearch(e.target.value)}
                  placeholder={t("wizard.search_skills")}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-civic-200 text-sm focus:outline-none focus:ring-2 focus:ring-saathi-500"
                />
              </div>

              {/* Skills Chips */}
              <div className="flex flex-wrap gap-2 max-h-64 overflow-y-auto p-1">
                {filteredSkills.map((sk) => {
                  const isSelected = selectedSkills.includes(sk.code);
                  return (
                    <button
                      key={sk.code}
                      type="button"
                      onClick={() => toggleSkill(sk.code)}
                      className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium border transition touch-target flex items-center gap-1.5 ${
                        isSelected
                          ? "bg-saathi-600 text-white border-saathi-700 shadow-xs"
                          : "bg-white text-civic-800 border-civic-200 hover:border-civic-400"
                      }`}
                    >
                      <span>{isHindi ? sk.name_hi : sk.name_en}</span>
                      {isSelected && <Check className="w-3.5 h-3.5" />}
                    </button>
                  );
                })}
              </div>

              {selectedSkills.length > 0 && (
                <p className="text-xs text-civic-700 font-medium">
                  Selected ({selectedSkills.length}) skills.
                </p>
              )}
            </div>
          )}

          {/* STEP 3: SECTOR INTERESTS */}
          {step === 3 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700">
                  <Briefcase className="w-4 h-4" />
                  <span>{t("wizard.step_3")}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-civic-900">
                  {t("wizard.step_3_title")}
                </h2>
                <p className="text-sm text-civic-700">
                  {t("wizard.step_3_sub")}
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                {options?.sectors.map((sec) => {
                  const isSelected = selectedSectors.includes(sec.code);
                  return (
                    <button
                      key={sec.code}
                      type="button"
                      onClick={() => toggleSector(sec.code)}
                      className={`p-3.5 rounded-xl border text-left flex items-center justify-between transition touch-target ${
                        isSelected
                          ? "bg-saathi-50 border-saathi-600 ring-2 ring-saathi-600 text-saathi-900 font-bold"
                          : "bg-white border-civic-200 hover:border-civic-300 text-civic-800 font-medium"
                      }`}
                    >
                      <span className="text-sm">
                        {isHindi ? sec.name_hi : sec.name_en}
                      </span>
                      {isSelected && (
                        <div className="w-5 h-5 rounded-full bg-saathi-600 text-white flex items-center justify-center flex-shrink-0">
                          <Check className="w-3 h-3" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 4: LOCATION & MOBILITY */}
          {step === 4 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-saathi-700">
                  <MapPin className="w-4 h-4" />
                  <span>{t("wizard.step_4")}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-civic-900">
                  {t("wizard.step_4_title")}
                </h2>
                <p className="text-sm text-civic-700">
                  {t("wizard.step_4_sub")}
                </p>
              </div>

              {/* State & District Selectors */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label htmlFor="state-select" className="block text-xs font-bold text-civic-800">
                    {t("wizard.select_state")}
                  </label>
                  <select
                    id="state-select"
                    value={stateName}
                    onChange={(e) => {
                      setStateName(e.target.value);
                      setDistrictName("");
                    }}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-civic-200 bg-white text-sm font-medium text-civic-900 focus:outline-none focus:ring-2 focus:ring-saathi-500 touch-target"
                  >
                    <option value="">-- {t("wizard.select_state")} --</option>
                    {options?.states_and_districts.map((s) => (
                      <option key={s.state_en} value={s.state_en}>
                        {isHindi ? s.state_hi : s.state_en}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="district-select" className="block text-xs font-bold text-civic-800">
                    {t("wizard.select_district")}
                  </label>
                  <select
                    id="district-select"
                    value={districtName}
                    disabled={!stateName}
                    onChange={(e) => setDistrictName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-civic-200 bg-white text-sm font-medium text-civic-900 focus:outline-none focus:ring-2 focus:ring-saathi-500 disabled:opacity-50 touch-target"
                  >
                    <option value="">{t("wizard.all_districts")}</option>
                    {selectedStateObj?.districts.map((d) => (
                      <option key={d.name_en} value={d.name_en}>
                        {isHindi ? d.name_hi : d.name_en}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Work Mode Select */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-civic-800">
                  {t("wizard.work_mode")}
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {options?.work_modes.map((wm) => {
                    const isSelected = workMode === wm.code;
                    return (
                      <button
                        key={wm.code}
                        type="button"
                        onClick={() => setWorkMode(wm.code)}
                        className={`p-2.5 rounded-xl border text-xs font-semibold text-center transition touch-target ${
                          isSelected
                            ? "bg-saathi-600 text-white border-saathi-700 shadow-xs"
                            : "bg-white text-civic-800 border-civic-200 hover:bg-civic-50"
                        }`}
                      >
                        {isHindi ? wm.label_hi : wm.label_en}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Preference vs Mandatory Constraints */}
              <div className="space-y-3 pt-3 border-t border-civic-100">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={willingToRelocate}
                    onChange={(e) => setWillingToRelocate(e.target.checked)}
                    className="w-4 h-4 mt-0.5 rounded text-saathi-600 focus:ring-saathi-500 border-civic-300"
                  />
                  <span className="text-xs sm:text-sm text-civic-800 font-medium leading-tight">
                    {t("wizard.relocate_label")}
                  </span>
                </label>

                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isWorkModeMandatory}
                    onChange={(e) => setIsWorkModeMandatory(e.target.checked)}
                    className="w-4 h-4 mt-0.5 rounded text-saathi-600 focus:ring-saathi-500 border-civic-300"
                  />
                  <span className="text-xs sm:text-sm text-civic-800 font-medium leading-tight">
                    {t("wizard.must_be_remote")}
                  </span>
                </label>

                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isLocationMandatory}
                    disabled={!stateName}
                    onChange={(e) => setIsLocationMandatory(e.target.checked)}
                    className="w-4 h-4 mt-0.5 rounded text-saathi-600 focus:ring-saathi-500 border-civic-300 disabled:opacity-50"
                  />
                  <span className="text-xs sm:text-sm text-civic-800 font-medium leading-tight">
                    {t("wizard.strict_location")}
                  </span>
                </label>
              </div>
            </div>
          )}

          {/* Navigation Controls */}
          <div className="pt-8 border-t border-civic-100 flex items-center justify-between gap-3">
            {step > 1 ? (
              <button
                type="button"
                onClick={handleBack}
                className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-civic-200 text-civic-700 hover:bg-civic-50 text-sm font-semibold transition touch-target"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>{t("wizard.back")}</span>
              </button>
            ) : (
              <div />
            )}

            {step < 4 ? (
              <button
                type="button"
                onClick={handleNext}
                className="inline-flex items-center gap-1.5 px-6 py-2.5 rounded-xl bg-saathi-600 hover:bg-saathi-700 text-white text-sm font-bold shadow-sm transition touch-target"
              >
                <span>{t("wizard.next")}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-saathi-600 hover:bg-saathi-700 text-white text-sm font-bold shadow-md transition disabled:opacity-75 touch-target"
              >
                {submitting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                <span>{submitting ? t("wizard.loading") : t("wizard.submit")}</span>
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
