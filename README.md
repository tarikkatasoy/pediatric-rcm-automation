

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
* **Responsibility:** Acts as the "**LLM-as-a-Judge**". It calculates a mathematical confidence score based on medical necessity and age-logic (e.g., Scenario 4). It has the authority to reject a draft and send it back to the Coder for revision.

### Compliance Officer (`BillingFinalizer`)
* **Role:** Final Report Generation.
* **Responsibility:** Consolidates audited data into a professional **Final Patient Encounter Record**, ready for insurance submission.

---

## Phase 2: Technical Foundation (Kurulum ve Tech Stack)
- Getting Started: ADK kurulumu ve .env yapılandırması.
- Tech Stack: Python 3.10+, Google ADK, Gemini 2.0 Flash & 2.5 Pro.

## Phase 3: The Brain (Data Structure & File Overview)
- Data Structure: tech_spec (JSON) ve billing_draft (Markdown) farkını teknik olarak açıklayacağız.
- Repository Architecture: common_tools.py ve subagents klasör yapısının dökümü.

## Phase 4: Onboarding Guide for LLMs (Altın Kurallar)
- Ajanların uyması gereken "Golden Rules" (Örn: "Manual is the only truth", "Search before you code").

## Phase 5: Roadmap (Epics & Stories)
- Projeyi nasıl geliştirdiğinin hikayesi.
- Epic 1: Foundation  
- Epic 2: Entity Extraction  
- Epic 3: Iterative Audit Loop (Bizim en güçlü yanımız!)  
- Epic 4: Final Reporting.

## Phase 6: Testing & Verification (QA)
- O meşhur 10 test senaryosunun (Note 1 - Note 10) teknik tablosu.
