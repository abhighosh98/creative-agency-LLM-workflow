"""Tests for agents/graph.py"""
import pytest
from unittest.mock import Mock, patch
import json
from agents.graph import create_agent_graph, AgentState


class TestAgentGraph:
    """Test suite for LangGraph multi-agent system."""
    
    def test_agent_state_structure(self):
        """Test AgentState structure and initialization."""
        state = {
            "personas": ["Persona 1", "Persona 2"],
            "product_description": "Test product",
            "persona_reactions": ["Reaction 1", "Reaction 2"],
            "branding_output": {},
            "marketing_output": {},
            "product_output": {},
            "trends_output": {},
            "final_report": ""
        }
        
        assert len(state["personas"]) == 2
        assert state["product_description"] == "Test product"
        assert len(state["persona_reactions"]) == 2
        assert isinstance(state["branding_output"], dict)
        assert isinstance(state["marketing_output"], dict)
        assert isinstance(state["product_output"], dict)
        assert isinstance(state["trends_output"], dict)
        assert state["final_report"] == ""
    
    @patch('agents.graph.chat_llm')
    def test_branding_agent_node(self, mock_chat_llm):
        """Test branding agent node execution."""
        # Mock the chat_llm response
        mock_chat_llm.return_value = json.dumps({
            "branding_advice": [
                "Improve color palette",
                "Enhance logo design",
                "Strengthen brand voice"
            ]
        })
        
        # Create test state
        state = {
            "personas": ["Tech-savvy millennial"],
            "product_description": "Innovative smartphone app",
            "persona_reactions": ["Excited about the features"],
            "branding_output": {},
            "marketing_output": {},
            "product_output": {},
            "trends_output": {},
            "final_report": ""
        }
        
        # Import and test the actual branding agent
        from agents.graph import branding_agent
        result = branding_agent(state)
        
        # Verify the function was called and returned expected structure
        assert isinstance(result, dict)
        assert "branding_output" in result
        assert isinstance(result["branding_output"], dict)
        assert "branding_advice" in result["branding_output"]
    
    @patch('agents.graph.chat_llm')
    def test_marketing_agent_node(self, mock_chat_llm):
        """Test marketing agent node execution."""
        mock_chat_llm.return_value = json.dumps({
            "marketing_plan": ["Social media campaign", "Influencer partnerships"],
            "pricing_tips": ["Premium pricing strategy", "Bundle offers"]
        })
        
        state = {
            "personas": ["Budget-conscious student"],
            "product_description": "Affordable meal planning app",
            "persona_reactions": ["Interested but price-sensitive"],
            "branding_output": {},
            "marketing_output": {},
            "product_output": {},
            "trends_output": {},
            "final_report": ""
        }
        
        from agents.graph import marketing_agent
        result = marketing_agent(state)
        
        assert isinstance(result, dict)
        assert "marketing_output" in result
        assert isinstance(result["marketing_output"], dict)
    
    @patch('agents.graph.chat_llm')
    def test_product_agent_node(self, mock_chat_llm):
        """Test product agent node execution."""
        mock_chat_llm.return_value = json.dumps({
            "feature_gaps": ["Missing offline mode", "Need better onboarding"],
            "quick_wins": ["Add dark mode", "Improve search functionality"]
        })
        
        state = {
            "personas": ["Power user"],
            "product_description": "Productivity software",
            "persona_reactions": ["Wants more advanced features"],
            "branding_output": {},
            "marketing_output": {},
            "product_output": {},
            "trends_output": {},
            "final_report": ""
        }
        
        from agents.graph import product_agent
        result = product_agent(state)
        
        assert isinstance(result, dict)
        assert "product_output" in result
        assert isinstance(result["product_output"], dict)
    
    @patch('agents.graph.search_recent_trends')
    @patch('agents.graph.chat_llm')
    def test_trends_agent_node(self, mock_chat_llm, mock_search_trends):
        """Test online trends agent node execution."""
        mock_search_trends.return_value = [
            "TikTok marketing is trending",
            "Sustainability focus increasing",
            "AI integration becoming standard"
        ]
        
        mock_chat_llm.return_value = json.dumps({
            "trends": [
                "TikTok marketing is trending",
                "Sustainability focus increasing",
                "AI integration becoming standard"
            ]
        })
        
        state = {
            "personas": ["Gen Z consumer"],
            "product_description": "Eco-friendly fashion brand",
            "persona_reactions": ["Loves sustainable options"],
            "branding_output": {},
            "marketing_output": {},
            "product_output": {},
            "trends_output": {},
            "final_report": ""
        }
        
        from agents.graph import trends_agent
        result = trends_agent(state)
        
        assert isinstance(result, dict)
        assert "trends_output" in result
        assert isinstance(result["trends_output"], dict)
    
    @patch('agents.graph.chat_llm')
    def test_supervisor_agent_merge_logic(self, mock_chat_llm):
        """Test supervisor agent aggregation logic."""
        # Mock supervisor to return a comprehensive report
        mock_chat_llm.return_value = """
# Executive Summary
Comprehensive analysis completed for all personas.

## SWOT Analysis
**Strengths:** Strong brand positioning
**Weaknesses:** Price sensitivity
**Opportunities:** Emerging trends alignment
**Threats:** Market competition

## GTM Strategy
1. Multi-channel approach
2. Competitive pricing
3. Feature enhancement

## Action Items
- [ ] Implement suggested features
- [ ] Launch marketing campaign
- [ ] Monitor market trends
        """.strip()
        
        # Create state with all agent outputs populated
        state = {
            "personas": ["Persona 1", "Persona 2"],
            "product_description": "Test product",
            "persona_reactions": ["Reaction 1", "Reaction 2"],
            "branding_output": {"branding_advice": ["advice1", "advice2"]},
            "marketing_output": {"marketing_plan": ["plan1"], "pricing_tips": ["tip1"]},
            "product_output": {"feature_gaps": ["gap1"], "quick_wins": ["win1"]},
            "trends_output": {"trends": ["trend1", "trend2"]},
            "final_report": ""
        }
        
        from agents.graph import supervisor_agent
        result = supervisor_agent(state)
        
        assert isinstance(result, dict)
        assert "final_report" in result
        assert len(result["final_report"]) > 0
        assert "Executive Summary" in result["final_report"]
        assert "SWOT" in result["final_report"]
        assert "Action Items" in result["final_report"]
    
    def test_create_agent_graph_structure(self):
        """Test that the agent graph is created with correct structure."""
        graph = create_agent_graph()
        
        # Verify graph exists and has expected structure
        assert graph is not None
        
        # Test that we can compile the graph
        compiled_graph = graph.compile()
        assert compiled_graph is not None 