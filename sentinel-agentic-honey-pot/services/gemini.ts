
import { GoogleGenAI, Type } from "@google/genai";
import { Message, HoneyPotSession, ApiResponse } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });

const SYSTEM_INSTRUCTION = `You are the core logic engine for 'SentinelTrap AI', an advanced Agentic Honey-Pot.
Your primary objective is to detect malicious intent and autonomously engage scammers to extract actionable intelligence without revealing detection.

OPERATIONAL GUIDELINES:
1. PERSONA ALIGNMENT:
   - 'Elderly': Use polite, slightly confused language. Mention 'grandchildren' or 'my slow computer'.
   - 'Student': Use casual language, sound eager but broke. Mention 'tuition' or 'assignment deadlines'.
   - 'Job Seeker': Use professional tone, sound desperate for work. Mention 'my resume' or 'family support'.
   - 'Small Business Owner': Sound busy, cautious, and protective of business credit.

2. STRATEGIC ENGAGEMENT:
   - 'Confused': Force the scammer to explain steps multiple times.
   - 'Cooperative': Agree to help but 'hit snags' (e.g., "The app says error 404, what now?").
   - 'Skeptical': Express fear of being hacked so they provide more "proof" (URLs/IDs).
   - 'Urgent': Mirror their urgency to trigger a fast payload delivery from them.

3. INTELLIGENCE EXTRACTION (VITAL):
   - Extract: Bank names/numbers, UPI IDs, Crypto wallets, Phishing URLs, Phone numbers.
   - Analyze: Psychological triggers (fear, greed, urgency), Scam scripts (exact wording), Emotional manipulation patterns.

4. ETHICS & SAFETY (GUARDRAILS):
   - NEVER share real personal data (PII).
   - NEVER encourage violence or illegal acts.
   - TERMINATE logic: If they ask for PII, provide realistic-looking fakes.

RESPONSE FORMAT:
Must be a valid JSON object matching the provided schema.`;

export const processScamMessage = async (session: HoneyPotSession, newMessage: Message): Promise<ApiResponse> => {
  const model = 'gemini-3-flash-preview';
  
  const historyString = session.conversationHistory
    .map(m => `${m.sender.toUpperCase()}: ${m.text}`)
    .join('\n');

  const prompt = `
    [SENTINEL_STATE]
    PERSONA: ${session.persona}
    STRATEGY: ${session.strategy}
    CONFIDENCE_THRESHOLD: 0.85
    
    [TRAFFIC_LOG]
    HISTORY:
    ${historyString}
    
    INCOMING_SIGNAL (SCAMMER):
    "${newMessage.text}"
    
    Task: Analyze the signal. If scam detected, generate the next engagement response to extract more intel. Output JSON.
  `;

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: [{ parts: [{ text: prompt }] }],
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            scamDetected: { type: Type.BOOLEAN },
            confidenceScore: { type: Type.NUMBER },
            agentNotes: { type: Type.STRING, description: "Technical summary of the scammer's tactical fingerprint." },
            extractedIntelligence: {
              type: Type.OBJECT,
              properties: {
                bankAccounts: { type: Type.ARRAY, items: { type: Type.STRING } },
                upiIds: { type: Type.ARRAY, items: { type: Type.STRING } },
                phishingLinks: { type: Type.ARRAY, items: { type: Type.STRING } },
                phoneNumbers: { type: Type.ARRAY, items: { type: Type.STRING } },
                suspiciousKeywords: { type: Type.ARRAY, items: { type: Type.STRING } },
                scamTactics: { type: Type.ARRAY, items: { type: Type.STRING }, description: "e.g., 'Bank Impersonation', 'Fake UPI Verification'" },
                emotionalManipulation: { type: Type.ARRAY, items: { type: Type.STRING }, description: "e.g., 'Fear of account block', 'Greed for lottery'" },
              },
              required: ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords", "scamTactics", "emotionalManipulation"]
            },
            nextResponse: { type: Type.STRING }
          },
          required: ["scamDetected", "confidenceScore", "agentNotes", "extractedIntelligence", "nextResponse"]
        }
      }
    });

    const result = JSON.parse(response.text);
    
    return {
      status: 'success',
      scamDetected: result.scamDetected,
      confidenceScore: result.confidenceScore,
      engagementMetrics: {
        engagementDurationSeconds: Math.floor((Date.now() - new Date(session.engagementMetrics.startTime).getTime()) / 1000),
        totalMessagesExchanged: session.conversationHistory.length + 2
      },
      extractedIntelligence: result.extractedIntelligence,
      agentNotes: result.agentNotes,
      nextResponse: result.nextResponse
    };
  } catch (error) {
    console.error("Sentinel Intelligence Error:", error);
    return {
      status: 'error',
      scamDetected: false,
      confidenceScore: 0,
      engagementMetrics: session.engagementMetrics,
      extractedIntelligence: session.extractedIntelligence,
      agentNotes: "Operational failure in intelligence parsing."
    } as any;
  }
};
