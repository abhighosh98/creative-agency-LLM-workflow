"""
Creative Agency Multi-Agent Analysis Tool
Streamlit application for persona-based product analysis using LangGraph agents.
"""
import streamlit as st
import time
from typing import List, Tuple
from dotenv import load_dotenv
import os

# Import our modules
from ollama_client import generate_persona_reaction, test_ollama_connection
from agents.graph import run_agent_analysis

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Creative Agency AI Analyst",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_persona_inputs() -> List[str]:
    """
    Get dynamic persona inputs from user.
    
    Returns:
        List of persona descriptions
    """
    st.sidebar.header("📊 Persona Configuration")
    
    # Use session state to persist the number of personas
    if 'num_personas' not in st.session_state:
        st.session_state.num_personas = 2
    
    # Number input for personas
    num_personas = st.sidebar.number_input(
        "Number of Personas",
        min_value=0,
        max_value=10,
        value=st.session_state.num_personas,
        step=1,
        help="Select how many customer personas to analyze"
    )
    
    st.session_state.num_personas = num_personas
    
    personas = []
    
    if num_personas > 0:
        st.sidebar.subheader("Persona Descriptions")
        
        for i in range(num_personas):
            persona_key = f"persona_{i}"
            if persona_key not in st.session_state:
                st.session_state[persona_key] = ""
            
            persona = st.sidebar.text_area(
                f"Persona {i+1}",
                value=st.session_state[persona_key],
                height=100,
                placeholder=f"Describe persona {i+1}... (demographics, interests, pain points, buying behavior)",
                help=f"Provide detailed description of persona {i+1}"
            )
            
            st.session_state[persona_key] = persona
            
            if persona.strip():
                personas.append(persona.strip())
    
    return personas


def validate_inputs(personas: List[str], product_description: str) -> Tuple[bool, str]:
    """
    Validate user inputs.
    
    Args:
        personas: List of persona descriptions
        product_description: Product/brand description
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not personas:
        return False, "Please add at least one persona."
    
    for i, persona in enumerate(personas):
        if not persona.strip():
            return False, f"Persona {i+1} is empty. Please provide a description."
    
    if not product_description.strip():
        return False, "Please provide a product/brand description."
    
    if len(product_description.strip()) < 20:
        return False, "Product description should be at least 20 characters long."
    
    return True, ""


def display_connection_status():
    """Display Ollama connection status in sidebar."""
    st.sidebar.header("🔗 Connection Status")
    
    with st.spinner("Testing Ollama connection..."):
        is_connected = test_ollama_connection()
    
    if is_connected:
        st.sidebar.success("✅ Ollama connection active")
    else:
        st.sidebar.error("❌ Ollama connection failed")
        st.sidebar.warning("Please ensure Ollama is running on http://localhost:11434")


def main():
    """Main Streamlit application."""
    # Header
    st.title("🎯 Creative Agency AI Analyst")
    st.markdown("""
    **Multi-Agent Analysis System** for product/brand evaluation across customer personas.
    
    This tool uses AI agents to analyze your product from multiple perspectives:
    - 🎨 **Branding Agent**: Visual identity and positioning
    - 📈 **Marketing Agent**: GTM strategy and pricing  
    - 🛠️ **Product Agent**: Feature gaps and opportunities
    - 🌐 **Trends Agent**: Live market signals and viral content
    - 👑 **Supervisor Agent**: Synthesized insights and action plan
    """)
    
    # Display connection status
    display_connection_status()
    
    # Get persona inputs
    personas = get_persona_inputs()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Product/Brand Description")
        
        # Product description input
        product_description = st.text_area(
            "Describe your product or brand",
            height=200,
            placeholder="Provide a comprehensive description of your product/brand including:\n- Core features and benefits\n- Target market\n- Value proposition\n- Competitive positioning\n- Brand personality",
            help="The more detailed your description, the better the analysis will be."
        )
        
        # Validation and submission
        is_valid, error_message = validate_inputs(personas, product_description)
        
        if error_message:
            st.error(error_message)
        
        # Submit button
        if st.button(
            "🚀 Run Multi-Agent Analysis", 
            disabled=not is_valid,
            type="primary",
            use_container_width=True
        ):
            run_analysis(personas, product_description)
    
    with col2:
        st.header("ℹ️ How It Works")
        st.markdown("""
        **Step 1:** Configure your personas
        - Add 1-10 customer personas
        - Describe demographics, needs, behaviors
        
        **Step 2:** Describe your product/brand
        - Include features, benefits, positioning
        - Be as detailed as possible
        
        **Step 3:** AI Analysis Pipeline
        1. Generate persona reactions via Ollama
        2. Run 4 specialist AI agents in parallel
        3. Synthesize insights into final report
        
        **Step 4:** Review actionable insights
        - Executive summary
        - SWOT analysis per persona  
        - GTM and pricing recommendations
        - Prioritized action items
        """)
        
        if st.session_state.get('last_analysis_time'):
            st.success(f"✅ Last analysis: {st.session_state.last_analysis_time}")


def run_analysis(personas: List[str], product_description: str):
    """
    Run the complete analysis pipeline.
    
    Args:
        personas: List of persona descriptions
        product_description: Product/brand description
    """
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Generate persona reactions
        status_text.text("🎭 Generating persona reactions via Ollama...")
        progress_bar.progress(20)
        
        persona_reactions = []
        for i, persona in enumerate(personas):
            with st.spinner(f"Analyzing persona {i+1}/{len(personas)}..."):
                reaction = generate_persona_reaction(persona, product_description)
                persona_reactions.append(reaction)
            
            # Update progress
            progress_step = 20 + (40 * (i + 1) / len(personas))
            progress_bar.progress(int(progress_step))
        
        # Step 2: Run multi-agent analysis
        status_text.text("🤖 Running multi-agent analysis...")
        progress_bar.progress(70)
        
        with st.spinner("Agents are working..."):
            final_report = run_agent_analysis(personas, product_description, persona_reactions)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display results
        display_results(personas, persona_reactions, final_report)
        
        # Update session state
        st.session_state.last_analysis_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.error("Please check your Ollama server connection and try again.")
    
    finally:
        # Clean up progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()


def display_results(personas: List[str], persona_reactions: List[str], final_report: str):
    """
    Display analysis results.
    
    Args:
        personas: Original persona descriptions
        persona_reactions: Generated persona reactions
        final_report: Final synthesized report
    """
    st.header("📊 Analysis Results")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Final Report", "🎭 Persona Reactions", "💾 Export"])
    
    with tab1:
        st.markdown("### 🎯 Creative Agency Analysis Report")
        st.markdown(final_report)
        
        # Download button for report
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=final_report,
            file_name=f"creative_agency_report_{int(time.time())}.md",
            mime="text/markdown"
        )
    
    with tab2:
        st.markdown("### 🎭 Generated Persona Reactions")
        
        for i, (persona, reaction) in enumerate(zip(personas, persona_reactions)):
            with st.expander(f"Persona {i+1} Reaction", expanded=i == 0):
                st.markdown(f"**Original Persona:**")
                st.info(persona)
                
                st.markdown(f"**Generated Reaction:**")
                st.success(reaction)
    
    with tab3:
        st.markdown("### 💾 Export Options")
        
        # Prepare full export data
        export_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "personas": personas,
            "persona_reactions": persona_reactions,
            "final_report": final_report
        }
        
        # JSON export
        import json
        json_data = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="📥 Download Full Analysis (JSON)",
            data=json_data,
            file_name=f"creative_agency_analysis_{int(time.time())}.json",
            mime="application/json"
        )
        
        # CSV export for personas
        import io
        csv_buffer = io.StringIO()
        csv_buffer.write("Persona,Reaction\n")
        for persona, reaction in zip(personas, persona_reactions):
            # Escape CSV content
            persona_clean = persona.replace('"', '""')
            reaction_clean = reaction.replace('"', '""')
            csv_buffer.write(f'"{persona_clean}","{reaction_clean}"\n')
        
        st.download_button(
            label="📥 Download Persona Data (CSV)", 
            data=csv_buffer.getvalue(),
            file_name=f"persona_reactions_{int(time.time())}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main() 