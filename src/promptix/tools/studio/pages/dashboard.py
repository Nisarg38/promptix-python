import streamlit as st
from typing import Optional, Dict, Any, List
from promptix.tools.studio.data import PromptManager  

def render_quick_actions():
    """Render quick action buttons"""
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 Create Prompt", use_container_width=True, key="dashboard_new_prompt"):
            st.session_state["prompt_id"] = None
            st.session_state["current_page"] = "Prompt Library"
            st.session_state["library_view"] = "create"
            st.rerun()
    
    with col2:
        if st.button("📚 View Library", use_container_width=True, key="dashboard_view_library"):
            st.session_state["current_page"] = "Prompt Library"
            st.rerun()

def render_recent_prompts():
    """Render the recent prompts section"""
    st.subheader("Recent Prompts")
    
    # Get recent prompts from storage
    prompt_manager = PromptManager()
    all_prompts = prompt_manager.load_prompts()
    
    # Filter out non-prompt keys like 'schema' 
    prompts_dict = {k: v for k, v in all_prompts.items() if k != "schema" and isinstance(v, dict)}
    
    # Create list of prompts with IDs
    prompt_list = [{"id": k, **v} for k, v in prompts_dict.items()]
    
    # Sort by last_modified
    prompt_list.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
    
    # Take the first 5
    recent_prompts = prompt_list[:5]
    
    if not recent_prompts:
        st.info("No prompts created yet. Create your first prompt!")
        return
    
    # Display recent prompts
    for prompt in recent_prompts:
        with st.container(border=True):
            # Header with prompt name
            st.write(f"### {prompt.get('name', 'Unnamed Prompt')}")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                # Description
                if prompt.get('description'):
                    st.write(prompt['description'])
                
                # Show version and model info
                version_count = len(prompt.get('versions', {}))
                
                # Find live version
                live_version = None
                for ver_id, ver_data in prompt.get('versions', {}).items():
                    if ver_data.get('is_live', False):
                        live_version = ver_id
                        break
                
                version_text = f"**Versions:** {version_count}"
                if live_version:
                    version_text += f" (Live: {live_version})"
                st.write(version_text)
                
                # Show last modified date if available
                last_modified = prompt.get('last_modified', '')
                if last_modified and isinstance(last_modified, str):
                    st.write(f"**Last modified:** {last_modified[:10]}")
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{prompt['id']}", use_container_width=True):
                    st.session_state["prompt_id"] = prompt["id"]
                    st.session_state["current_page"] = "Version Manager"
                    st.rerun()
            

def render_stats():
    """Render statistics about prompts"""
    st.subheader("Stats")
    
    prompt_manager = PromptManager()
    prompts = prompt_manager.load_prompts()
    
    # Filter out non-prompt keys like 'schema'
    prompts_dict = {k: v for k, v in prompts.items() if k != "schema" and isinstance(v, dict)}
    
    total_prompts = len(prompts_dict)
    
    # Count versions and live versions
    total_versions = 0
    total_live = 0
    providers = {}
    models = {}
    
    for prompt in prompts_dict.values():
        versions = prompt.get('versions', {})
        total_versions += len(versions)
        
        for version in versions.values():
            if version.get('is_live', False):
                total_live += 1
            
            # Track providers and models
            if 'config' in version:
                provider = version['config'].get('provider')
                if provider:
                    providers[provider] = providers.get(provider, 0) + 1
                
                model = version['config'].get('model')
                if model:
                    models[model] = models.get(model, 0) + 1
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Prompts", total_prompts)
    with col2:
        st.metric("Total Versions", total_versions)
    with col3:
        st.metric("Live Versions", total_live)
    
    # Show most used models and providers
    if models or providers:
        st.write("#### Most Used")
        col1, col2 = st.columns(2)
        
        with col1:
            if models:
                top_models = sorted(models.items(), key=lambda x: x[1], reverse=True)[:3]
                st.write("**Models:**")
                for model, count in top_models:
                    st.write(f"- {model}: {count}")
        
        with col2:
            if providers:
                top_providers = sorted(providers.items(), key=lambda x: x[1], reverse=True)[:3]
                st.write("**Providers:**")
                for provider, count in top_providers:
                    st.write(f"- {provider}: {count}")

def render_dashboard():
    """Main dashboard render function"""
    st.title("Welcome to Promptix Studio 👋")
    st.write("Your AI prompt management journey starts here. Build, test, and deploy your prompts with ease.")
    
    # Add some spacing
    st.markdown("---")
    
    # Layout the dashboard sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_recent_prompts()
    
    with col2:
        render_quick_actions()
        st.markdown("---")
        render_stats() 