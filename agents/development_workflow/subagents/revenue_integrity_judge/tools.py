from google.adk.tools import ToolContext
from typing import Dict, Literal

def set_review_status_and_exit_if_approved(
    status: Literal["APPROVED", "NEEDS_REVISION"],
    confidence_score: int,
    review_feedback: str,
    tool_context: ToolContext
) -> Dict[str, str]:
    """
    Sets the audit status and confidence score. 
    If score is 90% or higher and status is APPROVED, it exits the loop.
    """
    if not status:
        return {"status": "error", "message": "Status cannot be empty."}

    tool_context.state['review_status'] = status
    tool_context.state['confidence_score'] = confidence_score
    tool_context.state['review_feedback'] = f"Score: {confidence_score}% | Feedback: {review_feedback}"
    
    if status == "APPROVED" and confidence_score >= 90:
        tool_context.actions.escalate = True 
        return {
            "status": "success",
            "message": f"Encounter APPROVED with {confidence_score}% confidence. Finalizing bill."
        }
    else:
        return {
            "status": "success",
            "message": f"Revision Required (Score: {confidence_score}%). Feedback sent to Coder Agent."
        }