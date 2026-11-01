import React, { useEffect, useState } from "react";
import { FileText, Sparkles, Download, AlertCircle, CheckCircle2, LoaderCircle } from "lucide-react";
import { tailorResume, exportTailoredResume, fetchInternshipsForTailoring, fetchInternshipDetail, type ResumeTailoringResult } from "../services/api";

export const ResumeTailoringPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<ResumeTailoringResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState<Record<string, boolean>>({});
  const [internships, setInternships] = useState<Array<{ id: string; title: string; organization_name: string }>>([]);
  const [selectedInternship, setSelectedInternship] = useState("");

  useEffect(() => {
    fetchInternshipsForTailoring().then(setInternships).catch(() => setInternships([]));
  }, []);

  const chooseInternship = async (id: string) => {
    setSelectedInternship(id);
    if (!id) return;
    try {
      const detail = await fetchInternshipDetail(id);
      if (detail.description) setJd(detail.description);
    } catch {
      setError("Could not load this internship description. You can paste the JD manually.");
    }
  };

  const runTailoring = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(""); setResult(null); setLoading(true);
    try { setResult(await tailorResume(file as File, jd)); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to tailor resume."); }
    finally { setLoading(false); }
  };

  const updateList = (key: "skills" | "experience_bullets" | "projects" | "education" | "other_sections", value: string) => {
    setResult((current) => current ? { ...current, [key]: value.split("\n").map((item) => item.trim()).filter(Boolean) } : current);
  };

  const downloadResume = async () => {
    if (!result) return;
    try {
      const blob = await exportTailoredResume(result);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a"); anchor.href = url; anchor.download = result.filename || "internship_saathi_tailored_resume.docx"; anchor.click(); URL.revokeObjectURL(url);
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to export resume."); }
  };

  const renderList = (title: string, items?: string[]) => items?.length ? (
    <section className="bg-white rounded-xl border border-civic-200 p-4 space-y-2" key={title}>
      <h3 className="font-bold text-civic-900">{title}</h3>
      <ul className="list-disc pl-5 space-y-1 text-sm text-civic-700">{items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul>
    </section>
  ) : null;

  return <div className="max-w-4xl mx-auto space-y-6">
    <header className="space-y-2">
      <div className="inline-flex items-center gap-2 text-sm font-bold text-saathi-700"><Sparkles className="w-4 h-4" /> RESUME TOOL</div>
      <h1 className="text-2xl sm:text-3xl font-extrabold text-civic-900">Tailor your resume to a job description</h1>
      <p className="text-sm text-civic-700 max-w-2xl">Compare your resume with a specific internship, review relevant requirements, and generate a downloadable DOCX. Your original resume is not changed.</p>
    </header>

    <form onSubmit={runTailoring} className="bg-white rounded-2xl border border-civic-200 p-5 sm:p-6 space-y-5">
      <label className="block space-y-2"><span className="text-sm font-semibold text-civic-900">Upload resume (PDF or DOCX, max 5 MB)</span><span className="flex items-center gap-3 rounded-xl border border-dashed border-civic-300 p-4"><FileText className="w-6 h-6 text-saathi-600" /><input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required className="block w-full text-sm" /></span></label>
      <label className="block space-y-2"><span className="text-sm font-semibold text-civic-900">Choose an internship (optional)</span><select value={selectedInternship} onChange={(e) => chooseInternship(e.target.value)} className="w-full rounded-xl border border-civic-300 p-3 text-sm"><option value="">Paste a custom job description instead</option>{internships.map((item) => <option key={item.id} value={item.id}>{item.title} — {item.organization_name}</option>)}</select><span className="text-xs text-civic-700">Selecting an internship fills the description when one is available.</span></label>
      <label className="block space-y-2"><span className="text-sm font-semibold text-civic-900">Job description (JD)</span><textarea value={jd} onChange={(e) => setJd(e.target.value)} required minLength={30} maxLength={12000} rows={9} placeholder="Paste the internship job description, required skills, responsibilities and qualifications..." className="w-full rounded-xl border border-civic-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-saathi-500" /></label>
      <p className="text-xs text-civic-700">The resume text will be sent to the configured LLM provider for tailoring. Do not upload a resume unless you are comfortable with this processing.</p>
      {error && <div role="alert" className="rounded-lg bg-red-50 border border-red-200 text-red-700 p-3 text-sm flex gap-2"><AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />{error}</div>}
      <button type="submit" disabled={!file || jd.trim().length < 30 || loading} className="inline-flex items-center justify-center gap-2 rounded-xl bg-saathi-600 hover:bg-saathi-700 disabled:opacity-50 text-white px-5 py-3 text-sm font-bold">{loading ? <><LoaderCircle className="w-4 h-4 animate-spin" /> Analyzing and tailoring...</> : <><Sparkles className="w-4 h-4" /> Analyze and tailor resume</>}</button>
    </form>

    {result && <div className="space-y-4">
      <div className="bg-saathi-50 border border-saathi-200 rounded-xl p-4 flex gap-3"><CheckCircle2 className="w-5 h-5 text-saathi-700 shrink-0" /><div><h2 className="font-bold text-civic-900">Tailored resume is ready to review</h2><p className="text-sm text-civic-700 mt-1">{result.disclaimer}</p></div></div>
      <section className="bg-white rounded-xl border border-civic-200 p-4 space-y-4">
        <h3 className="font-bold text-civic-900">Review and edit your tailored resume</h3>
        <label className="block space-y-1"><span className="text-sm font-semibold">Professional summary</span><textarea value={result.professional_summary || ""} onChange={(e) => setResult((old) => old ? { ...old, professional_summary: e.target.value } : old)} rows={3} className="w-full rounded-lg border border-civic-300 p-3 text-sm" /></label>
        {([ ["Skills", "skills"], ["Experience bullets", "experience_bullets"], ["Projects", "projects"], ["Education", "education"], ["Additional information", "other_sections"] ] as const).map(([label, key]) => <label key={key} className="block space-y-1"><span className="text-sm font-semibold">{label} <span className="font-normal text-civic-700">(one item per line)</span></span><textarea value={(result[key] || []).join("\n")} onChange={(e) => updateList(key, e.target.value)} rows={Math.min(8, Math.max(2, (result[key] || []).length + 1))} className="w-full rounded-lg border border-civic-300 p-3 text-sm" /></label>)}
      </section>
      {renderList("Matched requirements", result.matched_requirements)}
      {renderList("Requirements not found in resume", result.missing_requirements)}
      {renderList("Why these changes were suggested", result.change_notes)}
      <div className="bg-white rounded-xl border border-civic-200 p-4 space-y-3"><p className="text-sm font-semibold text-civic-900">Before downloading</p>{["I checked that all statements are accurate","I removed claims I cannot support with real experience","I proofread the final document"].map((label) => <label key={label} className="flex gap-2 items-start text-sm text-civic-700"><input type="checkbox" checked={!!approved[label]} onChange={(e) => setApproved((old) => ({ ...old, [label]: e.target.checked }))} className="mt-1 accent-emerald-600" />{label}</label>)}<button type="button" onClick={downloadResume} disabled={!Object.values(approved).every(Boolean) || Object.keys(approved).length !== 3} className="inline-flex items-center gap-2 rounded-xl bg-saathi-600 hover:bg-saathi-700 disabled:opacity-50 text-white px-5 py-3 text-sm font-bold"><Download className="w-4 h-4" /> Download tailored DOCX</button></div>
    </div>}
  </div>;
};
