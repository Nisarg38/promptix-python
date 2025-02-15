import streamlit as st
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager

def render_prompt_list():
    """Render the list of all prompts"""
    prompt_manager = PromptManager()
    prompts = prompt_manager.load_prompts()
    
    # Search bar
    search_query = st.text_input(
        "🔍",
        placeholder="Search prompts...",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    
    # Filter prompts based on search
    filtered_prompts = []
    for prompt_id, prompt in prompts.items():
        if (search_query.lower() in prompt["name"].lower() or 
            search_query.lower() in prompt.get("description", "").lower()):
            filtered_prompts.append({"id": prompt_id, **prompt})
    
    # Sort prompts by last modified
    filtered_prompts.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
    
    # Display prompts in a grid
    if not filtered_prompts:
        st.info("No prompts found matching your search.")
        return
    
    for i in range(0, len(filtered_prompts), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(filtered_prompts):
                render_prompt_card(filtered_prompts[i])
        
        with col2:
            if i + 1 < len(filtered_prompts):
                render_prompt_card(filtered_prompts[i + 1])

def render_prompt_card(prompt: Dict):
    """Render a single prompt card"""
    with st.container():
        # Add custom CSS for hover effect and better styling
        st.markdown("""
        <style>
        .prompt-card {
            padding: 1.25rem;
            border: 1px solid #434556;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }
        .prompt-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        .prompt-description {
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1.25rem;
        }
        .button-container {
            display: flex;
            gap: 0.75rem;
        }
        </style>
        """, unsafe_allow_html=True)

        # Render the card
        st.markdown(f"""
        <div class="prompt-card">
            <div class="prompt-title">{prompt['name']}</div>
            <div class="prompt-description">{prompt.get('description', 'No description provided.')}</div>
        """, unsafe_allow_html=True)
        
        # Action buttons with better styling
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✨ Select", key=f"select_{prompt['id']}", 
                        use_container_width=True,
                        type="primary"):
                st.session_state["prompt_id"] = prompt["id"]
                st.session_state["library_view"] = "version"
                st.rerun()
        with col2:
            if st.button("🗑 Delete", key=f"delete_{prompt['id']}", 
                        use_container_width=True,
                        type="secondary"):
                if st.session_state.get("delete_confirm") == prompt["id"]:
                    prompt_manager = PromptManager()
                    prompt_manager.delete_prompt(prompt["id"])
                    st.success("Prompt deleted!")
                    st.session_state.pop("delete_confirm", None)
                    st.rerun()
                else:
                    st.session_state["delete_confirm"] = prompt["id"]
                    st.warning("Click again to confirm deletion")
        
        # Close the card
        st.markdown("</div>", unsafe_allow_html=True)

def render_prompt_library():
    """Main prompt library render function"""
    # Initialize library view state if not exists
    if "library_view" not in st.session_state:
        st.session_state["library_view"] = "list"
    
    # Header
    st.title("Prompt Library")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("↩️ Back to List" if st.session_state["library_view"] != "list" else "🔄 Refresh", 
                    use_container_width=True):
            st.session_state["library_view"] = "list"
            st.session_state.pop("prompt_id", None)
            st.rerun()
    with col3:
        if st.button("📝 New Prompt", use_container_width=True):
            st.session_state["prompt_id"] = None
            st.session_state["library_view"] = "version"
            st.rerun()
    
    st.markdown("---")
    
    # Render appropriate view
    if st.session_state["library_view"] == "list":
        render_prompt_list()
    elif st.session_state["library_view"] == "version":
        from promptix.tools.studio.pages.version import render_version_editor
        render_version_editor() 