from pydantic import BaseModel, Field
from typing import List, Optional

class TriageRequest(BaseModel):
    message: str = Field(..., description="The incoming finance communication text.")

class ExtractedEntities(BaseModel):
    account_ids: List[str] = Field(default_factory=list, description="Extracted account numbers or IDs.")
    dates: List[str] = Field(default_factory=list, description="Mentioned dates or timeframes.")
    amounts: List[str] = Field(default_factory=list, description="Monetary amounts mentioned.")
    other_entities: List[str] = Field(default_factory=list, description="Other critical entities like company names or locations.")

class TriageResponse(BaseModel):
    intent: str = Field(..., description="The primary intent of the message (e.g., Wire Transfer, Dispute, Inquiry).")
    urgency: str = Field(..., description="Urgency level: Low, Medium, High, or Critical.")
    entities: ExtractedEntities = Field(..., description="Entities extracted from the text.")
    draft_response: str = Field(..., description="A professional draft response addressing the user's message.")
