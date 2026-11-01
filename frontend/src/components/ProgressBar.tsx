import React from "react";
import { useTranslation } from "react-i18next";

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentStep,
  totalSteps,
}) => {
  const { t } = useTranslation();
  const stepLabels = [
    t("wizard.step_1"),
    t("wizard.step_2"),
    t("wizard.step_3"),
    t("wizard.step_4"),
  ];

  return (
    <div className="w-full mb-8">
      {/* Visual step bar */}
      <div className="flex items-center justify-between relative mb-2">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-civic-200 -z-0 -translate-y-1/2" />
        <div
          className="absolute top-1/2 left-0 h-1 bg-saathi-600 -z-0 -translate-y-1/2 transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }}
        />

        {Array.from({ length: totalSteps }, (_, i) => {
          const stepNum = i + 1;
          const isDone = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <div key={stepNum} className="flex flex-col items-center relative z-10">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all shadow-sm ${
                  isCurrent
                    ? "bg-saathi-600 text-white ring-4 ring-saathi-100"
                    : isDone
                    ? "bg-saathi-700 text-white"
                    : "bg-white text-civic-700 border-2 border-civic-200"
                }`}
                aria-current={isCurrent ? "step" : undefined}
              >
                {stepNum}
              </div>
              <span
                className={`text-xs mt-1.5 hidden sm:block font-medium ${
                  isCurrent ? "text-saathi-700 font-bold" : "text-civic-700"
                }`}
              >
                {stepLabels[i]}
              </span>
            </div>
          );
        })}
      </div>
      <div className="text-center sm:hidden text-xs font-semibold text-saathi-700">
        {stepLabels[currentStep - 1]} ({currentStep}/{totalSteps})
      </div>
    </div>
  );
};
