import type { GlobalState } from "./types";
import { v4 as uuidv4 } from "uuid";

// Helper to query Semantic Scholar
async function searchSemanticScholar(query: string): Promise<any[]> {
  try {
    const url = `https://api.semanticscholar.org/graph/v1/paper/search?query=${encodeURIComponent(
      query
    )}&fields=paperId,title,abstract,authors,year,citationCount,referenceCount,openAccessPdf,fieldsOfStudy,tldr&limit=12`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Semantic Scholar API status: ${response.status}`);
    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.error("Semantic Scholar search failed, using fallback:", error);
    return [];
  }
}

// Unified query helper for Gemini and Groq
async function queryLLM(
  provider: "gemini" | "groq",
  apiKey: string,
  model: string,
  prompt: string
): Promise<any> {
  if (provider === "groq") {
    const url = "https://api.groq.com/openai/v1/chat/completions";
    const payload = {
      model,
      messages: [{ role: "user", content: prompt }],
      response_format: { type: "json_object" }
    };
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(
        err?.error?.message || `Groq API returned status ${response.status}`
      );
    }
    const result = await response.json();
    const text = result?.choices?.[0]?.message?.content;
    if (!text) throw new Error("Empty response from Groq API");
    
    try {
      return JSON.parse(text);
    } catch (e) {
      console.error("Failed to parse Groq response as JSON. Output was:", text);
      throw new Error("Groq response was not valid JSON");
    }
  } else {
    // Gemini
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    const payload: any = {
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { responseMimeType: "application/json" }
    };
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData?.error?.message || `Gemini API returned status ${response.status}`
      );
    }
    const result = await response.json();
    const text = result?.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!text) throw new Error("Empty response from Gemini API");
    
    try {
      return JSON.parse(text);
    } catch (e) {
      console.error("Failed to parse Gemini response as JSON. Output was:", text);
      throw new Error("Gemini response was not valid JSON");
    }
  }
}

export async function runFullResearchPipeline(
  provider: "gemini" | "groq",
  question: string,
  apiKey: string,
  model: string = "gemini-2.5-flash",
  onProgress: (step: string, message: string, state?: Partial<GlobalState>) => void
): Promise<GlobalState> {
  onProgress("orchestrator_parse", "Forwarding request to Python Backend (Agents)...");

  try {
    const response = await fetch("http://localhost:8000/api/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question, api_key: apiKey })
    });
    
    if (!response.ok) {
      throw new Error(`Backend returned status ${response.status}`);
    }
    
    const globalState = await response.json();
    onProgress("completed", "Pipeline completed successfully!", globalState);
    return globalState;
  } catch (error) {
    console.error("Failed to hit Python backend:", error);
    onProgress("completed", "Pipeline failed to communicate with backend.", {});
    throw error;
  }
}
