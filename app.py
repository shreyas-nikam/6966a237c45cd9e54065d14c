
import streamlit as st
import pandas as pd
import uuid
import json
import os
from datetime import datetime
from source import * # Assuming source.py contains Pydantic models (SystemMetadata, LifecycleRiskEntry, TieringResult, etc.), enums (AIType, LifecyclePhase, etc.), and database/CRUD functions.

# Lifecycle Risk Management Helper Functions
def add_lifecycle_risk(risk_entry: LifecycleRiskEntry):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lifecycle_risks (risk_id, system_id, json, created_at) VALUES (?, ?, ?, ?)",
        (str(risk_entry.risk_id), str(risk_entry.system_id), risk_entry.model_dump_json(), risk_entry.created_at.isoformat())
    )
    conn.commit()
    conn.close()

def get_risks_for_system(system_id: uuid.UUID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM lifecycle_risks WHERE system_id = ?", (str(system_id),))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        # Assuming row can be a tuple or a dict depending on db_connection setup
        # If using row_factory = sqlite3.Row, row behaves like a dict. Otherwise, it's a tuple.
        json_str = row['json'] if isinstance(row, dict) or hasattr(row, 'keys') else row[0]
        results.append(LifecycleRiskEntry.model_validate_json(json_str))
    return results

def get_lifecycle_risk(risk_id: uuid.UUID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        json_str = row['json'] if isinstance(row, dict) or hasattr(row, 'keys') else row[0]
        return LifecycleRiskEntry.model_validate_json(json_str)
    return None

def update_lifecycle_risk(risk_id: uuid.UUID, updates: dict):
    current_risk = get_lifecycle_risk(risk_id)
    if not current_risk:
        st.error(f"Risk with ID {risk_id} not found.")
        return False
    
    # Use Pydantic v2's model_dump()
    updated_data = current_risk.model_dump()
    
    # Ensure all enum values are converted to their enum instances if they are coming from forms as strings
    if 'lifecycle_phase' in updates:
        updates['lifecycle_phase'] = LifecyclePhase(updates['lifecycle_phase'])
    if 'risk_vector' in updates:
        updates['risk_vector'] = RiskVector(updates['risk_vector'])

    updated_data.update(updates)
    
    # Recalculate severity if impact or likelihood are updated
    # The LifecycleRiskEntry model_post_init will handle this automatically upon re-instantiation
    # So we just need to ensure impact and likelihood are in updated_data if changed.
    
    # Update created_at (acting as a last modified timestamp for the record)
    updated_data['created_at'] = datetime.now() # Store as datetime object, will be isoformatted on DB write

    try:
        updated_risk = LifecycleRiskEntry(**updated_data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE lifecycle_risks SET json = ?, created_at = ? WHERE risk_id = ?",
            # Use Pydantic v2's model_dump_json() and isoformat for datetime
            (updated_risk.model_dump_json(), updated_risk.created_at.isoformat(), str(risk_id))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating risk: {e}")
        return False

def delete_lifecycle_risk(risk_id: uuid.UUID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
    conn.commit()
    conn.close()

# Session State Helpers
def refresh_systems():
    systems = get_all_systems()
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
    if st.session_state['selected_system_id']:
        st.session_state['tiering_result'] = get_tiering_result(uuid.UUID(st.session_state['selected_system_id']))
    else:
        st.session_state['tiering_result'] = None

def refresh_lifecycle_risks():
    if st.session_state['selected_system_id']:
        st.session_state['lifecycle_risks'] = get_risks_for_system(uuid.UUID(st.session_state['selected_system_id']))
    else:
        st.session_state['lifecycle_risks'] = []

def on_page_change():
    st.session_state['current_page'] = st.session_state['sidebar_selection']
    # Clear editing state when changing page
    st.session_state['editing_system'] = None
    st.session_state['editing_risk'] = None
    # Rerun to ensure page content updates
    st.rerun()

# App Setup
st.set_page_config(page_title="QuLab: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map")
st.divider()

create_tables()

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

st.sidebar.title("Navigation")
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
    st.sidebar.subheader("Selected AI System")
    
    system_names = {str(s.system_id): s.name for s in st.session_state['systems']}
    system_ids_list = list(system_names.keys())

    if system_ids_list: # Only show the selectbox if there are systems to choose from
        # Ensure selected_system_id is valid for the current list of systems.
        # refresh_systems already handles setting it to a default or None,
        # but this acts as an extra safety check in case the list changes dynamically.
        if st.session_state['selected_system_id'] not in system_ids_list:
            st.session_state['selected_system_id'] = system_ids_list[0] # Default to the first system
        
        # Ensure default_index is valid
        try:
            current_index = system_ids_list.index(st.session_state['selected_system_id'])
        except ValueError:
            current_index = 0 # Fallback if selected system somehow isn't in list

        selected_id_from_selectbox = st.sidebar.selectbox(
            "Choose an AI System for details:",
            options=system_ids_list,
            format_func=lambda x: system_names.get(x, x), # Use .get with default for robustness
            index=current_index,
            key='sidebar_system_selector'
        )
        
        # Update session state if the selection changed
        if selected_id_from_selectbox != st.session_state['selected_system_id']:
             st.session_state['selected_system_id'] = selected_id_from_selectbox
             refresh_tiering_result()
             refresh_lifecycle_risks()
             st.rerun()

        selected_system_obj = next((s for s in st.session_state['systems'] if str(s.system_id) == st.session_state['selected_system_id']), None)
        if selected_system_obj:
            st.sidebar.markdown(f"**{selected_system_obj.name}**")
            st.sidebar.markdown(f"*{selected_system_obj.description[:50]}...*")
    else:
        st.sidebar.warning("No systems available. Please add or load sample systems.")
        # Explicitly ensure selected_system_id is None if no systems are available to prevent errors on other pages.
        st.session_state['selected_system_id'] = None

# Page: Inventory Management
if st.session_state['current_page'] == "Inventory Management":
    st.header("AI System Inventory")
    st.markdown(f"As Alex, the AI Product Engineer, your task is to maintain an accurate and up-to-date inventory of all AI systems. This is the single source of truth for understanding deployed AI, ownership, purpose, and technical characteristics.")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Load Sample Systems", help="Load predefined sample AI systems into the inventory."):
            load_sample_systems_data()
            refresh_systems()
            refresh_tiering_result() # Refresh results for newly loaded systems
            refresh_lifecycle_risks() # Refresh risks for newly loaded systems
            st.success("Sample systems loaded successfully!")
            st.rerun()
    with col2:
        if st.button("Add New System", help="Click to open a form to register a new AI system."):
            st.session_state['editing_system'] = SystemMetadata(
                name="", description="", domain="", ai_type=AIType.ML, 
                owner_role="", deployment_mode=DeploymentMode.INTERNAL_ONLY, 
                decision_criticality=DecisionCriticality.LOW, 
                automation_level=AutomationLevel.ADVISORY, 
                data_sensitivity=DataSensitivity.PUBLIC
            )
            st.session_state['system_form_key'] += 1 # Increment key to force form redraw
            st.rerun()

    st.markdown("---")

    if st.session_state['editing_system']:
        sys_edit = st.session_state['editing_system']
        is_existing = any(str(s.system_id) == str(sys_edit.system_id) for s in st.session_state['systems']) if sys_edit.system_id else False
        
        form_title = f"Edit System: {sys_edit.name}" if is_existing else "Add New AI System"
        
        # Use a form container for submission logic
        with st.form(key=f"system_form_{st.session_state['system_form_key']}", clear_on_submit=False):
            st.subheader(form_title)
            c1, c2 = st.columns(2)
            with c1:
                f_name = st.text_input("Name", value=sys_edit.name)
                f_domain = st.text_input("Domain", value=sys_edit.domain)
                f_owner = st.text_input("Owner Role", value=sys_edit.owner_role)
                ai_opts = [e.value for e in AIType]
                f_ai_type = st.selectbox("AI Type", options=ai_opts, index=ai_opts.index(sys_edit.ai_type.value))
                dm_opts = [e.value for e in DeploymentMode]
                f_deploy = st.selectbox("Deployment Mode", options=dm_opts, index=dm_opts.index(sys_edit.deployment_mode.value))

            with c2:
                f_desc = st.text_area("Description", value=sys_edit.description)
                dc_opts = [e.value for e in DecisionCriticality]
                f_crit = st.selectbox("Decision Criticality", options=dc_opts, index=dc_opts.index(sys_edit.decision_criticality.value))
                al_opts = [e.value for e in AutomationLevel]
                f_auto = st.selectbox("Automation Level", options=al_opts, index=al_opts.index(sys_edit.automation_level.value))
                ds_opts = [e.value for e in DataSensitivity]
                f_sens = st.selectbox("Data Sensitivity", options=ds_opts, index=ds_opts.index(sys_edit.data_sensitivity.value))

            curr_deps = ", ".join(sys_edit.external_dependencies)
            f_deps_str = st.text_input("External Dependencies (comma-separated)", value=curr_deps)
            
            b1, b2 = st.columns([1,1])
            submitted = b1.form_submit_button("Save System")
            cancelled = b2.form_submit_button("Cancel")

            if submitted:
                try:
                    deps_list = [d.strip() for d in f_deps_str.split(',') if d.strip()]
                    sys_data = {
                        "name": f_name, "description": f_desc, "domain": f_domain,
                        "ai_type": AIType(f_ai_type), "owner_role": f_owner,
                        "deployment_mode": DeploymentMode(f_deploy),
                        "decision_criticality": DecisionCriticality(f_crit),
                        "automation_level": AutomationLevel(f_auto),
                        "data_sensitivity": DataSensitivity(f_sens),
                        "external_dependencies": deps_list
                    }
                    
                    if is_existing:
                        update_system(sys_edit.system_id, sys_data)
                        st.success("System updated!")
                    else:
                        new_sys = SystemMetadata(**sys_data)
                        add_system(new_sys)
                        st.success("System added!")
                    
                    st.session_state['editing_system'] = None
                    refresh_systems()
                    refresh_tiering_result() # Refresh for potentially new selected system
                    refresh_lifecycle_risks() # Refresh for potentially new selected system
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

            if cancelled:
                st.session_state['editing_system'] = None
                st.rerun()
        st.markdown("---")

    st.subheader("Current Inventory")
    if st.session_state['systems']:
        data_list = []
        for s in st.session_state['systems']:
            d = s.model_dump() # Pydantic v2 change: .dict() -> .model_dump()
            d['system_id'] = str(d['system_id'])
            d['ai_type'] = d['ai_type'].value
            d['deployment_mode'] = d['deployment_mode'].value
            d['decision_criticality'] = d['decision_criticality'].value
            d['automation_level'] = d['automation_level'].value
            d['data_sensitivity'] = d['data_sensitivity'].value
            d['external_dependencies'] = ", ".join(d['external_dependencies'])
            data_list.append(d)
        
        df = pd.DataFrame(data_list)
        st.dataframe(df[['name', 'domain', 'ai_type', 'owner_role', 'decision_criticality', 'updated_at']], use_container_width=True)
        
        sys_opts = df['system_id'].tolist()
        sys_names = df['name'].tolist()
        
        # Ensure selected system for edit/delete exists in the list
        if st.session_state['selected_system_id'] and st.session_state['selected_system_id'] in sys_opts:
            default_index = sys_opts.index(st.session_state['selected_system_id'])
        elif sys_opts: # If there are systems, but selected_system_id is invalid or None
            default_index = 0
            st.session_state['selected_system_id'] = sys_opts[0] # Set a valid default
        else: # No systems at all
            default_index = 0
            sel_sys = None

        if sys_opts: # Only show the selectbox if there are options
            sel_sys = st.selectbox(
                "Select System to Edit/Delete", 
                options=sys_opts, 
                format_func=lambda x: next((name for i, name in enumerate(sys_names) if sys_opts[i] == x), x),
                index=default_index
            )
            
            c_e, c_d = st.columns(2)
            if c_e.button("Edit Selected"):
                obj = get_system(uuid.UUID(sel_sys))
                st.session_state['editing_system'] = obj
                st.session_state['system_form_key'] += 1
                st.rerun()
            if c_d.button("Delete Selected"):
                delete_system(uuid.UUID(sel_sys))
                st.success("System deleted.")
                # After deletion, refresh all relevant session states
                refresh_systems()
                refresh_tiering_result()
                refresh_lifecycle_risks()
                st.rerun()
        else:
            st.info("No systems to select for editing or deletion.")
    else:
        st.info("No systems in the inventory. Add a new system or load sample systems to get started.")

# Page: Risk Tiering
elif st.session_state['current_page'] == "Risk Tiering":
    st.header("Deterministic Risk Tiering")
    st.markdown(f"As Alex, determine the inherent risk tier for the selected AI system. Aperture Analytics Corp. uses a **deterministic tiering algorithm** to objectively classify AI systems into Tier 1 (High Risk), Tier 2 (Medium Risk), or Tier 3 (Low Risk).")
    
    if not st.session_state['selected_system_id']:
        st.warning("Please select an AI system from the sidebar to view its risk tiering information.")
    else:
        curr_sys = next((s for s in st.session_state['systems'] if str(s.system_id) == st.session_state['selected_system_id']), None)
        if not curr_sys:
            st.error("Selected system not found in inventory. Please refresh or select another system.")
            st.session_state['selected_system_id'] = None # Clear invalid selection
            st.rerun()
        else:
            st.subheader(f"System: {curr_sys.name}")
            st.markdown(r"$$S = \sum_{d \in D} \text{points}(d)$$")
            st.markdown(f"The total score (S) is compared to predefined thresholds to assign the risk tier. A higher score indicates higher inherent risk.")
            
            if st.button("Compute Risk Tier"):
                res = calculate_risk_tier(curr_sys)
                save_tiering_result(res)
                st.session_state['tiering_result'] = res
                st.success(f"Risk tier calculated and saved for {curr_sys.name}!")
                st.rerun() # Rerun to update the displayed result immediately
            
            st.markdown("---")
            # Ensure the displayed tiering result corresponds to the currently selected system
            if st.session_state['tiering_result'] and str(st.session_state['tiering_result'].system_id) == str(curr_sys.system_id):
                res = st.session_state['tiering_result']
                st.subheader(f"Result: {res.risk_tier.value} (Total Score: {res.total_score})")
                
                bd_df = pd.DataFrame(res.score_breakdown.items(), columns=["Dimension", "Points"])
                st.dataframe(bd_df, use_container_width=True, hide_index=True)
                
                st.subheader("Controls & Justification")
                with st.form("tier_edit"):
                    just = st.text_area("Justification for this tier assignment:", value=res.justification)
                    ctrls_str = "\n".join(res.required_controls)
                    ctrls_edit = st.text_area("Required Controls (one per line):", value=ctrls_str)
                    
                    if st.form_submit_button("Save Changes to Tiering Result"):
                        res_data = res.model_dump() # Pydantic v2 change: .dict() -> .model_dump()
                        res_data['justification'] = just
                        res_data['required_controls'] = [c.strip() for c in ctrls_edit.split('\n') if c.strip()]
                        res_data['computed_at'] = datetime.now() # Store as datetime object
                        
                        new_res = TieringResult(**res_data)
                        save_tiering_result(new_res)
                        st.session_state['tiering_result'] = new_res
                        st.success("Tiering result updated successfully.")
                        st.rerun()
            else:
                st.info("No tiering result available for this system yet. Click 'Compute Risk Tier' to generate one.")

# Page: Lifecycle Risk Register
elif st.session_state['current_page'] == "Lifecycle Risk Register":
    st.header("Lifecycle Risk Register")
    st.markdown(f"As Alex, identify and document risks across the lifecycle of the selected AI system. Each risk is categorized by its lifecycle phase and risk vector, with a calculated severity based on impact and likelihood.")
    st.markdown(r"$$\text{Severity} = \text{Impact} \times \text{Likelihood}$$")
    
    if not st.session_state['selected_system_id']:
        st.warning("Please select an AI system from the sidebar to manage its lifecycle risks.")
    else:
        # Refresh risks if the selected system has changed or if risks are empty/invalid for the current system.
        # This check ensures that the lifecycle_risks in session_state always correspond to the selected system.
        if st.session_state['lifecycle_risks'] and \
           (not st.session_state['selected_system_id'] or str(st.session_state['lifecycle_risks'][0].system_id) != st.session_state['selected_system_id']):
            refresh_lifecycle_risks()
        elif not st.session_state['lifecycle_risks'] and st.session_state['selected_system_id'] and get_risks_for_system(uuid.UUID(st.session_state['selected_system_id'])):
            # Only refresh if there are risks in DB for current system but not in session state.
            refresh_lifecycle_risks()
        
        st.markdown("---")
        if st.button("Add New Risk"):
            st.session_state['editing_risk'] = LifecycleRiskEntry(
                system_id=uuid.UUID(st.session_state['selected_system_id']),
                lifecycle_phase=LifecyclePhase.INCEPTION,
                risk_vector=RiskVector.FUNCTIONAL,
                risk_statement="", impact=1, likelihood=1, mitigation="", owner_role="",
                # Severity is auto-calculated by LifecycleRiskEntry's model_post_init based on impact/likelihood
            )
            st.session_state['risk_form_key'] += 1 # Increment key to force form redraw
            st.rerun()
            
        if st.session_state['editing_risk']:
            r_edit = st.session_state['editing_risk']
            # Determine if this is an existing risk being edited or a new one being added
            is_new_risk = not any(str(r.risk_id) == str(r_edit.risk_id) for r in st.session_state['lifecycle_risks'])

            with st.form(key=f"risk_form_{st.session_state['risk_form_key']}"):
                st.subheader("Edit Risk" if not is_new_risk else "Add New Risk")
                c1, c2 = st.columns(2)
                
                lp_opts = [e.value for e in LifecyclePhase]
                rv_opts = [e.value for e in RiskVector]
                
                with c1:
                    n_lp = st.selectbox("Lifecycle Phase", options=lp_opts, index=lp_opts.index(r_edit.lifecycle_phase.value))
                    n_rv = st.selectbox("Risk Vector", options=rv_opts, index=rv_opts.index(r_edit.risk_vector.value))
                    n_imp = st.slider("Impact (1=Low, 5=High)", 1, 5, r_edit.impact)
                
                with c2:
                    n_own = st.text_input("Risk Owner Role", value=r_edit.owner_role)
                    n_like = st.slider("Likelihood (1=Rare, 5=Frequent)", 1, 5, r_edit.likelihood)
                    # Display current severity dynamically
                    st.info(f"Calculated Severity: {n_imp * n_like}")
                
                n_stmt = st.text_area("Risk Statement", value=r_edit.risk_statement, height=100)
                n_mit = st.text_area("Mitigation Strategy", value=r_edit.mitigation, height=100)
                n_ev = st.text_input("Evidence Links (comma-separated URLs)", value=", ".join(r_edit.evidence_links))
                
                b_save, b_cancel = st.columns(2)
                submitted = b_save.form_submit_button("Save Risk")
                cancelled = b_cancel.form_submit_button("Cancel")

                if submitted:
                    try:
                        r_data = {
                            "system_id": uuid.UUID(st.session_state['selected_system_id']),
                            "lifecycle_phase": n_lp, # Pass as string, pydantic will convert
                            "risk_vector": n_rv,     # Pass as string, pydantic will convert
                            "risk_statement": n_stmt,
                            "impact": n_imp,
                            "likelihood": n_like,
                            "mitigation": n_mit,
                            "owner_role": n_own,
                            "evidence_links": [l.strip() for l in n_ev.split(',') if l.strip()]
                        }
                        
                        if is_new_risk:
                            new_r = LifecycleRiskEntry(**r_data)
                            add_lifecycle_risk(new_r)
                            st.success(f"New risk '{new_r.risk_statement[:50]}...' added.")
                        else:
                            update_lifecycle_risk(r_edit.risk_id, r_data)
                            st.success(f"Risk '{r_edit.risk_statement[:50]}...' updated.")
                        
                        st.session_state['editing_risk'] = None
                        refresh_lifecycle_risks()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving risk: {e}")
                
                if cancelled:
                    st.session_state['editing_risk'] = None
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Existing Risks")
        if st.session_state['lifecycle_risks']:
            r_data = []
            for r in st.session_state['lifecycle_risks']:
                d = r.model_dump() # Pydantic v2 change: .dict() -> .model_dump()
                d['risk_id'] = str(d['risk_id'])
                d['lifecycle_phase'] = d['lifecycle_phase'].value
                d['risk_vector'] = d['risk_vector'].value
                r_data.append(d)
            
            df_r = pd.DataFrame(r_data)
            df_display = df_r[['risk_statement', 'lifecycle_phase', 'risk_vector', 'impact', 'likelihood', 'severity', 'owner_role', 'mitigation', 'created_at']]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Ensure the selected risk for edit/delete exists in the current list
            risk_id_options = df_r['risk_id'].tolist()
            if st.session_state['last_selected_risk_id'] not in risk_id_options:
                st.session_state['last_selected_risk_id'] = risk_id_options[0] if risk_id_options else None
            
            if st.session_state['last_selected_risk_id']:
                try:
                    default_index_risk = risk_id_options.index(st.session_state['last_selected_risk_id'])
                except ValueError:
                    default_index_risk = 0 # Fallback if selected risk ID is not in current options
                    if risk_id_options: st.session_state['last_selected_risk_id'] = risk_id_options[0]
                    else: st.session_state['last_selected_risk_id'] = None
            else:
                default_index_risk = 0
                if risk_id_options: st.session_state['last_selected_risk_id'] = risk_id_options[0]

            if risk_id_options: # Only show selectbox if there are risks
                sel_r_id = st.selectbox(
                    "Select a Risk to Edit or Delete:", 
                    options=risk_id_options, 
                    format_func=lambda x: df_r[df_r['risk_id'] == x].iloc[0]['risk_statement'][:70] + "...",
                    index=default_index_risk,
                    key='risk_selector'
                )
                st.session_state['last_selected_risk_id'] = sel_r_id # Store last selected for persistence

                ce, cd = st.columns(2)
                if ce.button("Edit Selected Risk"):
                    obj = get_lifecycle_risk(uuid.UUID(sel_r_id))
                    st.session_state['editing_risk'] = obj
                    st.session_state['risk_form_key'] += 1 # Increment key to force form redraw
                    st.rerun()
                if cd.button("Delete Selected Risk"):
                    delete_lifecycle_risk(uuid.UUID(sel_r_id))
                    refresh_lifecycle_risks()
                    st.success("Risk deleted successfully.")
                    st.rerun()
            else:
                st.info("No risks to select for editing or deletion.")

            st.markdown("---")
            st.subheader("Lifecycle Phase x Risk Vector Matrix")
            if st.session_state['selected_system_id']: # Ensure a system is still selected
                matrix = generate_risk_matrix(uuid.UUID(st.session_state['selected_system_id']))
                if not matrix.empty:
                    st.dataframe(matrix, use_container_width=True)
                else:
                    st.info("No risks documented to generate the matrix. Add some risks first!")
            else:
                st.info("No system selected to generate the risk matrix.")

        else:
            st.info("No lifecycle risks found for this AI system. Click 'Add New Risk' to document the first one.")

# Page: Exports
elif st.session_state['current_page'] == "Exports & Evidence":
    st.header("Generate Traceable Evidence Package")
    st.markdown(f"As Alex, prepare a formal evidence package with SHA-256 hashes for all AI systems and their associated risk data. This provides an immutable record for audit and compliance.")
    st.markdown(r"$$\text{EvidenceHash} = \text{SHA256}(\text{Artifacts})$$")
    
    if not st.session_state['systems']:
        st.warning("No AI systems are currently registered in the inventory. Please add systems before generating an evidence package.")
    else:
        u_name = st.text_input("Team/User Name (for evidence package record)", "AI Product Engineer Alex")
        if st.button("Generate Evidence Package"):
            if u_name:
                with st.spinner("Generating the traceable evidence package... This may take a moment."):
                    try:
                        path = generate_evidence_package("case1", u_name)
                        st.success(f"Evidence package successfully generated at: `{path}`")
                        # Provide a download button
                        with open(path, "rb") as f:
                            st.download_button(
                                label="Download Evidence Package (ZIP)",
                                data=f.read(),
                                file_name=os.path.basename(path),
                                mime="application/zip"
                            )
                        st.info("The package includes a manifest with SHA-256 hashes of all generated artifacts for traceability.")
                    except Exception as e:
                        st.error(f"An error occurred during package generation: {e}")
            else:
                st.error("Please provide your Team/User Name to generate the evidence package.")


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
