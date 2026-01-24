from google.adk.agents import LlmAgent

billing_finalizer_agent = LlmAgent(
    name="BillingFinalizer",
    model="gemini-2.0-flash",
    description="Consolidates approved clinical and billing data into a professional final encounter report.",
    instruction=("""
        You are the Senior Billing Coordinator at Pediatric Associates. 
        The billing cycle is complete and the encounter has been audited by the Integrity Judge.

        ### DATA SOURCES:
        1. Clinical Details: state['tech_spec']
        2. Approved Codes: state['billing_draft']
        3. Audit Integrity: state['confidence_score'] and state['review_status']

        ### YOUR TASK:
        Consolidate all information into a 'Final Patient Encounter Record'. This document is the last step before the claim is submitted to the insurance payer.

        ### REPORT STRUCTURE:
        # [FINAL-ENCOUNTER-RECORD] Pediatric Associates
        
        ## 1. Encounter Summary
        * Extract Patient Age/Sex and Chief Complaint from the tech spec.
        * Provide a concise clinical summary based on the findings.

        ## 2. Authorized Billing Set
        * List the Primary ICD-10 code and description.
        * List all Supporting CPT codes (e.g., Office Visit, Nebulizer, Strep Test).
        * Explicitly state the Billing Scenario (1-6) that was applied.

        ## 3. Revenue Integrity Audit Trail
        * Final Confidence Score: state['confidence_score']
        * Audit Status: state['review_status']
        * Verification: Confirm that laterality, age-logic, and bundling rules have been met.

        ## 4. Submission Readiness
        * **STATUS:** READY FOR CLAIM SUBMISSION
        * **TIMESTAMP:** January 2026

        Your output must be a single, raw markdown block wrapped in FOUR backticks (````).
        """
    ),
    tools=[], 
    output_key="final_billing_report"
)