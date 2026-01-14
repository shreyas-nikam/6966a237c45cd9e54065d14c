
import streamlit as st
import pandas as pd
import uuid
import json
import os
import datetime as dt
from datetime import datetime
import shutil
import tempfile
# Import all Pydantic models, enums, and thread-safe in-memory storage CRUD functions
from source import *

# Helper function to get user-specific stores


def get_user_stores():
    """Returns the user-specific data stores from session state."""
    return {
        'systems': st.session_state['user_systems_store'],
        'tiering': st.session_state['user_tiering_store'],
        'risks': st.session_state['user_risks_store']
    }

# Lifecycle Risk Management Helper Functions


def add_lifecycle_risk(risk_entry: LifecycleRiskEntry):
    """Adds a new lifecycle risk to the in-memory store."""
    from source import _risks_lock
    stores = get_user_stores()
    with _risks_lock:
        stores['risks'][risk_entry.risk_id] = risk_entry


def get_risks_for_system(system_id: uuid.UUID):
    stores = get_user_stores()
    return [risk for risk in stores['risks'].values() if risk.system_id == system_id]


def get_lifecycle_risk(risk_id: uuid.UUID):
    stores = get_user_stores()
    return stores['risks'].get(risk_id)


def update_lifecycle_risk(risk_id: uuid.UUID, updates: dict):
    """Updates an existing lifecycle risk entry with thread safety."""
    from source import _risks_lock
    stores = get_user_stores()

    with _risks_lock:
        current_risk = stores['risks'].get(risk_id)
        if not current_risk:
            st.error(f"Risk with ID {risk_id} not found.")
            return False

        # Use Pydantic v2's model_dump()
        updated_data = current_risk.model_dump()

        # Ensure all enum values are converted to their enum instances if they are coming from forms as strings
        if 'lifecycle_phase' in updates:
            updates['lifecycle_phase'] = LifecyclePhase(
                updates['lifecycle_phase'])
        if 'risk_vector' in updates:
            updates['risk_vector'] = RiskVector(updates['risk_vector'])

        updated_data.update(updates)

        # Recalculate severity if impact or likelihood are updated
        # The LifecycleRiskEntry model will handle this automatically upon re-instantiation

        # Update created_at (acting as a last modified timestamp for the record)
        updated_data['created_at'] = dt.datetime.now().isoformat()

        try:
            updated_risk = LifecycleRiskEntry(**updated_data)
            stores['risks'][risk_id] = updated_risk
            return True
        except Exception as e:
            st.error(f"Error updating risk: {e}")
            return False


def delete_lifecycle_risk(risk_id: uuid.UUID):
    """Deletes a lifecycle risk entry with thread safety."""
    from source import _risks_lock
    stores = get_user_stores()
    with _risks_lock:
        if risk_id in stores['risks']:
            del stores['risks'][risk_id]

# Session State Helpers


def refresh_systems():
    stores = get_user_stores()
    systems = get_all_systems(stores)
    st.session_state['systems'] = systems
    system_ids = [str(s.system_id) for s in systems]

    # If a system is currently selected but no longer exists, reset it to None
    if st.session_state['selected_system_id'] and st.session_state['selected_system_id'] not in system_ids:
        st.session_state['selected_system_id'] = None

    # If no system is selected AND there are systems available, select the first one
    if not st.session_state['selected_system_id'] and systems:
        st.session_state['selected_system_id'] = str(systems[0].system_id)
    # If there are no systems, ensure selected_system_id is None
    elif not systems:
        st.session_state['selected_system_id'] = None


def refresh_tiering_result():
    stores = get_user_stores()
    if st.session_state['selected_system_id']:
        st.session_state['tiering_result'] = get_tiering_result(
            uuid.UUID(st.session_state['selected_system_id']), stores)
    else:
        st.session_state['tiering_result'] = None


def refresh_lifecycle_risks():
    stores = get_user_stores()
    if st.session_state['selected_system_id']:
        st.session_state['lifecycle_risks'] = get_risks_for_system(
            uuid.UUID(st.session_state['selected_system_id']))
    else:
        st.session_state['lifecycle_risks'] = []


def on_page_change():
    st.session_state['current_page'] = st.session_state['sidebar_selection']
    # Clear editing state when changing page
    st.session_state['editing_system'] = None
    st.session_state['editing_risk'] = None
    # Streamlit automatically reruns after callbacks complete


# App Setup
st.set_page_config(
    page_title="QuLab: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map")
st.divider()

create_tables()

# Initialize user-specific data stores - MUST BE FIRST
if 'user_systems_store' not in st.session_state:
    st.session_state['user_systems_store'] = {}
if 'user_tiering_store' not in st.session_state:
    st.session_state['user_tiering_store'] = {}
if 'user_risks_store' not in st.session_state:
    st.session_state['user_risks_store'] = {}

# Initialize Session State - CRITICAL ORDERING
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Inventory Management"

# Initialize selected_system_id FIRST, as refresh_systems and other logic depend on it
if 'selected_system_id' not in st.session_state:
    st.session_state['selected_system_id'] = None

# Then refresh systems, which now intelligently sets or unsets selected_system_id based on available systems
if 'systems' not in st.session_state:
    refresh_systems()

# Then refresh dependent states, which now can safely check st.session_state['selected_system_id']
if 'tiering_result' not in st.session_state:
    refresh_tiering_result()
if 'lifecycle_risks' not in st.session_state:
    refresh_lifecycle_risks()

# Other UI state variables
if 'editing_system' not in st.session_state:
    st.session_state['editing_system'] = None
if 'system_form_key' not in st.session_state:
    st.session_state['system_form_key'] = 0
if 'editing_risk' not in st.session_state:
    st.session_state['editing_risk'] = None
if 'risk_form_key' not in st.session_state:
    st.session_state['risk_form_key'] = 0
if 'last_selected_risk_id' not in st.session_state:
    st.session_state['last_selected_risk_id'] = None
if 'success_message' not in st.session_state:
    st.session_state['success_message'] = None
if 'info_message' not in st.session_state:
    st.session_state['info_message'] = None


# Navigation
page_options = [
    "Inventory Management",
    "Risk Tiering",
    "Lifecycle Risk Register",
    "Exports & Evidence"
]

# Ensure current_page is one of the valid options
if st.session_state['current_page'] not in page_options:
    st.session_state['current_page'] = page_options[0]


st.sidebar.selectbox(
    "Select a section",
    page_options,
    index=page_options.index(st.session_state['current_page']),
    key='sidebar_selection',
    on_change=on_page_change
)

# Sidebar System Selector
# This section will only show if not on "Inventory Management" OR if a system is selected.
# If on "Inventory Management" and no system is selected (e.g., initially, no sample data loaded), this section will not show.
if st.session_state['current_page'] != "Inventory Management" or st.session_state['selected_system_id']:
    st.sidebar.markdown("---")

    system_names = {
        str(s.system_id): s.name for s in st.session_state['systems']}
    system_ids_list = list(system_names.keys())

    if system_ids_list:  # Only show the selectbox if there are systems to choose from
        # Ensure selected_system_id is valid for the current list of systems.
        # refresh_systems already handles setting it to a default or None,
        # but this acts as an extra safety check in case the list changes dynamically.
        if st.session_state['selected_system_id'] not in system_ids_list:
            # Default to the first system
            st.session_state['selected_system_id'] = system_ids_list[0]

        # Ensure default_index is valid
        try:
            current_index = system_ids_list.index(
                st.session_state['selected_system_id'])
        except ValueError:
            current_index = 0  # Fallback if selected system somehow isn't in list

        selected_id_from_selectbox = st.sidebar.selectbox(
            "Choose an AI System for details:",
            options=system_ids_list,
            # Use .get with default for robustness
            format_func=lambda x: system_names.get(x, x),
            index=current_index,
            key='sidebar_system_selector'
        )

        # Update session state if the selection changed
        if selected_id_from_selectbox != st.session_state['selected_system_id']:
            st.session_state['selected_system_id'] = selected_id_from_selectbox
            refresh_tiering_result()
            refresh_lifecycle_risks()
            st.rerun()

        selected_system_obj = next((s for s in st.session_state['systems'] if str(
            s.system_id) == st.session_state['selected_system_id']), None)
        if selected_system_obj:
            st.sidebar.markdown(f"**{selected_system_obj.name}**")
            st.sidebar.markdown(f"*{selected_system_obj.description[:50]}...*")
    else:
        st.sidebar.warning(
            "No systems available. Please add or load sample systems.")
        # Explicitly ensure selected_system_id is None if no systems are available to prevent errors on other pages.
        st.session_state['selected_system_id'] = None

# Page: Inventory Management
if st.session_state['current_page'] == "Inventory Management":
    st.header("AI System Inventory")
    st.markdown(f"As Alex, the AI Product Engineer, your task is to maintain an accurate and up-to-date inventory of all AI systems. This is the single source of truth for understanding deployed AI, ownership, purpose, and technical characteristics.")

    # Create tabs for different inventory operations
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

    # TAB 1: VIEW
    with tab1:
        st.subheader("Current Inventory")

        if st.session_state['systems']:
            data_list = []
            for s in st.session_state['systems']:
                d = s.model_dump()
                d['system_id'] = str(d['system_id'])
                d['ai_type'] = d['ai_type'].value
                d['deployment_mode'] = d['deployment_mode'].value
                d['decision_criticality'] = d['decision_criticality'].value
                d['automation_level'] = d['automation_level'].value
                d['data_sensitivity'] = d['data_sensitivity'].value
                d['external_dependencies'] = ", ".join(
                    d['external_dependencies'])
                data_list.append(d)

            df = pd.DataFrame(data_list)
            st.dataframe(df[['name', 'domain', 'ai_type', 'owner_role',
                         'decision_criticality', 'updated_at']], use_container_width=True)
        else:
            st.info(
                "No systems in the inventory. Add a new system or load sample systems to get started.")

    # TAB 2: ADD
    with tab2:
        st.subheader("Add New AI System")

        # Display success messages only for add operations
        if st.session_state.get('success_message') and st.session_state.get('success_message').startswith('✅ Success! AI System'):
            st.success(st.session_state['success_message'])
            st.session_state['success_message'] = None
        if st.session_state.get('info_message'):
            st.info(st.session_state['info_message'])
            st.session_state['info_message'] = None

        with st.form(key="add_system_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                f_name = st.text_input(
                    "Name *", value="", placeholder="Enter system name")
                f_domain = st.text_input(
                    "Domain *", value="", placeholder="e.g., Finance, Healthcare")
                f_owner = st.text_input(
                    "Owner Role *", value="", placeholder="e.g., Data Science Team")
                ai_opts = [e.value for e in AIType]
                f_ai_type = st.selectbox("AI Type", options=ai_opts, index=0)
                dm_opts = [e.value for e in DeploymentMode]
                f_deploy = st.selectbox(
                    "Deployment Mode", options=dm_opts, index=0)

            with c2:
                f_desc = st.text_area(
                    "Description *", value="", placeholder="Describe the AI system's purpose and functionality", height=100)
                dc_opts = [e.value for e in DecisionCriticality]
                f_crit = st.selectbox(
                    "Decision Criticality", options=dc_opts, index=0)
                al_opts = [e.value for e in AutomationLevel]
                f_auto = st.selectbox("Automation Level",
                                      options=al_opts, index=0)
                ds_opts = [e.value for e in DataSensitivity]
                f_sens = st.selectbox("Data Sensitivity",
                                      options=ds_opts, index=0)

            f_deps_str = st.text_input(
                "External Dependencies (comma-separated)", value="", placeholder="e.g., OpenAI API, AWS S3")

            st.caption("* Required fields")

            submitted = st.form_submit_button("Add System", type="primary")

            if submitted:
                # Comprehensive field validation
                errors = []

                if not f_name or not f_name.strip():
                    errors.append("❌ System name is required.")
                elif len(f_name.strip()) < 3:
                    errors.append(
                        "❌ System name must be at least 3 characters long.")

                if not f_domain or not f_domain.strip():
                    errors.append("❌ Domain is required.")

                if not f_owner or not f_owner.strip():
                    errors.append("❌ Owner role is required.")

                if not f_desc or not f_desc.strip():
                    errors.append("❌ Description is required.")
                elif len(f_desc.strip()) < 10:
                    errors.append(
                        "❌ Description must be at least 10 characters long.")

                # Display all validation errors
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        deps_list = [d.strip()
                                     for d in f_deps_str.split(',') if d.strip()]
                        sys_data = {
                            "name": f_name.strip(),
                            "description": f_desc.strip(),
                            "domain": f_domain.strip(),
                            "ai_type": AIType(f_ai_type),
                            "owner_role": f_owner.strip(),
                            "deployment_mode": DeploymentMode(f_deploy),
                            "decision_criticality": DecisionCriticality(f_crit),
                            "automation_level": AutomationLevel(f_auto),
                            "data_sensitivity": DataSensitivity(f_sens),
                            "external_dependencies": deps_list
                        }

                        new_sys = SystemMetadata(**sys_data)
                        stores = get_user_stores()
                        add_system(new_sys, stores)
                        st.session_state[
                            'success_message'] = f"✅ Success! AI System '{f_name.strip()}' has been added to the inventory."
                        st.session_state['info_message'] = f"📊 System ID: {new_sys.system_id} | Domain: {f_domain.strip()} | Owner: {f_owner.strip()}"
                        refresh_systems()
                        refresh_tiering_result()
                        refresh_lifecycle_risks()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding system: {e}")

    # TAB 3: EDIT
    with tab3:
        st.subheader("Edit AI System")

        # Display success messages only for edit operations
        if st.session_state.get('success_message') and 'updated successfully' in st.session_state.get('success_message', ''):
            st.success(st.session_state['success_message'])
            st.session_state['success_message'] = None

        if not st.session_state['systems']:
            st.info("No systems available to edit. Please add systems first.")
        else:
            # Create system selector
            sys_opts = [str(s.system_id) for s in st.session_state['systems']]
            sys_names = [s.name for s in st.session_state['systems']]

            # Determine default selection
            if st.session_state['selected_system_id'] and st.session_state['selected_system_id'] in sys_opts:
                default_index = sys_opts.index(
                    st.session_state['selected_system_id'])
            else:
                default_index = 0

            sel_sys_edit = st.selectbox(
                "Select System to Edit:",
                options=sys_opts,
                format_func=lambda x: next(
                    (name for i, name in enumerate(sys_names) if sys_opts[i] == x), x),
                index=default_index,
                key="edit_system_selector"
            )

            # Get the selected system object
            stores = get_user_stores()
            sys_edit = get_system(uuid.UUID(sel_sys_edit), stores)

            if sys_edit:
                st.markdown("---")
                with st.form(key="edit_system_form", clear_on_submit=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        f_name = st.text_input("Name", value=sys_edit.name)
                        f_domain = st.text_input(
                            "Domain", value=sys_edit.domain)
                        f_owner = st.text_input(
                            "Owner Role", value=sys_edit.owner_role)
                        ai_opts = [e.value for e in AIType]
                        f_ai_type = st.selectbox(
                            "AI Type", options=ai_opts, index=ai_opts.index(sys_edit.ai_type.value))
                        dm_opts = [e.value for e in DeploymentMode]
                        f_deploy = st.selectbox("Deployment Mode", options=dm_opts, index=dm_opts.index(
                            sys_edit.deployment_mode.value))

                    with c2:
                        f_desc = st.text_area(
                            "Description", value=sys_edit.description)
                        dc_opts = [e.value for e in DecisionCriticality]
                        f_crit = st.selectbox("Decision Criticality", options=dc_opts, index=dc_opts.index(
                            sys_edit.decision_criticality.value))
                        al_opts = [e.value for e in AutomationLevel]
                        f_auto = st.selectbox("Automation Level", options=al_opts, index=al_opts.index(
                            sys_edit.automation_level.value))
                        ds_opts = [e.value for e in DataSensitivity]
                        f_sens = st.selectbox("Data Sensitivity", options=ds_opts, index=ds_opts.index(
                            sys_edit.data_sensitivity.value))

                    curr_deps = ", ".join(sys_edit.external_dependencies)
                    f_deps_str = st.text_input(
                        "External Dependencies (comma-separated)", value=curr_deps)

                    submitted = st.form_submit_button("Update System")

                    if submitted:
                        try:
                            deps_list = [d.strip()
                                         for d in f_deps_str.split(',') if d.strip()]
                            sys_data = {
                                "name": f_name, "description": f_desc, "domain": f_domain,
                                "ai_type": AIType(f_ai_type), "owner_role": f_owner,
                                "deployment_mode": DeploymentMode(f_deploy),
                                "decision_criticality": DecisionCriticality(f_crit),
                                "automation_level": AutomationLevel(f_auto),
                                "data_sensitivity": DataSensitivity(f_sens),
                                "external_dependencies": deps_list
                            }

                            stores = get_user_stores()
                            update_system(sys_edit.system_id, sys_data, stores)
                            st.session_state['success_message'] = f"✅ System '{f_name}' updated successfully!"
                            refresh_systems()
                            refresh_tiering_result()
                            refresh_lifecycle_risks()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # TAB 4: DELETE
    with tab4:
        st.subheader("Delete AI System")

        # Display success messages only for delete operations
        if st.session_state.get('success_message') and 'deleted successfully' in st.session_state.get('success_message', ''):
            st.success(st.session_state['success_message'])
            st.session_state['success_message'] = None

        if not st.session_state['systems']:
            st.info("No systems available to delete.")
        else:
            st.warning(
                "⚠️ Warning: Deleting a system will permanently remove it and all associated data.")

            # Create system selector
            sys_opts = [str(s.system_id) for s in st.session_state['systems']]
            sys_names = [s.name for s in st.session_state['systems']]

            # Determine default selection
            if st.session_state['selected_system_id'] and st.session_state['selected_system_id'] in sys_opts:
                default_index = sys_opts.index(
                    st.session_state['selected_system_id'])
            else:
                default_index = 0

            sel_sys_delete = st.selectbox(
                "Select System to Delete:",
                options=sys_opts,
                format_func=lambda x: next(
                    (name for i, name in enumerate(sys_names) if sys_opts[i] == x), x),
                index=default_index,
                key="delete_system_selector"
            )

            # Show system details
            stores = get_user_stores()
            sys_to_delete = get_system(uuid.UUID(sel_sys_delete), stores)
            if sys_to_delete:
                st.markdown("---")
                st.markdown("**System Details:**")
                st.write(f"**Name:** {sys_to_delete.name}")
                st.write(f"**Domain:** {sys_to_delete.domain}")
                st.write(f"**Owner:** {sys_to_delete.owner_role}")
                st.write(f"**AI Type:** {sys_to_delete.ai_type.value}")
                st.markdown("---")

                if st.button("🗑️ Confirm Delete", type="primary", key="confirm_delete_btn"):
                    system_name = sys_to_delete.name
                    try:
                        stores = get_user_stores()
                        delete_system(uuid.UUID(sel_sys_delete), stores)

                        # Clear the selected system if we're deleting it
                        if st.session_state['selected_system_id'] == sel_sys_delete:
                            st.session_state['selected_system_id'] = None

                        st.session_state['success_message'] = f"✅ System '{system_name}' deleted successfully."
                        refresh_systems()
                        refresh_tiering_result()
                        refresh_lifecycle_risks()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete system: {e}")

# Page: Risk Tiering
elif st.session_state['current_page'] == "Risk Tiering":
    st.header("Deterministic Risk Tiering")
    st.markdown(f"As Alex, determine the inherent risk tier for the selected AI system. Aperture Analytics Corp. uses a **deterministic tiering algorithm** to objectively classify AI systems into Tier 1 (High Risk), Tier 2 (Medium Risk), or Tier 3 (Low Risk).")

    if not st.session_state['selected_system_id']:
        st.warning(
            "Please select an AI system from the sidebar to view its risk tiering information.")
    else:
        curr_sys = next((s for s in st.session_state['systems'] if str(
            s.system_id) == st.session_state['selected_system_id']), None)
        if not curr_sys:
            st.error(
                "Selected system not found in inventory. Please refresh or select another system.")
            # Clear invalid selection
            st.session_state['selected_system_id'] = None
            st.rerun()
        else:
            st.subheader(f"System: {curr_sys.name}")
            st.markdown(r"$$S = \sum_{d \in D} \text{points}(d)$$")
            st.markdown(
                f"The total score (S) is compared to predefined thresholds to assign the risk tier. A higher score indicates higher inherent risk.")

            if st.button("Compute Risk Tier"):
                res = calculate_risk_tier(curr_sys)
                stores = get_user_stores()
                save_tiering_result(res, stores)
                st.session_state['tiering_result'] = res
                st.success(
                    f"Risk tier calculated and saved for {curr_sys.name}!")
                st.rerun()  # Rerun to update the displayed result immediately

            st.markdown("---")
            # Ensure the displayed tiering result corresponds to the currently selected system
            if st.session_state['tiering_result'] and str(st.session_state['tiering_result'].system_id) == str(curr_sys.system_id):
                res = st.session_state['tiering_result']
                st.subheader(
                    f"Result: {res.risk_tier.value} (Total Score: {res.total_score})")

                bd_df = pd.DataFrame(res.score_breakdown.items(), columns=[
                                     "Dimension", "Points"])
                st.dataframe(bd_df, use_container_width=True, hide_index=True)

                st.subheader("Controls & Justification")
                with st.form("tier_edit"):
                    just = st.text_area(
                        "Justification for this tier assignment:", value=res.justification)
                    ctrls_str = "\n".join(res.required_controls)
                    ctrls_edit = st.text_area(
                        "Required Controls (one per line):", value=ctrls_str)

                    if st.form_submit_button("Save Changes to Tiering Result"):
                        res_data = res.model_dump()  # Pydantic v2 change: .dict() -> .model_dump()
                        res_data['justification'] = just
                        res_data['required_controls'] = [c.strip()
                                                         for c in ctrls_edit.split('\n') if c.strip()]
                        # Store as datetime object
                        res_data['computed_at'] = dt.datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S.%f")

                        new_res = TieringResult(**res_data)
                        stores = get_user_stores()
                        save_tiering_result(new_res, stores)
                        st.session_state['tiering_result'] = new_res
                        st.session_state['success_message'] = "✅ Tiering result updated successfully!"
                        st.rerun()

                    # Display success messages
                    if st.session_state.get('success_message'):
                        st.success(st.session_state['success_message'])
                        st.session_state['success_message'] = None
            else:
                st.info(
                    "No tiering result available for this system yet. Click 'Compute Risk Tier' to generate one.")

# Page: Lifecycle Risk Register
elif st.session_state['current_page'] == "Lifecycle Risk Register":
    st.header("Lifecycle Risk Register")
    st.markdown(f"As Alex, identify and document risks across the lifecycle of the selected AI system. Each risk is categorized by its lifecycle phase and risk vector, with a calculated severity based on impact and likelihood.")
    st.markdown(
        r"$$\text{Severity} = \text{Impact} \times \text{Likelihood}$$")

    if not st.session_state['selected_system_id']:
        st.warning(
            "Please select an AI system from the sidebar to manage its lifecycle risks.")
    else:
        # Refresh risks if the selected system has changed or if risks are empty/invalid for the current system.
        # This check ensures that the lifecycle_risks in session_state always correspond to the selected system.
        if st.session_state['lifecycle_risks'] and \
           (not st.session_state['selected_system_id'] or str(st.session_state['lifecycle_risks'][0].system_id) != st.session_state['selected_system_id']):
            refresh_lifecycle_risks()
        elif not st.session_state['lifecycle_risks'] and st.session_state['selected_system_id'] and get_risks_for_system(uuid.UUID(st.session_state['selected_system_id'])):
            # Only refresh if there are risks in storage for current system but not in session state.
            refresh_lifecycle_risks()

        # Create tabs for different risk operations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete", "📊 Matrix"])

        # TAB 1: VIEW
        with tab1:
            st.subheader("Existing Risks")
            if st.session_state['lifecycle_risks']:
                r_data = []
                for r in st.session_state['lifecycle_risks']:
                    d = r.model_dump()
                    d['risk_id'] = str(d['risk_id'])
                    d['lifecycle_phase'] = d['lifecycle_phase'].value
                    d['risk_vector'] = d['risk_vector'].value
                    r_data.append(d)

                df_r = pd.DataFrame(r_data)
                df_display = df_r[['risk_statement', 'lifecycle_phase', 'risk_vector',
                                   'impact', 'likelihood', 'severity', 'owner_role', 'mitigation', 'created_at']]
                st.dataframe(df_display, use_container_width=True,
                             hide_index=True)
            else:
                st.info(
                    "No lifecycle risks found for this AI system. Use the 'Add' tab to document the first risk.")

        # TAB 2: ADD
        with tab2:
            st.subheader("Add New Risk")

            # Display success messages for add operations
            if st.session_state.get('success_message') and 'added successfully' in st.session_state.get('success_message', ''):
                st.success(st.session_state['success_message'])
                st.session_state['success_message'] = None

            with st.form(key="add_risk_form", clear_on_submit=False):
                c1, c2 = st.columns(2)

                lp_opts = [e.value for e in LifecyclePhase]
                rv_opts = [e.value for e in RiskVector]

                with c1:
                    n_lp = st.selectbox("Lifecycle Phase",
                                        options=lp_opts, index=0)
                    n_rv = st.selectbox(
                        "Risk Vector", options=rv_opts, index=0)
                    n_imp = st.slider("Impact (1=Low, 5=High)", 1, 5, 1)

                with c2:
                    n_own = st.text_input(
                        "Risk Owner Role", value="", placeholder="e.g., Data Science Team")
                    n_like = st.slider(
                        "Likelihood (1=Rare, 5=Frequent)", 1, 5, 1)

                n_stmt = st.text_area(
                    "Risk Statement", value="", placeholder="Describe the risk...", height=100)
                n_mit = st.text_area("Mitigation Strategy",
                                     value="", placeholder="How will this risk be mitigated?", height=100)
                n_ev = st.text_input(
                    "Evidence Links (comma-separated URLs)", value="", placeholder="https://example.com/doc1, https://example.com/doc2")

                submitted = st.form_submit_button("Add Risk", type="primary")

                if submitted:
                    if not n_stmt.strip():
                        st.error("❌ Risk statement is required.")
                    elif not n_own.strip():
                        st.error("❌ Risk owner role is required.")
                    else:
                        try:
                            r_data = {
                                "system_id": uuid.UUID(st.session_state['selected_system_id']),
                                "lifecycle_phase": n_lp,
                                "risk_vector": n_rv,
                                "risk_statement": n_stmt,
                                "impact": n_imp,
                                "likelihood": n_like,
                                "mitigation": n_mit,
                                "owner_role": n_own,
                                "evidence_links": [l.strip() for l in n_ev.split(',') if l.strip()]
                            }

                            new_r = LifecycleRiskEntry(**r_data)
                            add_lifecycle_risk(new_r)
                            st.session_state[
                                'success_message'] = f"✅ New risk added successfully! Severity: {new_r.severity}"
                            refresh_lifecycle_risks()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error adding risk: {e}")

        # TAB 3: EDIT
        with tab3:
            st.subheader("Edit Existing Risk")

            # Display success messages for edit operations
            if st.session_state.get('success_message') and 'updated successfully' in st.session_state.get('success_message', ''):
                st.success(st.session_state['success_message'])
                st.session_state['success_message'] = None

            if not st.session_state['lifecycle_risks']:
                st.info(
                    "No risks available to edit. Add risks first using the 'Add' tab.")
            else:
                r_data = []
                for r in st.session_state['lifecycle_risks']:
                    d = r.model_dump()
                    d['risk_id'] = str(d['risk_id'])
                    d['lifecycle_phase'] = d['lifecycle_phase'].value
                    d['risk_vector'] = d['risk_vector'].value
                    r_data.append(d)

                df_r = pd.DataFrame(r_data)
                risk_id_options = df_r['risk_id'].tolist()

                # Ensure the selected risk for edit exists in the current list
                if st.session_state['last_selected_risk_id'] not in risk_id_options:
                    st.session_state['last_selected_risk_id'] = risk_id_options[0] if risk_id_options else None

                if st.session_state['last_selected_risk_id']:
                    try:
                        default_index_risk = risk_id_options.index(
                            st.session_state['last_selected_risk_id'])
                    except ValueError:
                        default_index_risk = 0
                else:
                    default_index_risk = 0

                sel_r_id = st.selectbox(
                    "Select a Risk to Edit:",
                    options=risk_id_options,
                    format_func=lambda x: df_r[df_r['risk_id'] ==
                                               x].iloc[0]['risk_statement'][:70] + "...",
                    index=default_index_risk,
                    key='edit_risk_selector'
                )
                st.session_state['last_selected_risk_id'] = sel_r_id

                r_edit = get_lifecycle_risk(uuid.UUID(sel_r_id))

                if r_edit:
                    st.markdown("---")
                    with st.form(key="edit_risk_form", clear_on_submit=False):
                        c1, c2 = st.columns(2)

                        lp_opts = [e.value for e in LifecyclePhase]
                        rv_opts = [e.value for e in RiskVector]

                        with c1:
                            n_lp = st.selectbox("Lifecycle Phase", options=lp_opts, index=lp_opts.index(
                                r_edit.lifecycle_phase.value))
                            n_rv = st.selectbox(
                                "Risk Vector", options=rv_opts, index=rv_opts.index(r_edit.risk_vector.value))
                            n_imp = st.slider(
                                "Impact (1=Low, 5=High)", 1, 5, r_edit.impact)

                        with c2:
                            n_own = st.text_input(
                                "Risk Owner Role", value=r_edit.owner_role)
                            n_like = st.slider(
                                "Likelihood (1=Rare, 5=Frequent)", 1, 5, r_edit.likelihood)
                            st.info(f"Calculated Severity: {n_imp * n_like}")

                        n_stmt = st.text_area(
                            "Risk Statement", value=r_edit.risk_statement, height=100)
                        n_mit = st.text_area("Mitigation Strategy",
                                             value=r_edit.mitigation, height=100)
                        n_ev = st.text_input(
                            "Evidence Links (comma-separated URLs)", value=", ".join(r_edit.evidence_links))

                        submitted = st.form_submit_button(
                            "Save Changes", type="primary")

                        if submitted:
                            try:
                                r_data = {
                                    "lifecycle_phase": n_lp,
                                    "risk_vector": n_rv,
                                    "risk_statement": n_stmt,
                                    "impact": n_imp,
                                    "likelihood": n_like,
                                    "mitigation": n_mit,
                                    "owner_role": n_own,
                                    "evidence_links": [l.strip() for l in n_ev.split(',') if l.strip()]
                                }

                                update_lifecycle_risk(r_edit.risk_id, r_data)
                                st.session_state['success_message'] = "✅ Risk updated successfully!"
                                refresh_lifecycle_risks()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error updating risk: {e}")

        # TAB 4: DELETE
        with tab4:
            st.subheader("Delete Risk")

            # Display success messages for delete operations
            if st.session_state.get('success_message') and 'deleted successfully' in st.session_state.get('success_message', ''):
                st.success(st.session_state['success_message'])
                st.session_state['success_message'] = None

            if not st.session_state['lifecycle_risks']:
                st.info("No risks available to delete.")
            else:
                st.warning(
                    "⚠️ Warning: Deleting a risk will permanently remove it from the register.")

                r_data = []
                for r in st.session_state['lifecycle_risks']:
                    d = r.model_dump()
                    d['risk_id'] = str(d['risk_id'])
                    d['lifecycle_phase'] = d['lifecycle_phase'].value
                    d['risk_vector'] = d['risk_vector'].value
                    r_data.append(d)

                df_r = pd.DataFrame(r_data)
                risk_id_options = df_r['risk_id'].tolist()

                # Determine default selection
                if st.session_state['last_selected_risk_id'] in risk_id_options:
                    default_index = risk_id_options.index(
                        st.session_state['last_selected_risk_id'])
                else:
                    default_index = 0

                sel_r_id_delete = st.selectbox(
                    "Select Risk to Delete:",
                    options=risk_id_options,
                    format_func=lambda x: df_r[df_r['risk_id'] ==
                                               x].iloc[0]['risk_statement'][:70] + "...",
                    index=default_index,
                    key="delete_risk_selector"
                )

                # Show risk details
                risk_to_delete = get_lifecycle_risk(uuid.UUID(sel_r_id_delete))
                if risk_to_delete:
                    st.markdown("---")
                    st.markdown("**Risk Details:**")
                    st.write(
                        f"**Risk Statement:** {risk_to_delete.risk_statement}")
                    st.write(
                        f"**Phase:** {risk_to_delete.lifecycle_phase.value}")
                    st.write(f"**Vector:** {risk_to_delete.risk_vector.value}")
                    st.write(
                        f"**Severity:** {risk_to_delete.severity} (Impact: {risk_to_delete.impact}, Likelihood: {risk_to_delete.likelihood})")
                    st.markdown("---")

                    if st.button("🗑️ Confirm Delete", type="primary", key="confirm_delete_risk_btn"):
                        try:
                            delete_lifecycle_risk(uuid.UUID(sel_r_id_delete))
                            st.session_state['success_message'] = "✅ Risk deleted successfully."
                            refresh_lifecycle_risks()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to delete risk: {e}")

        # TAB 5: MATRIX
        with tab5:
            st.subheader("Lifecycle Phase x Risk Vector Matrix")

            if st.session_state['lifecycle_risks']:
                stores = get_user_stores()
                matrix = generate_risk_matrix(
                    uuid.UUID(st.session_state['selected_system_id']), stores)
                if not matrix.empty:
                    st.dataframe(matrix, use_container_width=True)
                    st.info(
                        "ℹ️ This matrix shows the count and maximum severity of risks for each lifecycle phase and risk vector combination.")
                else:
                    st.info(
                        "No risks documented to generate the matrix.")
            else:
                st.info(
                    "No risks available. Add risks to see the matrix visualization.")

# Page: Exports
elif st.session_state['current_page'] == "Exports & Evidence":
    st.header("Generate Traceable Evidence Package")
    st.markdown(f"As Alex, prepare a formal evidence package with SHA-256 hashes for all AI systems and their associated risk data. This provides an immutable record for audit and compliance.")
    st.markdown(r"$$\text{EvidenceHash} = \text{SHA256}(\text{Artifacts})$$")

    if not st.session_state['systems']:
        st.warning(
            "No AI systems are currently registered in the inventory. Please add systems before generating an evidence package.")
    else:
        u_name = st.text_input(
            "Team/User Name (for evidence package record)", "AI Product Engineer Alex")
        if st.button("Generate Evidence Package"):
            if u_name:
                with st.spinner("Generating the traceable evidence package... This may take a moment."):
                    # Create unique temporary directory for this user's evidence package
                    temp_dir = tempfile.mkdtemp(prefix="evidence_")
                    try:
                        stores = get_user_stores()
                        # Use timestamp-based unique run_id
                        unique_run_id = f"case1_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        result = generate_evidence_package(
                            run_id=unique_run_id, team_or_user=u_name, output_dir_base=temp_dir, stores=stores)

                        # generate_evidence_package returns a manifest dict, not a path
                        # Extract the run_id and construct the zip path
                        run_id = result['run_id']
                        zip_path = os.path.join(
                            temp_dir, f"Case_01_{run_id}.zip")

                        st.success(
                            f"✅ Evidence package successfully generated!")
                        # Provide a download button
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                            st.download_button(
                                label="📥 Download Evidence Package (ZIP)",
                                data=zip_data,
                                file_name=f"Case_01_{run_id}.zip",
                                mime="application/zip"
                            )
                        st.info(
                            "The package includes a manifest with SHA-256 hashes of all generated artifacts for traceability.")

                        # Clean up the temporary directory after successful generation
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception as e:
                        # Clean up temp directory on error too
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        st.error(
                            f"An error occurred during package generation: {e}")
            else:
                st.error(
                    "Please provide your Team/User Name to generate the evidence package.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
