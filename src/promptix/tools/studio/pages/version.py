import streamlit as st
import json
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager  
from datetime import datetime
from promptix.core.storage.loaders import PromptLoaderFactory, InvalidPromptSchemaError

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
                created_at = version_data.get('created_at', '')
                if isinstance(created_at, str) and len(created_at) >= 10:
                    created_at = created_at[:10]
                st.text(f"Created: {created_at}")
                
                if "metadata" in version_data:
                    metadata = version_data["metadata"]
                    st.text(f"Author: {metadata.get('author', 'Unknown')}")
                
                if version_data.get("config"):
                    st.text(f"Model: {version_data['config'].get('model', 'Not set')}")
                    provider = version_data['config'].get('provider', 'Not set')
                    st.text(f"Provider: {provider}")
                
                # Show tools information if available
                if version_data.get("tools_config"):
                    tools = version_data["tools_config"].get("tools", {})
                    if tools:
                        st.text(f"Tools: {', '.join(tools.keys())}")
            
            with col2:
                if st.button("📝 Edit", key=f"edit_{version_id}", use_container_width=True):
                    st.session_state["version_id"] = version_id
                    st.session_state["current_page"] = "Playground"
                    st.rerun()
            
            with col3:
                if st.button(button_label, key=f"go_live_{version_id}", use_container_width=True): 
                    if not is_live:  # Only update if not already live
                        # Set all versions to not live first
                        prompt_manager = PromptManager()
                        prompt = prompt_manager.get_prompt(st.session_state["prompt_id"])
                        for v_id in prompt["versions"]:
                            prompt["versions"][v_id]["is_live"] = False
                        # Set this version to live
                        prompt["versions"][version_id]["is_live"] = True
                        prompt_manager.save_prompt(st.session_state["prompt_id"], prompt)
                        
                        st.session_state["version_id"] = version_id
                        st.session_state["current_page"] = "Playground"
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
    
    with col2:
        base_model = st.selectbox(
            "Base Model",
            ["gpt-4o", "gpt-3.5-turbo", "claude-3-5-sonnet", "mistral-large"],
            index=0
        )
    
    col3, col4 = st.columns([2, 2])
    with col3:
        provider = st.selectbox(
            "Provider",
            ["openai", "anthropic", "mistral", "custom"],
            index=0
        )
    
    with col4:
        include_tools = st.checkbox("Include Tools Configuration", value=False)
    
    if st.button("➕ Create Version", use_container_width=True):
        if not new_version:
            st.error("Please enter a version name")
            return
        
        prompt_manager = PromptManager()
        prompt_id = st.session_state["prompt_id"]
        prompt = prompt_manager.get_prompt(prompt_id)
        
        if not prompt:
            st.error(f"Prompt with ID {prompt_id} not found!")
            return
            
        if new_version in prompt.get("versions", {}):
            st.error("Version already exists!")
            return
        
        # Create current timestamp
        current_time = datetime.now().isoformat()
        
        # Create version with standard config
        version_data = {
            "is_live": False,
            "config": {
                "system_instruction": "You are a helpful AI assistant.",
                "model": base_model,
                "provider": provider,
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 1.0
            },
            "created_at": current_time,
            "metadata": {
                "created_at": current_time,
                "author": "Promptix User",
                "last_modified": current_time,
                "last_modified_by": "Promptix User"
            },
            "schema": {
                "required": [],
                "optional": [],
                "properties": {},
                "additionalProperties": False
            }
        }
        
        # Add tools configuration if requested
        if include_tools:
            version_data["tools_config"] = {
                "tools_template": "{% raw %}{% set combined_tools = [] %}{% for tool_name, tool_config in tools.items() %}{% if use_%s|replace({'%s': tool_name}) %}{% set combined_tools = combined_tools + [{'name': tool_name, 'description': tool_config.description, 'parameters': tool_config.parameters}] %}{% endif %}{% endfor %}{{ combined_tools | tojson }}{% endraw %}",
                "tools": {}
            }
        
        try:
            # Debug information
            st.info(f"Creating version with model: {base_model} and provider: {provider}")
            
            # Add the version directly to the prompt object first
            if 'versions' not in prompt:
                prompt['versions'] = {}
            
            # Verify version data has correct model and provider
            st.session_state["debug_new_version_data"] = version_data
            
            # Explicitly log the config values
            st.info(f"Config in version_data: model={version_data['config']['model']}, provider={version_data['config']['provider']}")
            
            prompt['versions'][new_version] = version_data
            prompt['last_modified'] = current_time
            
            # Verify the data was correctly added to the prompt
            st.session_state["debug_updated_prompt"] = prompt['versions'][new_version]['config']
            
            # Save the updated prompt
            prompt_manager.save_prompt(prompt_id, prompt)
            
            # Verify after save
            saved_prompt = prompt_manager.get_prompt(prompt_id)
            if saved_prompt and new_version in saved_prompt.get('versions', {}):
                saved_config = saved_prompt['versions'][new_version]['config']
                st.session_state["debug_saved_config"] = saved_config
                st.info(f"Saved config: model={saved_config.get('model')}, provider={saved_config.get('provider')}")
            
            # Update session state
            st.session_state["version_id"] = new_version
            st.session_state["current_page"] = "Playground"
            
            # Show success message
            st.success(f"Version {new_version} created successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating version: {str(e)}")
            st.error("Stack trace:", exc_info=True)
            return

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
    if prompt.get("description"):
        st.write(prompt.get("description"))
    
    st.markdown("---")
    
    # Layout sections
    render_version_list(prompt)
    st.markdown("---")
    render_new_version()