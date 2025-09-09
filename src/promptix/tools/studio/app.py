import streamlit as st
from importlib import resources
import promptix.tools.studio 
from typing import Optional, Dict, Any
import json
import traceback

from promptix.tools.studio.pages.dashboard import render_dashboard 
from promptix.tools.studio.pages.library import render_prompt_library
from promptix.tools.studio.pages.version import render_version_editor
from promptix.tools.studio.pages.playground import render_playground
from promptix.tools.studio.data import PromptManager

# State Management
def init_session_state():
    """Initialize session state variables"""
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"
    if "prompt_id" not in st.session_state:
        st.session_state["prompt_id"] = None
    if "version_id" not in st.session_state:
        st.session_state["version_id"] = None
    if "tools_config" not in st.session_state:
        st.session_state["tools_config"] = {}
    if "schema" not in st.session_state:
        st.session_state["schema"] = {}
    if "metadata" not in st.session_state:
        st.session_state["metadata"] = {}
    if "debug_version_data" not in st.session_state:
        st.session_state["debug_version_data"] = None
    if "library_view" not in st.session_state:
        st.session_state["library_view"] = "list"
    if "error_log" not in st.session_state:
        st.session_state["error_log"] = []

def render_sidebar():
    """Render the sidebar with navigation"""
    with resources.path('promptix.tools.studio', 'logo.webp') as logo_path:
        logo_path_str = str(logo_path)
    
    with st.sidebar:
        # Logo and name in a single line
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(logo_path_str, width=60)
        with col2:
            st.markdown("<h1 style='font-size: 1.8rem;'>Promptix</h1>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown("---")
        
        # Custom CSS for navigation buttons
        st.markdown("""
            <style>
                div[data-testid="stButton"] button {
                    border: none;
                    text-align: left;
                    width: 100%;
                    padding: 0.5rem;
                    margin: 0;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button("📊 Dashboard", key="nav_dashboard"):
            st.session_state["current_page"] = "Dashboard"
            st.session_state["prompt_id"] = None
            st.session_state["version_id"] = None
            st.rerun()
            
        if st.button("📚 Prompt Library", key="nav_library"):
            st.session_state["current_page"] = "Prompt Library"
            st.session_state["library_view"] = "list"
            st.rerun()
            
        # Only show Version and Playground if a prompt is selected
        if st.session_state.get("prompt_id"):
            if st.button("✏️ Version Manager", key="nav_version"):
                st.session_state["current_page"] = "Version Manager"
                st.rerun()
                
            # Only show Playground if both prompt and version are selected
            if st.session_state.get("version_id"):
                if st.button("🎮 Playground", key="nav_playground"):
                    st.session_state["current_page"] = "Playground"
                    st.rerun()
        
        # Settings section at bottom of sidebar
        st.markdown("---")
        
        # Display prompt and version info if selected
        if st.session_state.get("prompt_id"):
            try:
                prompt_manager = PromptManager()
                prompt = prompt_manager.get_prompt(st.session_state["prompt_id"])
                if prompt:
                    st.markdown(f"**Current Prompt:** {prompt.get('name', 'Unnamed')}")
                    
                    version_id = st.session_state.get("version_id")
                    if version_id and version_id in prompt.get("versions", {}):
                        is_live = prompt["versions"][version_id].get("is_live", False)
                        status = "🟢 Live" if is_live else "🔴 Draft"
                        st.markdown(f"**Version:** {version_id} ({status})")
            except Exception as e:
                st.error(f"Error loading prompt info: {str(e)}")
                
        # # Debug section
        # with st.expander("Debug Info", expanded=False):
        #     st.write("Session State:")
        #     st.json({
        #         "current_page": st.session_state.get("current_page"),
        #         "prompt_id": st.session_state.get("prompt_id"),
        #         "version_id": st.session_state.get("version_id"),
        #         "library_view": st.session_state.get("library_view")
        #     })
            
        #     if st.session_state.get("error_log"):
        #         st.write("Errors:")
        #         for error in st.session_state["error_log"][-5:]:
        #             st.text(error)

def get_current_prompt() -> Optional[Dict[str, Any]]:
    """Helper function to get the current prompt data"""
    if not st.session_state.get("prompt_id"):
        return None
    
    try:
        prompt_manager = PromptManager()
        return prompt_manager.get_prompt(st.session_state["prompt_id"])
    except Exception as e:
        error_msg = f"Error getting prompt: {str(e)}"
        st.session_state["error_log"].append(error_msg)
        return None

def get_current_version() -> Optional[Dict[str, Any]]:
    """Helper function to get the current version data"""
    prompt = get_current_prompt()
    if not prompt or not st.session_state.get("version_id"):
        return None
    
    version_id = st.session_state["version_id"]
    if version_id in prompt.get("versions", {}):
        return prompt["versions"][version_id]
    
    return None

def main():
    """Main application entry point"""
    try:
        st.set_page_config(
            page_title="Promptix Studio",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )
        
        # Hide default Streamlit pages navigation and header
        hide_streamlit_style = """
            <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                .css-18e3th9 {padding-top: 0rem;}
                .css-1d391kg {display: none;}
                [data-testid="stSidebarNav"] {display: none;}
                [data-testid="stSidebarHeader"] {display: none;}
            </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        
        # Initialize session state
        init_session_state()
        
        # Ensure prompts.yaml exists
        prompt_manager = PromptManager()
        
        # Render sidebar
        render_sidebar()
        
        # Render current page
        if st.session_state["current_page"] == "Dashboard":
            render_dashboard()
        elif st.session_state["current_page"] == "Prompt Library":
            render_prompt_library()
        elif st.session_state["current_page"] == "Version Manager":
            # Check that prompt_id is valid
            if not st.session_state.get("prompt_id"):
                st.error("No prompt selected. Please select a prompt first.")
                st.session_state["current_page"] = "Prompt Library"
                st.rerun()
            else:
                # Render version manager
                render_version_editor()
        elif st.session_state["current_page"] == "Playground":
            if st.session_state.get("prompt_id") and st.session_state.get("version_id"):
                # Before rendering, update any tools configuration if available
                version_data = get_current_version()
                if version_data and "tools_config" in version_data:
                    st.session_state["tools_config"] = version_data["tools_config"]
                render_playground()
            else:
                st.error("No prompt or version selected. Please select a prompt and version first.")
                st.session_state["current_page"] = "Version Manager"
                st.rerun()
    except Exception as e:
        error_msg = f"Application error: {str(e)}\n{traceback.format_exc()}"
        st.session_state["error_log"].append(error_msg)
        st.error("An error occurred in the application. See details in the debug section.")
        st.error(str(e))

if __name__ == "__main__":
    main()