
# Pediatric RCM: High-Confidence Medical Billing Automation

This document serves as the **Single Source of Truth** for the Pediatric Associates Revenue Cycle Management (RCM) project. It outlines the multi-agent architecture, the clinical knowledge base, and the automated audit workflows designed to eliminate claim denials.

---

## Project Goal
The primary objective is to automate the transition from raw physician encounter notes to validated, itemized billing codes (**ICD-10 & CPT**). By utilizing a **Hierarchical Multi-Agent Pipeline**, the system achieves high-precision automation:

* **Precision-First:** Processes clear clinical cases autonomously.
* **Safety-First:** Flags ambiguous or contradictory notes for human review by enforcing a strict **90% confidence threshold**.
* **Compliance-Grounded:** All logic is hard-coded into an internal knowledge base to prevent "AI hallucinations".

---

## The Virtual RCM Team (Architecture)
Rather than human developers, this project is managed by a team of specialized AI agents, each assuming a professional role within the Revenue Cycle.



### The Architect (`root_agent`)
* **Role:** Workflow Manager.
* **Responsibility:** Orchestrates the entire pipeline from initial clinical extraction to the final report. It manages the "state" and ensures data flows correctly between sub-agents.

### Clinical Data Scientist (`ClinicalEntityExtractor`)
* **Role:** Semantic Parser.
* **Responsibility:** Analyzes raw, unstructured physician notes to identify critical "entities" such as patient age, laterality (Right/Left), and clinical triggers.

### Certified Medical Coder (`MedicalCoder`)
* **Role:** Billing Implementation Specialist.
* **Responsibility:** Maps clinical findings to the **Master Code Lookup Table**. It utilizes the `search_knowledge_base` tool to perform targeted queries for ICD-10 and CPT codes.

### Senior Revenue Integrity Auditor (`RevenueIntegrityJudge`)
* **Role:** Compliance & Quality Control.
* **Responsibility:** Acts as the "**LLM-as-a-Judge**". It calculates a mathematical confidence score based on medical necessity and age-logic. It has the authority to reject a draft and send it back to the Coder for revision.

### Compliance Officer (`BillingFinalizer`)
* **Role:** Final Report Generation.
* **Responsibility:** Consolidates audited data into a professional **Final Patient Encounter Record**, ready for insurance submission.

---

## Phase 2: Technical Foundation

### Tech Stack
* **Language:** Python 3.10+ (Strict typing and Pydantic validation).
* **Framework:** **Google Agent Development Kit (ADK)** for stateful agent orchestration.
* **Models:** Gemini 2.0 Flash (Extraction) & Gemini 2.5 Pro (Integrity Auditing).

### Getting Started
1. **Auth:** Run `gcloud auth application-default login` to authorize Vertex AI access.
2. **Setup:** Install dependencies via `pip install -r requirements.txt`.
3. **Environment:** Configure your `.env` with `GOOGLE_CLOUD_PROJECT` and `CONFIDENCE_THRESHOLD=0.90`.

---

## Phase 3: The Brain (Data Structure)

The system maintains a strict separation between machine-readable data and human-readable reports:



* **`tech_spec.json`**: The internal state containing raw clinical entities, age verification, and raw ICD-10/CPT mappings.
* **`billing_draft.md`**: The audited report generated for human verification, highlighting the logic used for code selection.
* **Repository Architecture**:
    * `/subagents`: Specialized logic and prompts for each AI role.
    * `common_tools.py`: Shared utilities for knowledge base searching and state management.

---

## Phase 4: Onboarding Guide for LLMs

To maintain a 90%+ confidence interval, all agents must adhere to the **Golden Rules**:
1. **Manual is the Only Truth**: Never guess a code; if it is not in the Master Reference, flag for human review.
2. **Search Before You Code**: Every ICD-10 selection must be preceded by a `search_knowledge_base` tool call.
3. **Zero-Inference Laterality**: If the note does not specify Right, Left, or Bilateral, the agent must reject the claim.

---

## Phase 5: Roadmap

* **Epic 1: Foundation**: ADK integration and environment configuration.
* **Epic 2: Entity Extraction**: Developing the `ClinicalEntityExtractor` to parse complex pediatric notes.
* **Epic 3: Iterative Audit Loop**: Implementing the "Judge-Coder" feedback loop where the Judge can send incorrect drafts back for revision.
* **Epic 4: Final Reporting**: Automated generation of submission-ready encounter records.



---

## Phase 6: Testing & Verification (QA)

The system is validated against **10 High-Stakes Pediatric Scenarios**, including:
* **Note 1**: Acute Otitis Media (Laterality Test).
* **Note 4**: Well-Child Exam (Age-Logic Verification for CPT 99392 vs 99393).
* **Note 2**: Asthma Exacerbation (Bundling Rule for Nebulizer CPT 94640).

All scenarios must achieve a **Confidence Score > 0.90** for autonomous processing.