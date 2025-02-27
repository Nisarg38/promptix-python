import streamlit as st
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager  

def render_version_list(prompt: Dict):
    """Render the list of versions"""
    st.subheader("Versions")
    
    versions = prompt.get("versions", {})
    if not versions:
        st.info("No versions yet. Create your first version below.")
        return
    
    # Sort versions by creation date
    sorted_versions = sorted(
        versions.items(),
        key=lambda x: x[1].get("created_at", ""),
        reverse=True
    )
    
    for version_id, version_data in sorted_versions:
        is_live = version_data.get('is_live', False)
        button_label = "✅ Live" if is_live else "🚀 Go Live" 
        with st.expander(f"Version {version_id}", expanded=version_id == sorted_versions[0][0]):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.text(f"Created: {version_data.get('created_at', '')[:10]}")
                if version_data.get("config"):
                    st.text(f"Model: {version_data['config'].get('model', 'Not set')}")
            
            with col2:
                if st.button("📝 Edit", key=f"edit_{version_id}", use_container_width=True):
                    st.session_state["version_id"] = version_id
                    st.session_state["current_page"] = "Playground"
                    st.rerun()
            
            with col3:
                if st.button(button_label, key=f"go_live_{version_id}", use_container_width=True): 
                    if not is_live:  # Only update if not already live
                        st.session_state["version_id"] = version_id
                        st.session_state["current_page"] = "Playground"
                        # Update is_live status in prompt.json
                        prompt_manager = PromptManager()
                        prompt = prompt_manager.get_prompt(st.session_state["prompt_id"])
                        prompt["versions"][version_id]["is_live"] = True
                        prompt_manager.save_prompt(st.session_state["prompt_id"], prompt)
                    st.rerun()

def render_new_version():
    """Render the new version creation section"""
    st.subheader("Create New Version")
    
    col1, col2 = st.columns([2, 2])
    with col1:
        new_version = st.text_input(
            "Version Name",
            placeholder="e.g., v1, production, test, etc."
        )
    
    if st.button("➕ Create Version", use_container_width=True):
        if not new_version:
            st.error("Please enter a version name")
            return
        
        prompt_manager = PromptManager()
        prompt_id = st.session_state["prompt_id"]
        prompt = prompt_manager.get_prompt(prompt_id)
        
        if new_version in prompt.get("versions", {}):
            st.error("Version already exists!")
            return
        
        # Create empty version
        version_data = {
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 1.0
            },
            "system_prompt": "You are a helpful AI assistant."
        }
        prompt_manager.add_version(prompt_id, new_version, version_data)
        
        # Navigate to playground
        st.session_state["version_id"] = new_version
        st.session_state["current_page"] = "Playground"
        st.rerun()

def render_version_editor():
    """Main prompt version render function"""
    prompt_id = st.session_state.get("prompt_id")
    
    # Load prompt data
    prompt_manager = PromptManager()
    prompt = prompt_manager.get_prompt(prompt_id)
    
    if not prompt:
        st.error("Prompt not found!")
        return
    
    # Header
    st.title(prompt.get("name", "Unnamed Prompt"))
    
    # # Back to library button
    # if st.button("← Back to Library"):
    #     st.session_state["current_page"] = "Prompt Library"
    #     st.rerun()
    
    st.markdown("---")
    
    # Layout sections
    render_version_list(prompt)
    st.markdown("---")
    render_new_version()