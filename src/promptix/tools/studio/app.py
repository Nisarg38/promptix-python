import streamlit as st
from importlib import resources
import promptix.tools.studio 
from typing import Optional
import json

from promptix.tools.studio.pages.dashboard import render_dashboard 
from promptix.tools.studio.pages.library import render_prompt_library
from promptix.tools.studio.pages.version import render_version_editor
from promptix.tools.studio.pages.playground import render_playground

# State Management
def init_session_state():
    """Initialize session state variables"""
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"
    if "prompt_id" not in st.session_state:
        st.session_state["prompt_id"] = None
    if "version_id" not in st.session_state:
        st.session_state["version_id"] = None

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
            st.rerun()
            
        # Only show Version and Playground if a prompt is selected
        if st.session_state.get("prompt_id"):
            if st.button("✏️ Version Manager", key="nav_version"):
                st.session_state["current_page"] = "Version Manager"
                st.rerun()
                
            if st.button("🎮 Playground", key="nav_playground"):
                st.session_state["current_page"] = "Playground"
                st.rerun()
        
        # Settings section at bottom of sidebar
        st.markdown("---")

def main():
    """Main application entry point"""
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
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    if st.session_state["current_page"] == "Dashboard":
        render_dashboard()
    elif st.session_state["current_page"] == "Prompt Library":
        render_prompt_library()
    elif st.session_state["current_page"] == "Version Manager":
        # Render version manager
        render_version_editor()
    elif st.session_state["current_page"] == "Playground":
        if st.session_state.get("prompt_id") and st.session_state.get("version_id"):
            render_playground()
        else:
            st.error("No prompt or version selected. Please select a prompt and version first.")
            st.session_state["current_page"] = "Version Manager"
            st.rerun()

if __name__ == "__main__":
    main()