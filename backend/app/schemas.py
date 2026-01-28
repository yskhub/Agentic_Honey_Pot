from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MessageModel(BaseModel):
    sender: str
    text: str
    timestamp: datetime

class IngestRequest(BaseModel):
    sessionId: str
    message: MessageModel
    # Use None as default to avoid mutable default issues
    conversationHistory: Optional[List[MessageModel]] = None
    metadata: Optional[dict] = None

class IngestResponse(BaseModel):
    status: str = "success"
    scamProbability: float
    routeToAgent: bool = False
    sessionId: str
    reasons: Optional[List[str]] = []
