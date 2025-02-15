import streamlit as st
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager  

def render_recent_prompts():
    """Render the recent prompts section"""
    st.subheader("Recent Prompts")
    
    # Get recent prompts from storage
    prompt_manager = PromptManager()
    recent_prompts = prompt_manager.get_recent_prompts(limit=5)
    
    if not recent_prompts:
        st.info("No prompts created yet. Create your first prompt!")
        return
    
    for prompt in recent_prompts:
        with st.expander(prompt["name"], expanded=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"Last modified: {prompt['last_modified'][:10]}")
                if prompt.get('description'):
                    st.text(prompt['description'])
                version_count = len(prompt.get('versions', {}))
                st.text(f"Versions: {version_count}")
            with col2:
                if st.button("View", key=f"view_{prompt['id']}", use_container_width=True):
                    st.session_state["prompt_id"] = prompt["id"]
                    st.session_state["current_page"] = "Prompt Library"
                    st.session_state["library_view"] = "version"
                    st.rerun()

def render_quick_actions():
    """Render quick action buttons"""
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Create New Prompt", use_container_width=True):
            st.session_state["current_page"] = "Prompt Library"
            st.session_state["library_view"] = "version"
            st.session_state["prompt_id"] = None
            st.rerun()
    
    with col2:
        if st.button("🔍 Browse All Prompts", use_container_width=True):
            st.session_state["current_page"] = "Prompt Library"
            st.session_state["library_view"] = "list"
            st.rerun()

def render_stats():
    """Render statistics about prompts"""
    prompt_manager = PromptManager()
    prompts = prompt_manager.load_prompts()
    
    total_prompts = len(prompts)
    total_versions = sum(len(p.get('versions', {})) for p in prompts.values())
    
    st.subheader("Stats")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Prompts", total_prompts)
    with col2:
        st.metric("Total Versions", total_versions)
    with col3:
        # Calculate average versions per prompt
        avg_versions = total_versions / total_prompts if total_prompts > 0 else 0
        st.metric("Avg. Versions per Prompt", f"{avg_versions:.1f}")

def render_dashboard():
    """Main dashboard render function"""
    st.title("Welcome to Promptix! 👋")
    st.write("Your AI prompt management journey starts here. Let's get you set up.")
    
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