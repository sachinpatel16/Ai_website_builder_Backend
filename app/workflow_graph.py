"""
LangGraph workflow graph for website generation.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.workflow_state import WorkflowState
from app.workflow_nodes import (
    business_gathering_node,
    planning_node,
    image_description_node,
    image_generation_node,
    html_generation_node,
    file_storage_node
)


def should_continue_to_planning(state: WorkflowState) -> str:
    """
    Route based on whether we have enough business information.
    Returns 'planning' if ready, otherwise END to wait for user input.
    """
    if state.get("ready"):
        return "planning"
    return END


def create_website_workflow():
    """
    Create and compile the LangGraph workflow for website generation.
    
    Workflow:
    START -> business_gathering -> [conditional: if ready] -> planning -> image_description -> image_generation -> html_generation -> file_storage -> END
    """
    # Create workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("business_gathering", business_gathering_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("image_description", image_description_node)
    workflow.add_node("image_generation", image_generation_node)
    workflow.add_node("html_generation", html_generation_node)
    workflow.add_node("file_storage", file_storage_node)
    
    # Define edges
    # Start with business gathering
    workflow.add_edge(START, "business_gathering")
    
    # Conditional routing: proceed to planning only if ready
    workflow.add_conditional_edges(
        "business_gathering",
        should_continue_to_planning,
        {
            "planning": "planning",
            END: END
        }
    )
    
    # Rest of the workflow (linear after planning)
    workflow.add_edge("planning", "image_description")
    workflow.add_edge("image_description", "image_generation")
    workflow.add_edge("image_generation", "html_generation")
    workflow.add_edge("html_generation", "file_storage")
    workflow.add_edge("file_storage", END)
    
    # Compile with checkpointer for state persistence
    checkpointer = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=checkpointer)
    
    return compiled_workflow


# Create global workflow instance
website_workflow = create_website_workflow()
