import streamlit as st
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager

def render_model_config():
    """Render model configuration section"""
    st.subheader("Model Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "Model",
            ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            index=0
        )
    
    with col2:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )
    
    col3, col4 = st.columns(2)
    with col3:
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=1,
            max_value=4096,
            value=1024
        )
    
    with col4:
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1
        )
    
    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p
    }

def render_system_prompt():
    """Render system prompt section"""
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "System Message",
        value="You are a helpful AI assistant.",
        height=100
    )
    return system_prompt

def render_test_interface():
    """Render the test interface"""
    st.subheader("Test Your Prompt")
    
    user_input = st.text_area(
        "User Message",
        placeholder="Enter a test message...",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🚀 Test", use_container_width=True):
            if not user_input:
                st.warning("Please enter a test message.")
            else:
                with st.spinner("Generating response..."):
                    # TODO: Implement actual API call
                    st.info("API integration coming soon!")
    
    with col2:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("Configuration saved!")

def render_playground():
    """Main playground render function"""
    prompt_id = st.session_state.get("prompt_id")
    version_id = st.session_state.get("version_id")
    
    # Header with context
    st.title("Prompt Playground")
    st.write(f"Testing prompt version: {version_id}")
    
    # Back to version manager button
    if st.button("← Back to Version Manager"):
        st.session_state["current_page"] = "Version Manager"
    
    st.markdown("---")
    
    # Load prompt data
    prompt_manager = PromptManager()
    prompt = prompt_manager.get_prompt(prompt_id)
    version_data = prompt["versions"].get(version_id, {}) if prompt else {}
    
    # Configuration tabs
    tab1, tab2, tab3 = st.tabs(["Model Config", "System Prompt", "Test"])
    
    with tab1:
        config = render_model_config()
    
    with tab2:
        system_prompt = render_system_prompt()
    
    with tab3:
        render_test_interface()
    
    # Save button for all configurations
    st.markdown("---")
    if st.button("💾 Save All Changes", use_container_width=True):
        version_data = {
            "config": config,
            "system_prompt": system_prompt
        }
        prompt_manager.add_version(prompt_id, version_id, version_data)
        st.success("All changes saved successfully!") 