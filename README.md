# Manuscript Workbench | PS-AG8 Research Engine

An advanced, multi-agent AI pipeline designed to autonomously synthesize full academic research proposals from a single research question. The workbench utilizes a specialized architecture dividing cognitive workloads between **Groq (Llama 3.3)** and **Google Gemini (2.5 Flash)** to maximize speed and bypass rate limits.

## 🧠 Multi-Agent Architecture

The pipeline consists of 5 specialized agents that work sequentially:
1. **Orchestrator**: Parses the raw user query into structured variables.
2. **Literature Agent**: Interfaces with the Semantic Scholar API to retrieve real-world academic papers and synthesizes the current state of the art.
3. **Hypothesis Agent**: Formulates 3 distinct, testable hypotheses (Gap-filling, Mechanistic, Contrarian).
4. **Experiment Agent**: Designs rigorous, double-blind experimental methodologies with power analyses and budget estimates.
5. **Critique Agent & Synthesizer**: Peer-reviews the generated proposals for scientific rigor and ethical considerations before compiling the final APA-formatted manuscript.

## 🚀 Tech Stack
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Backend**: Python, FastAPI, Uvicorn
- **AI Models**: `llama-3.3-70b-versatile` (Groq), `gemini-2.5-flash` (Google Gemini)

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/AyushZorix/GenAI-hack.git
cd GenAI-hack
git checkout feature/multi-agent-llm-architecture
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your API keys. To ensure maximum throughput and avoid rate-limiting, the architecture expects multiple keys:
```env
# Specialized Agent Keys
GROQ_API_KEY_1=your_groq_key_here
GROQ_API_KEY_2=your_groq_key_here
GEMINI_API_KEY_1=your_gemini_key_here
GEMINI_API_KEY_2=your_gemini_key_here

# Academic Databases
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key
```

### 3. Start the Backend (FastAPI)
The Python backend handles all LLM orchestration and web scraping.
```bash
pip install fastapi uvicorn groq google-generativeai requests pydantic
uvicorn main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

### 4. Start the Frontend (Vite)
Open a second terminal window to run the React interface.
```bash
npm install
npm run dev
```
The frontend will run on `http://localhost:5173`.

## 💡 Usage
1. Open the frontend in your browser.
2. Enter a research question (e.g., *"What is the impact of microplastics on soil microbiome diversity?"*).
3. Click **Run Engine** in the navigation dock.
4. Watch the terminal logs as the autonomous agents perform literature reviews and draft the manuscript.
5. Export the final proposal to Markdown or copy the JSON payload directly from the UI.
