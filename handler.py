import json
import asyncio
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.development_workflow.agent import root_agent

import os
from dotenv import load_dotenv

# Setup Logging for CloudWatch and local debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

# Initialize services globally
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="pediatric-rcm-automation",
    session_service=session_service
)

async def run_pipeline(patient_note, request_id):
    """Handles the async execution of the ADK runner and logs steps."""
    
    # 1. Properly await the session creation to avoid NoneType errors
    session = await session_service.create_session(
        app_name="pediatric-rcm-automation",
        user_id="api-user",
        session_id=request_id
    )

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=patient_note)]
    )

    final_report = "No report generated."
    
    # 2. Use a regular 'for' loop for the runner.run generator to avoid loop conflicts
    for adk_event in runner.run(
        user_id="api-user",
        session_id=session.id,
        new_message=content
    ):
        # 3. Use getattr to safely log attributes that may be missing on some event types
        agent_name = getattr(adk_event, 'agent_name', None)
        if agent_name:
            logger.info(f"--- [AGENT: {agent_name}] ---")

        tool_use = getattr(adk_event, 'tool_use', None)
        if tool_use:
            logger.info(f"Tool Call: {tool_use.name} | Args: {tool_use.input}")

        # Capture the final text result from the BillingFinalizer agent
        if adk_event.is_final_response():
            final_report = adk_event.content.parts[0].text
            
    return final_report

def lambda_handler(event, context):
    try:
        # Support both direct invocation and API Gateway events
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)
            
        patient_note = body.get("note", "")
        
        if not patient_note:
            return {"statusCode": 400, "body": json.dumps({"error": "No note provided"})}

        # Run the async pipeline within the synchronous Lambda entry point
        report = asyncio.run(run_pipeline(patient_note, context.aws_request_id))

        # --- Return as JSON with the key 'result' as requested ---
        return {
            "statusCode": 200,
            "body": json.dumps({"result": report})
        }
    except Exception as e:
        logger.error(f"Lambda Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
