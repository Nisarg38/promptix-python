import streamlit as st
from typing import Optional, Dict, Any
from promptix.tools.studio.data import PromptManager
import datetime

def render_prompt_card(prompt: Dict[str, Any]):
    """Render a single prompt card"""
    with st.container(border=True):
        # Title and description
        st.subheader(prompt.get("name", "Unnamed Prompt"))
        if prompt.get("description"):
            st.write(prompt.get("description"))
        
        # Metadata display
        col1, col2, col3 = st.columns(3)
        with col1:
            version_count = len(prompt.get("versions", {}))
            st.write(f"📚 **Versions:** {version_count}")
        
        with col2:
            # Get live version count
            live_versions = sum(1 for v in prompt.get("versions", {}).values() if v.get("is_live", False))
            st.write(f"🟢 **Live:** {live_versions}")
        
        with col3:
            # Get the most recent modification date from metadata or top-level
            last_modified = prompt.get("last_modified", "N/A")
            if isinstance(last_modified, str) and len(last_modified) >= 10:
                last_modified = last_modified[:10]  # Get just the date part
            st.write(f"📅 **Last Modified:** {last_modified}")
        
        # Model information
        models = []
        providers = set()
        
        for version in prompt.get("versions", {}).values():
            if "config" in version and "model" in version["config"]:
                model = version["config"]["model"]
                if model not in models:
                    models.append(model)
            
            if "config" in version and "provider" in version["config"]:
                providers.add(version["config"]["provider"])
        
        if models:
            st.write(f"🤖 **Models:** {', '.join(models[:3])}{' and more' if len(models) > 3 else ''}")
        
        if providers:
            st.write(f"🔌 **Providers:** {', '.join(providers)}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Edit", key=f"edit_{prompt['id']}", use_container_width=True):
                st.session_state["prompt_id"] = prompt["id"]
                st.session_state["current_page"] = "Version Manager"
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete", key=f"delete_{prompt['id']}", use_container_width=True):
                # Show confirmation
                confirm_key = f"confirm_delete_{prompt['id']}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                st.session_state[confirm_key] = True
                st.rerun()
            
            # Show confirmation dialog
            if st.session_state.get(f"confirm_delete_{prompt['id']}", False):
                st.warning(f"Are you sure you want to delete '{prompt.get('name')}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key=f"confirm_yes_{prompt['id']}", use_container_width=True):
                        prompt_manager = PromptManager()
                        prompt_manager.delete_prompt(prompt["id"])
                        st.session_state[f"confirm_delete_{prompt['id']}"] = False
                        st.success(f"Deleted {prompt.get('name')}")
                        st.rerun()
                with col2:
                    if st.button("No", key=f"confirm_no_{prompt['id']}", use_container_width=True):
                        st.session_state[f"confirm_delete_{prompt['id']}"] = False
                        st.rerun()

def render_prompt_list():
    """Render the list of all prompts"""
    prompt_manager = PromptManager()
    prompts = prompt_manager.load_prompts()
    
    # Filter out schema or other metadata
    filtered_prompts_data = {k: v for k, v in prompts.items() if k != "schema" and isinstance(v, dict)}
    
    # Search bar
    search_query = st.text_input(
        "🔍",
        placeholder="Search prompts...",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    
    # Filter prompts based on search
    filtered_prompts = []
    for prompt_id, prompt in filtered_prompts_data.items():
        if (search_query.lower() in prompt.get("name", "").lower() or 
            search_query.lower() in prompt.get("description", "").lower()):
            filtered_prompts.append({"id": prompt_id, **prompt})
    
    # Sort prompts by last modified, with fallback to name
    filtered_prompts.sort(
        key=lambda x: (x.get("last_modified", ""), x.get("name", "")), 
        reverse=True
    )
    
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

def render_create_prompt():
    """Render create new prompt form"""
    st.subheader("Create New Prompt")
    
    # Basic prompt information
    prompt_name = st.text_input("Prompt Name", placeholder="Enter a name for your prompt")
    prompt_description = st.text_area("Description", placeholder="Describe what this prompt is for")
    
    # Initial version configuration
    st.write("Initial Version Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        initial_version = st.text_input("Initial Version", value="v1")
    
    with col2:
        model = st.selectbox(
            "Model",
            ["gpt-4o", "gpt-3.5-turbo", "claude-3-5-sonnet", "mistral-large"],
            index=0
        )
    
    col3, col4 = st.columns(2)
    with col3:
        provider = st.selectbox(
            "Provider",
            ["openai", "anthropic", "mistral", "custom"],
            index=0
        )
    
    # Create button
    if st.button("Create Prompt", use_container_width=True):
        if not prompt_name:
            st.error("Please enter a prompt name")
            return
        
        # Create the prompt
        prompt_manager = PromptManager()
        
        # Generate unique ID based on name
        prompt_id = prompt_name.lower().replace(" ", "_").replace("-", "_")
        
        # Check if ID already exists, append number if needed
        existing_prompts = prompt_manager.load_prompts()
        if prompt_id in existing_prompts:
            base_id = prompt_id
            counter = 1
            while f"{base_id}_{counter}" in existing_prompts:
                counter += 1
            prompt_id = f"{base_id}_{counter}"
        
        # Create prompt with metadata
        current_time = datetime.datetime.now().isoformat()
        prompt_data = {
            "name": prompt_name,
            "description": prompt_description,
            "created_at": current_time,
            "last_modified": current_time,
            "versions": {
                initial_version: {
                    "is_live": True,
                    "config": {
                        "system_instruction": "You are a helpful AI assistant.",
                        "model": model,
                        "provider": provider,
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0
                    },
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
            }
        }
        
        prompt_manager.save_prompt(prompt_id, prompt_data)
        
        # Navigate to the version manager
        st.session_state["prompt_id"] = prompt_id
        st.session_state["version_id"] = initial_version
        st.session_state["current_page"] = "Version Manager"
        st.rerun()

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
            st.session_state["library_view"] = "create"
            st.rerun()
    
    st.markdown("---")
    
    # Render appropriate view
    if st.session_state["library_view"] == "list":
        render_prompt_list()
    elif st.session_state["library_view"] == "create":
        render_create_prompt()
    elif st.session_state["library_view"] == "version":
        from promptix.tools.studio.pages.version import render_version_editor
        render_version_editor() 