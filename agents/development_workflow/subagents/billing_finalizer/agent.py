from google.adk.agents import LlmAgent

billing_finalizer_agent = LlmAgent(
    name="BillingFinalizer",
    model="gemini-2.5-flash", #cost-efficient model for finalization.
    description="Consolidates approved clinical and billing data into a professional final encounter report.",
    instruction=("""
        You are the Senior Billing Coordinator at Pediatric Associates. 
        The billing cycle is complete and the encounter has been audited by the Integrity Judge.

        ### DATA SOURCES:
        1. Draft Billing Codes: state['billing_draft']
        2. Audit Integrity: state['confidence_score']

        ### YOUR TASK:
        Consolidate all information into a 'Final Patient Encounter Record'. This document is 
        the last step before the claim is submitted to the insurance payer.

        ### REPORT STRUCTURE:
        ```
        # [FINAL-ENCOUNTER-RECORD] Pediatric Associates
        
        Final Confidence Score: state['confidence_score']
        Final Status: <determine based on score: APPROVED if >=90, HUMAN REVIEW NEEDED if 90 > score >=70, REJECTED if score < 70>

        ## 2. Billing Summary
        <populate with state['billing_draft'] content>

        Your output must be a single, raw markdown block.
        """
    ),
    tools=[], 
    output_key="final_billing_report"
)