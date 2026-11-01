# Demonstration & Walkthrough Guide

This walkthrough guide provides step-by-step instructions for evaluating **Internship Saathi** across multiple realistic user personas.

---

## 1. Prerequisites Check
Ensure both backend and frontend servers are running:
- Backend: `http://127.0.0.1:8000` (API documentation at `/docs`)
- Frontend: `http://127.0.0.1:5173`

---

## 2. Test Scenarios

### Scenario A: Rural First-Time Applicant (10th Pass, Beginner / No Computer Skills)
**Objective**: Verify that the system recommends entry-level positions without penalizing the candidate for lack of skills or resume.

1. Open `http://127.0.0.1:5173`.
2. Click **Start Finding Internships** (or toggle language to हिन्दी).
3. **Step 1 (Education)**: Choose **10th Pass / Secondary**. Click Continue.
4. **Step 2 (Skills)**: Click **"I am a beginner / Not sure yet"**. Notice that no specific skills are required. Click Continue.
5. **Step 3 (Sectors)**: Select **Agriculture & Rural Tech** and **Logistics & Retail Operations**. Click Continue.
6. **Step 4 (Location)**:
   - State: **Maharashtra**
   - District: **Pune**
   - Work Mode: **On-site**
   - Keep "I am open to relocating" checked.
7. Click **Find My Internships**.
8. **Expected Result**:
   - Up to 5 recommendations appear with badges such as *"Open to beginners: no prior specialized skills required."* and *"Aligned with your sector interest"*.
   - Entry-level agricultural and warehouse opportunities are ranked highest.
   - Match scores are truthful (Good Match / Relevant Opportunity) without claiming inflated numbers.

---

### Scenario B: 12th Pass Applicant with IT Skills & Strict Remote Constraint
**Objective**: Verify mandatory constraint enforcement and skill overlap scoring.

1. Navigate to `/wizard`.
2. **Step 1 (Education)**: Select **12th Pass / Higher Secondary**.
3. **Step 2 (Skills)**: Search and select **Python Programming** and **MS Excel & Spreadsheets**.
4. **Step 3 (Sectors)**: Select **IT & Digital Services**.
5. **Step 4 (Location & Mode)**:
   - Work Mode: **Remote / Work from Home**
   - Check **"Strictly Remote only (Work from Home)"** (Mandatory Constraint).
6. Click **Find My Internships**.
7. **Expected Result**:
   - 100% of the returned recommendations have work mode **remote**.
   - High relative match score (>= 80%, "Strong Match") reflecting Python and MS Excel skill alignment.
   - Clear reasons detailing skill overlap.

---

### Scenario C: Bilingual Language Switcher
**Objective**: Verify seamless English-to-Hindi language switching.

1. On any page, locate the **हिन्दी / English** pill in the top navigation bar.
2. Click the button.
3. Observe all static labels, progress titles, sector names, and reason codes smoothly transition to Hindi.
4. Refresh the page: the selected language persists in `localStorage`.

---

### Scenario D: Bookmarking & Offline PWA Shell
**Objective**: Verify client-side bookmarking and offline awareness.

1. On the recommendations page, click the **Bookmark icon** on any card.
2. Notice the bookmark badge updates to "Bookmarked".
3. Navigate to the **Saved** tab in the navigation bar.
4. The bookmarked internship is displayed with complete details.
5. In Developer Tools (F12) -> Network tab, toggle **Offline**.
6. Refresh the page: the application shell loads immediately from the service worker cache, and an amber alert informs the user: *"You are offline. Recommendations require an active local connection."*
