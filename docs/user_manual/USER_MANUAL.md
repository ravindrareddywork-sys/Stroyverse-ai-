# StoryVerse AI — Official User Manual & Operations Guide
**Platform Name:** StoryVerse AI  
**Project Title:** Story and Script Generator Using Generative AI  
**Version:** 2.0.0 (Production & Academic Edition)  
**Date:** November 2026  

---

## 1. System Requirements & Prerequisites

Before setting up StoryVerse AI, verify your system meets the following specifications:

- **Operating System:** Windows 10/11, macOS 12+, or modern Linux (Ubuntu 22.04 LTS / Debian 12).
- **Python Runtime:** Python 3.10, 3.11, or 3.12 (Python 3.11+ recommended).
- **Web Browser:** Google Chrome 110+, Microsoft Edge 110+, Mozilla Firefox 115+, or Apple Safari 16+.
- **Internet Access:** Required only when using live Google Gemini API mode (not required in Mock AI mode).
- **Disk Space:** Approximately 250 MB free disk space for Python virtual environment and dependencies.

---

## 2. Step-by-Step Installation & Setup

### Step 2.1: Clone or Extract Project
Open your terminal (PowerShell, Command Prompt, or bash) and navigate to the project directory:
```bash
cd "C:\Users\djana\Downloads\STORYVERSE AI final\StoryVerse-AI"
```

### Step 2.2: Create and Activate a Python Virtual Environment
Creating a virtual environment ensures Python packages are isolated:

**On Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux (bash/zsh):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### Step 2.3: Install Python Backend Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Environment Configuration

### Step 3.1: Configure Environment Variables
In the `backend/` folder, copy `.env.example` to create `.env`:

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**On macOS / Linux:**
```bash
cp .env.example .env
```

### Step 3.2: Choose Your AI Provider Mode

#### Mode A: Mock Mode (Recommended for Offline Testing / Viva Evaluation)
If you do not have an API key, or wish to run quota-free evaluations:
```ini
AI_PROVIDER=mock
AI_MOCK_MODE=true
```
In this mode, all story generation, screenplay formatting, character bibles, and writing assistant features will operate deterministically using the built-in mock engine.

#### Mode B: Live Google Gemini Mode
To connect real Google Gemini generative AI:
1. Obtain a free API key from Google AI Studio: [https://aistudio.google.com](https://aistudio.google.com)
2. Open `backend/.env` in a text editor and set:
```ini
AI_PROVIDER=gemini
AI_MOCK_MODE=false
GEMINI_API_KEY=AIzaSyYourActualSecretKeyHere
GEMINI_MODEL=gemini-2.5-flash
```
*(Never share, commit, or publicly publish your `.env` file!)*

---

## 4. Starting the Application

### Step 4.1: Start the Flask Backend Server
With your virtual environment activated inside the `backend/` directory:
```bash
python app.py
```
You will see output similar to:
```
[INFO] app: Starting StoryVerse AI in 'development' mode
[INFO] app: Database tables created / verified.
[INFO] services.export_service: Registered ReportLab Unicode font: NirmalaUI
[INFO] app: All route blueprints registered.
 * Running on http://127.0.0.1:5000
```
Verify the backend is live by opening [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health) in your browser. You should receive `{"success": true, "data": {"status": "healthy"}}`.

### Step 4.2: Start the Frontend Interface
You can serve the frontend using any static web server:

**Option 1: Using Python's built-in HTTP server (Simplest):**
Open a second terminal window:
```powershell
cd "C:\Users\djana\Downloads\STORYVERSE AI final\StoryVerse-AI\frontend"
python -m http.server 3000
```
Then open [http://localhost:3000](http://localhost:3000) in your web browser.

**Option 2: Using VS Code Live Server Extension:**
Right-click `frontend/index.html` in VS Code and select **"Open with Live Server"** (runs on port 5500).

---

## 5. Feature Walkthroughs & User Guides

### 5.1: Story Generator (`pages/story.html`)
1. Click **"Story Generator"** in the top navigation bar.
2. In the **Story Topic** field, enter your premise (e.g. *"A lighthouse keeper discovers a radio signal broadcasting events 24 hours into the future"*).
3. Select your **Genre** (Fantasy, Sci-Fi, Horror, Mystery, Thriller, Romance, etc.).
4. Select your **Language** (English, Telugu, Tamil, or Hindi).
5. Choose **Tone**, **Length** (Short, Medium, Long), and **Audience**.
6. Click **"🚀 Generate Full Story"**.
7. The system displays:
   - **Synopsis & Narrative Metadata**.
   - **Structured 10-Act Outline Accordions** (Exposition, Inciting Incident, Climax, Resolution).
   - **Editable Manuscript View** allowing manual additions.
8. Click **"🔍 Expand"** to inject vivid sensory details, or **"✍️ Continue"** to extend the narrative.
9. Click **"💾 Save Project"** to store your story in the database portfolio.

### 5.2: Screenplay Studio (`pages/script.html`)
1. Click **"Script Generator"** in the navigation bar.
2. Enter your screenplay logline or scene prompt (e.g. *"A detective interrogates an art dealer about a missing Renaissance painting"*).
3. Select the number of initial scenes (1 to 20).
4. Click **"🎬 Generate Screenplay"**.
5. The screenplay is rendered in Hollywood Courier format with centered character speaking cues and scene headings.
6. Toggle between **"Screenplay Format"**, **"Scene Cards"**, and **"Editable Manuscript"**.
7. Click **"➕ Add Scene"** to automatically generate and append subsequent scenes.
8. Click **"💾 Save Project"** to save to your portfolio.

### 5.3: Character Studio (`pages/characters.html`)
1. Click **"Character Studio"** in the navigation bar.
2. Enter a character concept (e.g. *"A retired cybernetic surgeon living in the neon underbelly of Neo-Tokyo"*).
3. Select Role (Protagonist, Antagonist, Supporting/Mentor, etc.), Genre, and Language.
4. Click **"🎭 Forging 3D Character Profile"**.
5. The 19-dimensional profile matrix renders:
   - Physical appearance, strengths, weaknesses, and fatal flaw.
   - Core psychological matrix (Core Want vs. Core Need, The Lie They Believe).
   - Backstory, internal conflict, and narrative development arc.
6. To generate companion characters, switch to **"Ensemble Variations"** and click **"Generate Ensemble Concepts"**.
7. Click **"💾 Save Project"** to store the character bible.

### 5.4: Workspace Editor & AI Writing Assistant (`pages/editor.html`)
1. Click **"Workspace Editor"** in the navigation bar.
2. Type or paste your manuscript in the main writing area.
3. Use the right-hand **AI Assistant Toolkit**:
   - **Rewrite Tab:** Highlight text and select a style (Improve Clarity, Make it Creative, Make it Engaging, etc.).
   - **Translate Tab:** Translate highlighted text or the full draft into Telugu, Tamil, or Hindi.
   - **Summarize Tab:** Generate a Short, Medium, or Detailed executive summary.
   - **Dialogue Tab:** Enter character names and scene context to generate back-and-forth dialogue.
   - **Plot Twist Tab:** Input a premise to receive surprising, logically grounded plot twists.
   - **Continue Tab:** Seamlessly continue the story from your last sentence.
4. Click **"💾 Save Draft"** to update your working project.

### 5.5: Project Portfolio & Dashboard (`pages/dashboard.html`)
1. Click **"Dashboard"** in the navigation bar.
2. View real-time portfolio statistics (Total Projects, Stories, Scripts, Characters).
3. Use the **Search bar** to find projects instantly by title or description keyword.
4. Filter by clicking category pills (**All**, **Stories**, **Screenplays**, **Characters**, **Other**).
5. Sort projects by **Recently Updated**, **Date Created**, or **Alphabetical (A–Z / Z–A)**.
6. Click **"✏️ Open"** on any project card to open it in the Workspace Editor.
7. Click **"📜 Versions"** to open the version history modal:
   - View past snapshots and changelog notes.
   - Inspect historical manuscript text.
   - Click **"Restore this Version"** to instantly revert your project to any prior snapshot.
8. Click **"🗑️"** to safely delete a project with confirmation.

---

## 6. Document Exporting Guide (TXT, PDF, DOCX)

Every page (Story, Script, Character, Editor, and Dashboard) includes an **"📥 Export ▾"** dropdown menu:

### Format 1: Plain Text (`.txt`)
- Generates clean UTF-8 text containing title, metadata headers, separator rules, and formatted paragraphs.
- Compatible with all text editors and word processors.

### Format 2: Adobe PDF (`.pdf`)
- Generates publication-ready PDF documents using ReportLab.
- Features custom running headers, document metadata callouts, and two-pass "Page X of Y" footers.
- Features embedded `NirmalaUI` TrueType font for rendering complex Telugu, Tamil, and Hindi scripts.

### Format 3: Microsoft Word (`.docx`)
- Generates genuine OpenXML Word documents via `python-docx`.
- Features Title styles, Heading 2 section headers, metadata banners, and styled paragraph spacing.
- Compatible with Microsoft Word, LibreOffice Writer, and Google Docs.

---

## 7. Troubleshooting Common Problems

| Problem | Cause | Solution |
|---|---|---|
| **Port 5000 Already in Use** | Another application or previous Flask instance is running on port 5000. | In PowerShell run: `Get-Process python \| Stop-Process` or run Flask on port 5001: `flask run -p 5001`. |
| **CORS Network Error in Browser Console** | The backend is not running, or frontend is served on an unlisted port. | 1. Ensure `python app.py` is actively running in a terminal. <br> 2. Ensure frontend is served on port 3000, 5000, 5500, or 8000. |
| **AI Quota Error (HTTP 429)** | Google Gemini API quota or rate limit exceeded. | Switch to Mock Mode in `backend/.env` (`AI_MOCK_MODE=true` and `AI_PROVIDER=mock`) to continue evaluation quota-free. |
| **PDF Indic Characters Show Fallback Font** | Running on a Linux machine without Indic fonts installed. | Install Indic font packages via: `sudo apt-get install fonts-deva fonts-telu fonts-taml` or run via Docker. |
| **Database Locks or Migration Warnings** | An old SQLite file has schema mismatches. | Delete `backend/storyverse.db` or `backend/instance/storyverse.db`; the application will automatically recreate fresh tables on startup. |
