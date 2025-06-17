"""LangGraph multi-agent system for creative agency analysis."""
from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
import json
from ollama_client import chat_llm
from agents.prompts import (
    SYSTEM_BRANDING_AGENT, SYSTEM_MARKETING_AGENT, SYSTEM_PRODUCT_AGENT,
    SYSTEM_ONLINE_TRENDS_AGENT, SYSTEM_SUPERVISOR, SUPERVISOR_SYNTHESIS_PROMPT
)
from agents.tools import search_recent_trends


class AgentState(TypedDict):
    """State structure for the multi-agent system."""
    personas: List[str]
    product_description: str
    persona_reactions: List[str]
    branding_output: Dict[str, Any]
    marketing_output: Dict[str, Any]
    product_output: Dict[str, Any]
    trends_output: Dict[str, Any]
    final_report: str


def branding_agent(state: AgentState) -> Dict[str, Any]:
    """
    Branding agent that evaluates brand positioning and aesthetics.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with branding analysis
    """
    try:
        # Prepare context for branding analysis
        context = f"""
Product/Brand: {state['product_description']}

Persona Reactions:
{chr(10).join([f"- {reaction}" for reaction in state['persona_reactions']])}

As a senior brand strategist from McKinsey & Company with an MBA from Harvard Business School, analyze the brand positioning, visual identity, and tone-of-voice alignment with these personas. Provide strategic insights that would be expected from a top-tier consulting firm.
        """.strip()
        
        messages = [
            {"role": "system", "content": SYSTEM_BRANDING_AGENT},
            {"role": "user", "content": context}
        ]
        
        response = chat_llm(messages)
        
        # Try to parse JSON response, fallback to structured format
        try:
            branding_output = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: extract advice from text
            branding_output = {
                "branding_advice": [
                    line.strip() for line in response.split('\n') 
                    if line.strip() and not line.strip().startswith('{')
                ][:5]
            }
        
        return {"branding_output": branding_output}
        
    except Exception as e:
        print(f"Branding agent error: {e}")
        return {
            "branding_output": {
                "branding_advice": ["Error in branding analysis", str(e)]
            }
        }


def marketing_agent(state: AgentState) -> Dict[str, Any]:
    """
    Marketing agent that proposes GTM strategy and pricing.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with marketing analysis
    """
    try:
        context = f"""
Product/Brand: {state['product_description']}

Persona Reactions:
{chr(10).join([f"- {reaction}" for reaction in state['persona_reactions']])}

As a senior marketing strategist from Google with an MBA from Wharton School of Business, analyze the go-to-market strategy, distribution channels, and pricing model. Provide strategic insights that would be expected from a top-tier tech company's marketing team.
        """.strip()
        
        messages = [
            {"role": "system", "content": SYSTEM_MARKETING_AGENT},
            {"role": "user", "content": context}
        ]
        
        response = chat_llm(messages)
        
        try:
            marketing_output = json.loads(response)
        except json.JSONDecodeError:
            # Fallback structure
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            marketing_output = {
                "marketing_plan": lines[:len(lines)//2] if lines else ["No marketing plan generated"],
                "pricing_tips": lines[len(lines)//2:] if lines else ["No pricing tips generated"]
            }
        
        return {"marketing_output": marketing_output}
        
    except Exception as e:
        print(f"Marketing agent error: {e}")
        return {
            "marketing_output": {
                "marketing_plan": ["Error in marketing analysis"],
                "pricing_tips": [str(e)]
            }
        }


def product_agent(state: AgentState) -> Dict[str, Any]:
    """
    Product agent that analyzes feature gaps and opportunities.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with product analysis
    """
    try:
        context = f"""
Product/Brand: {state['product_description']}

Persona Reactions:
{chr(10).join([f"- {reaction}" for reaction in state['persona_reactions']])}

As a senior product manager from Apple with an MBA from Stanford Graduate School of Business, analyze feature alignment with persona needs and identify gaps and quick wins. Provide strategic insights that would be expected from a top-tier tech company's product team.
        """.strip()
        
        messages = [
            {"role": "system", "content": SYSTEM_PRODUCT_AGENT},
            {"role": "user", "content": context}
        ]
        
        response = chat_llm(messages)
        
        try:
            product_output = json.loads(response)
        except json.JSONDecodeError:
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            product_output = {
                "feature_gaps": lines[:len(lines)//2] if lines else ["No feature gaps identified"],
                "quick_wins": lines[len(lines)//2:] if lines else ["No quick wins identified"]
            }
        
        return {"product_output": product_output}
        
    except Exception as e:
        print(f"Product agent error: {e}")
        return {
            "product_output": {
                "feature_gaps": ["Error in product analysis"],
                "quick_wins": [str(e)]
            }
        }


def trends_agent(state: AgentState) -> Dict[str, Any]:
    """
    Online trends agent that fetches live market signals.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with trends analysis
    """
    try:
        # Extract keywords from product description for trend search
        product_keywords = state['product_description'][:100]  # First 100 chars
        
        # Search for recent trends
        trend_results = search_recent_trends(product_keywords, days_back=90)
        
        # Use LLM to analyze trends in context
        context = f"""
Product/Brand: {state['product_description']}

Recent Trends Found:
{chr(10).join([f"- {trend}" for trend in trend_results])}

Analyze how these trends relate to the product and personas.
        """.strip()
        
        messages = [
            {"role": "system", "content": SYSTEM_ONLINE_TRENDS_AGENT},
            {"role": "user", "content": context}
        ]
        
        response = chat_llm(messages)
        
        try:
            trends_output = json.loads(response)
        except json.JSONDecodeError:
            trends_output = {
                "trends": trend_results if trend_results else ["No recent trends found"]
            }
        
        return {"trends_output": trends_output}
        
    except Exception as e:
        print(f"Trends agent error: {e}")
        return {
            "trends_output": {
                "trends": ["Error in trends analysis", str(e)]
            }
        }


def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor agent that synthesizes all analyses into final report.
    
    Args:
        state: Current agent state with all agent outputs
        
    Returns:
        Updated state with final report
    """
    try:
        # Format all outputs for synthesis
        synthesis_prompt = SUPERVISOR_SYNTHESIS_PROMPT.format(
            branding_output=json.dumps(state['branding_output'], indent=2),
            marketing_output=json.dumps(state['marketing_output'], indent=2),
            product_output=json.dumps(state['product_output'], indent=2),
            trends_output=json.dumps(state['trends_output'], indent=2),
            persona_reactions='\n'.join([f"- {reaction}" for reaction in state['persona_reactions']]),
            product_description=state['product_description']
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_SUPERVISOR},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        final_report = chat_llm(messages)
        
        return {"final_report": final_report}
        
    except Exception as e:
        print(f"Supervisor agent error: {e}")
        return {
            "final_report": f"""
# Creative Agency Analysis Report

## Executive Summary
An error occurred during analysis synthesis: {str(e)}

## Error Details
- Branding Analysis: {state.get('branding_output', {})}
- Marketing Analysis: {state.get('marketing_output', {})}
- Product Analysis: {state.get('product_output', {})}
- Trends Analysis: {state.get('trends_output', {})}

Please check the system logs and try again.
            """.strip()
        }


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph multi-agent workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("branding", branding_agent)
    workflow.add_node("marketing", marketing_agent)
    workflow.add_node("product", product_agent)
    workflow.add_node("trends", trends_agent)
    workflow.add_node("supervisor", supervisor_agent)
    
    # Set entry point
    workflow.set_entry_point("branding")
    
    # Add edges (parallel execution of first 4 agents, then supervisor)
    workflow.add_edge("branding", "marketing")
    workflow.add_edge("marketing", "product")
    workflow.add_edge("product", "trends")
    workflow.add_edge("trends", "supervisor")
    workflow.add_edge("supervisor", END)
    
    return workflow


def run_agent_analysis(
    personas: List[str], 
    product_description: str, 
    persona_reactions: List[str]
) -> str:
    """
    Run the complete agent analysis workflow.
    
    Args:
        personas: List of persona descriptions
        product_description: Product/brand description
        persona_reactions: List of persona reactions from Ollama
        
    Returns:
        Final markdown report from supervisor
    """
    # Create initial state
    initial_state = AgentState(
        personas=personas,
        product_description=product_description,
        persona_reactions=persona_reactions,
        branding_output={},
        marketing_output={},
        product_output={},
        trends_output={},
        final_report=""
    )
    
    # Create and compile graph
    graph = create_agent_graph()
    compiled_graph = graph.compile()
    
    # Run the workflow
    result = compiled_graph.invoke(initial_state)
    
    return result.get("final_report", "No report generated") 