# Product Requirements Document (PRD)

## Product Name

**SentinelTrap AI**

## One‑Line Pitch

An agentic AI honeypot that detects scam intent in real time, safely engages scammers, and extracts actionable intelligence without exposing users or tipping off attackers.

---

## 1. Problem Statement

Online scams (UPI fraud, phishing, fake job offers, romance scams, bank impersonation) evolve faster than static rule‑based systems. Existing solutions focus on blocking or flagging scams, which causes two major problems:

1. Low recall. Adaptive scammers bypass detection.
2. Zero intelligence gain. Once blocked, the scammer disappears.

There is a missing layer. Systems that **engage**, **learn**, and **extract intelligence** from scammers while keeping users safe.

---

## 2. Vision & Goals

### Vision

Build an AI‑powered agentic honeypot that behaves like a real human victim, dynamically adapts to scammer tactics, and extracts structured intelligence for prevention, law enforcement, and future model training.

### Primary Goals

* Detect scam intent with >95% precision
* Engage scammers autonomously without human intervention
* Extract structured intelligence (scripts, payment rails, phone numbers, wallets, domains)
* Never reveal detection or trigger scammer suspicion
* Operate ethically with strict guardrails

### Non‑Goals

* Not a user‑facing chat app
* Not a scammer harassment tool
* No real financial transactions

---

## 3. Target Users

1. **Banks & FinTechs** – Fraud intelligence
2. **Telecom Providers** – Scam call pattern detection
3. **Cybersecurity Teams** – Threat intelligence feeds
4. **Government & Law Enforcement** – Evidence‑ready scam intelligence

---

## 4. Core Use Case Flow

1. Incoming interaction (SMS, WhatsApp, email, chat, call transcript)
2. Scam intent classifier scores message
3. If score exceeds threshold, route to honeypot agent
4. Agent simulates a believable victim persona
5. Multi‑turn engagement with adaptive strategy
6. Intelligence extraction and validation
7. Risk‑free termination
8. Intelligence stored and visualized

---

## 5. System Architecture (High Level)

### Components

* Ingestion Layer
* Scam Intent Engine
* Agentic Conversation Engine
* Intelligence Extraction Engine
* Ethics & Safety Guardrails
* Intelligence Store
* Analyst Dashboard

---

## 6. Functional Requirements

### 6.1 Ingestion Layer

**Capabilities**

* Accept text, email, chat, call transcripts
* Normalize and timestamp messages

**Tech**

* FastAPI / Node.js
* Kafka / AWS SQS

---

### 6.2 Scam Intent Detection

**Capabilities**

* Binary and multi‑class classification
* Confidence scoring
* Continual learning

**Models**

* Transformer‑based classifier (BERT / DeBERTa)
* Fine‑tuned on scam corpora

**Tech**

* Python
* PyTorch
* AWS SageMaker

---

### 6.3 Agentic Honeypot Engine

**Capabilities**

* Multi‑persona simulation (elderly, student, job seeker)
* Strategy switching (confused, cooperative, skeptical)
* Long‑term memory per session
* Tool‑calling for fake artifacts

**Agent Design**

* Planner Agent
* Conversation Agent
* Memory Agent
* Safety Agent

**Tech**

* LangGraph / AutoGen‑style orchestration
* OpenAI / open‑source LLMs
* Redis (short‑term memory)

---

### 6.4 Intelligence Extraction

**Extracted Signals**

* Phone numbers
* Wallet IDs
* UPI IDs
* URLs and domains
* Scam scripts
* Emotional manipulation patterns

**Tech**

* Regex + NER
* LLM‑based structured extraction
* Confidence scoring

---

### 6.5 Ethics & Safety Layer

**Hard Rules**

* No real payments
* No PII exposure
* Automatic termination if illegal escalation detected

**Soft Rules**

* Emotionally neutral engagement
* No encouragement of violence or self‑harm

---

### 6.6 Intelligence Store

**Data Stored**

* Raw conversations
* Structured intelligence
* Risk metadata

**Tech**

* PostgreSQL (structured)
* S3 (raw logs)
* Vector DB (Pinecone / FAISS)

---

### 6.7 Analyst Dashboard

**Features**

* Live scam engagement view
* Intelligence timeline
* Pattern clustering
* Exportable reports

**Tech**

* Next.js
* Tailwind
* Framer Motion
* WebSockets (simulated for demo)

---

## 7. Non‑Functional Requirements

* Latency < 300ms per response
* Horizontal scalability
* Full audit logs
* GDPR‑aligned data handling

---

## 8. Development Phases

### Phase 1. Foundation (Weeks 1‑2)

* Define scam taxonomy
* Build ingestion APIs
* Create baseline classifier

**Deliverables**

* API skeleton
* Working intent model

---

### Phase 2. Agent MVP (Weeks 3‑4)

* Single persona honeypot
* Multi‑turn engagement
* Manual termination

**Deliverables**

* End‑to‑end demo

---

### Phase 3. Intelligence Extraction (Weeks 5‑6)

* Entity extraction
* Confidence scoring
* Storage pipeline

**Deliverables**

* Structured intelligence output

---

### Phase 4. Safety & Ethics (Week 7)

* Guardrails
* Kill‑switch logic
* Red‑team testing

---

### Phase 5. Dashboard & UX (Weeks 8‑9)

* Live conversation animation
* Session switching
* Light/dark mode

---

### Phase 6. Optimization & Scale (Week 10)

* Load testing
* Model fine‑tuning
* Final polish for judges

---

## 9. Tech Stack Summary

### Backend

* Python, FastAPI
* Node.js
* Kafka / AWS SQS

### AI/ML

* PyTorch
* OpenAI / Llama
* LangGraph

### Frontend

* Next.js
* Tailwind CSS
* Framer Motion

### Infra

* AWS (Lambda, ECS, S3)
* Docker
* GitHub Actions

---

## 10. Success Metrics

* Scam detection precision
* Average intelligence extracted per session
* Scammer engagement duration
* Zero real‑world harm incidents

---

## 11. Judge‑Appeal Factors

* Agentic autonomy
* Ethical clarity
* Real‑world applicability
* Visual intelligence extraction

---

## 12. Future Roadmap

* Voice‑based honeypot
* Cross‑scam graph analysis
* Law‑enforcement integrations

---



**Below is the competetion RUles and regulations must follow**

1. Online scams such as bank fraud, UPI fraud, phishing, and fake offers are becoming increasingly adaptive. Scammers change their tactics based on user responses, making traditional detection systems ineffective.
This challenge requires participants to build an Agentic Honey-Pot — an AI-powered system that detects scam intent and autonomously engages scammers to extract useful intelligence without revealing detection.
2. Objective
Design and deploy an AI-driven honeypot system that can:
●	Detect scam or fraudulent messages
●	Activate an autonomous AI Agent
●	Maintain a believable human-like persona
●	Handle multi-turn conversations
●	Extract scam-related intelligence
●	Return structured results via an API
3. What You Need to Build
Participants must deploy a public REST API that:
●	Accepts incoming message events
●	Detects scam intent
●	Hands control to an AI Agent
●	Engages scammers autonomously
●	Extracts actionable intelligence
●	Returns a structured JSON response
●	Secures access using an API key

4. API Authentication
●	x-api-key: YOUR_SECRET_API_KEY
●	Content-Type: application/json
5. Evaluation Flow
1.	Platform sends a suspected scam message
2.	Your system analyzes the message
3.	If scam intent is detected, the AI Agent is activated
4.	The Agent continues the conversation
5.	Intelligence is extracted and returned
6.	Performance is evaluated
6. API Request Format (Input)
Each API request represents one incoming message in a conversation.
6.1 First Message (Start of Conversation)
This is the initial message sent by a suspected scammer. There is no prior conversation history.
{
“sessionId”: “wertyu-dfghj-ertyui”,
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
6.2 Second Message (Follow-Up Message)
This request represents a continuation of the same conversation.
Previous messages are now included in conversationHistory.
{
“sessionId”: “wertyu-dfghj-ertyui”,
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": "2026-01-21T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": "2026-01-21T10:15:30Z"
    },
    {
      "sender": "user",
      "text": "Why will my account be blocked?",
      "timestamp": "2026-01-21T10:16:10Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
6.3 Request Body Field Explanation
message (Required)
The latest incoming message in the conversation.
Field	Description
sender	scammer or user
text	Message content
timestamp	ISO-8601 format
conversationHistory (Optional)
All previous messages in the same conversation.
●	Empty array ([]) for first message
●	Required for follow-up messages

metadata (Optional but Recommended)
Field	Description
channel	SMS / WhatsApp / Email / Chat
language	Language used
locale	Country or region
7. Agent Behavior Expectations
The AI Agent must:
●	Handle multi-turn conversations
●	Adapt responses dynamically
●	Avoid revealing scam detection
●	Behave like a real human
●	Perform self-correction if needed
8. Expected Output Format (Response)
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 420,
    "totalMessagesExchanged": 18
  },
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
9. Evaluation Criteria
●	Scam detection accuracy
●	Quality of agentic engagement
●	Intelligence extraction
●	API stability and response time
●	Ethical behavior
10. Constraints & Ethics
●	❌ No impersonation of real individuals
●	❌ No illegal instructions
●	❌ No harassment
●	✅ Responsible data handling
11. One-Line Summary
Build an AI-powered agentic honeypot API that detects scam messages, handles multi-turn conversations, and extracts scam intelligence without exposing detection.
12. Mandatory Final Result Callback (Very Important)
Once the system detects scam intent and the AI Agent completes the engagement, participants must send the final extracted intelligence to the GUVI evaluation endpoint.
This is mandatory for evaluation.
Callback Endpoint
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
Content-Type: application/json
Payload to Send
Participants must send the following JSON payload to the above endpoint:
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+91XXXXXXXXXX"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
🧠 When Should This Be Sent?
You must send this only after:
1.	Scam intent is confirmed (scamDetected = true)
2.	The AI Agent has completed sufficient engagement
3.	Intelligence extraction is finished
This should be treated as the final step of the conversation lifecycle.
________________________________________
🧩 Field Explanation
Field	Description
sessionId	Unique session ID received from the platform for this conversation
scamDetected	Whether scam intent was confirmed
totalMessagesExchanged	Total number of messages exchanged in the session
extractedIntelligence	All intelligence gathered by the agent
agentNotes	Summary of scammer behavior
⚠️ Important Rules
●	This callback is mandatory for scoring
●	If this API call is not made, the solution cannot be evaluated
●	The platform uses this data to measure:
○	Engagement depth
○	Intelligence quality
○	Agent effectiveness
💻 Example Implementation (Python)
intelligence_dict = {
    "bankAccounts": intelligence.bankAccounts,
    "upiIds": intelligence.upiIds,
    "phishingLinks": intelligence.phishingLinks,
    "phoneNumbers": intelligence.phoneNumbers,
    "suspiciousKeywords": intelligence.suspiciousKeywords
}

payload = {
    "sessionId": session_id,
    "scamDetected": scam_detected,
    "totalMessagesExchanged": total_messages,
    "extractedIntelligence": intelligence_dict,
    "agentNotes": agent_notes
}

response = requests.post(
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
    json=payload,
    timeout=5
)
🧾 Updated One-Line Summary
Build an AI-powered agentic honeypot API that detects scam messages, engages scammers in multi-turn conversations, extracts intelligence, and reports the final result back to the GUVI evaluation endpoint.


**Initial Submission to Judge**
Once evrythingcompleted we need to send below details to judge for initial stage:
This Honeypot API Endpoint Tester allows participants to validate whether their deployed honeypot service is reachable, secured, and responding correctly. The tester verifies authentication, endpoint availability, and response behavior using a simple request.
How to Use the Honeypot Endpoint Tester
This tool helps participants verify that their Honeypot API endpoint is properly deployed and secured.
Steps:
•	Enter your deployed Honeypot API endpoint URL
•	Provide the required API key in the request header
•	Click Test Honeypot Endpoint to send the request
What This Tests:
•	API authentication using headers
•	Endpoint availability and connectivity
•	Proper request handling
•	Response structure and status codes
•	Basic honeypot behavior validation
Note: This tester is for validation only. The final evaluation will involve automated security interaction scenarios.

**Final Submission to Judge**
•Agentic Honey-Pot — Your API must accept scam messages and return extracted intelligence

Evaluation Readiness
•	Ensure your API handles multiple requests reliably
•	Ensure correct JSON response format as defined in the problem statement
•	Ensure low latency and proper error handling

Outcome of This Level
•	Your endpoint moves to the automated evaluation stage
•	Results and scores will be generated based on API performance

**End of PRD**