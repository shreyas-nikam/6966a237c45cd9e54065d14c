
import pytest
import os
import sqlite3
import uuid
from streamlit.testing.v1 import AppTest

# Define the database name used by the app and source.py
# This variable is used in the fixture to manage the test database file.
DB_NAME = "test_qulab.db"

@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Ensures a clean database state before and after each test.
    The `source.py` module, which the Streamlit app imports, uses this
    database file. Deleting it ensures each test starts with no previous data.
    """
    # Setup: Ensure a clean database before each test
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    yield # This is where the test function will run
    
    # Teardown: Clean up the database after each test
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    # Clean up any dummy evidence packages created during tests
    temp_dir = "temp_evidence_packages"
    if os.path.exists(temp_dir):
        for f_name in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f_name))
        # Remove the directory itself if it's empty
        if not os.listdir(temp_dir):
            os.rmdir(temp_dir)

def test_initial_load_and_navigation():
    """
    Tests the initial loading of the app and navigation between main pages.
    Verifies default page content and successful page transitions via sidebar.
    """
    at = AppTest.from_file("app.py").run()
    
    # Assert initial page header for "Inventory Management"
    assert at.header[0].value == "AI System Inventory"
    # Assert default navigation selectbox value
    assert at.selectbox[0].value == "Inventory Management"
    
    # Change navigation to "Risk Tiering" and assert header change
    at.selectbox[0].set_value("Risk Tiering").run()
    assert at.header[0].value == "Deterministic Risk Tiering"
    
    # Change navigation to "Lifecycle Risk Register" and assert header change
    at.selectbox[0].set_value("Lifecycle Risk Register").run()
    assert at.header[0].value == "Lifecycle Risk Register"

    # Change navigation to "Exports & Evidence" and assert header change
    at.selectbox[0].set_value("Exports & Evidence").run()
    assert at.header[0].value == "Generate Traceable Evidence Package"

def test_load_sample_systems():
    """
    Tests the functionality to load sample systems into the inventory.
    Verifies success message and that systems appear in the displayed dataframe.
    """
    at = AppTest.from_file("app.py").run()
    
    # Ensure on "Inventory Management" page
    at.selectbox[0].set_value("Inventory Management").run()
    
    # Click "Load Sample Systems" button (assuming it's the first button on this page)
    at.button[0].click().run()
    
    # Assert success message is displayed
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Assert that the dataframe contains data (indicating systems were loaded)
    assert len(at.dataframe[0].value) > 0
    # Check for specific sample system names
    assert "Fraud Detection AI" in at.dataframe[0].value['name'].values
    assert "Customer Churn Prediction" in at.dataframe[0].value['name'].values

def test_add_new_system():
    """
    Tests adding a new AI system via the "Add New System" form.
    Verifies form interaction, success message, and the new system's presence in the inventory.
    """
    at = AppTest.from_file("app.py").run()
    
    # Ensure on "Inventory Management" page and load samples first for context
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!" # Acknowledge success
    
    # Click "Add New System" (assuming it's the second button on the page after loading samples)
    at.button[1].click().run()
    
    # Fill in the form fields. Indices are relative to the current set of visible widgets.
    # The form key needs to be dynamically read from session_state for `at.form` access.
    
    at.text_input[0].set_value("Financial Model AI").run() # Name
    at.text_input[1].set_value("Finance").run() # Domain
    at.text_input[2].set_value("Quant Analyst").run() # Owner Role
    at.selectbox[1].set_value("Machine Learning").run() # AI Type (index 1 after sidebar nav)
    at.selectbox[2].set_value("Internal Only").run() # Deployment Mode
    at.text_area[0].set_value("AI model for pricing complex financial derivatives.").run() # Description
    at.selectbox[3].set_value("High").run() # Decision Criticality
    at.selectbox[4].set_value("Semi-Automated").run() # Automation Level
    at.selectbox[5].set_value("Confidential").run() # Data Sensitivity
    at.text_input[3].set_value("Market Data API, Risk Engine").run() # External Dependencies
    
    # Click "Save System" within the dynamically keyed form
    current_system_form_key = at.session_state['system_form_key']
    at.form[f"system_form_{current_system_form_key}"].button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "System added!"
    
    # Re-run to update the displayed dataframe with the new system
    at.run()
    
    # Assert the new system appears in the dataframe
    assert "Financial Model AI" in at.dataframe[0].value['name'].values

def test_edit_existing_system():
    """
    Tests editing an existing AI system's details.
    Verifies form interaction, success message, and updated system details in the inventory.
    """
    at = AppTest.from_file("app.py").run()
    
    # Load sample systems to have data to edit
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Get the ID of the first system from the dataframe to edit
    initial_df = at.dataframe[0].value
    system_to_edit_id = initial_df['system_id'].iloc[0] # Assuming first row is the target
    
    # Select the system in the 'Select System to Edit/Delete' selectbox (last selectbox on the page)
    at.selectbox[-1].set_value(system_to_edit_id).run()
    
    # Click "Edit Selected" (assuming it's the second-to-last button on the page)
    at.button[-2].click().run()
    
    # Modify fields within the edit form
    updated_description = "This is an updated description for the edited system."
    updated_owner_role = "New Lead Engineer"
    
    at.text_input[2].set_value(updated_owner_role).run() # Owner Role field in the form
    at.text_area[0].set_value(updated_description).run() # Description field in the form
    
    # Click "Save System" within the edit form
    current_system_form_key = at.session_state['system_form_key']
    at.form[f"system_form_{current_system_form_key}"].button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "System updated!"
    
    # Re-run to refresh the dataframe with updated data
    at.run()
    
    # Assert the updated description and owner role are reflected in the dataframe
    updated_df = at.dataframe[0].value
    edited_system_row = updated_df[updated_df['system_id'] == system_to_edit_id]
    assert edited_system_row['description'].iloc[0] == updated_description
    assert edited_system_row['owner_role'].iloc[0] == updated_owner_role

def test_delete_system():
    """
    Tests deleting an existing AI system from the inventory.
    Verifies success message and that the system is no longer present in the dataframe.
    """
    at = AppTest.from_file("app.py").run()
    
    # Load sample systems to have data to delete
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Get the ID of the system to delete (e.g., the first one)
    initial_df = at.dataframe[0].value
    system_to_delete_id = initial_df['system_id'].iloc[0]
    
    # Select the system in the 'Select System to Edit/Delete' selectbox
    at.selectbox[-1].set_value(system_to_delete_id).run()
    
    # Click "Delete Selected" (assuming it's the last button on the page)
    at.button[-1].click().run()
    
    # Assert success message
    assert at.success[0].value == "Deleted."
    
    # Re-run to refresh the dataframe
    at.run()
    
    # Assert the system is no longer in the dataframe
    updated_df = at.dataframe[0].value
    assert system_to_delete_id not in updated_df['system_id'].values

def test_risk_tiering_workflow():
    """
    Tests the deterministic risk tiering process, including computation and saving justifications/controls.
    """
    at = AppTest.from_file("app.py").run()
    
    # Load sample systems first to ensure a system is available for tiering
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Navigate to "Risk Tiering"
    at.selectbox[0].set_value("Risk Tiering").run()
    
    # The sidebar system selector should automatically pick the first available system
    # We can check for its presence or default selection if needed, but for now,
    # assume a system is selected as per app logic.
    
    # Click "Compute Risk Tier" (first button on the Risk Tiering page)
    at.button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "Calculated and saved."
    
    # Assert that the risk tier result is displayed (e.g., "Result: Tier X (Score: Y)")
    # The exact tier and score depend on the `calculate_risk_tier` implementation in source.py
    assert "Result:" in at.subheader[2].value
    assert "Score:" in at.subheader[2].value
    
    # Modify "Justification" and "Required Controls" within the tiering form
    updated_justification = "This risk tiering result has been reviewed and justified."
    updated_controls_str = "Control A: Implement monitoring\nControl B: Regular audits"
    
    at.text_area[0].set_value(updated_justification).run() # Justification textarea
    at.text_area[1].set_value(updated_controls_str).run() # Required Controls textarea
    
    # Click "Save Changes" button within the "tier_edit" form
    at.form["tier_edit"].button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "Saved."
    
    # Re-run the app state to reflect the saved changes
    at.run()
    
    # Assert that the text areas now display the updated values
    assert at.text_area[0].value == updated_justification
    assert at.text_area[1].value == updated_controls_str

def test_lifecycle_risk_register_add_edit_delete():
    """
    Tests the full lifecycle of a risk entry: adding, editing, and deleting.
    Verifies form interactions, success messages, and data updates in the risk register.
    """
    at = AppTest.from_file("app.py").run()
    
    # Load sample systems first to ensure a system is selected for risk association
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Navigate to "Lifecycle Risk Register"
    at.selectbox[0].set_value("Lifecycle Risk Register").run()
    
    # --- Add New Risk ---
    # Click "Add New Risk" (first button on the Lifecycle Risk Register page)
    at.button[0].click().run()
    
    # Fill in the new risk form
    at.selectbox[1].set_value("Development").run() # Lifecycle Phase (index 1 after sidebar)
    at.selectbox[2].set_value("Fairness").run() # Risk Vector
    at.slider[0].set_value(3).run() # Impact
    at.text_input[0].set_value("Data Scientist").run() # Owner
    at.slider[1].set_value(4).run() # Likelihood
    at.text_area[0].set_value("Bias detected in training data.").run() # Risk Statement
    at.text_area[1].set_value("Retrain model with debiased data.").run() # Mitigation
    at.text_input[1].set_value("data_audit.pdf, fairness_report.docx").run() # Evidence Links
    
    # Click "Save Risk" within the dynamically keyed risk form
    current_risk_form_key = at.session_state['risk_form_key']
    at.form[f"risk_form_{current_risk_form_key}"].button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "Risk saved."
    
    # Re-run to refresh the displayed risk dataframe
    at.run()
    
    # Assert the new risk is present in the dataframe
    assert "Bias detected in training data." in at.dataframe[0].value['risk_statement'].values
    
    # --- Edit Existing Risk ---
    # Get the risk_id of the newly added risk to select it for editing
    initial_risk_df = at.dataframe[0].value
    risk_to_edit_id = initial_risk_df[initial_risk_df['risk_statement'] == "Bias detected in training data."]['risk_id'].iloc[0]
    
    # Select the risk in the 'Select Risk to Edit/Delete' selectbox (last selectbox on page)
    at.selectbox[-1].set_value(risk_to_edit_id).run()
    
    # Click "Edit Risk" (second-to-last button on the page)
    at.button[-2].click().run()
    
    # Modify the risk statement and mitigation
    updated_risk_statement = "Mitigated: Residual bias still present."
    updated_mitigation = "Continue monitoring for bias and implement post-processing."
    
    at.text_area[0].set_value(updated_risk_statement).run() # Risk Statement
    at.text_area[1].set_value(updated_mitigation).run() # Mitigation
    
    # Click "Save Risk" within the edit form
    current_risk_form_key = at.session_state['risk_form_key']
    at.form[f"risk_form_{current_risk_form_key}"].button[0].click().run()
    
    # Assert success message
    assert at.success[0].value == "Risk saved."
    
    # Re-run to refresh the dataframe
    at.run()
    
    # Assert the updated risk statement is now in the dataframe
    assert updated_risk_statement in at.dataframe[0].value['risk_statement'].values
    assert "Bias detected in training data." not in at.dataframe[0].value['risk_statement'].values # Original should be gone
    
    # --- Delete Risk ---
    # Select the modified risk for deletion
    risk_to_delete_id = at.dataframe[0].value[at.dataframe[0].value['risk_statement'] == updated_risk_statement]['risk_id'].iloc[0]
    at.selectbox[-1].set_value(risk_to_delete_id).run()
    
    # Click "Delete Risk" (last button on the page)
    at.button[-1].click().run()
    
    # Assert success message
    assert at.success[0].value == "Deleted."
    
    # Re-run to refresh the dataframe
    at.run()
    
    # Assert the risk is no longer in the dataframe
    assert updated_risk_statement not in at.dataframe[0].value['risk_statement'].values
    # Check if there are remaining risks if applicable, or if the dataframe is empty.

def test_exports_evidence_generation():
    """
    Tests the functionality to generate an evidence package.
    Verifies user input, successful package generation message, and the presence of a download button.
    """
    at = AppTest.from_file("app.py").run()
    
    # Load sample systems first, as evidence package generation might rely on existing data
    at.selectbox[0].set_value("Inventory Management").run()
    at.button[0].click().run() # Click "Load Sample Systems"
    assert at.success[0].value == "Sample systems loaded successfully!"
    
    # Navigate to "Exports & Evidence"
    at.selectbox[0].set_value("Exports & Evidence").run()
    
    # Enter a user name for the package generation
    test_user_name = "QA Tester Team"
    at.text_input[0].set_value(test_user_name).run()
    
    # Click "Generate Evidence Package" (first button on the Exports page)
    at.button[0].click().run()
    
    # Assert success message, checking that it starts with the expected text
    assert at.success[0].value.startswith("Generated at")
    
    # Assert that a download button is present
    assert at.download_button[0].label == "Download ZIP"
    
    # The fixture will handle cleaning up the generated file and directory.
