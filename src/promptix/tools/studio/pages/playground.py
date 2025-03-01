import streamlit as st
import json
from typing import Optional, Dict, Any, List
from promptix.tools.studio.data import PromptManager
import traceback
from datetime import datetime

def render_model_config(config: Dict[str, Any] = None):
    """Render model configuration section"""
    st.subheader("Model Configuration")
    
    if not config:
        config = {}
    
    # Define options lists
    model_options = ["gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo", "claude-3-5-sonnet", "claude-3-opus", "mistral-large", "mistral-medium"]
    provider_options = ["openai", "anthropic", "mistral", "custom"]
    
    # Get current values from config
    current_model = config.get("model", "gpt-4o")
    current_provider = config.get("provider", "openai")
    
    # Find indices of current values
    try:
        model_index = model_options.index(current_model)
    except ValueError:
        model_index = 0  # Default to first option if not found
        
    try:
        provider_index = provider_options.index(current_provider)
    except ValueError:
        provider_index = 0  # Default to first option if not found
    
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "Model",
            model_options,
            index=model_index,
            key="model_selector"
        )
    
    with col2:
        provider = st.selectbox(
            "Provider",
            provider_options,
            index=provider_index,
            key="provider_selector"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=config.get("temperature", 0.7),
            step=0.1,
            key="temp_slider"
        )
    
    with col4:
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=1,
            max_value=32000,
            value=config.get("max_tokens", 1024),
            key="tokens_input"
        )
    
    col5, col6 = st.columns(2)
    with col5:
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=config.get("top_p", 1.0),
            step=0.01,
            key="top_p_slider"
        )
    
    with col6:
        frequency_penalty = st.slider(
            "Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=config.get("frequency_penalty", 0.0),
            step=0.1,
            key="freq_penalty_slider"
        )
    
    return {
        "model": model,
        "provider": provider,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty
    }

def render_system_prompt(system_instruction: str = "You are a helpful AI assistant."):
    """Render system prompt section"""
    # Replace escaped newlines with actual newlines for editing
    if system_instruction:
        if isinstance(system_instruction, str) and "\\n" in system_instruction:
            system_instruction = system_instruction.replace("\\n", "\n")
    
    # Get schema variables from session state if available
    schema_properties = {}
    schema_required = []
    schema_optional = []
    
    if "schema_properties" in st.session_state:
        schema_properties = st.session_state.schema_properties
    if "schema_required" in st.session_state:
        schema_required = st.session_state.schema_required
    if "schema_optional" in st.session_state:
        schema_optional = st.session_state.schema_optional
    
    # Display available variables in a simple, concise format ABOVE the system instruction
    st.markdown("### Available Variables")
    
    if not schema_properties:
        st.info("No Dynamic variable creating for system instruction")
    else:
        # Create horizontal display of variables
        var_items = []
        
        # Add required variables with styling
        for var_name in schema_required:
            var_props = schema_properties.get(var_name, {})
            var_type = var_props.get("type", "string")
            var_items.append(f"<span style='background-color: rgba(255,255,255,0.1); padding: 3px 6px; margin: 2px; border-radius: 4px; display: inline-block;'>{{{{ <b>{var_name}</b> }}}} <small>({var_type})</small></span>")
        
        # Add optional variables with styling
        for var_name in schema_optional:
            var_props = schema_properties.get(var_name, {})
            var_type = var_props.get("type", "string")
            var_items.append(f"<span style='background-color: rgba(255,255,255,0.1); padding: 3px 6px; margin: 2px; border-radius: 4px; display: inline-block;'>{{{{ <i>{var_name}</i> }}}} <small>({var_type})</small></span>")
        
        if var_items:
            # Join items with spaces to keep them horizontal
            vars_html = " ".join(var_items)
            # Use markdown to display the HTML with proper styling
            st.markdown(f"<div style='background-color: rgba(30,30,30,0.6); padding: 10px; border-radius: 5px; overflow-x: auto; white-space: nowrap;'>{vars_html}</div>", unsafe_allow_html=True)
    
    # Add the system instruction heading
    st.markdown("### System Instruction")
    
    # Text area for system instruction (AFTER variables)
    system_text = st.text_area(
        "Enter your instruction here",
        value=system_instruction,
        height=300,
        key="system_instruction_input"
    )
    
    return system_text

def render_schema_editor(schema: Dict[str, Any] = None):
    """Render schema editor for validation"""
    # st.subheader("Schema Validation")
    
    # Add helpful explanatory text about schema usage in a collapsible dropdown
    with st.expander("How to Use", expanded=False):
        st.markdown("""
        ### How Schema Variables Work
        
        ✨ Schema variables define inputs your prompt can accept when used through the API or UI.
        
        📝 **Not required**: You can create prompts without any schema variables for simple use cases.
        
        🔄 **Dynamic content**: Variables you define here can be referenced in your system instructions like this:
        ```
        {{variable_name}}
        ```
        
        💡 **Example**: If you define a variable called "user_query", you can use "{{user_query}}" in your system instruction.
        
        🛠️ **Advanced usage**: Schema variables are particularly useful for building dynamic prompts with the builder interface.
        """)
    
    if not schema:
        schema = {
            "required": [],
            "optional": [],
            "properties": {},
            "additionalProperties": False
        }
    
    # Initialize state variables if they don't exist
    if "schema_changes" not in st.session_state:
        st.session_state.schema_changes = False
    if "schema_properties" not in st.session_state:
        st.session_state.schema_properties = schema.get("properties", {})
    if "schema_required" not in st.session_state:
        st.session_state.schema_required = schema.get("required", [])
    if "schema_optional" not in st.session_state:
        st.session_state.schema_optional = schema.get("optional", [])
    if "schema_additional_props" not in st.session_state:
        st.session_state.schema_additional_props = schema.get("additionalProperties", False)
    
    # Create tabs for different editing modes
    schema_tab1, schema_tab2 = st.tabs(["Visual Editor", "JSON Editor"])
    
    with schema_tab1:
        st.markdown("### Variable Configuration")
        st.info("Variables you define here become available when using your prompt. They can be referenced in your system instruction using double curly braces: {{variable_name}}")
        
        # Get current properties from session state
        properties = st.session_state.schema_properties
        required_vars = st.session_state.schema_required
        optional_vars = st.session_state.schema_optional
        
        # Allow setting additional properties
        additional_props = st.checkbox(
            "Allow Additional Properties",
            value=st.session_state.schema_additional_props,
            help="If checked, the prompt will accept variables not defined here. Useful for flexible prompts.",
            key="schema_additional_props_cb"
        )
        if additional_props != st.session_state.schema_additional_props:
            st.session_state.schema_additional_props = additional_props
            st.session_state.schema_changes = True
        
        # Combined list of all variables (required + optional)
        all_vars = sorted(set(required_vars + optional_vars + list(properties.keys())))
        
        # Add new variable section
        st.markdown("#### Add New Variable")
        
        # Simple example for common use case
        with st.expander("💡 Quick Example", expanded=False):
            st.markdown("""
            **Common example:** If you're building a customer service assistant, you might want:
            
            - **user_query** (Required, String): The question from the user
            - **customer_name** (Optional, String): The name of the customer
            - **previous_interactions** (Optional, Array): List of previous messages
            
            Then in your system instruction, you can use:
            ```
            You are a helpful customer service assistant. 
            The customer's name is {{customer_name}}.
            
            Here is their query: {{user_query}}
            
            Previous interactions:
            {{previous_interactions}}
            ```
            """)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_var_name = st.text_input("Variable Name", key="new_var_name", placeholder="e.g., user_query, customer_name")
        with col2:
            new_var_type = st.selectbox(
                "Type", 
                ["string", "number", "boolean", "object", "array"], 
                key="new_var_type",
                help="The data type expected for this variable"
            )
        with col3:
            new_var_required = st.checkbox("Required", key="new_var_required", value=True, 
                                         help="If checked, this variable must be provided when using the prompt")
        
        new_var_description = st.text_area(
            "Description", 
            key="new_var_description", 
            placeholder="What is this variable for? e.g., 'The user's question' or 'Customer's full name'",
            height=100
        )
        
        # Add variable button
        if st.button("Add Variable", key="add_var_btn", use_container_width=True):
            if new_var_name and new_var_name.strip():
                var_name = new_var_name.strip()
                
                # Add to properties
                properties[var_name] = {
                    "type": new_var_type,
                    "description": new_var_description if new_var_description else f"{var_name} variable"
                }
                
                # Add to required or optional list
                if new_var_required:
                    if var_name not in required_vars:
                        required_vars.append(var_name)
                    if var_name in optional_vars:
                        optional_vars.remove(var_name)
                else:
                    if var_name not in optional_vars:
                        optional_vars.append(var_name)
                    if var_name in required_vars:
                        required_vars.remove(var_name)
                        
                # Update all_vars
                all_vars = sorted(set(required_vars + optional_vars + list(properties.keys())))
                
                # Mark that changes were made
                st.session_state.schema_changes = True
                
                st.success(f"Added variable: {var_name}")
                # We will not directly clear the session state, instead we'll use a rerun
                st.rerun()
        
        # Display existing variables
        if all_vars:
            st.markdown("---")
            st.markdown("#### Current Variables")
            
            # Table header
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown("**Variable Name**")
            with col2:
                st.markdown("**Type**")
            with col3:
                st.markdown("**Status**")
            with col4:
                st.markdown("**Actions**")
            
            # Create rows for each variable
            for var_name in all_vars:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.text(var_name)
                
                with col2:
                    if var_name in properties:
                        var_type = properties[var_name].get("type", "string")
                        st.text(var_type)
                    else:
                        st.text("string")
                
                with col3:
                    if var_name in required_vars:
                        st.markdown("🔴 Required")
                    elif var_name in optional_vars:
                        st.markdown("🟢 Optional")
                    else:
                        st.markdown("⚪ Undefined")
                
                with col4:
                    if st.button("✏️", key=f"edit_{var_name}"):
                        st.session_state["edit_var"] = var_name
                    if st.button("🗑️", key=f"delete_{var_name}"):
                        # Remove from all lists
                        if var_name in required_vars:
                            required_vars.remove(var_name)
                        if var_name in optional_vars:
                            optional_vars.remove(var_name)
                        if var_name in properties:
                            del properties[var_name]
                        st.session_state.schema_changes = True
                        st.success(f"Removed variable: {var_name}")
                        st.rerun()
                
                # If this variable is being edited
                if st.session_state.get("edit_var") == var_name:
                    with st.expander(f"Edit {var_name}", expanded=True):
                        var_props = properties.get(var_name, {"type": "string", "description": ""})
                        
                        edit_col1, edit_col2 = st.columns([2, 2])
                        with edit_col1:
                            edited_type = st.selectbox(
                                "Type", 
                                ["string", "number", "boolean", "object", "array"],
                                index=["string", "number", "boolean", "object", "array"].index(var_props.get("type", "string")),
                                key=f"edit_type_{var_name}"
                            )
                        
                        with edit_col2:
                            edited_required = st.checkbox(
                                "Required", 
                                value=var_name in required_vars,
                                key=f"edit_required_{var_name}"
                            )
                        
                        edited_description = st.text_area(
                            "Description",
                            value=var_props.get("description", ""),
                            key=f"edit_desc_{var_name}",
                            height=100
                        )
                        
                        # Example section based on type
                        if edited_type == "string":
                            st.markdown("#### String Configuration")
                            min_length = st.number_input(
                                "Min Length", 
                                min_value=0, 
                                value=var_props.get("minLength", 0),
                                key=f"min_length_{var_name}"
                            )
                            max_length = st.number_input(
                                "Max Length", 
                                min_value=0, 
                                value=var_props.get("maxLength", 0),
                                key=f"max_length_{var_name}"
                            )
                            pattern = st.text_input(
                                "Pattern (regex)", 
                                value=var_props.get("pattern", ""),
                                key=f"pattern_{var_name}"
                            )
                        
                        elif edited_type == "number":
                            st.markdown("#### Number Configuration")
                            minimum = st.number_input(
                                "Minimum", 
                                value=var_props.get("minimum", 0.0),
                                key=f"minimum_{var_name}"
                            )
                            maximum = st.number_input(
                                "Maximum", 
                                value=var_props.get("maximum", 0.0),
                                key=f"maximum_{var_name}"
                            )
                        
                        # Save and cancel buttons
                        save_col1, save_col2 = st.columns(2)
                        with save_col1:
                            if st.button("Save Changes", key=f"save_{var_name}", use_container_width=True):
                                # Update property
                                updated_props = {"type": edited_type, "description": edited_description}
                                
                                # Add type-specific properties
                                if edited_type == "string":
                                    if min_length > 0:
                                        updated_props["minLength"] = min_length
                                    if max_length > 0:
                                        updated_props["maxLength"] = max_length
                                    if pattern:
                                        updated_props["pattern"] = pattern
                                elif edited_type == "number":
                                    if minimum != 0.0:
                                        updated_props["minimum"] = minimum
                                    if maximum != 0.0:
                                        updated_props["maximum"] = maximum
                                
                                properties[var_name] = updated_props
                                
                                # Update required/optional status
                                if edited_required:
                                    if var_name not in required_vars:
                                        required_vars.append(var_name)
                                    if var_name in optional_vars:
                                        optional_vars.remove(var_name)
                                else:
                                    if var_name not in optional_vars:
                                        optional_vars.append(var_name)
                                    if var_name in required_vars:
                                        required_vars.remove(var_name)
                                
                                # Mark that changes were made
                                st.session_state.schema_changes = True
                                
                                # Clear edit state
                                if "edit_var" in st.session_state:
                                    del st.session_state["edit_var"]
                                    
                                st.success(f"Updated variable: {var_name}")
                                st.rerun()
                        
                        with save_col2:
                            if st.button("Cancel", key=f"cancel_{var_name}", use_container_width=True):
                                if "edit_var" in st.session_state:
                                    del st.session_state["edit_var"]
                                st.rerun()
        else:
            st.info("No variables defined yet. Add your first variable above to get started.")
    
    with schema_tab2:
        st.markdown("### JSON Schema Editor")
        st.info("Edit the schema directly as JSON. This is for advanced users familiar with JSON Schema format.")
        
        # Create the schema object from the session state
        schema_obj = {
            "required": st.session_state.schema_required,
            "optional": st.session_state.schema_optional,
            "properties": st.session_state.schema_properties,
            "additionalProperties": st.session_state.schema_additional_props
        }
        
        schema_json = st.text_area(
            "Schema JSON",
            value=json.dumps(schema_obj, indent=2),
            height=400,
            key="schema_json_editor"
        )
        
        try:
            json_schema = json.loads(schema_json)
            # Basic validation
            if not isinstance(json_schema, dict):
                st.error("Schema must be a JSON object")
            elif "properties" not in json_schema:
                st.warning("Schema should include a 'properties' object")
            elif "required" not in json_schema and "optional" not in json_schema:
                st.warning("Schema should include 'required' or 'optional' arrays")
            else:
                # Apply the JSON editor changes to session state
                if st.button("Apply JSON Changes", key="apply_json_schema", use_container_width=True):
                    st.session_state.schema_properties = json_schema.get("properties", {})
                    st.session_state.schema_required = json_schema.get("required", [])
                    st.session_state.schema_optional = json_schema.get("optional", [])
                    st.session_state.schema_additional_props = json_schema.get("additionalProperties", False)
                    st.session_state.schema_changes = True
                    st.success("Schema updated from JSON editor")
                    st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {str(e)}")
    
    # Return the current schema state
    return {
        "required": st.session_state.schema_required,
        "optional": st.session_state.schema_optional,
        "properties": st.session_state.schema_properties,
        "additionalProperties": st.session_state.schema_additional_props
    }

def render_tools_config(tools_config: Dict[str, Any] = None):
    """Render tools configuration section"""
    st.subheader("Tools Configuration")
    
    if not tools_config:
        tools_config = {
            "tools_template": "{% raw %}{% set combined_tools = [] %}{% for tool_name, tool_config in tools.items() %}{% if use_%s|replace({'%s': tool_name}) %}{% set combined_tools = combined_tools + [{'name': tool_name, 'description': tool_config.description, 'parameters': tool_config.parameters}] %}{% endif %}{% endfor %}{{ combined_tools | tojson }}{% endraw %}",
            "tools": {}
        }
    
    # Simple tools editor
    st.info("Tools configuration is available as JSON")
    
    # Allow direct JSON editing
    tools_json = st.text_area(
        "Tools Configuration JSON",
        value=json.dumps(tools_config, indent=2),
        height=300,
        key="tools_json_editor"
    )
    
    try:
        tools_config = json.loads(tools_json)
    except json.JSONDecodeError:
        st.error("Invalid JSON. Changes will not be saved.")
    
    return tools_config

def render_playground():
    """Main playground render function"""
    try:
        prompt_id = st.session_state.get("prompt_id")
        version_id = st.session_state.get("version_id")
        
        if not prompt_id or not version_id:
            st.error("No prompt or version selected. Please select a prompt and version first.")
            st.session_state["current_page"] = "Version Manager"
            return
        
        # Header with context
        st.title("Prompt Playground")
        
        # Load prompt data
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(prompt_id)
        if not prompt:
            st.error(f"Prompt not found: {prompt_id}")
            return
        
        # Check if version exists
        if version_id not in prompt.get("versions", {}):
            st.error(f"Version {version_id} not found in prompt {prompt.get('name')}!")
            st.session_state["version_id"] = None
            return
        
        # Display prompt name and version
        st.write(f"<div style='font-size: 24px; font-weight: normal;'>Prompt: {prompt.get('name')} - Version: {version_id}</div>", unsafe_allow_html=True)

        st.write("")

        # Create a row with back and save buttons
        col1, spacer, col2 = st.columns([1, 3, 1])
        
        with col1:
            # Back to version manager button (left-aligned)
            if st.button("← Back to Version Manager", key="back_to_versions", use_container_width=True):
                st.session_state["current_page"] = "Version Manager"
                st.rerun()
        
        # Empty spacer column
        
        with col2:
            # Save button (right-aligned with different color)
            save_button_clicked = st.button("💾 Save All Changes", 
                                  key="save_all_changes", 
                                  use_container_width=True,
                                  type="primary")  # Type primary gives it a different color (usually blue)
        
        
        # Get version data
        version_data = prompt["versions"].get(version_id, {})
        
        # Log for debugging
        st.session_state["debug_version_data"] = version_data
        
        # Initialize schema session state on first load
        if "schema_properties" not in st.session_state:
            schema = version_data.get("schema", {})
            st.session_state.schema_properties = schema.get("properties", {})
            st.session_state.schema_required = schema.get("required", [])
            st.session_state.schema_optional = schema.get("optional", [])
            st.session_state.schema_additional_props = schema.get("additionalProperties", False)
            st.session_state.schema_changes = False
        
        # Configuration tabs - reduced from 5 to 4 tabs by removing the Test tab
        tab1, tab2, tab3, tab4 = st.tabs([
            "Model Config", "System Instruction", "Schema", "Tools"
        ])
        
        # Process each tab
        with tab1:
            try:
                config = render_model_config(version_data.get("config", {}))
            except Exception as e:
                st.error(f"Error in Model Config tab: {str(e)}")
                config = {}
        
        with tab2:
            try:
                system_instruction = render_system_prompt(
                    version_data.get("config", {}).get("system_instruction", "You are a helpful AI assistant.")
                )
            except Exception as e:
                st.error(f"Error in System Instruction tab: {str(e)}")
                system_instruction = "You are a helpful AI assistant."
        
        with tab3:
            try:
                schema = render_schema_editor(version_data.get("schema", {}))
            except Exception as e:
                st.error(f"Error in Schema tab: {str(e)}")
                schema = {"required": [], "optional": [], "properties": {}, "additionalProperties": False}
        
        with tab4:
            try:
                tools_config = render_tools_config(version_data.get("tools_config", None))
            except Exception as e:
                st.error(f"Error in Tools tab: {str(e)}")
                tools_config = None
        
        # Process save button click (moved from below)
        if save_button_clicked:
            try:
                # Create updated version data
                updated_version = {
                    "is_live": version_data.get("is_live", False),
                    "config": {
                        **config,
                        "system_instruction": system_instruction
                    },
                    "schema": schema,
                }
                
                # Debug information
                st.info(f"Saving with model: {config.get('model')} and provider: {config.get('provider')}")
                st.session_state["debug_updated_config"] = updated_version['config']
                
                # Preserve existing metadata or create new
                if "metadata" in version_data:
                    updated_version["metadata"] = version_data["metadata"]
                    updated_version["metadata"]["last_modified"] = datetime.now().isoformat()
                else:
                    updated_version["metadata"] = {
                        "author": "Promptix User",
                        "last_modified": datetime.now().isoformat(),
                        "last_modified_by": "Promptix User"
                    }
                    
                # Preserve created_at if it exists
                if "created_at" in version_data:
                    updated_version["created_at"] = version_data["created_at"]
                
                # Add tools_config if it exists
                if tools_config:
                    updated_version["tools_config"] = tools_config
                
                # Update the prompt
                prompt["versions"][version_id] = updated_version
                prompt_manager.save_prompt(prompt_id, prompt)
                
                # Reset schema_changes flag
                st.session_state.schema_changes = False
                
                # Clear form input fields by resetting session state
                for key in list(st.session_state.keys()):
                    if key.startswith("new_var_"):
                        del st.session_state[key]
                
                # Verify the save worked
                saved_prompt = prompt_manager.get_prompt(prompt_id)
                if saved_prompt and version_id in saved_prompt.get('versions', {}):
                    saved_config = saved_prompt['versions'][version_id]['config']
                    st.session_state["debug_saved_config"] = saved_config
                    st.info(f"Saved successfully with model: {saved_config.get('model')} and provider: {saved_config.get('provider')}")
                
                st.success("All changes saved successfully!")
            except Exception as e:
                st.error(f"Error saving changes: {str(e)}")
                st.error(traceback.format_exc())
    except Exception as e:
        st.error(f"Error rendering playground: {str(e)}")
        st.error(traceback.format_exc()) 