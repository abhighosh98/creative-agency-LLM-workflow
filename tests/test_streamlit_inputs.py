"""Tests for Streamlit input functions in app.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app import validate_inputs


class MockSessionState(dict):
    """Mock session state that supports both dict and attribute access."""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value


class TestStreamlitInputs:
    """Test suite for Streamlit input functionality."""
    
    @patch('app.st')
    def test_get_persona_inputs_correct_length(self, mock_st):
        """Test that get_persona_inputs returns correct number of personas."""
        # Create mock session state
        session_state = MockSessionState({
            'num_personas': 3,
            'persona_0': "Persona 1: Tech-savvy millennial who loves gadgets",
            'persona_1': "Persona 2: Budget-conscious student looking for value", 
            'persona_2': "Persona 3: Busy professional needing efficiency"
        })
        
        # Mock streamlit components
        mock_st.session_state = session_state
        mock_st.sidebar.header = Mock()
        mock_st.sidebar.number_input = Mock(return_value=3)
        mock_st.sidebar.subheader = Mock()
        mock_st.sidebar.text_area = Mock(side_effect=[
            "Persona 1: Tech-savvy millennial who loves gadgets",
            "Persona 2: Budget-conscious student looking for value",
            "Persona 3: Busy professional needing efficiency"
        ])
        
        # Import and call function
        from app import get_persona_inputs
        personas = get_persona_inputs()
        
        # Assertions
        assert len(personas) == 3
        assert personas[0] == "Persona 1: Tech-savvy millennial who loves gadgets"
        assert personas[1] == "Persona 2: Budget-conscious student looking for value"
        assert personas[2] == "Persona 3: Busy professional needing efficiency"
    
    @patch('app.st')
    def test_get_persona_inputs_single_persona(self, mock_st):
        """Test get_persona_inputs with single persona."""
        session_state = MockSessionState({
            'num_personas': 1,
            'persona_0': "Single persona description"
        })
        
        mock_st.session_state = session_state
        mock_st.sidebar.header = Mock()
        mock_st.sidebar.number_input = Mock(return_value=1)
        mock_st.sidebar.subheader = Mock()
        mock_st.sidebar.text_area = Mock(return_value="Single persona description")
        
        from app import get_persona_inputs
        personas = get_persona_inputs()
        
        assert len(personas) == 1
        assert personas[0] == "Single persona description"
    
    @patch('app.st')
    def test_get_persona_inputs_zero_personas(self, mock_st):
        """Test get_persona_inputs with zero personas."""
        session_state = MockSessionState({'num_personas': 0})
        
        mock_st.session_state = session_state
        mock_st.sidebar.header = Mock()
        mock_st.sidebar.number_input = Mock(return_value=0)
        
        from app import get_persona_inputs
        personas = get_persona_inputs()
        
        assert len(personas) == 0
    
    @patch('app.st')
    def test_get_persona_inputs_max_personas(self, mock_st):
        """Test get_persona_inputs with maximum number of personas."""
        max_personas = 10
        session_state = MockSessionState({
            'num_personas': max_personas,
            **{f'persona_{i}': f"Persona {i+1}" for i in range(max_personas)}
        })
        
        mock_st.session_state = session_state
        mock_st.sidebar.header = Mock()
        mock_st.sidebar.number_input = Mock(return_value=max_personas)
        mock_st.sidebar.subheader = Mock()
        mock_st.sidebar.text_area = Mock(side_effect=[f"Persona {i+1}" for i in range(max_personas)])
        
        from app import get_persona_inputs
        personas = get_persona_inputs()
        
        assert len(personas) == max_personas
        for i, persona in enumerate(personas):
            assert persona == f"Persona {i+1}"
    
    def test_validate_inputs_valid_data(self):
        """Test input validation with valid data."""
        personas = ["Valid persona 1", "Valid persona 2"]
        product_description = "This is a valid product description with enough detail."
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is True
        assert error_message == ""
    
    def test_validate_inputs_empty_personas(self):
        """Test input validation with empty personas list."""
        personas = []
        product_description = "Valid product description"
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is False
        assert "at least one persona" in error_message.lower()
    
    def test_validate_inputs_empty_persona_content(self):
        """Test input validation with empty persona content."""
        personas = ["", "Valid persona"]
        product_description = "Valid product description"
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is False
        assert "persona 1 is empty" in error_message.lower()
    
    def test_validate_inputs_empty_product_description(self):
        """Test input validation with empty product description."""
        personas = ["Valid persona"]
        product_description = ""
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is False
        assert "product/brand description" in error_message.lower()
    
    def test_validate_inputs_short_product_description(self):
        """Test input validation with too short product description."""
        personas = ["Valid persona"]
        product_description = "Too short"
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is False
        assert "at least 20 characters" in error_message.lower()
    
    def test_validate_inputs_whitespace_only(self):
        """Test input validation with whitespace-only inputs."""
        personas = ["   ", "Valid persona"]
        product_description = "   \n\t   "
        
        is_valid, error_message = validate_inputs(personas, product_description)
        
        assert is_valid is False
        # Should catch both empty persona and empty product description
        assert any(keyword in error_message.lower() for keyword in ["empty", "product/brand description"])
    
    def test_session_state_persistence(self):
        """Test that session state is used for persistence."""
        # This test just verifies the concept of session state usage
        # In actual Streamlit app, session state would be managed by Streamlit
        mock_session_state = MockSessionState({})
        
        # Test that session state can be used
        mock_session_state['test_key'] = 'test_value'
        assert mock_session_state.get('test_key') == 'test_value'
        
        # Test attribute access
        mock_session_state.test_attr = 'attr_value'
        assert mock_session_state.test_attr == 'attr_value' 