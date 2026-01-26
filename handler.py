import json
import uuid
import boto3
import asyncio
import logging
import os
from dotenv import load_dotenv

# ADK and Gemini Imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.development_workflow.agent import root_agent

# 1. Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

# 2. Global Resource Initialization
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="pediatric-rcm-automation",
    session_service=session_service
)

# DynamoDB table name comes from template.yml environment variables
RESULTS_TABLE = os.environ.get('RESULTS_TABLE', 'PediatricRcmResults')
dynamo = boto3.resource('dynamodb').Table(RESULTS_TABLE)
lambda_client = boto3.client('lambda')

# 3. --- CORE ADK PIPELINE ---
async def run_pipeline(patient_note, request_id):
    logger.info(f"PIPELINE START: Request {request_id}")
    
    session = await session_service.create_session(
        app_name="pediatric-rcm-automation",
        user_id="api-user",
        session_id=request_id
    )

    content = types.Content(role="user", parts=[types.Part.from_text(text=patient_note)])
    final_report = "No report generated."
    
    # --- RETRY LOGIC FOR 429 ERRORS ---
    max_retries = 5
    for attempt in range(max_retries):
        try:
            for adk_event in runner.run(
                user_id="api-user",
                session_id=session.id,
                new_message=content
            ):
                agent_name = getattr(adk_event, 'agent_name', None)
                if agent_name:
                    logger.info(f"[AGENT: {agent_name}] processing... event: {adk_event}")
                if adk_event.is_final_response():
                    content = getattr(adk_event, 'content', None)
                    if content and hasattr(content, 'parts') and content.parts:
                        final_report = getattr(content.parts[0], 'text', str(content.parts[0]))
            
            break # Success! Exit the retry loop.

        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                # Exponential backoff: 2, 4, 8 seconds + a little "jitter"
                wait_time = (2 ** attempt) + random.random()
                logger.warning(f"429 Rate Limit hit. Retrying in {wait_time:.2f}s... (Attempt {attempt+1})")
                await asyncio.sleep(wait_time)
            else:
                raise e # Re-raise if it's not a 429 or we're out of retries
            
    return final_report

# 4. --- HELPER FLOW METHODS ---

def handle_get_flow(event):
    """Handles polling requests to check job status."""
    job_id = event.get("pathParameters", {}).get("jobId")
    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing jobId"})}

    logger.info(f"GET: Fetching status for {job_id}")
    response = dynamo.get_item(Key={'jobId': job_id})
    item = response.get('Item')

    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Job ID not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(item)
    }

def handle_post_flow(event, context):
    """Handles initial job dispatches and hand-off to worker."""
    job_id = str(uuid.uuid4())
    logger.info(f"POST: Initiating Job {job_id}")
    
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        note = body.get("note", "")
        
        if not note:
            return {"statusCode": 400, "body": json.dumps({"error": "No note provided"})}

        # Save 'Running' status
        dynamo.put_item(Item={'jobId': job_id, 'status': 'Running'})

        # Trigger Worker asynchronously
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',
            Payload=json.dumps({"worker_mode": True, "job_id": job_id, "note": note})
        )

        return {
            "statusCode": 202,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"jobId": job_id, "message": "Flow started"})
        }
    except Exception as e:
        logger.error(f"Post Flow Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to start flow"})}

def handle_worker_flow(event):
    """Handles background execution of the ADK pipeline."""
    job_id = event["job_id"]
    note = event["note"]
    logger.info(f"WORKER: Execution started for {job_id}")
    
    try:
        report = asyncio.run(run_pipeline(note, job_id))
        
        # FIXED: Use #r as a placeholder for the reserved keyword 'result'
        dynamo.update_item(
            Key={'jobId': job_id},
            UpdateExpression="set #s = :s, #res = :r",
            ExpressionAttributeNames={
                '#s': 'status', 
                '#res': 'result'  # This maps the placeholder to the actual column
            },
            ExpressionAttributeValues={
                ':s': 'Completed', 
                ':r': report
            }
        )
        logger.info(f"WORKER SUCCESS: Job {job_id} complete.")
        
    except Exception as e:
        logger.error(f"WORKER FAILURE: {str(e)}")
        # Note: 'error' is also risky, so we map it too
        dynamo.update_item(
            Key={'jobId': job_id},
            UpdateExpression="set #s = :s, #err = :e",
            ExpressionAttributeNames={
                '#s': 'status', 
                '#err': 'error'
            },
            ExpressionAttributeValues={
                ':s': 'Failed', 
                ':e': str(e)
            }
        )

# 5. --- MAIN ENTRY POINT ---

def lambda_handler(event, context):
    """Main router for API and Worker events."""
    
    # Check for internal Worker trigger
    if event.get("worker_mode"):
        handle_worker_flow(event)
        return
    
    # Route based on HTTP Method
    method = event.get("httpMethod")
    if method == "GET":
        return handle_get_flow(event)
    elif method == "POST":
        return handle_post_flow(event, context)

    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method not allowed"})
    }
