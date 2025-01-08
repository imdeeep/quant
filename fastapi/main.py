from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
from typing import Optional, Dict, Any
from scrap import scrape_instagram_profile

app = FastAPI()

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "9edb9b8e-f9ed-418a-8cf9-4c44fb6c36b7"
FLOW_ID = "8f31b8ec-f233-42de-80b2-e4531bdd709e"
APPLICATION_TOKEN = "AstraCS:GGdXaiSpFWFHxopZzLlJwCiQ:0afc2bca9af24ac11bea466215f8adb1b77691a8ced551164d1b146bb5580940"
ENDPOINT = FLOW_ID

# Default tweaks
TWEAKS = {
    "ChatInput-PVxoG": {},
    "ChatOutput-QqjiD": {},
    "Prompt-pXVnT": {},
    "Agent-UcVdC": {},
    "AstraDBToolComponent-Wy97B": {}
}

# Request model
class FlowRequest(BaseModel):
    message: str
    tweaks: Optional[Dict[str, Any]] = TWEAKS
    output_type: str = "chat"
    input_type: str = "chat"

async def run_flow(message: str,
                  endpoint: str,
                  output_type: str = "chat",
                  input_type: str = "chat",
                  tweaks: Optional[dict] = None) -> dict:
    """Run a flow with a given message and optional tweaks."""
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }

    if tweaks:
        payload["tweaks"] = tweaks

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

def clean_response(raw_response):
    """Clean and format the Langflow response"""
    try:
        # Extract the main message from the nested response
        outputs = raw_response.get('outputs', [])[0]
        if not outputs:
            return {"error": "No output found"}

        message_result = outputs.get('outputs', [])[0].get('results', {}).get('message', {})
        
        cleaned_response = {
            "status": "success",
            "message": {
                "text": message_result.get('text', ''),
                "timestamp": message_result.get('timestamp', ''),
                "session_id": message_result.get('session_id', '')
            }
        }

        # Extract content blocks if they exist
        content_blocks = message_result.get('content_blocks', [])
        if content_blocks:
            for block in content_blocks:
                if block.get('title') == 'Agent Steps':
                    cleaned_response['agent_steps'] = block.get('contents', [])

        return cleaned_response

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error formatting response: {str(e)}"
        }

@app.get("/")
def read_root():
    return {"Applicaiton Working": "True"}

@app.post("/run-flow")
async def process_flow(request: FlowRequest):
    """
    Process a flow with the given message and parameters
    """
    try:
        raw_response = await run_flow(
            message=request.message,
            endpoint=ENDPOINT,
            output_type=request.output_type,
            input_type=request.input_type,
            tweaks=request.tweaks
        )
        
        # Format the response
        formatted_response = clean_response(raw_response)
        return formatted_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}  #124 lines

class InstagramRequest(BaseModel):
    username: str
    results_limit: Optional[int] = 5

class PostInsertStatus(BaseModel):
    post_id: str
    post_data: dict
    db_insert_status: bool
    insert_message: str

class InstagramResponse(BaseModel):
    success: bool
    profile_data: Optional[dict]
    profile_db_status: bool
    profile_db_message: str
    posts_data: list[PostInsertStatus]
    total_posts: int
    error: Optional[str] = None

@app.post("/scrape-instagram/", response_model=InstagramResponse)
async def scrape_instagram(request: InstagramRequest):
    """
    Scrape Instagram profile and posts data with database insertion status
    
    Parameters:
    - username: Instagram username to scrape
    - results_limit: Number of posts to fetch (default: 5)
    
    Returns:
    - Profile data with DB insertion status
    - Posts data with individual DB insertion status
    - Total posts count
    """
    try:
        result = scrape_instagram_profile(
            username=request.username,
            results_limit=request.results_limit
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['error'] or "Failed to scrape Instagram data"
            )
        
        # Add total_posts to the result
        result['total_posts'] = result['profile_data'].get('total_posts', len(result['posts_data']))
            
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

