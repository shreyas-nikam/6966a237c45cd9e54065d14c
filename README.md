Here's a comprehensive `README.md` file for your Streamlit application lab project, designed for clarity, professionalism, and completeness.

---

# QuLab: Enterprise AI Inventory, Risk Tiering, and Lifecycle Risk Management

![QuLab Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## Project Title and Description

**QuLab: Enterprise AI Inventory, Risk Tiering, and Lifecycle Risk Management** is a Streamlit-based web application designed to help organizations, specifically AI Product Engineers like "Alex," establish a robust framework for managing their AI systems. It provides a centralized, "single source of truth" for tracking AI deployments, assessing inherent risks through a deterministic tiering algorithm, and documenting lifecycle-specific risks. The application aims to facilitate responsible AI development and operations by offering clear visibility, structured risk assessment, and traceable evidence generation for audit and compliance purposes.

## Features

This application offers the following core functionalities:

### 1. AI System Inventory Management
*   **Create New Systems**: Register new AI systems with comprehensive metadata including name, description, domain, AI type, owner, deployment mode, decision criticality, automation level, data sensitivity, and external dependencies.
*   **View Inventory**: Display a tabular overview of all registered AI systems.
*   **Edit Systems**: Modify the details of existing AI systems.
*   **Delete Systems**: Remove AI systems from the inventory.
*   **Load Sample Data**: Quickly populate the inventory with predefined sample AI systems for testing and demonstration.

### 2. Deterministic Risk Tiering
*   **Automated Tier Calculation**: Compute an inherent risk tier (Tier 1: High, Tier 2: Medium, Tier 3: Low) for any selected AI system based on a deterministic scoring algorithm that considers various system attributes.
*   **Score Breakdown**: View a detailed breakdown of how points are assigned for each dimension contributing to the total risk score.
*   **Justification & Controls**: Document a justification for the assigned risk tier and specify required controls directly within the application.
*   **Persistence**: Save and retrieve tiering results for each system.

### 3. Lifecycle Risk Register
*   **Risk Identification**: Document specific risks associated with an AI system across its lifecycle phases (e.g., Inception, Design, Development, Deployment, Monitoring, Decommissioning).
*   **Categorization**: Classify risks by various risk vectors (e.g., Functional, Performance, Security, Fairness, Explainability).
*   **Severity Calculation**: Automatically calculate risk severity based on user-defined impact and likelihood scores (Severity = Impact × Likelihood).
*   **Risk Details**: Record risk statements, mitigation strategies, and assign owner roles.
*   **Evidence Links**: Attach links to external evidence or documentation for each risk.
*   **Risk Matrix Visualization**: Generate and display a matrix showing the distribution of risks across lifecycle phases and risk vectors, providing a quick overview of risk concentrations.
*   **CRUD Operations**: Add, view, edit, and delete lifecycle risk entries for a selected system.

### 4. Exports & Evidence Package Generation
*   **Traceable Evidence**: Generate a formal, auditable evidence package in a ZIP archive.
*   **Immutable Records**: The package includes a manifest with SHA-256 hashes of all generated artifacts (system metadata, tiering results, risk entries) to ensure data integrity and traceability.
*   **User/Team Attribution**: Record the team or user generating the evidence package.

### General Application Features
*   **Streamlit UI**: Intuitive and interactive web interface built with Streamlit.
*   **Session Management**: Persists user selections and form states across interactions.
*   **Embedded Database**: Uses SQLite for data storage, simplifying setup and deployment for a lab environment.
*   **Pydantic Data Models**: Robust data validation and serialization using Pydantic v2.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   **Python 3.8+**: The application is developed with Python.
*   **pip**: Python package installer (usually comes with Python).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    *(Replace `your-username/your-repo-name.git` with the actual repository URL)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    The application relies on several Python libraries. You'll need a `requirements.txt` file for this step.
    Create a `requirements.txt` in your project root with the following content:
    ```
    streamlit
    pandas
    pydantic==2.*
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ensure `source.py` exists:**
    The provided `app.py` imports models and functions from `source.py`. Make sure `source.py` is present in the same directory as `app.py` and contains all the necessary Pydantic models (`SystemMetadata`, `LifecycleRiskEntry`, `TieringResult`, etc.), Enums (`AIType`, `LifecyclePhase`, `RiskVector`, `DeploymentMode`, `DecisionCriticality`, `AutomationLevel`, `DataSensitivity`, `RiskTier`, `Severity`), database connection functions (`get_db_connection`, `create_tables`), and CRUD operations (`add_system`, `get_all_systems`, `update_system`, `delete_system`, `get_tiering_result`, `save_tiering_result`, `calculate_risk_tier`, `generate_risk_matrix`, `generate_evidence_package`, etc.).

    For example, `source.py` would contain code similar to this (conceptual structure):
    ```python
    # source.py
    import sqlite3
    import uuid
    from datetime import datetime
    from enum import Enum
    from typing import List, Dict, Any, Optional
    from pydantic import BaseModel, Field, UUID4, validator

    # --- Enums ---
    class AIType(str, Enum):
        ML = "Machine Learning"
        DL = "Deep Learning"
        NLP = "Natural Language Processing"
        CV = "Computer Vision"
        GEN_AI = "Generative AI"
        ...

    # ... other enums ...

    # --- Pydantic Models ---
    class SystemMetadata(BaseModel):
        system_id: UUID4 = Field(default_factory=uuid.uuid4)
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
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)

        @validator('updated_at', pre=True, always=True)
        def set_updated_at(cls, v, values):
            return v or datetime.now()
        
        # ... other validators or methods ...

    class LifecycleRiskEntry(BaseModel):
        risk_id: UUID4 = Field(default_factory=uuid.uuid4)
        system_id: UUID4
        lifecycle_phase: LifecyclePhase
        risk_vector: RiskVector
        risk_statement: str
        impact: int = Field(..., ge=1, le=5)
        likelihood: int = Field(..., ge=1, le=5)
        severity: int = Field(0) # Calculated
        mitigation: str
        owner_role: str
        evidence_links: List[str] = Field(default_factory=list)
        created_at: datetime = Field(default_factory=datetime.now)

        def model_post_init(self, __context: Any) -> None:
            self.severity = self.impact * self.likelihood

        # ... other methods ...

    class TieringResult(BaseModel):
        result_id: UUID4 = Field(default_factory=uuid.uuid4)
        system_id: UUID4
        risk_tier: RiskTier
        total_score: int
        score_breakdown: Dict[str, int]
        justification: str = ""
        required_controls: List[str] = Field(default_factory=list)
        computed_at: datetime = Field(default_factory=datetime.now)
    
    class EvidencePackageMetadata(BaseModel):
        package_id: UUID4 = Field(default_factory=uuid.uuid4)
        package_name: str
        generated_by: str
        timestamp: datetime
        manifest_path: str
        zip_path: str

    # --- Database Functions ---
    DATABASE_NAME = "data.db"

    def get_db_connection():
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        return conn

    def create_tables():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS systems (
                system_id TEXT PRIMARY KEY,
                json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tiering_results (
                result_id TEXT PRIMARY KEY,
                system_id TEXT NOT NULL,
                json TEXT NOT NULL,
                computed_at TEXT NOT NULL,
                FOREIGN KEY (system_id) REFERENCES systems (system_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lifecycle_risks (
                risk_id TEXT PRIMARY KEY,
                system_id TEXT NOT NULL,
                json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (system_id) REFERENCES systems (system_id)
            )
        ''')
        conn.commit()
        conn.close()

    # --- CRUD Functions for SystemMetadata ---
    def add_system(system: SystemMetadata):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO systems (system_id, json, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (str(system.system_id), system.model_dump_json(), system.created_at.isoformat(), system.updated_at.isoformat())
        )
        conn.commit()
        conn.close()

    def get_all_systems() -> List[SystemMetadata]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT json FROM systems")
        rows = cursor.fetchall()
        conn.close()
        return [SystemMetadata.model_validate_json(row['json']) for row in rows]

    def get_system(system_id: uuid.UUID) -> Optional[SystemMetadata]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT json FROM systems WHERE system_id = ?", (str(system_id),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return SystemMetadata.model_validate_json(row['json'])
        return None

    def update_system(system_id: uuid.UUID, updates: Dict[str, Any]):
        current_system = get_system(system_id)
        if not current_system:
            raise ValueError(f"System with ID {system_id} not found.")

        updated_data = current_system.model_dump()
        for k, v in updates.items():
            if k in ['ai_type', 'deployment_mode', 'decision_criticality', 'automation_level', 'data_sensitivity']:
                # Convert string representation back to Enum member
                enum_type = {
                    'ai_type': AIType,
                    'deployment_mode': DeploymentMode,
                    'decision_criticality': DecisionCriticality,
                    'automation_level': AutomationLevel,
                    'data_sensitivity': DataSensitivity
                }[k]
                updated_data[k] = enum_type(v)
            else:
                updated_data[k] = v
        
        updated_data['updated_at'] = datetime.now() # Update timestamp

        updated_system = SystemMetadata(**updated_data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE systems SET json = ?, updated_at = ? WHERE system_id = ?",
            (updated_system.model_dump_json(), updated_system.updated_at.isoformat(), str(system_id))
        )
        conn.commit()
        conn.close()

    def delete_system(system_id: uuid.UUID):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM systems WHERE system_id = ?", (str(system_id),))
        # Also delete associated tiering results and lifecycle risks
        cursor.execute("DELETE FROM tiering_results WHERE system_id = ?", (str(system_id),))
        cursor.execute("DELETE FROM lifecycle_risks WHERE system_id = ?", (str(system_id),))
        conn.commit()
        conn.close()

    # --- Sample Data Loading ---
    def load_sample_systems_data():
        systems_to_add = [
            SystemMetadata(name="Fraud Detection Engine v2", description="Identifies fraudulent transactions in real-time using ML models.", domain="Finance", ai_type=AIType.ML, owner_role="Head of Risk Management", deployment_mode=DeploymentMode.PRODUCTION_EXTERNAL, decision_criticality=DecisionCriticality.HIGH, automation_level=AutomationLevel.AUTOMATED, data_sensitivity=DataSensitivity.CONFIDENTIAL),
            SystemMetadata(name="Customer Service Chatbot", description="AI-powered chatbot for first-level customer support inquiries.", domain="Customer Service", ai_type=AIType.NLP, owner_role="VP Customer Experience", deployment_mode=DeploymentMode.PRODUCTION_EXTERNAL, decision_criticality=DecisionCriticality.MEDIUM, automation_level=AutomationLevel.ADVISORY, data_sensitivity=DataSensitivity.PII),
            SystemMetadata(name="Inventory Optimization Tool", description="Predicts demand and optimizes inventory levels for retail stores.", domain="Supply Chain", ai_type=AIType.ML, owner_role="Supply Chain Director", deployment_mode=DeploymentMode.INTERNAL_ONLY, decision_criticality=DecisionCriticality.LOW, automation_level=AutomationLevel.AUTOMATED, data_sensitivity=DataSensitivity.INTERNAL_ONLY),
        ]
        conn = get_db_connection()
        cursor = conn.cursor()
        for sys_data in systems_to_add:
            # Check if system with same name already exists to prevent duplicates on rerun
            cursor.execute("SELECT system_id FROM systems WHERE json LIKE ?", (f'%\"name\": \"{sys_data.name}\"%',))
            if not cursor.fetchone():
                add_system(sys_data)
        conn.close()

    # --- Tiering Functions ---
    def calculate_risk_tier(system: SystemMetadata) -> TieringResult:
        score_breakdown = {}
        total_score = 0

        # Example scoring logic (simplify for README)
        score_breakdown['Decision Criticality'] = system.decision_criticality.value_points
        score_breakdown['Automation Level'] = system.automation_level.value_points
        score_breakdown['Data Sensitivity'] = system.data_sensitivity.value_points
        score_breakdown['Deployment Mode'] = system.deployment_mode.value_points
        
        # Add points for specific AI types if desired
        if system.ai_type == AIType.GEN_AI:
            score_breakdown['AI Type (Generative)'] = 5
        elif system.ai_type == AIType.DL:
            score_breakdown['AI Type (Deep Learning)'] = 3
        
        # Consider external dependencies as a risk factor
        if system.external_dependencies:
            score_breakdown['External Dependencies'] = len(system.external_dependencies) * 2 # 2 points per dependency
        
        total_score = sum(score_breakdown.values())

        # Determine tier based on total_score
        if total_score >= 20: # Example thresholds
            risk_tier = RiskTier.TIER_1
        elif total_score >= 10:
            risk_tier = RiskTier.TIER_2
        else:
            risk_tier = RiskTier.TIER_3
        
        return TieringResult(
            system_id=system.system_id,
            risk_tier=risk_tier,
            total_score=total_score,
            score_breakdown=score_breakdown,
            justification=f"Deterministic calculation based on system attributes. Total score: {total_score}",
            required_controls=[]
        )

    def save_tiering_result(result: TieringResult):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if a result already exists for this system_id and update, otherwise insert
        cursor.execute("SELECT result_id FROM tiering_results WHERE system_id = ?", (str(result.system_id),))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE tiering_results SET json = ?, computed_at = ? WHERE system_id = ?",
                (result.model_dump_json(), result.computed_at.isoformat(), str(result.system_id))
            )
        else:
            cursor.execute(
                "INSERT INTO tiering_results (result_id, system_id, json, computed_at) VALUES (?, ?, ?, ?)",
                (str(result.result_id), str(result.system_id), result.model_dump_json(), result.computed_at.isoformat())
            )
        conn.commit()
        conn.close()

    def get_tiering_result(system_id: uuid.UUID) -> Optional[TieringResult]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT json FROM tiering_results WHERE system_id = ?", (str(system_id),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return TieringResult.model_validate_json(row['json'])
        return None

    # --- Risk Matrix Generation ---
    import pandas as pd
    def generate_risk_matrix(system_id: uuid.UUID) -> pd.DataFrame:
        risks = get_risks_for_system(system_id)
        if not risks:
            return pd.DataFrame()

        phases = [e.value for e in LifecyclePhase]
        vectors = [e.value for e in RiskVector]
        
        matrix_data = {v: [''] * len(phases) for v in vectors}
        
        for risk in risks:
            phase_idx = phases.index(risk.lifecycle_phase.value)
            vector_name = risk.risk_vector.value
            
            current_entry = matrix_data[vector_name][phase_idx]
            if current_entry:
                matrix_data[vector_name][phase_idx] += f"; {risk.risk_statement[:50]} (Sev: {risk.severity})"
            else:
                matrix_data[vector_name][phase_idx] = f"{risk.risk_statement[:50]} (Sev: {risk.severity})"
        
        df = pd.DataFrame(matrix_data, index=phases)
        df.index.name = "Lifecycle Phase"
        return df

    # --- Evidence Package Generation ---
    import zipfile
    import hashlib
    import json
    import os

    def generate_evidence_package(project_id: str, generated_by: str) -> str:
        output_dir = "evidence_packages"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"{project_id}_evidence_{timestamp}"
        zip_filepath = os.path.join(output_dir, f"{package_name}.zip")
        manifest_filepath = os.path.join(output_dir, f"{package_name}_manifest.json")

        manifest = {
            "package_id": str(uuid.uuid4()),
            "package_name": package_name,
            "generated_by": generated_by,
            "timestamp": datetime.now().isoformat(),
            "artifacts": []
        }

        temp_dir = os.path.join(output_dir, "temp_artifacts")
        os.makedirs(temp_dir, exist_ok=True)

        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Systems Data
            all_systems = get_all_systems()
            systems_data = [s.model_dump_json() for s in all_systems]
            systems_json_path = os.path.join(temp_dir, "ai_systems_inventory.json")
            with open(systems_json_path, 'w') as f:
                json.dump(systems_data, f, indent=4)
            
            with open(systems_json_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            zipf.write(systems_json_path, os.path.basename(systems_json_path))
            manifest["artifacts"].append({"filename": os.path.basename(systems_json_path), "sha256": file_hash, "type": "AI Systems Inventory"})

            # Add Tiering Results and Lifecycle Risks per System
            for system in all_systems:
                # Tiering Result
                tier_result = get_tiering_result(system.system_id)
                if tier_result:
                    tier_json_path = os.path.join(temp_dir, f"tiering_result_{system.name.replace(' ', '_')}.json")
                    with open(tier_json_path, 'w') as f:
                        f.write(tier_result.model_dump_json(indent=4))
                    with open(tier_json_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    zipf.write(tier_json_path, os.path.basename(tier_json_path))
                    manifest["artifacts"].append({"filename": os.path.basename(tier_json_path), "sha256": file_hash, "type": f"Tiering Result for {system.name}"})
                
                # Lifecycle Risks
                risks = get_risks_for_system(system.system_id)
                if risks:
                    risks_data = [r.model_dump_json() for r in risks]
                    risks_json_path = os.path.join(temp_dir, f"lifecycle_risks_{system.name.replace(' ', '_')}.json")
                    with open(risks_json_path, 'w') as f:
                        json.dump(risks_data, f, indent=4)
                    with open(risks_json_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    zipf.write(risks_json_path, os.path.basename(risks_json_path))
                    manifest["artifacts"].append({"filename": os.path.basename(risks_json_path), "sha256": file_hash, "type": f"Lifecycle Risks for {system.name}"})
            
            # Add Manifest itself
            with open(manifest_filepath, 'w') as f:
                json.dump(manifest, f, indent=4)
            with open(manifest_filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            zipf.write(manifest_filepath, os.path.basename(manifest_filepath))
            manifest["artifacts"].append({"filename": os.path.basename(manifest_filepath), "sha256": file_hash, "type": "Evidence Package Manifest"})

        # Clean up temporary files
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)

        return zip_filepath
    ```
    *(Note: The above `source.py` example is a conceptual outline. You would need to fill in all the enum definitions with their `value_points` properties, and ensure all model fields, validators, and helper functions are fully implemented as needed by `app.py`.)*

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
2.  **Access the application:**
    Your default web browser should automatically open to `http://localhost:8501`. If not, navigate there manually.
3.  **Initial Setup:**
    *   On the first run, the database tables (`systems`, `tiering_results`, `lifecycle_risks`) will be created automatically.
    *   You can start by clicking "Load Sample Systems" on the "Inventory Management" page to populate the application with some initial data.
4.  **Navigation:**
    *   Use the sidebar on the left to navigate between "Inventory Management", "Risk Tiering", "Lifecycle Risk Register", and "Exports & Evidence".
    *   The "Selected AI System" dropdown in the sidebar allows you to quickly switch context to a specific system across different pages (except for "Inventory Management" where systems are managed).
5.  **Explore Features:**
    *   **Inventory Management**: Add, edit, or delete AI systems.
    *   **Risk Tiering**: Select a system, compute its risk tier, and add justifications/controls.
    *   **Lifecycle Risk Register**: Select a system, then add new risks, view existing ones, edit them, or delete them. Observe the dynamically generated Risk Matrix.
    *   **Exports & Evidence**: Enter a user name and generate a downloadable ZIP file containing an auditable package of all your AI systems and their risk data.

## Project Structure

```
.
├── app.py                      # Main Streamlit application file
├── source.py                   # Contains Pydantic models, Enums, database functions,
|                               # CRUD operations, and core business logic (tiering, matrix, evidence).
├── requirements.txt            # List of Python dependencies
├── data/                       # Directory for storing application data
│   └── data.db                 # SQLite database file
│   └── evidence_packages/      # Directory for generated evidence package ZIPs and manifests
├── README.md                   # This file
└── .gitignore                  # Git ignore file (optional but recommended)
```

## Technology Stack

*   **Frontend / Web Framework**: [Streamlit](https://streamlit.io/)
*   **Backend / Logic**: [Python 3.8+](https://www.python.org/)
*   **Data Modeling & Validation**: [Pydantic v2](https://pydantic.dev/)
*   **Database**: [SQLite](https://www.sqlite.org/index.html) (embedded, file-based)
*   **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
*   **Other Libraries**:
    *   `uuid`: For generating unique identifiers.
    *   `datetime`: For handling timestamps.
    *   `json`: For serializing/deserializing Pydantic models to/from JSON.
    *   `os`: For file system operations.
    *   `hashlib`: For generating SHA-256 hashes for evidence packages.
    *   `zipfile`: For creating compressed archive files.

## Contributing

Contributions are welcome! If you have suggestions for improvements or encounter any issues, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`).
3.  Commit your changes (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
*(Note: You will need to create a `LICENSE` file in your repository if you haven't already.)*

## Contact

For questions, feedback, or further information, please reach out to:

*   **QuantUniversity Labs**
*   **Project Lead**: [Alex (AI Product Engineer)]
*   **GitHub**: [https://github.com/your-username/your-repo-name](https://github.com/your-username/your-repo-name) *(Replace with actual link)*
*   **LinkedIn**: [Link to your LinkedIn profile (optional)]

---