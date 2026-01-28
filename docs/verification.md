# System Verification and Monitoring

This document contains visual evidence of the system's execution, monitoring, and testing.

## 1. AWS CloudWatch Logs
Execution logs demonstrating the workflow steps in the cloud environment.

### POST Request Execution Logs

![CloudWatch POST API Log 1](../images/CloudWatch_PostApi_1.png)
*Figure 1: Initial POST request received - Lambda dispatcher creates jobId and initiates async worker invocation.*

![CloudWatch POST API Log 2](../images/CloudWatch_PostApi_2.png)
*Figure 2: Worker execution started - ADK pipeline initialization and ClinicalEntityExtractor processing.*

![CloudWatch POST API Log 3](../images/CloudWatch_PostApi_3.png)
*Figure 3: Agent refinement loop - MedicalCoderAgent and RevenueIntegrityJudge iterative processing.*

### GET Request Execution Logs

![CloudWatch GET API Log](../images/CloudWatch_GetApi_1.png)
*Figure 4: Status check request - Lambda queries DynamoDB and returns completed billing report.*

---

## 2. ADK Web Interface
Visualizations from the Agent Development Kit (ADK) showing the agent interactions.

![ADK Workflow Architecture](../images/GoogleAdk_Sample_Workflow_Diagram.png)
*Figure 5: Auto-generated workflow diagram showing multi-agent pipeline structure (SequentialAgent with nested LoopAgent).*

![ADK Agent Execution Trace - Clinical Extraction](../images/GoogleAdk_TraveView_1.png)
*Figure 6: ClinicalEntityExtractor phase - Tool calls (onboard_project, list_git_files, read_file) and clinical spec generation.*

![ADK Agent Execution Trace - Billing Refinement](../images/GoogleAdk_TraveView_2.png)
*Figure 7: BillingRefinementLoop execution - Knowledge base searches (11x), code proposal, audit verification, and approval.*

---

## 3. Postman API Testing
API endpoint testing results ensuring correct HTTP responses.

![Postman POST Request](../images/Postman_PostApi.png)
*Figure 8: POST /process-encounter - Job creation with 202 Accepted response (Duration: 3.92s, jobId returned).*

![Postman GET Status](../images/Postman_GetApi.png)
*Figure 9: GET /status/{jobId} - Completed job retrieval with 200 OK response (Duration: 557ms, final billing report returned).*

---

