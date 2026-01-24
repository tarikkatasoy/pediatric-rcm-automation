from google.adk.agents import SequentialAgent, LoopAgent

from .subagents.clinical_entity_extractor.agent import clinical_entity_extractor_agent
from .subagents.medical_coder.agent import medical_coder_agent
from .subagents.revenue_integrity_judge.agent import revenue_integrity_judge_agent
from .subagents.billing_finalizer.agent import billing_finalizer_agent


# --- Define the Loop Agent (Iterative Refinement) ---
billing_refinement_loop = LoopAgent(
    name="BillingRefinementLoop",
    max_iterations=5,
    sub_agents=[
        medical_coder_agent,
        revenue_integrity_judge_agent,
    ],
    description="Iteratively refines medical codes based on audit feedback."
)

# --- Define the Root Sequential Agent ---
root_agent = SequentialAgent(
    name="PediatricRCMWorkflowAgent",
    sub_agents=[
        clinical_entity_extractor_agent,
        billing_refinement_loop,
        billing_finalizer_agent,
    ],
    description="Manages the end-to-end medical billing and audit process."
)
