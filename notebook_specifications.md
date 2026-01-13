
# Enterprise AI System Governance: Inventory, Tiering, and Risk Management

## Introduction: The AI Product Engineer's Workflow at Aperture Analytics Corp.

Welcome to Aperture Analytics Corp., a rapidly growing technology firm leveraging AI across its product portfolio. As an **AI Product Engineer**, your role is pivotal in ensuring that our AI systems are not only performant but also compliant, auditable, and managed responsibly throughout their lifecycle. This means establishing robust controls and a clear understanding of each system's risk profile.

In many organizations, the journey to responsible AI often stumbles on foundational issues: a fragmented inventory of AI systems, inconsistent risk classifications, and a lack of a clear framework for tracking and mitigating risks. Our goal today is to address these challenges head-on by implementing a pragmatic, enterprise-grade control surface for AI systems.

This notebook will guide you through the real-world workflow of an AI Product Engineer, Alex, as they work to onboard and manage a critical new AI system: "ApertureMind Assist," an LLM-powered customer service agent. You will perform the following key tasks:

1.  **Initialize the Environment and Data Schemas**: Set up the necessary tools and define the data structures that underpin our governance framework.
2.  **Build the AI System Inventory**: Register and manage AI systems with consistent, auditable metadata.
3.  **Implement Deterministic Risk Tiering**: Automatically assess the inherent risk of AI systems to determine required controls and review intensity.
4.  **Maintain a Lifecycle Risk Register**: Identify, document, and track specific risks across the AI system's lifecycle phases, complete with severity scoring.
5.  **Visualize Lifecycle Risks**: Understand the overall risk landscape for a system through an intuitive matrix visualization.
6.  **Generate a Traceable Evidence Package**: Compile all relevant data and artifacts into a secure, verifiable package suitable for internal governance and audit.

By the end of this workflow, you will have a comprehensive understanding of how to implement these critical components, reducing operational risk, ensuring model reliability, and enabling timely intervention for AI systems at Aperture Analytics Corp.

---

### 1. Environment Setup & Data Schema Definition

#### Story + Context + Real-World Relevance

As Alex, the AI Product Engineer, the first step in any new project is to prepare the workspace. This involves installing necessary libraries and defining the standardized data structures (schemas) that will govern all AI system information at Aperture Analytics Corp. Using explicit schemas ensures data integrity, facilitates auditing, and provides a "contract" for how AI system metadata, risk tiers, and lifecycle risks are represented and stored. This prevents common issues like missing or inconsistent data, which can derail governance efforts.

Our persistence layer will be a local SQLite database, allowing us to store and retrieve structured data efficiently. We will also define a configuration file that centralizes all risk tiering thresholds and default controls, ensuring consistency and ease of modification.

#### Code cell (function definition + function execution)

```python
# 1. Install required libraries
!pip install pydantic pandas uuid datetime json hashlib zipfile

import sqlite3
import json
import uuid
import datetime
import hashlib
import pandas as pd
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

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
        "opaque_vendor_bonus": 2, # Added if any dependency matches opaque keywords
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
    "random_seed": None # Explicitly None if not used, or set to a fixed int for determinism
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
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class TieringResult(BaseModel):
    system_id: uuid.UUID
    risk_tier: RiskTier
    total_score: int
    score_breakdown: Dict[str, int]
    justification: str = ""
    required_controls: List[str] = Field(default_factory=list)
    computed_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    scoring_version: str = CONFIG["scoring_version"]

class LifecycleRiskEntry(BaseModel):
    risk_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    system_id: uuid.UUID
    lifecycle_phase: LifecyclePhase
    risk_vector: RiskVector
    risk_statement: str
    impact: int = Field(..., ge=1, le=5)
    likelihood: int = Field(..., ge=1, le=5)
    severity: int # Will be calculated: impact * likelihood
    mitigation: str = ""
    owner_role: str
    evidence_links: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.severity = self.impact * self.likelihood

# --- SQLite Database Functions ---
DATABASE_PATH = "reports/labs.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS systems (
            system_id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiering (
            system_id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            computed_at TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lifecycle_risks (
            risk_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (system_id) REFERENCES systems (system_id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

# Initialize database
create_tables()

print("Environment setup complete: Libraries installed, Pydantic schemas defined, and SQLite tables created.")
```

#### Explanation of execution

This initial setup block ensures that all necessary Python packages are available. More importantly, it defines the backbone of our data governance system: the `Pydantic` models for `SystemMetadata`, `TieringResult`, and `LifecycleRiskEntry`. These models act as strict contracts, validating all incoming data against predefined types and constraints (e.g., `impact` and `likelihood` must be between 1 and 5).

The `CONFIG` dictionary centralizes all parameters critical for risk tiering and default controls. This makes the system transparent and easily auditable.

Finally, the `create_tables()` function sets up a local SQLite database named `reports/labs.sqlite`. This database will persist our AI system inventory, their computed risk tiers, and all associated lifecycle risks. Each table stores the core data as a JSON blob, allowing for flexible schema evolution while keeping key identifiers (like `system_id` and `risk_id`) easily queryable as primary keys.

---

### 2. Building the AI System Inventory

#### Story + Context + Real-World Relevance

Alex's core responsibility includes maintaining an accurate and up-to-date inventory of all AI systems at Aperture Analytics Corp. This inventory is the single source of truth for understanding what AI systems are deployed, who owns them, what their purpose is, and their basic technical characteristics. Without a clear inventory, it's impossible to implement consistent controls, track ownership, or conduct audits effectively.

Today, Alex needs to register "ApertureMind Assist," a new LLM-powered customer service agent. They'll start by loading some existing sample systems into the inventory to demonstrate the `CRUD` (Create, Read, Update, Delete) operations, and then add the new system.

#### Code cell (function definition + function execution)

```python
# --- Inventory CRUD Operations ---

def load_sample_systems_data(filepath: str = "data/sample_case1_systems.json"):
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
            "name": "Content Generation LLM",
            "description": "Generates marketing content based on prompts.",
            "domain": "Marketing",
            "ai_type": "LLM",
            "owner_role": "Marketing Team",
            "deployment_mode": "HUMAN_IN_LOOP",
            "decision_criticality": "MEDIUM",
            "automation_level": "HUMAN_APPROVAL",
            "data_sensitivity": "INTERNAL",
            "external_dependencies": ["OpenAI API (vendor)"] # Example of opaque vendor
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
            add_system(system)
            print(f"Loaded: {system.name}")
        except ValidationError as e:
            print(f"Validation error loading sample system {item.get('name', 'Unknown')}: {e}")
        except sqlite3.IntegrityError:
            print(f"System with ID {item.get('system_id', 'Unknown')} already exists. Skipping.")
    print("-------------------------------------------\n")

def add_system(system_metadata: SystemMetadata):
    """Adds a new AI system to the inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO systems (system_id, json, updated_at) VALUES (?, ?, ?)",
            (str(system_metadata.system_id), system_metadata.json(), system_metadata.updated_at)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: System with ID {system_metadata.system_id} already exists.")
    finally:
        conn.close()

def get_system(system_id: uuid.UUID) -> Optional[SystemMetadata]:
    """Retrieves an AI system by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM systems WHERE system_id = ?", (str(system_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return SystemMetadata.parse_raw(row['json'])
    return None

def get_all_systems() -> List[SystemMetadata]:
    """Retrieves all AI systems in the inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM systems")
    rows = cursor.fetchall()
    conn.close()
    return [SystemMetadata.parse_raw(row['json']) for row in rows]

def update_system(system_id: uuid.UUID, updates: Dict[str, Any]):
    """Updates an existing AI system's metadata."""
    current_system = get_system(system_id)
    if not current_system:
        print(f"Error: System with ID {system_id} not found for update.")
        return False
    
    updated_data = current_system.dict()
    updated_data.update(updates)
    updated_data['updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    try:
        updated_system = SystemMetadata(**updated_data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE systems SET json = ?, updated_at = ? WHERE system_id = ?",
            (updated_system.json(), updated_system.updated_at, str(system_id))
        )
        conn.commit()
        conn.close()
        return True
    except ValidationError as e:
        print(f"Validation error updating system {system_id}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}")
        return False

def delete_system(system_id: uuid.UUID):
    """Deletes an AI system from the inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM systems WHERE system_id = ?", (str(system_id),))
    conn.commit()
    conn.close()

# --- Execution ---

# 1. Load sample systems
# Simulating the data/sample_case1_systems.json content directly as a list of dicts.
load_sample_systems_data()

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
    external_dependencies=["Anthropic Claude API (vendor)", "Internal CRM API", "Knowledge Base API"]
)
add_system(aperture_mind_assist)

# 3. Retrieve and display all systems
print("--- Current AI System Inventory ---")
all_systems = get_all_systems()
for system in all_systems:
    print(f"ID: {system.system_id}, Name: {system.name}, Type: {system.ai_type}, Criticality: {system.decision_criticality}")
print("-----------------------------------")

# 4. Example: Update a system (e.g., description for ApertureMind Assist)
update_system(aperture_mind_assist_id, {"description": "Enhanced LLM agent for internal customer support, handling a wider range of queries."})
updated_aperture_mind = get_system(aperture_mind_assist_id)
print(f"\nUpdated ApertureMind Assist description: {updated_aperture_mind.description}")
```

#### Explanation of execution

This section first demonstrates how to populate the `systems` table with predefined sample data, simulating existing AI systems at Aperture Analytics Corp. The `load_sample_systems_data` function acts as our "Load sample" mechanism.

Following this, Alex registers the new "ApertureMind Assist" system using the `add_system` function. The data for this system adheres strictly to the `SystemMetadata` Pydantic schema, ensuring that all required fields are present and correctly formatted. This includes details like its `ai_type` (LLM), `decision_criticality` (Medium), and `external_dependencies` (including an opaque vendor, 'Anthropic Claude API').

The `get_all_systems()` function then retrieves and displays a summary of all registered systems, confirming their successful addition to the inventory. Finally, an example update using `update_system` shows how to modify a system's metadata, automatically updating the `updated_at` timestamp for auditability. These `CRUD` operations are fundamental for managing the inventory effectively and reliably.

---

### 3. Deterministic Risk Tiering

#### Story + Context + Real-World Relevance

After registering "ApertureMind Assist," Alex's next crucial task is to determine its inherent risk tier. Aperture Analytics Corp. uses a **deterministic tiering algorithm** to objectively classify AI systems into `Tier 1` (High Risk), `Tier 2` (Medium Risk), or `Tier 3` (Low Risk). This tier directly dictates the level of oversight, controls, and review intensity required for the system. A deterministic approach ensures consistency, reduces subjective bias, and makes the tiering process transparent and auditable.

The algorithm calculates a total score based on various dimensions of the AI system (e.g., decision criticality, data sensitivity, automation level) using predefined point mappings. This score is then compared against configurable thresholds to assign the final tier. The formula for the total score $S$ is the sum of points across dimensions:

$$S = \sum_{d \in D} \text{points}(d)$$

Where $D$ is the set of relevant dimensions and $\text{points}(d)$ is the score derived from the system's characteristic for dimension $d$.

The tier is then assigned based on these thresholds:
*   $\text{Tier 1 if } S \ge T_{1,min}$
*   $\text{Tier 2 if } S \ge T_{2,min}$
*   $\text{Tier 3 otherwise}$

Where $T_{1,min}$ and $T_{2,min}$ are the configurable minimum scores for Tier 1 and Tier 2, respectively, as defined in our `CONFIG`.

#### Code cell (function definition + function execution)

```python
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
        attr_value = getattr(system_metadata, dim).value if isinstance(getattr(system_metadata, dim), Enum) else getattr(system_metadata, dim)
        score = mappings.get(attr_value, 0) # Default to 0 if value not found, should not happen with Pydantic Enums
        total_score += score
        score_breakdown[dim] = score

    # External Dependencies Scoring
    dep_count = len(system_metadata.external_dependencies)
    dep_score = 0
    if dep_count == 0:
        dep_score = CONFIG["external_dependencies_scoring"]["0_deps"]
    elif 1 <= dep_count <= 2:
        dep_score = CONFIG["external_dependencies_scoring"]["1_2_deps"]
    else: # dep_count >= 3
        dep_score = CONFIG["external_dependencies_scoring"]["3_plus_deps"]
    
    # Check for opaque vendors
    for dep in system_metadata.external_dependencies:
        if any(keyword in dep.lower() for keyword in CONFIG["external_dependencies_scoring"]["opaque_keywords"]):
            dep_score += CONFIG["external_dependencies_scoring"]["opaque_vendor_bonus"]
            break # Only add bonus once
            
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

def save_tiering_result(tiering_result: TieringResult):
    """Saves a tiering result for an AI system, updating if already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use UPSERT (OR REPLACE) to handle updates if tiering already exists for the system_id
    cursor.execute(
        "INSERT OR REPLACE INTO tiering (system_id, json, computed_at) VALUES (?, ?, ?)",
        (str(tiering_result.system_id), tiering_result.json(), tiering_result.computed_at)
    )
    conn.commit()
    conn.close()

def get_tiering_result(system_id: uuid.UUID) -> Optional[TieringResult]:
    """Retrieves a tiering result by system ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM tiering WHERE system_id = ?", (str(system_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return TieringResult.parse_raw(row['json'])
    return None

# --- Execution ---

# 1. Retrieve ApertureMind Assist system metadata
aperture_mind_system = get_system(aperture_mind_assist_id)
if aperture_mind_system:
    # 2. Calculate its risk tier
    tiering_result = calculate_risk_tier(aperture_mind_system)
    
    # 3. Display the results
    print(f"--- Risk Tiering for '{aperture_mind_system.name}' ---")
    print(f"Total Score: {tiering_result.total_score}")
    print(f"Assigned Risk Tier: {tiering_result.risk_tier.value}")
    print("Score Breakdown:")
    for dim, score in tiering_result.score_breakdown.items():
        print(f"  - {dim.replace('_', ' ').title()}: {score} points")
    print(f"\nJustification: {tiering_result.justification}")
    print("Default Required Controls:")
    for control in tiering_result.required_controls:
        print(f"  - {control}")

    # 4. Save the tiering result (which includes default controls and justification)
    save_tiering_result(tiering_result)
    print("\nRisk tiering result saved to database.")

    # 5. Example: Alex might want to customize controls or justification
    # For instance, add a specific custom control for LLMs.
    custom_controls = tiering_result.required_controls + ["Specific LLM prompt injection testing protocol"]
    custom_justification = tiering_result.justification + " Added specific LLM controls."
    
    updated_tiering_result = tiering_result.copy(update={
        "required_controls": custom_controls,
        "justification": custom_justification,
        "computed_at": datetime.datetime.now(datetime.timezone.utc).isoformat() # Update timestamp
    })
    save_tiering_result(updated_tiering_result)
    print("\nRisk tiering result updated with custom controls and justification.")
    
    # Verify update
    verified_tiering = get_tiering_result(aperture_mind_system.system_id)
    print(f"\nVerified Controls for '{aperture_mind_system.name}':")
    for control in verified_tiering.required_controls:
        print(f"  - {control}")
else:
    print(f"Error: ApertureMind Assist (ID: {aperture_mind_assist_id}) not found.")
```

#### Explanation of execution

This section calculates the risk tier for "ApertureMind Assist" using the `calculate_risk_tier` function. This function embodies Aperture Analytics Corp.'s deterministic tiering algorithm. It iterates through various system attributes (like `decision_criticality`, `data_sensitivity`, `ai_type`) and assigns points based on predefined mappings from the `CONFIG` dictionary. A special scoring logic is applied to `external_dependencies`, including a bonus for "opaque vendors" (e.g., "Anthropic Claude API").

The resulting `total_score` is then compared against `TIER_1_MIN` (22 points) and `TIER_2_MIN` (15 points) thresholds to assign the final `RiskTier` (e.g., `TIER_1`, `TIER_2`, `TIER_3`). For "ApertureMind Assist", with its LLM type, real-time deployment, and confidential data, it's likely to fall into a higher risk tier.

The output explicitly shows the `total_score`, the assigned `risk_tier`, and a detailed `score_breakdown`, which is crucial for transparency and explaining the tiering decision. The function also retrieves default `required_controls` based on the assigned tier. These results, including the automatically generated `justification` and `required_controls`, are then saved to the `tiering` table using `save_tiering_result`, demonstrating how Alex persists this critical governance information. An example update shows how Alex can then edit and save `required_controls` and `justification` as per the user requirements.

---

### 4. Maintaining the Lifecycle Risk Register

#### Story + Context + Real-World Relevance

Now that "ApertureMind Assist" has a defined risk tier, Alex must proactively identify and document specific risks across its entire lifecycle. This **lifecycle risk register** is a living document that captures potential issues from inception to retirement, categorizing them by `lifecycle_phase` (e.g., `DATA`, `DEPLOYMENT`) and `risk_vector` (e.g., `BIAS_FAIRNESS`, `OPERATIONAL`).

Each risk entry includes an `impact` and `likelihood` score (both 1-5), from which a `severity` score is deterministically calculated. This structured approach helps Aperture Analytics Corp. understand, prioritize, and mitigate risks systematically. The formula for severity is:

$$\text{Severity} = \text{Impact} \times \text{Likelihood}$$

Alex's task is to add several specific risks for "ApertureMind Assist" to ensure comprehensive coverage and begin building a robust mitigation plan.

#### Code cell (function definition + function execution)

```python
# --- Lifecycle Risk Register Operations ---

def add_lifecycle_risk(risk_entry: LifecycleRiskEntry):
    """Adds a new lifecycle risk entry for an AI system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO lifecycle_risks (risk_id, system_id, json, created_at) VALUES (?, ?, ?, ?)",
            (str(risk_entry.risk_id), str(risk_entry.system_id), risk_entry.json(), risk_entry.created_at)
        )
        conn.commit()
        print(f"Added risk: {risk_entry.risk_statement} (Severity: {risk_entry.severity})")
    except sqlite3.IntegrityError:
        print(f"Error: Risk with ID {risk_entry.risk_id} already exists.")
    finally:
        conn.close()

def get_risks_for_system(system_id: uuid.UUID) -> List[LifecycleRiskEntry]:
    """Retrieves all lifecycle risks for a specific AI system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM lifecycle_risks WHERE system_id = ?", (str(system_id),))
    rows = cursor.fetchall()
    conn.close()
    return [LifecycleRiskEntry.parse_raw(row['json']) for row in rows]

def update_lifecycle_risk(risk_id: uuid.UUID, updates: Dict[str, Any]):
    """Updates an existing lifecycle risk entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
    row = cursor.fetchone()
    if not row:
        print(f"Error: Risk with ID {risk_id} not found for update.")
        conn.close()
        return False
    
    current_risk = LifecycleRiskEntry.parse_raw(row['json'])
    updated_data = current_risk.dict()
    updated_data.update(updates)
    
    # Recalculate severity if impact or likelihood changes
    if 'impact' in updates or 'likelihood' in updates:
        updated_data['severity'] = updated_data['impact'] * updated_data['likelihood']

    try:
        updated_risk = LifecycleRiskEntry(**updated_data)
        cursor.execute(
            "UPDATE lifecycle_risks SET json = ?, created_at = ? WHERE risk_id = ?", # created_at is updated for simplicity, could be 'updated_at'
            (updated_risk.json(), datetime.datetime.now(datetime.timezone.utc).isoformat(), str(risk_id))
        )
        conn.commit()
        conn.close()
        return True
    except ValidationError as e:
        print(f"Validation error updating risk {risk_id}: {e}")
        return False

def delete_lifecycle_risk(risk_id: uuid.UUID):
    """Deletes a lifecycle risk entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lifecycle_risks WHERE risk_id = ?", (str(risk_id),))
    conn.commit()
    conn.close()

# --- Execution ---

# 1. Add several lifecycle risks for "ApertureMind Assist"
print(f"--- Adding Lifecycle Risks for '{aperture_mind_system.name}' ---")

# Risk 1: Data Phase - Bias/Fairness
risk_1_id = uuid.uuid4()
add_lifecycle_risk(LifecycleRiskEntry(
    risk_id=risk_1_id,
    system_id=aperture_mind_assist_id,
    lifecycle_phase=LifecyclePhase.DATA,
    risk_vector=RiskVector.BIAS_FAIRNESS,
    risk_statement="Training data for LLM agent contains historical biases leading to unfair responses for certain user demographics.",
    impact=4, likelihood=3, owner_role="AI Ethics Team", mitigation="Implement bias detection tools and data re-weighting."
))

# Risk 2: Design/Build Phase - Robustness
risk_2_id = uuid.uuid4()
add_lifecycle_risk(LifecycleRiskEntry(
    risk_id=risk_2_id,
    system_id=aperture_mind_assist_id,
    lifecycle_phase=LifecyclePhase.DESIGN_BUILD,
    risk_vector=RiskVector.ROBUSTNESS,
    risk_statement="Agent is susceptible to adversarial attacks, leading to misinterpretation of user queries.",
    impact=5, likelihood=2, owner_role="ML Engineering Team", mitigation="Implement adversarial training and input validation."
))

# Risk 3: Deployment Phase - Operational
risk_3_id = uuid.uuid4()
add_lifecycle_risk(LifecycleRiskEntry(
    risk_id=risk_3_id,
    system_id=aperture_mind_assist_id,
    lifecycle_phase=LifecyclePhase.DEPLOYMENT,
    risk_vector=RiskVector.OPERATIONAL,
    risk_statement="High latency in LLM responses could degrade user experience and service levels.",
    impact=3, likelihood=4, owner_role="Operations Team", mitigation="Optimize model serving infrastructure and implement caching."
))

# Risk 4: Operations Phase - Security
risk_4_id = uuid.uuid4()
add_lifecycle_risk(LifecycleRiskEntry(
    risk_id=risk_4_id,
    system_id=aperture_mind_assist_id,
    lifecycle_phase=LifecyclePhase.OPERATIONS,
    risk_vector=RiskVector.SECURITY,
    risk_statement="LLM agent may leak sensitive internal information if not properly sandboxed and monitored.",
    impact=5, likelihood=3, owner_role="Security Team", mitigation="Implement strict access controls and real-time output filtering."
))

# Risk 5: Validation Phase - Interpretability
risk_5_id = uuid.uuid4()
add_lifecycle_risk(LifecycleRiskEntry(
    risk_id=risk_5_id,
    system_id=aperture_mind_assist_id,
    lifecycle_phase=LifecyclePhase.VALIDATION,
    risk_vector=RiskVector.INTERPRETABILITY,
    risk_statement="Lack of interpretability makes debugging difficult and understanding decision rationale opaque.",
    impact=2, likelihood=3, owner_role="ML Engineering Team", mitigation="Develop and integrate interpretability tools for LLM."
))

# 2. Retrieve and display all risks for ApertureMind Assist
print(f"\n--- All Lifecycle Risks for '{aperture_mind_system.name}' ---")
aperture_mind_risks = get_risks_for_system(aperture_mind_assist_id)
for risk in aperture_mind_risks:
    print(f"Risk ID: {risk.risk_id}")
    print(f"  Phase: {risk.lifecycle_phase.value}, Vector: {risk.risk_vector.value}")
    print(f"  Statement: {risk.risk_statement}")
    print(f"  Impact: {risk.impact}, Likelihood: {risk.likelihood}, Severity: {risk.severity}")
    print(f"  Owner: {risk.owner_role}, Mitigation: {risk.mitigation}\n")

# 3. Example: Update a risk's impact and mitigation
print(f"--- Updating Risk ID: {risk_1_id} ---")
update_lifecycle_risk(risk_1_id, {
    "impact": 5, # Increasing impact after new assessment
    "mitigation": "Implemented advanced bias mitigation techniques and external audit."
})
updated_risk_1 = [r for r in get_risks_for_system(aperture_mind_assist_id) if r.risk_id == risk_1_id][0]
print(f"Updated Risk Statement: {updated_risk_1.risk_statement}")
print(f"New Impact: {updated_risk_1.impact}, New Likelihood: {updated_risk_1.likelihood}, New Severity: {updated_risk_1.severity}")
```

#### Explanation of execution

In this section, Alex uses the `add_lifecycle_risk` function to document various potential risks associated with "ApertureMind Assist." Each risk is characterized by its `lifecycle_phase` (e.g., `DATA`, `DESIGN_BUILD`), `risk_vector` (e.g., `BIAS_FAIRNESS`, `ROBUSTNESS`), a detailed `risk_statement`, `impact` (1-5), and `likelihood` (1-5).

Critically, the `severity` of each risk is automatically calculated as the product of `impact` and `likelihood` ($ \text{Severity} = \text{Impact} \times \text{Likelihood} $), ensuring a consistent measure of risk magnitude. This calculation is handled directly by the `LifecycleRiskEntry` Pydantic model's `__init__` method, simplifying data entry and preventing calculation errors.

By adding at least five risks spanning multiple lifecycle phases, Alex fulfills the requirement for comprehensive risk coverage for the AI system. The `get_risks_for_system` function then retrieves and displays all documented risks, providing a clear overview. The example update shows how Alex can modify existing risks, automatically recalculating the severity if `impact` or `likelihood` changes, thus maintaining an accurate and dynamic risk register.

---

### 5. Visualizing Lifecycle Risks

#### Story + Context + Real-World Relevance

After populating the lifecycle risk register, Alex needs a quick and insightful way to understand the overall risk posture for "ApertureMind Assist." A simple list of risks, while comprehensive, doesn't immediately highlight patterns or areas of concern. To address this, Aperture Analytics Corp. uses a **lifecycle $\times$ risk vector matrix visualization**.

This matrix provides a powerful, at-a-glance summary, showing the distribution of risks across different `lifecycle_phases` (rows) and `risk_vectors` (columns). Each cell in the matrix displays the count of risks for that specific phase-vector combination, and optionally the maximum severity, allowing Alex to quickly identify phases or risk categories that are particularly exposed or require more attention. This visualization is essential for communicating risks to stakeholders and for prioritizing mitigation efforts effectively.

#### Code cell (function definition + function execution)

```python
# --- Risk Matrix Visualization ---

def generate_risk_matrix(system_id: uuid.UUID) -> pd.DataFrame:
    """
    Generates a lifecycle x risk vector matrix for a given system,
    showing count of risks and max severity in each cell.
    """
    risks = get_risks_for_system(system_id)
    if not risks:
        print(f"No risks found for system ID: {system_id}.")
        return pd.DataFrame(columns=[rv.value for rv in RiskVector]) # Empty DF

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
            cell_risks = df[(df['lifecycle_phase'] == phase.value) & (df['risk_vector'] == vector.value)]
            
            count = len(cell_risks)
            max_severity = cell_risks['severity'].max() if count > 0 else 0
            
            # Store as a tuple (count, max_severity)
            matrix_data[phase.value][vector.value] = f"Count: {count}, Max Severity: {int(max_severity)}"

    # Convert to DataFrame for better display
    matrix_df = pd.DataFrame(matrix_data).T # Transpose to get phases as rows
    matrix_df.index.name = "Lifecycle Phase"
    matrix_df.columns.name = "Risk Vector"
    
    # Ensure all lifecycle phases and risk vectors are present, even if empty
    full_phases = [phase.value for phase in LifecyclePhase]
    full_vectors = [vector.value for vector in RiskVector]
    
    # Reindex to ensure all phases and vectors are present
    matrix_df = matrix_df.reindex(index=full_phases, columns=full_vectors, fill_value="Count: 0, Max Severity: 0")
    
    return matrix_df

# --- Execution ---

# 1. Generate the risk matrix for ApertureMind Assist
print(f"--- Lifecycle x Risk Vector Matrix for '{aperture_mind_system.name}' ---")
risk_matrix_df = generate_risk_matrix(aperture_mind_assist_id)

# 2. Display the matrix
# Using display for better rendering in Jupyter, but print will also work.
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
display(risk_matrix_df)
# print(risk_matrix_df.to_markdown()) # For pure markdown output if needed
```

#### Explanation of execution

This section generates the `lifecycle_phase` $\times$ `risk_vector` matrix using the `generate_risk_matrix` function. This function retrieves all lifecycle risks associated with "ApertureMind Assist" from the database. It then processes this data to count the number of risks and find the maximum severity for each unique combination of `lifecycle_phase` and `risk_vector`.

The output is a `pandas.DataFrame`, which provides a clear, tabular view of the risk landscape. Each cell in the matrix shows both the `Count` of risks and the `Max Severity` for that particular phase-vector intersection. This allows Alex to quickly identify which lifecycle phases are experiencing the most risks, which risk vectors are most prevalent, and where the highest severity risks are concentrated. For example, Alex might see a high count of `OPERATIONAL` risks in the `DEPLOYMENT` phase, indicating a need for more robust deployment practices. This visualization is invaluable for communicating complex risk profiles in an easily digestible format to various stakeholders within Aperture Analytics Corp.

---

### 6. Generating a Traceable Evidence Package

#### Story + Context + Real-World Relevance

As "ApertureMind Assist" moves towards full operational deployment, Alex must prepare a formal **evidence package**. This package serves as an immutable record of the AI system's governance artifacts, critical for internal audits, compliance checks, and stakeholder reviews. It includes various data exports (`.csv`, `.json`, `.md`), a `config_snapshot.json` to capture the exact tiering rules used, and crucially, an `evidence_manifest.json` that lists all artifacts along with their cryptographic **SHA-256 hashes**.

The use of hashes ensures the integrity and traceability of the package: any modification to an artifact would change its hash, immediately signaling tampering. This ensures that Aperture Analytics Corp. maintains an "evidence-grade" record of its AI systems' governance. Alex will generate this package, capturing a snapshot of the current state of the system's inventory, tiering, and risks.

The `inputs_hash` in the manifest must be SHA-256 over a deterministic JSON serialization of:
*   `case: "case1"`
*   `systems_count` (total number of systems in the inventory at the time of export)
*   `config_snapshot` (hash of the serialized CONFIG)

The `outputs_hash` must be SHA-256 over the ordered list of artifact hashes (sorted by artifact name).

#### Code cell (function definition + function execution)

```python
import os
import zipfile
import json
import hashlib
import uuid
import datetime
import pandas as pd # Ensure pandas is imported as it's used for CSV export

# --- Helper Functions for Hashing and Serialization ---
def compute_sha256(data: bytes) -> str:
    """Computes the SHA-256 hash of provided bytes data."""
    return hashlib.sha256(data).hexdigest()

def to_deterministic_json(obj: Any) -> str:
    """Serializes an object to a deterministic JSON string."""
    return json.dumps(obj, sort_keys=True, indent=None, ensure_ascii=False, separators=(',', ':'))

# --- Export and Evidence Package Generation ---
def generate_evidence_package(run_id: str, output_dir_base: str = "reports/case1"):
    """
    Generates all required artifacts, evidence manifest, and a ZIP package.
    """
    output_run_dir = os.path.join(output_dir_base, run_id)
    os.makedirs(output_run_dir, exist_ok=True)
    
    artifacts = []
    artifact_hashes = {}

    # 1. model_inventory.csv
    all_systems_metadata = get_all_systems()
    systems_df = pd.DataFrame([s.dict() for s in all_systems_metadata])
    # Ensure external_dependencies are pipe-separated string
    systems_df['external_dependencies'] = systems_df['external_dependencies'].apply(lambda x: '|'.join(x))
    # Select and order columns as per artifact definition
    inventory_columns = [
        'system_id', 'name', 'domain', 'ai_type', 'owner_role', 
        'decision_criticality', 'automation_level', 'data_sensitivity', 
        'deployment_mode', 'external_dependencies', 'updated_at'
    ]
    # Filter columns that actually exist in the DataFrame
    existing_inventory_columns = [col for col in inventory_columns if col in systems_df.columns]
    systems_df = systems_df[existing_inventory_columns]
    
    inventory_path = os.path.join(output_run_dir, "model_inventory.csv")
    systems_df.to_csv(inventory_path, index=False)
    with open(inventory_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "model_inventory.csv", "path": inventory_path, "sha256": hash_val})
        artifact_hashes["model_inventory.csv"] = hash_val
    print(f"Generated: {inventory_path}")

    # 2. risk_tiering.json
    all_tiering_results = [get_tiering_result(s.system_id) for s in all_systems_metadata if get_tiering_result(s.system_id)]
    tiering_data_export = {
        "scoring_version": CONFIG["scoring_version"],
        "systems": [t.dict() for t in all_tiering_results]
    }
    tiering_path = os.path.join(output_run_dir, "risk_tiering.json")
    with open(tiering_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(tiering_data_export))
    with open(tiering_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "risk_tiering.json", "path": tiering_path, "sha256": hash_val})
        artifact_hashes["risk_tiering.json"] = hash_val
    print(f"Generated: {tiering_path}")

    # 3. lifecycle_risk_map.json
    lifecycle_risk_map_data = {"systems": []}
    for system in all_systems_metadata:
        risks_for_system = get_risks_for_system(system.system_id)
        if risks_for_system:
            lifecycle_risk_map_data["systems"].append({
                "system_id": str(system.system_id),
                "risks": [r.dict() for r in risks_for_system]
            })
    risk_map_path = os.path.join(output_run_dir, "lifecycle_risk_map.json")
    with open(risk_map_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(lifecycle_risk_map_data))
    with open(risk_map_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "lifecycle_risk_map.json", "path": risk_map_path, "sha256": hash_val})
        artifact_hashes["lifecycle_risk_map.json"] = hash_val
    print(f"Generated: {risk_map_path}")

    # 4. case1_executive_summary.md
    summary_content = f"# Executive Summary for Case 1 (Run ID: {run_id})\n\n"
    summary_content += f"Generated At: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
    summary_content += f"App Version: {CONFIG['app_version']}\n\n"
    summary_content += "## AI System Inventory Summary\n"
    summary_content += f"Total AI Systems: {len(all_systems_metadata)}\n\n"

    summary_content += "## Risk Tiering Overview\n"
    tier_counts = pd.Series([t.risk_tier.value for t in all_tiering_results]).value_counts().reindex([tier.value for tier in RiskTier], fill_value=0)
    summary_content += "Tier Distribution:\n"
    for tier, count in tier_counts.items():
        summary_content += f"- {tier}: {count} systems\n"
    summary_content += "\n"
    
    summary_content += "## Top Risks by Severity (across all systems)\n"
    all_risks = []
    for system in all_systems_metadata:
        all_risks.extend(get_risks_for_system(system.system_id))
    
    if all_risks:
        top_risks_df = pd.DataFrame([r.dict() for r in all_risks])
        top_risks_df = top_risks_df.sort_values(by='severity', ascending=False).head(5)
        for _, row in top_risks_df.iterrows():
            system_name = next((s.name for s in all_systems_metadata if s.system_id == uuid.UUID(row['system_id'])), "Unknown System")
            summary_content += f"- **System**: {system_name}\n"
            summary_content += f"  **Phase/Vector**: {row['lifecycle_phase']}/{row['risk_vector']}\n"
            summary_content += f"  **Severity**: {row['severity']} (Impact: {row['impact']}, Likelihood: {row['likelihood']})\n"
            summary_content += f"  **Statement**: {row['risk_statement']}\n\n"
    else:
        summary_content += "No risks registered.\n\n"

    # Notes on missing justifications/coverage (if any)
    summary_content += "## Notes & Recommendations\n"
    summary_content += "- Ensure all high-tier systems have comprehensive risk register entries.\n"
    summary_content += "- Regularly review justifications for risk tiering decisions.\n"

    executive_summary_path = os.path.join(output_run_dir, "case1_executive_summary.md")
    with open(executive_summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    with open(executive_summary_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "case1_executive_summary.md", "path": executive_summary_path, "sha256": hash_val})
        artifact_hashes["case1_executive_summary.md"] = hash_val
    print(f"Generated: {executive_summary_path}")

    # 5. config_snapshot.json
    config_snapshot_path = os.path.join(output_run_dir, "config_snapshot.json")
    with open(config_snapshot_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(CONFIG))
    with open(config_snapshot_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "config_snapshot.json", "path": config_snapshot_path, "sha256": hash_val})
        artifact_hashes["config_snapshot.json"] = hash_val
    print(f"Generated: {config_snapshot_path}")

    # Calculate inputs_hash
    inputs_hash_data = {
        "case": "case1",
        "systems_count": len(all_systems_metadata),
        "config_snapshot_hash": artifact_hashes["config_snapshot.json"]
    }
    inputs_hash_val = compute_sha256(to_deterministic_json(inputs_hash_data).encode('utf-8'))

    # Calculate outputs_hash
    sorted_artifact_names = sorted(artifact_hashes.keys())
    outputs_hash_concat_string = "".join(artifact_hashes[name] for name in sorted_artifact_names)
    outputs_hash_val = compute_sha256(outputs_hash_concat_string.encode('utf-8'))

    # 6. evidence_manifest.json
    manifest_data = {
        "run_id": run_id,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "team_or_user": "AI Product Engineer (Alex)",
        "app_version": CONFIG["app_version"],
        "inputs_hash": inputs_hash_val,
        "outputs_hash": outputs_hash_val,
        "artifacts": sorted(artifacts, key=lambda x: x['name']) # Sort artifacts by name for determinism
    }
    manifest_path = os.path.join(output_run_dir, "evidence_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(to_deterministic_json(manifest_data))
    with open(manifest_path, 'rb') as f:
        hash_val = compute_sha256(f.read())
        artifacts.append({"name": "evidence_manifest.json", "path": manifest_path, "sha256": hash_val})
        artifact_hashes["evidence_manifest.json"] = hash_val
    print(f"Generated: {manifest_path}")

    # 7. Create ZIP package
    zip_filename = os.path.join(output_dir_base, f"Case_01_{run_id}.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for artifact in artifacts:
            zf.write(artifact['path'], os.path.relpath(artifact['path'], output_run_dir)) # Add to root of zip
    print(f"\nGenerated ZIP package: {zip_filename}")
    
    print("\n--- Evidence Manifest Content ---")
    print(json.dumps(manifest_data, indent=2))
    return manifest_data

# --- Execution ---
current_run_id = str(uuid.uuid4())
manifest = generate_evidence_package(current_run_id)
```

#### Explanation of execution

This final section orchestrates the creation of Aperture Analytics Corp.'s **traceable evidence package**. The `generate_evidence_package` function performs several critical steps:

1.  **Artifact Generation**: It queries the SQLite database to fetch all system metadata, tiering results, and lifecycle risks. This data is then formatted into specific files: `model_inventory.csv`, `risk_tiering.json`, and `lifecycle_risk_map.json`. It also generates `case1_executive_summary.md` (providing a high-level overview of tier distribution and top risks) and `config_snapshot.json` (a verbatim copy of the `CONFIG` used for deterministic tiering).
2.  **Hashing**: For each generated artifact, a **SHA-256 hash** is computed using `compute_sha256`. This hash uniquely identifies the content of the file.
3.  **`inputs_hash` Calculation**: This hash is computed over a deterministic JSON representation of key input parameters (`case`, `systems_count`, and the hash of the `config_snapshot`). This ensures that if any initial conditions or configurations change, the input hash will reflect it.
4.  **`outputs_hash` Calculation**: This hash is computed by concatenating the SHA-256 hashes of all generated artifacts (excluding the manifest itself), sorted by artifact name, and then hashing the resulting string. This provides an overall integrity check for the entire output package.
5.  **`evidence_manifest.json` Creation**: A manifest file is created, detailing the `run_id`, `generated_at` timestamp, `inputs_hash`, `outputs_hash`, and a list of all artifacts along with their individual hashes and paths. This manifest acts as a tamper-evident log of the entire package.
6.  **ZIP Packaging**: Finally, all generated artifacts (including the manifest) are compressed into a single ZIP file (`Case_01_<run_id>.zip`). This makes the package easy to store, transfer, and verify.

By executing these steps, Alex creates a complete, verifiable, and immutable record of the governance state of "ApertureMind Assist." Any future auditor or reviewer can use the provided hashes to confirm that the package's contents have not been altered since its generation, providing high assurance and traceability for AI governance at Aperture Analytics Corp.

---
