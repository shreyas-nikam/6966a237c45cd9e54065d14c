from enum import Enum
from typing import Any, List, Dict, Optional
import zipfile
import os
import json
import uuid
import datetime
import hashlib
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, model_validator
import threading

# --- Configuration for Tiering and Controls ---
# Centralized configuration as a Python dictionary for easy access and snapshotting
# In a real application, this might be loaded from a config file (e.g., YAML, TOML)
# For this lab, we define it directly for determinism and simplicity.

CONFIG = {
    "app_version": "1.0",
    "scoring_version": "1.0",
    "tier_thresholds": {
        "TIER_1_MIN": 22,
        "TIER_2_MIN": 15
    },
    "point_mappings": {
        "decision_criticality": {"LOW": 1, "MEDIUM": 3, "HIGH": 5},
        "data_sensitivity": {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 4, "REGULATED_PII": 5},
        "automation_level": {"ADVISORY": 1, "HUMAN_APPROVAL": 3, "FULLY_AUTOMATED": 5},
        "ai_type": {"ML": 3, "LLM": 4, "AGENT": 5},
        "deployment_mode": {"INTERNAL_ONLY": 1, "BATCH": 2, "HUMAN_IN_LOOP": 2, "REAL_TIME": 4}
    },
    "external_dependencies_scoring": {
        "0_deps": 0,
        "1_2_deps": 2,
        "3_plus_deps": 4,
        "opaque_vendor_bonus": 2,  # Added if any dependency matches opaque keywords
        "opaque_keywords": ["openai", "anthropic", "vendor", "3rd-party", "external"]
    },
    "default_required_controls": {
        "TIER_1": [
            "Independent validation required",
            "Full documentation pack (purpose, data, training, limitations)",
            "Pre-deploy stress/robustness testing",
            "Security testing suite (adversarial + abuse cases)",
            "Bias & interpretability assessment (if applicable)",
            "Monitoring dashboard + alert thresholds",
            "Formal change control with rollback plan",
            "Incident response runbook"
        ],
        "TIER_2": [
            "Peer validation (independent reviewer)",
            "Standard documentation pack",
            "Basic robustness tests",
            "Basic security tests",
            "Monitoring + periodic review",
            "Controlled releases"
        ],
        "TIER_3": [
            "Basic documentation",
            "Basic testing",
            "Periodic spot checks / lightweight monitoring"
        ]
    },
    "random_seed": None  # Explicitly None if not used, or set to a fixed int for determinism
}

# --- Pydantic Data Models (Schemas) ---


class AIType(str, Enum):
    ML = "ML"
    LLM = "LLM"
    AGENT = "AGENT"


class DeploymentMode(str, Enum):
    BATCH = "BATCH"
    REAL_TIME = "REAL_TIME"
    HUMAN_IN_LOOP = "HUMAN_IN_LOOP"
    INTERNAL_ONLY = "INTERNAL_ONLY"


class DecisionCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AutomationLevel(str, Enum):
    ADVISORY = "ADVISORY"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    FULLY_AUTOMATED = "FULLY_AUTOMATED"


class DataSensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    REGULATED_PII = "REGULATED_PII"


class RiskTier(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"


class LifecyclePhase(str, Enum):
    INCEPTION = "INCEPTION"
    DATA = "DATA"
    DESIGN_BUILD = "DESIGN_BUILD"
    VALIDATION = "VALIDATION"
    DEPLOYMENT = "DEPLOYMENT"
    OPERATIONS = "OPERATIONS"
    CHANGE_RETIRE = "CHANGE_RETIRE"


class RiskVector(str, Enum):
    FUNCTIONAL = "FUNCTIONAL"
    ROBUSTNESS = "ROBUSTNESS"
    SECURITY = "SECURITY"
    BIAS_FAIRNESS = "BIAS_FAIRNESS"
    INTERPRETABILITY = "INTERPRETABILITY"
    OPERATIONAL = "OPERATIONAL"
    VENDOR_OPACITY = "VENDOR_OPACITY"
    COMPLIANCE = "COMPLIANCE"


class SystemMetadata(BaseModel):
    system_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str
    domain: str
    ai_type: AIType
    owner_role: str
    deployment_mode: DeploymentMode
    decision_criticality: DecisionCriticality
    automation_level: AutomationLevel
    data_sensitivity: DataSensitivity
    external_dependencies: List[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now(
        datetime.timezone.utc).isoformat())


class TieringResult(BaseModel):
    system_id: uuid.UUID
    risk_tier: RiskTier
    total_score: int
    score_breakdown: Dict[str, int]
    justification: str = ""
    required_controls: List[str] = Field(default_factory=list)
    computed_at: str = Field(default_factory=lambda: datetime.datetime.now(
        datetime.timezone.utc).isoformat())
    scoring_version: str = CONFIG["scoring_version"]


class LifecycleRiskEntry(BaseModel):
    risk_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    system_id: uuid.UUID
    lifecycle_phase: LifecyclePhase
    risk_vector: RiskVector
    risk_statement: str
    impact: int = Field(..., ge=1, le=5)
    likelihood: int = Field(..., ge=1, le=5)
    severity: int = 0  # Will be calculated: impact * likelihood
    mitigation: str = ""
    owner_role: str
    evidence_links: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(
        datetime.timezone.utc).isoformat())

    @model_validator(mode='after')
    def calculate_severity(self) -> 'LifecycleRiskEntry':
        """Calculate severity as impact * likelihood after validation"""
        self.severity = self.impact * self.likelihood
        return self


# --- In-Memory Storage with Thread Safety ---
# Using module-level dictionaries with locks for thread-safe access in multi-user Streamlit apps
SYSTEMS_STORE: Dict[uuid.UUID, SystemMetadata] = {}
TIERING_STORE: Dict[uuid.UUID, TieringResult] = {}
LIFECYCLE_RISKS_STORE: Dict[uuid.UUID, LifecycleRiskEntry] = {}

# Thread locks for each store to ensure thread-safe operations
_systems_lock = threading.RLock()
_tiering_lock = threading.RLock()
_risks_lock = threading.RLock()


def create_tables():
    """Initialize in-memory storage (no-op, kept for API compatibility)."""
    pass


print("Environment setup complete: Libraries installed, Pydantic schemas defined, and thread-safe in-memory storage initialized.")
# --- Inventory CRUD Operations ---


def load_sample_systems_data(filepath: str = "data/sample_case1_systems.json", stores=None):
    """
    Loads sample system data from a JSON file and inserts it into the inventory.
    """
    sample_data = [
        {
            "system_id": str(uuid.uuid4()),
            "name": "Fraud Detection ML Model",
            "description": "Detects fraudulent transactions in real-time.",
            "domain": "Finance",
            "ai_type": "ML",
            "owner_role": "Risk Management Team",
            "deployment_mode": "REAL_TIME",
            "decision_criticality": "HIGH",
            "automation_level": "FULLY_AUTOMATED",
            "data_sensitivity": "REGULATED_PII",
            "external_dependencies": ["AWS SageMaker", "Stripe API"]
        },
        {
            "system_id": str(uuid.uuid4()),
            "description": "Generates marketing content based on prompts.",
            "domain": "Marketing",
            "ai_type": "LLM",
            "owner_role": "Marketing Team",
            "deployment_mode": "HUMAN_IN_LOOP",
            "decision_criticality": "MEDIUM",
            "automation_level": "HUMAN_APPROVAL",
            "data_sensitivity": "INTERNAL",
            # Example of opaque vendor
            "external_dependencies": ["OpenAI API (vendor)"]
        },
        {
            "system_id": str(uuid.uuid4()),
            "name": "HR Chatbot Agent",
            "description": "Answers common HR questions for employees.",
            "domain": "Human Resources",
            "ai_type": "AGENT",
            "owner_role": "HR Operations",
            "deployment_mode": "REAL_TIME",
            "decision_criticality": "LOW",
            "automation_level": "ADVISORY",
            "data_sensitivity": "CONFIDENTIAL",
            "external_dependencies": ["Zendesk API"]
        }
    ]
    # For a real lab, you'd load from `filepath`. For this spec, we define inline.
    # with open(filepath, 'r') as f:
    #    sample_data = json.load(f)

    print(f"--- Loading {len(sample_data)} sample systems ---")
    for item in sample_data:
        try:
            # Ensure system_id is a UUID object before passing to Pydantic
            item['system_id'] = uuid.UUID(item['system_id'])
            system = SystemMetadata(**item)
            add_system(system, stores)
            print(f"Loaded: {system.name}")
        except ValidationError as e:
            print(
                f"Validation error loading sample system {item.get('name', 'Unknown')}: {e}")
    print("-------------------------------------------\n")


def add_system(system_metadata: SystemMetadata, stores=None):
    """Adds a new AI system to the inventory (thread-safe)."""
    if stores is None:
        stores = {'systems': SYSTEMS_STORE}
    with _systems_lock:
        stores['systems'][system_metadata.system_id] = system_metadata


def get_system(system_id: uuid.UUID, stores=None) -> Optional[SystemMetadata]:
    """Retrieves an AI system by its ID (thread-safe)."""
    if stores is None:
        stores = {'systems': SYSTEMS_STORE}
    with _systems_lock:
        return stores['systems'].get(system_id)


def get_all_systems(stores=None) -> List[SystemMetadata]:
    """Retrieves all AI systems in the inventory (thread-safe)."""
    if stores is None:
        stores = {'systems': SYSTEMS_STORE}
    with _systems_lock:
        return list(stores['systems'].values())


def update_system(system_id: uuid.UUID, updates: Dict[str, Any], stores=None):
    """Updates an existing AI system's metadata (thread-safe)."""
    if stores is None:
        stores = {'systems': SYSTEMS_STORE}
    with _systems_lock:
        current_system = stores['systems'].get(system_id)
        if not current_system:
            print(f"Error: System with ID {system_id} not found for update.")
            return False

        updated_data = current_system.model_dump()
        updated_data.update(updates)
        updated_data['updated_at'] = datetime.datetime.now(
            datetime.timezone.utc).isoformat()

        try:
            updated_system = SystemMetadata(**updated_data)
            stores['systems'][system_id] = updated_system
            return True
        except ValidationError as e:
            print(f"Validation error updating system {system_id}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during update: {e}")
            return False


def delete_system(system_id: uuid.UUID, stores=None):
    """Deletes an AI system from the inventory and all related data (thread-safe)."""
    if stores is None:
        stores = {'systems': SYSTEMS_STORE,
                  'tiering': TIERING_STORE, 'risks': LIFECYCLE_RISKS_STORE}
    try:
        # Use all locks to ensure atomicity of the multi-store operation
        with _systems_lock, _tiering_lock, _risks_lock:
            # Delete related lifecycle risks
            risks_to_delete = [risk_id for risk_id, risk in stores['risks'].items()
                               if risk.system_id == system_id]
            for risk_id in risks_to_delete:
                del stores['risks'][risk_id]

            # Delete tiering result
            if system_id in stores['tiering']:
                del stores['tiering'][system_id]

            # Delete the system itself
            if system_id in stores['systems']:
                del stores['systems'][system_id]
                return True
            else:
                raise Exception(f"System {system_id} not found")
    except Exception as e:
        raise Exception(f"Failed to delete system: {e}")

# --- Execution ---


# 1. Load sample systems
# Simulating the data/sample_case1_systems.json content directly as a list of dicts.
# load_sample_systems_data()

# 2. Register "ApertureMind Assist"
aperture_mind_assist_id = uuid.uuid4()
aperture_mind_assist = SystemMetadata(
    system_id=aperture_mind_assist_id,
    name="ApertureMind Assist (LLM Agent)",
    description="LLM-powered agent for internal customer service and support.",
    domain="Customer Service",
    ai_type=AIType.LLM,
    owner_role="Customer Experience Team",
    deployment_mode=DeploymentMode.REAL_TIME,
    decision_criticality=DecisionCriticality.MEDIUM,
    automation_level=AutomationLevel.HUMAN_APPROVAL,
    data_sensitivity=DataSensitivity.CONFIDENTIAL,
    external_dependencies=[
        "Anthropic Claude API (vendor)", "Internal CRM API", "Knowledge Base API"]
)
# add_system(aperture_mind_assist)

# # 3. Retrieve and display all systems
# print("--- Current AI System Inventory ---")
# all_systems = get_all_systems()
# for system in all_systems:
#     print(f"ID: {system.system_id}, Name: {system.name}, Type: {system.ai_type}, Criticality: {system.decision_criticality}")
# print("-----------------------------------")

# # 4. Example: Update a system (e.g., description for ApertureMind Assist)
# update_system(aperture_mind_assist_id, {
#               "description": "Enhanced LLM agent for internal customer support, handling a wider range of queries."})
# --- Risk Tiering Functions ---


def calculate_risk_tier(system_metadata: SystemMetadata) -> TieringResult:
    """
    Calculates the risk tier for an AI system based on its metadata.
    Uses the deterministic point mapping and thresholds defined in CONFIG.
    """
    total_score = 0
    score_breakdown = {}

    # Map dimensions to points
    for dim, mappings in CONFIG["point_mappings"].items():
        attr_value = getattr(system_metadata, dim).value if isinstance(
            getattr(system_metadata, dim), Enum) else getattr(system_metadata, dim)
        # Default to 0 if value not found, should not happen with Pydantic Enums
        score = mappings.get(attr_value, 0)
        total_score += score
        score_breakdown[dim] = score

    # External Dependencies Scoring
    dep_count = len(system_metadata.external_dependencies)
    dep_score = 0
    if dep_count == 0:
        dep_score = CONFIG["external_dependencies_scoring"]["0_deps"]
    elif 1 <= dep_count <= 2:
        dep_score = CONFIG["external_dependencies_scoring"]["1_2_deps"]
    else:  # dep_count >= 3
        dep_score = CONFIG["external_dependencies_scoring"]["3_plus_deps"]

    # Check for opaque vendors
    for dep in system_metadata.external_dependencies:
        if any(keyword in dep.lower() for keyword in CONFIG["external_dependencies_scoring"]["opaque_keywords"]):
            dep_score += CONFIG["external_dependencies_scoring"]["opaque_vendor_bonus"]
            break  # Only add bonus once

    total_score += dep_score
    score_breakdown["external_dependencies"] = dep_score

    # Determine Risk Tier
    tier_1_min = CONFIG["tier_thresholds"]["TIER_1_MIN"]
    tier_2_min = CONFIG["tier_thresholds"]["TIER_2_MIN"]

    if total_score >= tier_1_min:
        risk_tier = RiskTier.TIER_1
    elif total_score >= tier_2_min:
        risk_tier = RiskTier.TIER_2
    else:
        risk_tier = RiskTier.TIER_3

    # Get default required controls
    required_controls = CONFIG["default_required_controls"][risk_tier.value]

    justification = f"Automated tiering based on scoring version {CONFIG['scoring_version']}."

    return TieringResult(
        system_id=system_metadata.system_id,
        risk_tier=risk_tier,
        total_score=total_score,
        score_breakdown=score_breakdown,
        justification=justification,
        required_controls=required_controls
    )


def save_tiering_result(tiering_result: TieringResult, stores=None):
    """Saves a tiering result for an AI system, updating if already exists (thread-safe)."""
    if stores is None:
        stores = {'tiering': TIERING_STORE}
    with _tiering_lock:
        stores['tiering'][tiering_result.system_id] = tiering_result


def get_tiering_result(system_id: uuid.UUID, stores=None) -> Optional[TieringResult]:
    """Retrieves a tiering result by system ID (thread-safe)."""
    if stores is None:
        stores = {'tiering': TIERING_STORE}
    with _tiering_lock:
        return stores['tiering'].get(system_id)

# --- Execution ---


# 1. Retrieve ApertureMind Assist system metadata
# aperture_mind_system = get_system(aperture_mind_assist_id)
# if aperture_mind_system:
#     # 2. Calculate its risk tier
#     tiering_result = calculate_risk_tier(aperture_mind_system)

#     # 3. Display the results
#     print(f"--- Risk Tiering for '{aperture_mind_system.name}' ---")
#     print(f"Total Score: {tiering_result.total_score}")
#     print(f"Assigned Risk Tier: {tiering_result.risk_tier.value}")
#     print("Score Breakdown:")
#     for dim, score in tiering_result.score_breakdown.items():
#         print(f"  - {dim.replace('_', ' ').title()}: {score} points")
#     print(f"\nJustification: {tiering_result.justification}")
#     print("Default Required Controls:")
#     for control in tiering_result.required_controls:
#         print(f"  - {control}")

#     # 4. Save the tiering result (which includes default controls and justification)
#     save_tiering_result(tiering_result)
#     print("\nRisk tiering result saved to in-memory storage.")

#     # 5. Example: Alex might want to customize controls or justification
#     # For instance, add a specific custom control for LLMs.
#     custom_controls = tiering_result.required_controls + \
#         ["Specific LLM prompt injection testing protocol"]
#     custom_justification = tiering_result.justification + \
#         " Added specific LLM controls."

#     updated_tiering_result = tiering_result.copy(update={
#         "required_controls": custom_controls,
#         "justification": custom_justification,
#         # Update timestamp
#         "computed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
#     })
#     save_tiering_result(updated_tiering_result)
#     print("\nRisk tiering result updated with custom controls and justification.")

#     # Verify update
#     verified_tiering = get_tiering_result(aperture_mind_system.system_id)
#     print(f"\nVerified Controls for '{aperture_mind_system.name}':")
#     for control in verified_tiering.required_controls:
#         print(f"  - {control}")
# else:
#     print(
#         f"Error: ApertureMind Assist (ID: {aperture_mind_assist_id}) not found.")
# --- Lifecycle Risk Register Operations ---


def get_risks_for_system(system_id: uuid.UUID, stores=None) -> List[LifecycleRiskEntry]:
    """Retrieves all lifecycle risks for a specific AI system (thread-safe)."""
    if stores is None:
        stores = {'risks': LIFECYCLE_RISKS_STORE}
    with _risks_lock:
        return [risk for risk in stores['risks'].values() if risk.system_id == system_id]


def update_lifecycle_risk(risk_id: uuid.UUID, updates: Dict[str, Any], stores=None):
    """Updates an existing lifecycle risk entry (thread-safe)."""
    if stores is None:
        stores = {'risks': LIFECYCLE_RISKS_STORE}
    with _risks_lock:
        current_risk = stores['risks'].get(risk_id)

        if not current_risk:
            print(f"Error: Risk with ID {risk_id} not found for update.")
            return False

        updated_data = current_risk.model_dump()
        updated_data.update(updates)

        # Recalculate severity if impact or likelihood changes
        if 'impact' in updates or 'likelihood' in updates:
            updated_data['impact'] = updates.get('impact', current_risk.impact)
            updated_data['likelihood'] = updates.get(
                'likelihood', current_risk.likelihood)
            updated_data['severity'] = updated_data['impact'] * \
                updated_data['likelihood']
        try:
            updated_risk = LifecycleRiskEntry(**updated_data)
            stores['risks'][risk_id] = updated_risk
            return True
        except ValidationError as e:
            print(f"Validation error updating risk {risk_id}: {e}")
            return False


def delete_lifecycle_risk(risk_id: uuid.UUID, stores=None):
    """Deletes a lifecycle risk entry (thread-safe)."""
    if stores is None:
        stores = {'risks': LIFECYCLE_RISKS_STORE}
    with _risks_lock:
        if risk_id not in stores['risks']:
            print(f"Error: Risk with ID {risk_id} not found for deletion.")
            return False

        del stores['risks'][risk_id]
        return True


def generate_risk_matrix(system_id: uuid.UUID, stores=None) -> pd.DataFrame:
    """
    Generates a lifecycle x risk vector matrix for a given system,
    showing count of risks and max severity in each cell.
    """
    risks = get_risks_for_system(system_id, stores)
    if not risks:
        print(f"No risks found for system ID: {system_id}.")
        # Empty DF
        return pd.DataFrame(columns=[rv.value for rv in RiskVector])

    # Prepare data for DataFrame
    data = []
    for r in risks:
        data.append({
            "lifecycle_phase": r.lifecycle_phase.value,
            "risk_vector": r.risk_vector.value,
            "severity": r.severity
        })

    df = pd.DataFrame(data)

    # Create a multi-index for the columns to show both count and max severity
    matrix_data = {}
    for phase in LifecyclePhase:
        matrix_data[phase.value] = {}
        for vector in RiskVector:
            # Filter risks for current phase and vector
            cell_risks = df[(df['lifecycle_phase'] == phase.value)
                            & (df['risk_vector'] == vector.value)]

            count = len(cell_risks)
            max_severity = cell_risks['severity'].max() if count > 0 else 0

            # Store as a tuple (count, max_severity)
            matrix_data[phase.value][
                vector.value] = f"Count: {count}, Max Severity: {int(max_severity)}"

    # Convert to DataFrame for better display
    matrix_df = pd.DataFrame(matrix_data).T  # Transpose to get phases as rows
    matrix_df.index.name = "Lifecycle Phase"
    matrix_df.columns.name = "Risk Vector"

    # Ensure all lifecycle phases and risk vectors are present, even if empty
    full_phases = [phase.value for phase in LifecyclePhase]
    full_vectors = [vector.value for vector in RiskVector]

    # Reindex to ensure all phases and vectors are present
    matrix_df = matrix_df.reindex(
        index=full_phases, columns=full_vectors, fill_value="Count: 0, Max Severity: 0")

    return matrix_df

# --- Execution ---

# 2. Display the matrix
# Using display for better rendering in Jupyter, but print will also work.
# display(risk_matrix_df)

# --- Helper Functions for Hashing and Serialization ---


def compute_sha256(data: bytes) -> str:
    """Computes the SHA-256 hash of provided bytes data."""
    return hashlib.sha256(data).hexdigest()


def to_deterministic_json(obj: Any) -> str:
    """Serializes an object to a deterministic JSON string.
    Includes a custom default handler for UUID and Enum objects.
    """
    def default_json_serializer(o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Enum):
            return o.value
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable")

    return json.dumps(
        obj,
        sort_keys=True,
        indent=None,
        ensure_ascii=False,
        separators=(',', ':'),
        default=default_json_serializer
    )


# --- Export and Evidence Package Generation ---

def generate_evidence_package(run_id: str, team_or_user: str = "AI Product Engineer (Alex)", output_dir_base: str = "reports/case1", stores=None):
    """
    Generates all required artifacts, evidence manifest, and a ZIP package.
    """
    output_run_dir = os.path.join(output_dir_base, run_id)
    os.makedirs(output_run_dir, exist_ok=True)

    artifacts = []
    artifact_hashes = {}

    # 1. model_inventory.csv
    # Note: get_all_systems() is assumed to be defined globally or imported
    all_systems_metadata = get_all_systems(stores)
    systems_df = pd.DataFrame([s.model_dump()
                              # Use model_dump()
                               for s in all_systems_metadata])

    # Ensure external_dependencies are pipe-separated string
    systems_df['external_dependencies'] = systems_df['external_dependencies'].apply(
        lambda x: '|'.join(x))

    # Select and order columns as per artifact definition
    inventory_columns = [
        'system_id', 'name', 'domain', 'ai_type', 'owner_role',
        'decision_criticality', 'automation_level', 'data_sensitivity',
        'deployment_mode', 'external_dependencies', 'updated_at'
    ]

    # Filter columns that actually exist in the DataFrame
    existing_inventory_columns = [
        col for col in inventory_columns if col in systems_df.columns]
    systems_df = systems_df[existing_inventory_columns]

    inventory_path = os.path.join(output_run_dir, "model_inventory.csv")
    systems_df.to_csv(inventory_path, index=False)

    with open(inventory_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "model_inventory.csv",
                     "path": inventory_path, "sha256": hash_val})
    artifact_hashes["model_inventory.csv"] = hash_val
    print(f"Generated: {inventory_path}")

    # 2. risk_tiering.json
    # Note: get_tiering_result and CONFIG are assumed to be defined globally
    all_tiering_results = [
        get_tiering_result(s.system_id, stores)
        for s in all_systems_metadata
        if get_tiering_result(s.system_id, stores)
    ]

    tiering_data_export = {
        "scoring_version": CONFIG["scoring_version"],
        # Use model_dump()
        "systems": [t.model_dump() for t in all_tiering_results]
    }

    tiering_path = os.path.join(output_run_dir, "risk_tiering.json")
    with open(tiering_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(tiering_data_export))

    with open(tiering_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "risk_tiering.json",
                     "path": tiering_path, "sha256": hash_val})
    artifact_hashes["risk_tiering.json"] = hash_val
    print(f"Generated: {tiering_path}")

    # 3. lifecycle_risk_map.json
    lifecycle_risk_map_data = {"systems": []}
    for system in all_systems_metadata:
        # Note: get_risks_for_system is assumed to be defined globally
        risks_for_system = get_risks_for_system(system.system_id, stores)
        if risks_for_system:
            lifecycle_risk_map_data["systems"].append({
                "system_id": str(system.system_id),
                # Use model_dump()
                "risks": [r.model_dump() for r in risks_for_system]
            })

    risk_map_path = os.path.join(output_run_dir, "lifecycle_risk_map.json")
    with open(risk_map_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(lifecycle_risk_map_data))

    with open(risk_map_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "lifecycle_risk_map.json",
                     "path": risk_map_path, "sha256": hash_val})
    artifact_hashes["lifecycle_risk_map.json"] = hash_val
    print(f"Generated: {risk_map_path}")

    # 4. case1_executive_summary.md
    summary_content = f"# Executive Summary for Case 1 (Run ID: {run_id})\n\n"
    summary_content += f"**Generated At:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
    summary_content += f"**App Version:** {CONFIG['app_version']}\n"
    summary_content += f"**Prepared By:** {team_or_user}\n\n"

    summary_content += "---\n\n"
    summary_content += "## Executive Overview\n\n"
    summary_content += "This report provides a comprehensive assessment of our organization's AI system portfolio, "
    summary_content += "including risk tiering analysis and lifecycle risk evaluation. The assessment framework applies "
    summary_content += "a deterministic, rules-based methodology to ensure consistent and auditable risk classification "
    summary_content += "across all AI systems.\n\n"

    summary_content += "The inventory covers systems spanning multiple domains and use cases, from customer-facing "
    summary_content += "applications to internal automation tools. Each system has been evaluated against standardized "
    summary_content += "criteria including decision criticality, data sensitivity, automation level, and external dependencies.\n\n"

    summary_content += "## AI System Inventory Summary\n\n"
    summary_content += f"**Total AI Systems Registered:** {len(all_systems_metadata)}\n\n"

    # Add breakdown by AI type
    ai_type_counts = pd.Series(
        [s.ai_type.value for s in all_systems_metadata]).value_counts()
    summary_content += "**Breakdown by AI Type:**\n"
    for ai_type, count in ai_type_counts.items():
        summary_content += f"- {ai_type}: {count} system{'s' if count != 1 else ''}\n"
    summary_content += "\n"

    # Add breakdown by domain
    domain_counts = pd.Series(
        [s.domain for s in all_systems_metadata]).value_counts()
    summary_content += "**Systems by Business Domain:**\n"
    for domain, count in domain_counts.items():
        summary_content += f"- {domain}: {count} system{'s' if count != 1 else ''}\n"
    summary_content += "\n"

    # Add breakdown by criticality
    criticality_counts = pd.Series(
        [s.decision_criticality.value for s in all_systems_metadata]).value_counts()
    summary_content += "**Decision Criticality Distribution:**\n"
    for crit, count in criticality_counts.items():
        summary_content += f"- {crit}: {count} system{'s' if count != 1 else ''}\n"
    summary_content += "\n"

    summary_content += "## Risk Tiering Overview\n\n"
    summary_content += "Our risk tiering methodology assigns each AI system to one of three tiers based on a comprehensive "
    summary_content += "scoring model that evaluates decision criticality, data sensitivity, automation level, AI type, "
    summary_content += "deployment mode, and external dependencies. Higher tiers trigger more stringent governance controls "
    summary_content += "and oversight requirements.\n\n"

    # Note: RiskTier is assumed to be an Enum defined globally
    tier_counts = pd.Series([t.risk_tier.value for t in all_tiering_results]).value_counts().reindex(
        [tier.value for tier in RiskTier], fill_value=0
    )

    summary_content += "**Tier Distribution:**\n"
    for tier, count in tier_counts.items():
        summary_content += f"- **{tier}** (Highest Risk): {count} system{'s' if count != 1 else ''}\n"
    summary_content += "\n"

    # Add average score information
    if all_tiering_results:
        avg_score = sum(t.total_score for t in all_tiering_results) / \
            len(all_tiering_results)
        summary_content += f"**Average Risk Score Across All Systems:** {avg_score:.1f}\n\n"

    # List systems by tier with more detail
    for tier in [RiskTier.TIER_1, RiskTier.TIER_2, RiskTier.TIER_3]:
        tier_systems = [s for s in all_systems_metadata if get_tiering_result(s.system_id, stores)
                        and get_tiering_result(s.system_id, stores).risk_tier == tier]
        if tier_systems:
            summary_content += f"**{tier.value} Systems:**\n"
            for sys in tier_systems:
                tiering = get_tiering_result(sys.system_id, stores)
                summary_content += f"- {sys.name} (Score: {tiering.total_score}, Domain: {sys.domain}, "
                summary_content += f"Type: {sys.ai_type.value})\n"
            summary_content += "\n"

    summary_content += "## Lifecycle Risk Analysis\n\n"
    all_risks = []
    for system in all_systems_metadata:
        all_risks.extend(get_risks_for_system(system.system_id, stores))

    if all_risks:
        summary_content += f"**Total Risks Identified:** {len(all_risks)}\n\n"

        # Breakdown by lifecycle phase
        phase_counts = pd.Series(
            [r.lifecycle_phase.value for r in all_risks]).value_counts()
        summary_content += "**Risks by Lifecycle Phase:**\n"
        for phase, count in phase_counts.items():
            summary_content += f"- {phase}: {count} risk{'s' if count != 1 else ''}\n"
        summary_content += "\n"

        # Breakdown by risk vector
        vector_counts = pd.Series(
            [r.risk_vector.value for r in all_risks]).value_counts()
        summary_content += "**Risks by Vector:**\n"
        for vector, count in vector_counts.items():
            summary_content += f"- {vector}: {count} risk{'s' if count != 1 else ''}\n"
        summary_content += "\n"

        # Severity distribution
        severity_distribution = pd.Series(
            [r.severity for r in all_risks]).describe()
        summary_content += f"**Severity Statistics:**\n"
        summary_content += f"- Mean Severity: {severity_distribution['mean']:.2f}\n"
        summary_content += f"- Maximum Severity: {int(severity_distribution['max'])}\n"
        summary_content += f"- High Severity Risks (≥15): {len([r for r in all_risks if r.severity >= 15])}\n\n"
    else:
        summary_content += "**Total Risks Identified:** 0\n\n"
        summary_content += "*Note: No lifecycle risks have been registered yet. Risk register population is recommended "
        summary_content += "for all systems, particularly those in TIER_1.*\n\n"

    summary_content += "## Top Risks by Severity (Across All Systems)\n\n"
    if all_risks:
        summary_content += "The following represents the highest-severity risks identified across our AI system portfolio. "
        summary_content += "These risks require immediate attention and should be prioritized in mitigation planning.\n\n"

        top_risks_df = pd.DataFrame([r.model_dump() for r in all_risks])
        top_risks_df = top_risks_df.sort_values(
            by='severity', ascending=False).head(5)

        for idx, (_, row) in enumerate(top_risks_df.iterrows(), 1):
            system_name = next(
                (s.name for s in all_systems_metadata if s.system_id ==
                 row['system_id']),
                "Unknown System"
            )
            summary_content += f"### {idx}. {system_name}\n"
            summary_content += f"**Lifecycle Phase:** {row['lifecycle_phase']} | "
            summary_content += f"**Risk Vector:** {row['risk_vector']}\n\n"
            summary_content += f"**Severity Score:** {row['severity']} (Impact: {row['impact']}/5, Likelihood: {row['likelihood']}/5)\n\n"
            summary_content += f"**Risk Statement:** {row['risk_statement']}\n\n"
            if row['mitigation']:
                summary_content += f"**Mitigation Strategy:** {row['mitigation']}\n\n"
            summary_content += f"**Owner:** {row['owner_role']}\n\n"
            summary_content += "---\n\n"
    else:
        summary_content += "No risks have been registered in the system. It is strongly recommended to populate the "
        summary_content += "lifecycle risk register for all AI systems, especially those classified as TIER_1.\n\n"

    # Notes on missing justifications/coverage (if any)
    summary_content += "## Key Findings & Recommendations\n\n"

    # Count systems with/without risks
    systems_with_risks = len(set(r.system_id for r in all_risks))
    systems_without_risks = len(all_systems_metadata) - systems_with_risks

    if systems_without_risks > 0:
        summary_content += f"- **Action Required:** {systems_without_risks} system{'s' if systems_without_risks != 1 else ''} "
        summary_content += "currently lack lifecycle risk register entries. Risk assessment should be completed for all systems.\n"

    tier1_count = tier_counts.get('TIER_1', 0)
    if tier1_count > 0:
        summary_content += f"- **High-Risk Systems:** {tier1_count} TIER_1 system{'s' if tier1_count != 1 else ''} "
        summary_content += "require comprehensive governance controls including independent validation, full documentation, "
        summary_content += "security testing, and continuous monitoring.\n"

    # Check for external dependencies
    systems_with_external_deps = len(
        [s for s in all_systems_metadata if s.external_dependencies])
    if systems_with_external_deps > 0:
        summary_content += f"- **Vendor Risk:** {systems_with_external_deps} system{'s' if systems_with_external_deps != 1 else ''} "
        summary_content += "rely on external dependencies. Vendor risk assessments and contingency plans should be maintained.\n"

    summary_content += "- **Regular Review:** Risk tiering and lifecycle risk assessments should be reviewed quarterly or "
    summary_content += "whenever significant system changes occur.\n"
    summary_content += "- **Control Implementation:** Verify that all required controls for each risk tier are implemented "
    summary_content += "and functioning as intended.\n"
    summary_content += "- **Evidence Collection:** Maintain comprehensive evidence of control effectiveness for audit and "
    summary_content += "compliance purposes.\n\n"

    summary_content += "---\n\n"
    summary_content += "*This executive summary is auto-generated based on the current state of the AI system inventory "
    summary_content += f"and risk register as of the generation timestamp. For detailed technical information, refer to the "
    summary_content += "accompanying artifacts: model_inventory.csv, risk_tiering.json, and lifecycle_risk_map.json.*\n"

    executive_summary_path = os.path.join(
        output_run_dir, "case1_executive_summary.md")
    with open(executive_summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)

    with open(executive_summary_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "case1_executive_summary.md",
                     "path": executive_summary_path, "sha256": hash_val})
    artifact_hashes["case1_executive_summary.md"] = hash_val
    print(f"Generated: {executive_summary_path}")

    # 5. config_snapshot.json
    config_snapshot_path = os.path.join(output_run_dir, "config_snapshot.json")
    with open(config_snapshot_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(CONFIG))

    with open(config_snapshot_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "config_snapshot.json",
                     "path": config_snapshot_path, "sha256": hash_val})
    artifact_hashes["config_snapshot.json"] = hash_val
    print(f"Generated: {config_snapshot_path}")

    # Calculate inputs_hash
    inputs_hash_data = {
        "case": "case1",
        "systems_count": len(all_systems_metadata),
        "config_snapshot_hash": artifact_hashes["config_snapshot.json"]
    }
    inputs_hash_val = compute_sha256(
        to_deterministic_json(inputs_hash_data).encode('utf-8'))

    # Calculate outputs_hash
    sorted_artifact_names = sorted(artifact_hashes.keys())
    outputs_hash_concat_string = "".join(
        artifact_hashes[name] for name in sorted_artifact_names)
    outputs_hash_val = compute_sha256(
        outputs_hash_concat_string.encode('utf-8'))

    # 6. evidence_manifest.json
    manifest_data = {
        "run_id": run_id,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "team_or_user": team_or_user,
        "app_version": CONFIG["app_version"],
        "inputs_hash": inputs_hash_val,
        "outputs_hash": outputs_hash_val,
        # Sort artifacts by name for determinism
        "artifacts": sorted(artifacts, key=lambda x: x['name'])
    }

    manifest_path = os.path.join(output_run_dir, "evidence_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(manifest_data))

    with open(manifest_path, 'rb') as f:
        hash_val = compute_sha256(f.read())

    artifacts.append({"name": "evidence_manifest.json",
                     "path": manifest_path, "sha256": hash_val})
    artifact_hashes["evidence_manifest.json"] = hash_val
    print(f"Generated: {manifest_path}")

    # 7. Create ZIP package
    zip_filename = os.path.join(output_dir_base, f"Case_01_{run_id}.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for artifact in artifacts:
            zf.write(artifact['path'], os.path.relpath(
                artifact['path'], output_run_dir))  # Add to root of zip

    print(f"\nGenerated ZIP package: {zip_filename}")
    print("\n--- Evidence Manifest Content ---")
    print(json.dumps(manifest_data, indent=2))

    return manifest_data
