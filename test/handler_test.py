import json
import boto3
import os
import sys
import io
import zipfile
from moto import mock_aws

# Add parent directory to path so we can import handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handler import lambda_handler

# 1. Setup Mock Environment
os.environ['RESULTS_TABLE'] = 'PediatricRcmResults'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ.update({
    'AWS_ACCESS_KEY_ID': 'testing',
    'AWS_SECRET_ACCESS_KEY': 'testing'
})

class MockContext:
    def __init__(self):
        self.aws_request_id = "local-test-id-123"
        self.function_name = "PediatricRcmFunction"

def create_mock_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr('index.py', 'def handler(event, context): return {"statusCode": 200}')
    return zip_buffer.getvalue()

@mock_aws
def test_handler_full_loop(scenario_file):
    # --- SETUP: Mock Resources ---
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='PediatricRcmResults',
        KeySchema=[{'AttributeName': 'jobId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'jobId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    iam = boto3.client("iam", region_name="us-east-1")
    role = iam.create_role(RoleName="test-role", AssumeRolePolicyDocument=json.dumps({}))
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    lambda_client.create_function(
        FunctionName="PediatricRcmFunction",
        Runtime="python3.9",
        Role=role["Role"]["Arn"],
        Handler="index.handler",
        Code={"ZipFile": create_mock_zip()},
    )

    # --- STEP 1: POST Flow (The Dispatcher) ---
    print("\n--- 1. Testing POST Flow ---")
    print(f"Loading scenario from: {scenario_file}")
    with open(scenario_file, "r") as f:
        file_content = json.load(f)
    
    # Handle both full event (with body) and raw payload
    if "body" in file_content:
        post_event = file_content
    else:
        post_event = {
            "body": json.dumps(file_content)
        }
    
    # Ensure httpMethod is set for the handler to process it as a POST
    post_event["httpMethod"] = "POST"
    
    # Extract note for use in Step 2 manual trigger
    note = json.loads(post_event["body"])["note"]
    
    post_res = lambda_handler(post_event, MockContext())
    job_id = json.loads(post_res['body'])['jobId']
    print(f"Job Created: {job_id}")

    # --- STEP 2: Worker Flow (The Manual Trigger) ---
    # In AWS, this happens automatically. Locally, we call it ourselves.
    print("\n--- 2. Manually Triggering Worker Flow ---")
    worker_event = {
        "worker_mode": True,
        "job_id": job_id,
        "note": note
    }
    lambda_handler(worker_event, MockContext())
    print("Worker execution finished.")

    # --- STEP 3: GET Flow (The Result) ---
    print("\n--- 3. Testing GET Flow for Result ---")
    get_event = {"httpMethod": "GET", "pathParameters": {"jobId": job_id}}
    get_res = lambda_handler(get_event, MockContext())
    data = json.loads(get_res['body'])
    
    print(f"Final Status: {data.get('status')}")
    print(f"Final Report: {data.get('result')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python handler_test.py <scenario_filename>")
        print("Example: python handler_test.py noinfo.json")
        sys.exit(1)
    
    scenario_name = sys.argv[1]
    # Check if a full path is provided or just filename
    if os.path.exists(scenario_name):
         scenario_path = scenario_name
    else:
        # Assuming scenarios are in 'scenarios' folder relative to this script
        scenario_path = os.path.join(os.path.dirname(__file__), 'scenarios', scenario_name)
    
    if not os.path.exists(scenario_path):
         print(f"Error: Scenario file not found at {scenario_path} or {scenario_name}")
         sys.exit(1)

    test_handler_full_loop(scenario_path)
