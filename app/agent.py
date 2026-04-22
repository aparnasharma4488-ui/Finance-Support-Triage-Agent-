import os
import json
from google import genai
from pydantic import ValidationError
from .models import TriageRequest, TriageResponse, ExtractedEntities

client = None
try:
    if os.environ.get("GEMINI_API_KEY"):
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"Warning: Could not initialize Gemini client. {e}")

def get_mock_response(message: str) -> TriageResponse:
    # A simple mock fallback if no API key is present
    intent = "General Inquiry"
    urgency = "Medium"
    
    message_lower = message.lower()
    
    if "urgent" in message_lower or "asap" in message_lower or "immediate" in message_lower:
        urgency = "High"
    if "fraud" in message_lower or "unauthorized" in message_lower:
        urgency = "Critical"
        intent = "Fraud Report"
    elif "wire" in message_lower or "transfer" in message_lower:
        intent = "Wire Transfer"
    elif "dispute" in message_lower or "fee" in message_lower:
        intent = "Fee Dispute"
    
    import re
    # Extract Indian currency or US currency for the mock intelligently
    amounts_extracted = re.findall(r'(?:[₹$]|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?', message, flags=re.IGNORECASE)
        
    entities = ExtractedEntities(
        account_ids=["MOCK-ACC-9912"] if "account" in message_lower else [],
        dates=["Today"],
        amounts=amounts_extracted,
        other_entities=[]
    )
    
    draft = (
        f"Thank you for reaching out regarding your {intent.lower()}. We have prioritized your message as "
        f"{urgency.upper()} urgency. Our specialized finance team is currently reviewing your request and details. "
        "We will get back to you shortly with next steps."
    )
    
    return TriageResponse(
        intent=intent,
        urgency=urgency,
        entities=entities,
        draft_response=draft
    )

def analyze_finance_message(request: TriageRequest) -> TriageResponse:
    if not client:
        print("Using Mock Agent (No API Key found or client failed to init)")
        return get_mock_response(request.message)
        
    prompt = f"""
    You are an expert AI Triage Assistant for a Financial institution.
    Analyze the following incoming communication from a customer:
    
    "{request.message}"
    
    Perform the following tasks:
    1. Determine the primary intent of the message (e.g., Wire Transfer, Dispute, Account Inquiry, Fraud Report, Loan Application, etc.).
    2. Assess the urgency level (Low, Medium, High, Critical). Fraud or security issues are Critical.
    3. Extract relevant Named Entities: account IDs, dates, monetary amounts, and other notable entities.
    4. Draft a contextually accurate, compliant, and professional response (1-2 paragraphs) acknowledging their request and outlining logical next steps. Be polite and helpful.
    
    Provide your output strictly in the following JSON schema:
    {{
        "intent": "string",
        "urgency": "string",
        "entities": {{
            "account_ids": ["string"],
            "dates": ["string"],
            "amounts": ["string"],
            "other_entities": ["string"]
        }},
        "draft_response": "string"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        response_text = response.text
        data = json.loads(response_text)
        return TriageResponse(**data)
        
    except Exception as e:
        print(f"Error calling LLM APIs: {e}. Falling back to mock.")
        return get_mock_response(request.message)
