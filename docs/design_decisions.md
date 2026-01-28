# Design Decisions

This document explains key architectural choices made in this project and the trade-offs considered.

---

## 1. Docker + ECR (Instead of Lambda Layers)

### Decision
Package the application as a Docker container and store it in Amazon ECR (Elastic Container Registry).

### Context
AWS Lambda supports two deployment methods:
1. **Zip file + Lambda Layers** (max 250MB unzipped)
2. **Docker container images** (max 10GB)

Our dependencies exceed the Lambda layer limit:
```
google-adk (1.23.0) + google-genai (1.60.0) + pyarrow (18.0.0) ≈ 320MB
```

### Why Docker + ECR?
- **Dependency size**: Exceeds 250MB Lambda layer limit
- **Environment consistency**: Guarantees exact package versions across local dev, CI/CD, and AWS Lambda
- **Simplified packaging**: All code (agents, tools, knowledge base) bundled in one artifact
- **No layer management**: Don't need to track multiple layers or manage layer versions
- **Reproducibility**: Same `Dockerfile` runs identically on any machine

### Trade-offs
**Advantages:**
- No dependency size limits (up to 10GB)
- Includes system dependencies (if needed in future)
- Easier local testing (`docker run` matches Lambda exactly)

**Disadvantages:**
- Slightly slower cold starts (~500-800ms vs ~200ms for layers)
- Requires Docker Desktop installed locally
- Larger deployment artifacts (~500MB compressed vs ~150MB for layers)

### Alternatives Considered
1. **Lambda Layers + dependency trimming**
   - Rejected: Too fragile; removes important files, breaks unexpectedly
2. **Split into multiple Lambda functions with separate layers**
   - Rejected: Adds complexity; cold start still an issue per function
3. **AWS ECS/Fargate**
   - Rejected: Overkill for this workload; always-on costs

### Implementation
- Base image: `public.ecr.aws/lambda/python:3.13`
- Build time: ~2-3 minutes
- Deployed image size: ~500MB compressed
- Cold start: ~800ms, warm start: ~50ms

---

## 2. DynamoDB (Instead of RDS or S3)

### Decision
Use Amazon DynamoDB to store job state (jobId, status, result).

### Context
Need a storage solution to:
- Store job status during async processing
- Allow clients to poll for results via `GET /status/{jobId}`
- Support concurrent read/write from Lambda invocations

### Why DynamoDB?
- **Serverless**: No server management, auto-scales with load
- **Pay-per-request**: Only pay for actual reads/writes (no idle costs)
- **Low latency**: Sub-10ms reads for status polling
- **No connection pooling**: Unlike RDS, no need to manage connections in Lambda
- **Single-item lookups**: Our access pattern is simple (`GET by jobId`)

### Trade-offs
**Advantages:**
- $0.00 cost during development (free tier: 25GB storage, 25 read/write units)
- Instant scaling (no warm-up time)
- No cold starts (unlike RDS Aurora Serverless v1)

**Disadvantages:**
- Limited querying (can't do "get all jobs by user" without GSI)
- No ACID transactions across multiple jobs
- No complex joins or aggregations

### Alternatives Considered
1. **Amazon S3**
   - Rejected: 100ms+ latency unacceptable for status polling
   - Rejected: No atomic updates (race conditions on concurrent writes)
2. **Amazon RDS (PostgreSQL)**
   - Rejected: Connection pooling complexity in Lambda
   - Rejected: Minimum ~$15/month for smallest instance (vs $0 for DynamoDB in low usage)
3. **Amazon Aurora Serverless v2**
   - Rejected: Minimum 0.5 ACU = ~$45/month baseline cost

### Schema
```
Table: PediatricRcmResults
Primary Key: jobId (String, UUID format)
Attributes:
  - status: "Running" | "Completed" | "Failed"
  - result: Final billing report (String, Markdown format)
  - error: Error message (String, if status = "Failed")
  - confidence_score: 0-100 (Number, if status = "Completed")
```

### Cost Estimate
- Write: 1KB item × 100 requests/day = $0.00125/day
- Read: 1KB item × 200 requests/day = $0.00025/day
- **Total**: ~$0.05/month (well within free tier)

---

## 3. Two APIs: POST (Async) + GET (Polling)

### Decision
Split the API into two endpoints:
1. **POST /process-encounter** - Accepts patient note, returns jobId immediately (202 Accepted)
2. **GET /status/{jobId}** - Client polls this to check job status and retrieve results

### Context
The multi-agent pipeline (extractor → coder → auditor → finalizer) takes **30-90 seconds** to complete.

**Problem**: AWS API Gateway has a **29-second maximum timeout**. If we try to return the result synchronously, the request will fail.

### Why Async (POST) + Polling (GET)?
- **API Gateway timeout**: 29 seconds is not enough for agent execution (avg 45-60 seconds)
- **User experience**: Client gets immediate response (jobId) instead of waiting
- **Scalability**: Lambda can process multiple jobs in parallel
- **Resilience**: If client disconnects, job continues running
- **Standard pattern**: Common in long-running tasks (AWS Batch, Step Functions, etc.)

### Flow
```
1. Client → POST /process-encounter {note}
2. Lambda (Dispatcher Mode):
   - Generates jobId
   - Writes {jobId, status: "Running"} to DynamoDB
   - Invokes Lambda async (Worker Mode) with jobId
   - Returns 202 Accepted {jobId}
3. Lambda (Worker Mode):
   - Runs ADK pipeline (30-90 seconds)
   - Writes {jobId, status: "Completed", result} to DynamoDB
4. Client → GET /status/{jobId} (polls every 5 seconds)
5. Lambda (Dispatcher Mode):
   - Reads DynamoDB
   - Returns {jobId, status, result}
```

### Trade-offs
**Advantages:**
- No timeout issues (client gets instant response)
- Horizontal scaling (multiple jobs run in parallel)
- Client can poll at their own pace
- Works with any client (no WebSocket support needed)

**Disadvantages:**
- Client must implement polling logic
- More API calls (1 POST + N GETs vs 1 synchronous call)
- Slight UX delay (client waits 5-60 seconds polling)

### Alternatives Considered
1. **Synchronous API (return result in POST response)**
   - Rejected: API Gateway 29-second timeout
   - Rejected: Client must wait 60 seconds with connection open
2. **WebSockets (real-time push)**
   - Rejected: Requires WebSocket support on client
   - Rejected: More complex to implement and test
   - Rejected: Overkill for a polling interval of 5 seconds
3. **AWS Step Functions (orchestration)**
   - Rejected: Adds $25/month baseline cost (1000 state transitions/month minimum)
   - Rejected: Overkill for single Lambda function workflow
4. **Amazon SQS + Long Polling**
   - Rejected: Requires managing queue lifecycle
   - Rejected: DynamoDB + HTTP polling is simpler

### Why Not Use One API?
If we used only POST:
- Request times out after 29 seconds
- Client never gets the result
- Lambda continues running but client is disconnected

If we used only GET:
- How does client submit the patient note?
- Need POST for input, GET for output

**Conclusion**: Two APIs (POST + GET) is the standard pattern for async long-running tasks in serverless architectures.

---


## Summary

| Decision | Why? | Key Trade-off |
|----------|------|---------------|
| **Docker + ECR** | Dependencies exceed 250MB Lambda layer limit | Slower cold starts, but no size limits |
| **DynamoDB** | Serverless, pay-per-request, sub-10ms latency | Limited querying, but perfect for single-item lookups |
| **POST + GET APIs** | API Gateway 29s timeout, agents take 30-90s | Client must poll, but no timeout issues |

---

**Last Updated:** 2026-01-27  
**Author:** [@tarikkatasoy](https://github.com/tarikkatasoy)