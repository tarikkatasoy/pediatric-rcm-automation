import json
from handler import lambda_handler

# 1. Mock the AWS Context object (needed for context.aws_request_id)
class MockContext:
    def __init__(self):
        self.aws_request_id = "local-test-id-123"

# 2. Define your test input (simulating an API Gateway POST body)
test_note = """
Patient is a 6-year-old female presenting with a sore throat and difficulty swallowing. 
Physical exam shows white exudates on tonsils. Rapid strep test was performed and came back positive.
"""

event = {
    "body": json.dumps({
        "note": test_note
    })
}

# 3. Execute the handler
print("--- Starting Local Agent Test ---")
response = lambda_handler(event, MockContext())

# 4. Print the final result
print(json.dumps(response, indent=2))
