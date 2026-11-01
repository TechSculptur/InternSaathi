import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { WelcomePage } from "./pages/WelcomePage";
import { WizardPage } from "./pages/WizardPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { InternshipDetailPage } from "./pages/InternshipDetailPage";
import { SavedPage } from "./pages/SavedPage";
import { ResumeTailoringPage } from "./pages/ResumeTailoringPage";

export const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/wizard" element={<WizardPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/internships/:id" element={<InternshipDetailPage />} />
          <Route path="/saved" element={<SavedPage />} />
          <Route path="/tailor-resume" element={<ResumeTailoringPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
