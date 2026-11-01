import { useState, useEffect } from "react";

const STORAGE_KEY = "saathi_saved_ids";

export function useSavedInternships() {
  const [savedIds, setSavedIds] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(savedIds));
    } catch (e) {
      console.error("Failed to persist saved IDs to localStorage", e);
    }
  }, [savedIds]);

  const toggleSave = (id: string) => {
    setSavedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const isSaved = (id: string) => savedIds.includes(id);

  const clearSaved = () => {
    setSavedIds([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.error(e);
    }
  };

  return {
    savedIds,
    isSaved,
    toggleSave,
    clearSaved,
  };
}
