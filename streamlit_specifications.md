
# Streamlit Application Specification: AI System Governance Control Surface

## 1. Application Overview

This Streamlit application, "AI System Governance Control Surface," is designed for AI Product Engineers (like Alex at Aperture Analytics Corp.) to manage and govern AI systems throughout their lifecycle. It provides a pragmatic, enterprise-grade interface for core governance functions, addressing common challenges such as fragmented inventories, inconsistent risk classifications, and a lack of traceable risk management.

The application guides the user through a structured workflow:

1.  **Inventory Management**: Register, view, update, and delete AI systems with auditable metadata, ensuring a single source of truth. This is where Alex onboards new AI systems like "ApertureMind Assist."
2.  **Risk Tiering**: Automatically assess the inherent risk of selected AI systems using a deterministic algorithm, leading to the assignment of a risk tier and associated required controls. Alex uses this to understand the oversight needed for "ApertureMind Assist."
3.  **Lifecycle Risk Register**: Document and track specific risks across different lifecycle phases and risk vectors for a chosen system, calculating severity and managing mitigation plans. This helps Alex build a comprehensive risk profile for their AI systems.
4.  **Exports & Evidence**: Generate a traceable evidence package, including all governance artifacts and an integrity-checked manifest, suitable for internal audits and compliance. This is Alex's final step to formalize the governance record.

By following this workflow, users can operationalize responsible AI practices, reduce operational risk, and ensure compliance for their AI initiatives.

## 2. Code Requirements

### Import Statements

```python
import streamlit as st
import pandas as pd
import uuid
import json
from datetime import datetime
from source import (
    CONFIG, AIType, DeploymentMode, DecisionCriticality, AutomationLevel, DataSensitivity, RiskTier,
    LifecyclePhase, RiskVector, SystemMetadata, TieringResult, LifecycleRiskEntry,
    get_db_connection, create_tables, load_sample_systems_data, add_system, get_system,
    get_all_systems, update_system, delete_system, calculate_risk_tier, save_tiering_result,
    get_tiering_result, generate_risk_matrix, generate_evidence_package
)

# Assume these lifecycle risk CRUD functions are available in source.py as per requirements
# They are not explicitly in the provided source.py snippet but implied by the problem statement.
# Placeholder implementation for specification purposes if not already in source.py:
# def add_lifecycle_risk(risk_entry: LifecycleRiskEntry):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO lifecycle_risks (risk_id, system_id, json, created_at) VALUES (?, ?, ?, ?)",
#         (str(risk_entry.risk_id), str(risk_entry.system_id), risk_entry.json(), risk_entry.created_at)
#     )
#     conn.commit()
#     conn.close()

# def get_risks_for_system(system_id: uuid.UUID) -> List[LifecycleRiskEntry]:
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT json FROM lifecycle_risks WHERE system_id = ?", (str(system_id),))
#     rows = cursor.fetchall()
#     conn.close()
#     return [LifecycleRiskEntry.parse_raw(row['json']) for row in rows]

# def get_lifecycle_risk(risk_id: uuid.UUID) -> Optional[LifecycleRiskEntry]:
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT json FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
#     row = cursor.fetchone()
#     conn.close()
#     if row:
#         return LifecycleRiskEntry.parse_raw(row['json'])
#     return None

# def update_lifecycle_risk(risk_id: uuid.UUID, updates: Dict[str, Any]):
#     current_risk = get_lifecycle_risk(risk_id)
#     if not current_risk:
#         return False
#     updated_data = current_risk.dict()
#     updated_data.update(updates)
#     # Re-calculate severity if impact/likelihood changed
#     if 'impact' in updates or 'likelihood' in updates:
#         updated_data['severity'] = updated_data['impact'] * updated_data['likelihood']
#     updated_data['created_at'] = datetime.now(datetime.timezone.utc).isoformat()
#     try:
#         updated_risk = LifecycleRiskEntry(**updated_data)
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "UPDATE lifecycle_risks SET json = ?, created_at = ? WHERE risk_id = ?",
#             (updated_risk.json(), updated_risk.created_at, str(risk_id))
#         )
#         conn.commit()
#         conn.close()
#         return True
#     except ValidationError as e:
#         print(f"Validation error updating risk {risk_id}: {e}")
#         return False

# def delete_lifecycle_risk(risk_id: uuid.UUID):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
#     conn.commit()
#     conn.close()
```

### `st.session_state` Design

The following `st.session_state` keys will be used to maintain application state across user interactions and simulated "pages":

*   `st.session_state['current_page']`:
    *   **Initialized**: `'Inventory Management'`
    *   **Updated**: Via `st.sidebar.selectbox` callback (e.g., `on_page_change`).
    *   **Read**: To conditionally render the content of the main area.
*   `st.session_state['systems']`:
    *   **Initialized**: `[]` (empty list of `SystemMetadata` objects)
    *   **Updated**:
        *   After `load_sample_systems_data()` completes.
        *   After `add_system()`, `update_system()`, `delete_system()` calls.
        *   Refreshed via `refresh_systems()` helper function.
    *   **Read**: To populate the system inventory table, dropdowns for system selection, and provide data for tiering/risk management.
*   `st.session_state['selected_system_id']`:
    *   **Initialized**: `None`
    *   **Updated**: When a system is selected from a dropdown or table in the Inventory. Also reset to `None` if the selected system is deleted or no systems exist.
    *   **Read**: To filter `TieringResult` and `LifecycleRiskEntry` for the selected system.
*   `st.session_state['tiering_result']`:
    *   **Initialized**: `None`
    *   **Updated**: After `calculate_risk_tier()` is called, or when loading existing tiering results with `get_tiering_result()`. Also updated after `save_tiering_result()`.
    *   **Read**: To display tiering details (score, breakdown, controls, justification).
*   `st.session_state['lifecycle_risks']`:
    *   **Initialized**: `[]` (empty list of `LifecycleRiskEntry` objects)
    *   **Updated**: After `add_lifecycle_risk()`, `update_lifecycle_risk()`, `delete_lifecycle_risk()` calls. Refreshed using `get_risks_for_system()`.
    *   **Read**: To display the list of risks and generate the risk matrix.
*   `st.session_state['editing_system']`:
    *   **Initialized**: `None`
    *   **Updated**: Set to a `SystemMetadata` object when "Edit" is clicked for a system, or `None` when "Add New System" is clicked or the form is submitted/cancelled.
    *   **Read**: To pre-fill the system creation/edit form.
*   `st.session_state['system_form_key']`:
    *   **Initialized**: `0`
    *   **Updated**: Incremented to force a re-render/reset of the system creation/edit form after submission or cancellation.
    *   **Read**: Used as the `key` for `st.form`.
*   `st.session_state['editing_risk']`:
    *   **Initialized**: `None`
    *   **Updated**: Set to a `LifecycleRiskEntry` object when "Edit" is clicked for a risk, or `None` when "Add New Risk" is clicked or the form is submitted/cancelled.
    *   **Read**: To pre-fill the risk creation/edit form.
*   `st.session_state['risk_form_key']`:
    *   **Initialized**: `0`
    *   **Updated**: Incremented to force a re-render/reset of the risk creation/edit form after submission or cancellation.
    *   **Read**: Used as the `key` for `st.form`.

### Helper Functions for Session State and Data Refresh

```python
# Function to refresh the list of systems from the database and update session state
def refresh_systems():
    st.session_state['systems'] = get_all_systems()
    # Ensure selected_system_id is still valid
    if st.session_state['selected_system_id'] not in [str(s.system_id) for s in st.session_state['systems']]:
        st.session_state['selected_system_id'] = None
    if not st.session_state['systems'] and st.session_state['selected_system_id'] is not None:
        st.session_state['selected_system_id'] = None # If last system deleted

# Function to refresh tiering data for the selected system
def refresh_tiering_result():
    if st.session_state['selected_system_id']:
        st.session_state['tiering_result'] = get_tiering_result(uuid.UUID(st.session_state['selected_system_id']))
    else:
        st.session_state['tiering_result'] = None

# Function to refresh lifecycle risks for the selected system
def refresh_lifecycle_risks():
    if st.session_state['selected_system_id']:
        st.session_state['lifecycle_risks'] = get_risks_for_system(uuid.UUID(st.session_state['selected_system_id']))
    else:
        st.session_state['lifecycle_risks'] = []

# Callback for sidebar page selection
def on_page_change():
    st.session_state['current_page'] = st.session_state['sidebar_selection']

# Initial database setup and data refresh on app startup
create_tables()
if 'systems' not in st.session_state or not st.session_state['systems']: # Check if systems are already loaded
    refresh_systems()
if 'tiering_result' not in st.session_state:
    st.session_state['tiering_result'] = None
if 'lifecycle_risks' not in st.session_state:
    st.session_state['lifecycle_risks'] = []
```

### Application Structure, Flow, Widgets, and Function Invocations

---

#### Main Application Setup

```python
st.set_page_config(layout="wide", page_title="AI System Governance Control Surface")

st.sidebar.title("Navigation")
page_options = [
    "Inventory Management",
    "Risk Tiering",
    "Lifecycle Risk Register",
    "Exports & Evidence"
]
st.sidebar.selectbox(
    "Select a section",
    page_options,
    key='sidebar_selection',
    on_change=on_page_change
)

st.title("Aperture Analytics Corp. AI System Governance Control Surface")

# Conditional rendering based on selected page
if st.session_state['current_page'] == "Inventory Management":
    # Content for Inventory Management page
    pass
elif st.session_state['current_page'] == "Risk Tiering":
    # Content for Risk Tiering page
    pass
elif st.session_state['current_page'] == "Lifecycle Risk Register":
    # Content for Lifecycle Risk Register page
    pass
elif st.session_state['current_page'] == "Exports & Evidence":
    # Content for Exports & Evidence page
    pass

# Select a system for detailed views (visible on all pages except Inventory management
# if a system is selected, or if navigating from inventory)
if st.session_state['current_page'] != "Inventory Management" or st.session_state['selected_system_id']:
    if st.session_state['systems']:
        system_names = {str(s.system_id): s.name for s in st.session_state['systems']}
        selected_system_name = system_names.get(st.session_state['selected_system_id'])

        st.sidebar.markdown("---")
        st.sidebar.subheader("Selected AI System")
        selected_id = st.sidebar.selectbox(
            "Choose an AI System for details:",
            options=[s.system_id for s in st.session_state['systems']],
            format_func=lambda x: system_names[str(x)],
            key='sidebar_system_selector',
            index=list(system_names.keys()).index(st.session_state['selected_system_id']) if st.session_state['selected_system_id'] else 0
        )
        if selected_id:
            st.session_state['selected_system_id'] = str(selected_id)
            selected_system_obj = next((s for s in st.session_state['systems'] if str(s.system_id) == st.session_state['selected_system_id']), None)
            if selected_system_obj:
                st.sidebar.markdown(f"**{selected_system_obj.name}**")
                st.sidebar.markdown(f"*{selected_system_obj.description[:50]}...*")
            else:
                st.session_state['selected_system_id'] = None # System might have been deleted

    else:
        st.sidebar.markdown("---")
        st.sidebar.warning("No systems available. Please add or load sample systems.")
        st.session_state['selected_system_id'] = None # Clear selection if no systems
```

---

#### 1. Inventory Management Page

```python
if st.session_state['current_page'] == "Inventory Management":
    st.header("AI System Inventory")
    st.markdown(f"As Alex, the AI Product Engineer, your task is to maintain an accurate and up-to-date inventory of all AI systems. This is the single source of truth for understanding deployed AI, ownership, purpose, and technical characteristics.")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Load Sample Systems", help="Load predefined sample AI systems into the inventory."):
            load_sample_systems_data()
            refresh_systems()
            st.success("Sample systems loaded successfully!")
            st.experimental_rerun()
    with col2:
        if st.button("Add New System", help="Click to open a form to register a new AI system."):
            st.session_state['editing_system'] = SystemMetadata(name="", description="", domain="", ai_type=AIType.ML, owner_role="", deployment_mode=DeploymentMode.INTERNAL_ONLY, decision_criticality=DecisionCriticality.LOW, automation_level=AutomationLevel.ADVISORY, data_sensitivity=DataSensitivity.PUBLIC)
            st.session_state['system_form_key'] += 1
            st.experimental_rerun()

    st.markdown("---")

    # System Creation/Edit Form
    if st.session_state['editing_system']:
        system_to_edit = st.session_state['editing_system']
        is_new_system = system_to_edit.system_id is None # Pydantic default_factory means it's never None if initialized as new. Check if it's a default empty one.
        if isinstance(system_to_edit.system_id, uuid.UUID) and str(system_to_edit.system_id) == "00000000-0000-0000-0000-000000000000": # A common way to check if it's a freshly instantiated UUID for a new entry
             is_new_system = True
        elif not isinstance(system_to_edit.system_id, uuid.UUID): # If it's a placeholder string or None
             is_new_system = True
        else: # Actual UUID means it's an existing system
            is_new_system = False

        form_title = "Add New AI System" if is_new_system else f"Edit System: {system_to_edit.name}"
        with st.form(key=f"system_form_{st.session_state['system_form_key']}", clear_on_submit=False):
            st.subheader(form_title)
            new_name = st.text_input("Name", value=system_to_edit.name)
            new_description = st.text_area("Description", value=system_to_edit.description)
            new_domain = st.text_input("Domain", value=system_to_edit.domain)
            new_ai_type = st.selectbox("AI Type", options=[e.value for e in AIType], index=[e.value for e in AIType].index(system_to_edit.ai_type.value))
            new_owner_role = st.text_input("Owner Role", value=system_to_edit.owner_role)
            new_deployment_mode = st.selectbox("Deployment Mode", options=[e.value for e in DeploymentMode], index=[e.value for e in DeploymentMode].index(system_to_edit.deployment_mode.value))
            new_decision_criticality = st.selectbox("Decision Criticality", options=[e.value for e in DecisionCriticality], index=[e.value for e in DecisionCriticality].index(system_to_edit.decision_criticality.value))
            new_automation_level = st.selectbox("Automation Level", options=[e.value for e in AutomationLevel], index=[e.value for e in AutomationLevel].index(system_to_edit.automation_level.value))
            new_data_sensitivity = st.selectbox("Data Sensitivity", options=[e.value for e in DataSensitivity], index=[e.value for e in DataSensitivity].index(system_to_edit.data_sensitivity.value))
            
            # External Dependencies handling
            current_deps_str = ", ".join(system_to_edit.external_dependencies)
            new_external_dependencies_str = st.text_input("External Dependencies (comma-separated)", value=current_deps_str)
            new_external_dependencies = [d.strip() for d in new_external_dependencies_str.split(',') if d.strip()]

            submit_button = st.form_submit_button(label="Save System" if is_new_system else "Update System")
            cancel_button = st.form_submit_button(label="Cancel")

            if submit_button:
                try:
                    system_data = {
                        "name": new_name,
                        "description": new_description,
                        "domain": new_domain,
                        "ai_type": AIType(new_ai_type),
                        "owner_role": new_owner_role,
                        "deployment_mode": DeploymentMode(new_deployment_mode),
                        "decision_criticality": DecisionCriticality(new_decision_criticality),
                        "automation_level": AutomationLevel(new_automation_level),
                        "data_sensitivity": DataSensitivity(new_data_sensitivity),
                        "external_dependencies": new_external_dependencies
                    }
                    if is_new_system:
                        new_system = SystemMetadata(**system_data)
                        add_system(new_system)
                        st.success(f"System '{new_system.name}' added successfully!")
                    else:
                        update_system(system_to_edit.system_id, system_data)
                        st.success(f"System '{new_name}' updated successfully!")
                    
                    st.session_state['editing_system'] = None
                    st.session_state['system_form_key'] += 1
                    refresh_systems()
                    st.experimental_rerun()
                except ValidationError as e:
                    st.error(f"Validation Error: {e.errors()}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            elif cancel_button:
                st.session_state['editing_system'] = None
                st.session_state['system_form_key'] += 1
                st.info("System form cancelled.")
                st.experimental_rerun()
        st.markdown("---")

    st.subheader("Current Inventory")
    if st.session_state['systems']:
        # Convert Pydantic objects to dicts for DataFrame display
        systems_data_for_df = []
        for s in st.session_state['systems']:
            s_dict = s.dict()
            s_dict['system_id'] = str(s_dict['system_id']) # Convert UUID to string for display
            s_dict['ai_type'] = s_dict['ai_type'].value
            s_dict['deployment_mode'] = s_dict['deployment_mode'].value
            s_dict['decision_criticality'] = s_dict['decision_criticality'].value
            s_dict['automation_level'] = s_dict['automation_level'].value
            s_dict['data_sensitivity'] = s_dict['data_sensitivity'].value
            s_dict['external_dependencies'] = ", ".join(s_dict['external_dependencies'])
            systems_data_for_df.append(s_dict)

        df_systems = pd.DataFrame(systems_data_for_df)
        df_systems = df_systems[['name', 'description', 'ai_type', 'owner_role', 'decision_criticality', 'updated_at', 'system_id']]
        st.dataframe(df_systems, use_container_width=True, hide_index=True)

        selected_row_indices = st.multiselect(
            "Select systems to Edit or Delete:",
            options=df_systems.index.tolist(),
            format_func=lambda x: df_systems.loc[x, 'name']
        )
        if selected_row_indices:
            selected_system_id_to_action = df_systems.loc[selected_row_indices[0], 'system_id'] # Only action on the first selected for simplicity

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button(f"Edit Selected System (ID: {selected_system_id_to_action[:8]}...)", key="edit_system_btn"):
                    system_to_edit = get_system(uuid.UUID(selected_system_id_to_action))
                    st.session_state['editing_system'] = system_to_edit
                    st.session_state['system_form_key'] += 1
                    st.experimental_rerun()
            with col_delete:
                if st.button(f"Delete Selected System (ID: {selected_system_id_to_action[:8]}...)", key="delete_system_btn"):
                    delete_system(uuid.UUID(selected_system_id_to_action))
                    st.success(f"System {selected_system_id_to_action[:8]}... deleted successfully.")
                    refresh_systems()
                    st.experimental_rerun()
    else:
        st.info("No AI systems registered yet. Use 'Load Sample Systems' or 'Add New System' to get started.")

    # Update selected_system_id based on a primary selection for other pages
    if st.session_state['systems'] and not st.session_state['selected_system_id']:
        st.session_state['selected_system_id'] = str(st.session_state['systems'][0].system_id)
        st.info(f"Automatically selected '{st.session_state['systems'][0].name}' for detailed views.")
        st.experimental_rerun()
```

---

#### 2. Risk Tiering Page

```python
if st.session_state['current_page'] == "Risk Tiering":
    st.header("Deterministic Risk Tiering")
    st.markdown(f"As Alex, determine the inherent risk tier for the selected AI system. Aperture Analytics Corp. uses a **deterministic tiering algorithm** to objectively classify AI systems into Tier 1 (High Risk), Tier 2 (Medium Risk), or Tier 3 (Low Risk). This tier dictates the level of oversight, controls, and review intensity.")

    if not st.session_state['selected_system_id']:
        st.warning("Please select a system from the sidebar to view/compute its risk tier.")
    else:
        current_system = next((s for s in st.session_state['systems'] if str(s.system_id) == st.session_state['selected_system_id']), None)
        if not current_system:
            st.error("Selected system not found.")
            st.session_state['selected_system_id'] = None
            st.experimental_rerun()
        
        st.subheader(f"System: {current_system.name}")
        st.markdown(f"The algorithm calculates a total score based on various dimensions of the AI system (e.g., decision criticality, data sensitivity, automation level) using predefined point mappings. This score is then compared against configurable thresholds to assign the final tier.")
        st.markdown(r"$$S = \sum_{{d \in D}} \text{{points}}(d)$$")
        st.markdown(r"where $S$ is the total score, $D$ is the set of relevant dimensions, and $\text{{points}}(d)$ is the score derived from the system's characteristic for dimension $d$.")
        st.markdown(r"") # Separate formula and explanation
        st.markdown(r"The tier is then assigned based on these thresholds:")
        st.markdown(r"*   $\text{{Tier 1 if }} S \ge T_{{1,min}}$")
        st.markdown(r"*   $\text{{Tier 2 if }} S \ge T_{{2,min}}$")
        st.markdown(r"*   $\text{{Tier 3 otherwise}}$")
        st.markdown(r"where $T_{{1,min}}$ and $T_{{2,min}}$ are the configurable minimum scores for Tier 1 and Tier 2, respectively, as defined in our `CONFIG`.")

        if st.button(f"Compute Risk Tier for {current_system.name}", help="Calculate the risk tier based on system metadata."):
            tiering_result = calculate_risk_tier(current_system)
            st.session_state['tiering_result'] = tiering_result
            st.success(f"Risk tier calculated for {current_system.name}.")
            refresh_tiering_result() # Fetch updated result from DB (includes potential defaults)

        st.markdown("---")

        if st.session_state['tiering_result']:
            tier_res = st.session_state['tiering_result']
            st.subheader(f"Risk Tiering Result (Score: {tier_res.total_score})")
            st.info(f"**Assigned Risk Tier**: {tier_res.risk_tier.value}")

            st.markdown("**Score Breakdown:**")
            breakdown_df = pd.DataFrame(tier_res.score_breakdown.items(), columns=["Dimension", "Points"])
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Required Controls & Justification")

            with st.form(key="tiering_justification_form"):
                current_justification = st.text_area("Tier Justification", value=tier_res.justification, height=100)
                st.markdown("Default required controls are determined by the assigned tier. You can override or annotate them here.")
                
                # Convert list to string for text_area, allow editing
                current_controls_str = "\n".join(tier_res.required_controls)
                edited_controls_str = st.text_area("Required Controls (one control per line)", value=current_controls_str, height=200)
                edited_controls_list = [c.strip() for c in edited_controls_str.split('\n') if c.strip()]

                save_tier_button = st.form_submit_button("Save Tiering Result (with edits)")
                if save_tier_button:
                    # Update the existing TieringResult object
                    updated_tier_res_data = tier_res.dict()
                    updated_tier_res_data['justification'] = current_justification
                    updated_tier_res_data['required_controls'] = edited_controls_list
                    updated_tier_res_data['computed_at'] = datetime.now().isoformat() # Update timestamp

                    try:
                        updated_tier_result_obj = TieringResult(**updated_tier_res_data)
                        save_tiering_result(updated_tier_result_obj)
                        st.session_state['tiering_result'] = updated_tier_result_obj # Update session state immediately
                        st.success("Tiering result and controls saved successfully!")
                    except ValidationError as e:
                        st.error(f"Validation error saving tiering result: {e.errors()}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
                    
                    refresh_tiering_result()
                    st.experimental_rerun() # Rerun to display updated data

        else:
            st.info("No risk tiering result available for this system. Click 'Compute Risk Tier' above.")

    # Load tiering result for the newly selected system if not already loaded
    if st.session_state['selected_system_id'] and (not st.session_state['tiering_result'] or str(st.session_state['tiering_result'].system_id) != st.session_state['selected_system_id']):
        refresh_tiering_result()
        if st.session_state['tiering_result']:
            st.info(f"Loaded existing tiering result for {current_system.name}.")
        st.experimental_rerun() # Refresh to display the loaded tiering
```

---

#### 3. Lifecycle Risk Register Page

```python
if st.session_state['current_page'] == "Lifecycle Risk Register":
    st.header("Lifecycle Risk Register")
    st.markdown(f"As Alex, identify and document specific risks across the entire lifecycle of the selected AI system. This register captures potential issues from inception to retirement, categorizing them by `lifecycle_phase` and `risk_vector`.")
    st.markdown(f"Each risk entry includes an `impact` and `likelihood` score (both 1-5), from which a `severity` score is deterministically calculated. The formula for severity is:")
    st.markdown(r"$$\text{{Severity}} = \text{{Impact}} \times \text{{Likelihood}}$$")
    st.markdown(r"where $\text{{Impact}}$ and $\text{{Likelihood}}$ are scores ranging from 1 to 5.")

    if not st.session_state['selected_system_id']:
        st.warning("Please select a system from the sidebar to manage its lifecycle risks.")
    else:
        current_system = next((s for s in st.session_state['systems'] if str(s.system_id) == st.session_state['selected_system_id']), None)
        if not current_system:
            st.error("Selected system not found.")
            st.session_state['selected_system_id'] = None
            st.experimental_rerun()

        st.subheader(f"Risks for System: {current_system.name}")
        st.markdown(f"**UI Guidance**: Aim to add at least 5 risks per system, spanning at least 3 lifecycle phases.")

        if st.button("Add New Risk", help="Open a form to add a new lifecycle risk entry."):
            st.session_state['editing_risk'] = LifecycleRiskEntry(
                system_id=uuid.UUID(st.session_state['selected_system_id']),
                lifecycle_phase=LifecyclePhase.INCEPTION,
                risk_vector=RiskVector.FUNCTIONAL,
                risk_statement="",
                impact=1,
                likelihood=1,
                mitigation="",
                owner_role=""
            )
            st.session_state['risk_form_key'] += 1
            st.experimental_rerun()

        st.markdown("---")

        # Risk Creation/Edit Form
        if st.session_state['editing_risk']:
            risk_to_edit = st.session_state['editing_risk']
            is_new_risk = (not isinstance(risk_to_edit.risk_id, uuid.UUID) or str(risk_to_edit.risk_id) == "00000000-0000-0000-0000-000000000000")

            form_title = "Add New Lifecycle Risk" if is_new_risk else f"Edit Risk: {risk_to_edit.risk_statement[:50]}..."
            with st.form(key=f"risk_form_{st.session_state['risk_form_key']}", clear_on_submit=False):
                st.subheader(form_title)
                new_lifecycle_phase = st.selectbox("Lifecycle Phase", options=[e.value for e in LifecyclePhase], index=[e.value for e in LifecyclePhase].index(risk_to_edit.lifecycle_phase.value))
                new_risk_vector = st.selectbox("Risk Vector", options=[e.value for e in RiskVector], index=[e.value for e in RiskVector].index(risk_to_edit.risk_vector.value))
                new_risk_statement = st.text_area("Risk Statement", value=risk_to_edit.risk_statement)
                new_impact = st.slider("Impact (1-5)", min_value=1, max_value=5, value=risk_to_edit.impact)
                new_likelihood = st.slider("Likelihood (1-5)", min_value=1, max_value=5, value=risk_to_edit.likelihood)
                st.info(f"Calculated Severity: {new_impact * new_likelihood}")
                new_mitigation = st.text_area("Mitigation/Control Statement", value=risk_to_edit.mitigation)
                new_owner_role = st.text_input("Owner Role", value=risk_to_edit.owner_role)
                
                current_evidence_str = ", ".join(risk_to_edit.evidence_links)
                new_evidence_links_str = st.text_input("Evidence Links (comma-separated URLs)", value=current_evidence_str)
                new_evidence_links = [link.strip() for link in new_evidence_links_str.split(',') if link.strip()]

                submit_button = st.form_submit_button(label="Save Risk" if is_new_risk else "Update Risk")
                cancel_button = st.form_submit_button(label="Cancel")

                if submit_button:
                    try:
                        risk_data = {
                            "system_id": uuid.UUID(st.session_state['selected_system_id']),
                            "lifecycle_phase": LifecyclePhase(new_lifecycle_phase),
                            "risk_vector": RiskVector(new_risk_vector),
                            "risk_statement": new_risk_statement,
                            "impact": new_impact,
                            "likelihood": new_likelihood,
                            "mitigation": new_mitigation,
                            "owner_role": new_owner_role,
                            "evidence_links": new_evidence_links
                        }
                        if is_new_risk:
                            new_risk = LifecycleRiskEntry(**risk_data)
                            add_lifecycle_risk(new_risk)
                            st.success("Risk added successfully!")
                        else:
                            update_lifecycle_risk(risk_to_edit.risk_id, risk_data)
                            st.success("Risk updated successfully!")
                        
                        st.session_state['editing_risk'] = None
                        st.session_state['risk_form_key'] += 1
                        refresh_lifecycle_risks()
                        st.experimental_rerun()
                    except ValidationError as e:
                        st.error(f"Validation Error: {e.errors()}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                elif cancel_button:
                    st.session_state['editing_risk'] = None
                    st.session_state['risk_form_key'] += 1
                    st.info("Risk form cancelled.")
                    st.experimental_rerun()
            st.markdown("---")

        # Display existing risks
        refresh_lifecycle_risks() # Ensure risks are up-to-date
        if st.session_state['lifecycle_risks']:
            st.subheader("Existing Risks")
            risks_data_for_df = []
            for r in st.session_state['lifecycle_risks']:
                r_dict = r.dict()
                r_dict['risk_id'] = str(r_dict['risk_id'])
                r_dict['lifecycle_phase'] = r_dict['lifecycle_phase'].value
                r_dict['risk_vector'] = r_dict['risk_vector'].value
                r_dict['evidence_links'] = ", ".join(r_dict['evidence_links'])
                risks_data_for_df.append(r_dict)
            
            df_risks = pd.DataFrame(risks_data_for_df)
            df_risks = df_risks[['risk_statement', 'lifecycle_phase', 'risk_vector', 'impact', 'likelihood', 'severity', 'owner_role', 'mitigation', 'created_at', 'risk_id']]
            st.dataframe(df_risks, use_container_width=True, hide_index=True)

            selected_row_indices = st.multiselect(
                "Select risks to Edit or Delete:",
                options=df_risks.index.tolist(),
                format_func=lambda x: df_risks.loc[x, 'risk_statement'][:50] + "..."
            )
            if selected_row_indices:
                selected_risk_id_to_action = df_risks.loc[selected_row_indices[0], 'risk_id'] # Only action on first selected

                col_edit_risk, col_delete_risk = st.columns(2)
                with col_edit_risk:
                    if st.button(f"Edit Selected Risk (ID: {selected_risk_id_to_action[:8]}...)", key="edit_risk_btn"):
                        risk_to_edit = get_lifecycle_risk(uuid.UUID(selected_risk_id_to_action))
                        st.session_state['editing_risk'] = risk_to_edit
                        st.session_state['risk_form_key'] += 1
                        st.experimental_rerun()
                with col_delete_risk:
                    if st.button(f"Delete Selected Risk (ID: {selected_risk_id_to_action[:8]}...)", key="delete_risk_btn"):
                        delete_lifecycle_risk(uuid.UUID(selected_risk_id_to_action))
                        st.success(f"Risk {selected_risk_id_to_action[:8]}... deleted successfully.")
                        refresh_lifecycle_risks()
                        st.experimental_rerun()
        else:
            st.info("No lifecycle risks registered for this system yet.")

        st.markdown("---")
        st.subheader("Lifecycle x Risk Vector Matrix")
        st.markdown(f"This matrix provides a powerful, at-a-glance summary, showing the distribution of risks across different `lifecycle_phases` (rows) and `risk_vectors` (columns). Each cell displays the count of risks for that specific phase-vector combination, and optionally the maximum severity.")
        
        risk_matrix_df = generate_risk_matrix(uuid.UUID(st.session_state['selected_system_id']))
        if not risk_matrix_df.empty:
            st.dataframe(risk_matrix_df, use_container_width=True)
        else:
            st.info("No risks to display in the matrix.")
    
    # Load risks for the newly selected system if not already loaded
    if st.session_state['selected_system_id'] and (not st.session_state['lifecycle_risks'] or str(st.session_state['lifecycle_risks'][0].system_id) != st.session_state['selected_system_id'] if st.session_state['lifecycle_risks'] else True):
        refresh_lifecycle_risks()
        if st.session_state['lifecycle_risks']:
            st.info(f"Loaded existing lifecycle risks for {current_system.name}.")
        st.experimental_rerun()
```

---

#### 4. Exports & Evidence Page

```python
if st.session_state['current_page'] == "Exports & Evidence":
    st.header("Generate Traceable Evidence Package")
    st.markdown(f"As Alex, prepare a formal **evidence package** for internal audits, compliance checks, and stakeholder reviews. This package serves as an immutable record of the AI system's governance artifacts, including data exports, a `config_snapshot.json` and, crucially, an `evidence_manifest.json` with cryptographic **SHA-256 hashes**.")
    st.markdown(f"The `inputs_hash` in the manifest must be SHA-256 over a deterministic JSON serialization of:")
    st.markdown(r"*   `case: \"case1\"`")
    st.markdown(r"*   `systems_count` (total number of systems in the inventory at the time of export)")
    st.markdown(r"*   `config_snapshot` (hash of the serialized CONFIG)")
    st.markdown(r"") # Separate formula and explanation
    st.markdown(r"The `outputs_hash` must be SHA-256 over the ordered list of artifact hashes (sorted by artifact name).")


    st.markdown("---")

    if not st.session_state['systems']:
        st.warning("No AI systems available to generate an evidence package. Please add or load sample systems first.")
    else:
        st.markdown("Click the button below to generate a complete, traceable evidence package.")
        st.markdown("This will create a ZIP file containing `model_inventory.csv`, `risk_tiering.json`, `lifecycle_risk_map.json`, `case1_executive_summary.md`, `config_snapshot.json`, and `evidence_manifest.json`.")

        team_user = st.text_input("Enter your Team/User Name for the manifest:", value="AI Product Engineer Alex")
        
        if st.button("Generate Evidence Package"):
            if not team_user:
                st.error("Please enter a Team/User Name to generate the evidence package.")
            else:
                with st.spinner("Generating evidence package... This may take a moment."):
                    try:
                        zip_file_path = generate_evidence_package(case_name="case1", team_or_user=team_user)
                        
                        st.success(f"Evidence package generated successfully! Find it at `{zip_file_path}`")
                        
                        # Provide download button
                        with open(zip_file_path, "rb") as f:
                            st.download_button(
                                label="Download ZIP Package",
                                data=f.read(),
                                file_name=os.path.basename(zip_file_path),
                                mime="application/zip"
                            )
                        st.info("The downloaded ZIP file contains all required artifacts with cryptographic hashes for integrity and traceability.")
                    except Exception as e:
                        st.error(f"Failed to generate evidence package: {e}")
```
