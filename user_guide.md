id: 6966a237c45cd9e54065d14c_user_guide
summary: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Enterprise AI Inventory, Risk Tiering, & Lifecycle Risk Map

## 1. Introduction to QuLab: Your AI Governance Hub
Duration: 00:05:00

Welcome to **QuLab**, your comprehensive solution for managing and governing AI systems within an enterprise. As an AI Product Engineer, you play a crucial role in ensuring that AI systems are not only innovative but also responsible, compliant, and well-managed throughout their lifecycle. QuLab is designed to be your single source of truth for achieving these goals.

<aside class="positive">
This codelab will guide you, acting as **Alex, the AI Product Engineer**, through QuLab's core functionalities. You'll learn how to inventory AI systems, assess their inherent risks, manage risks across their lifecycle, and generate essential evidence for audit and compliance.
</aside>

**Why is this application important?**

In today's rapidly evolving AI landscape, organizations face increasing pressure to understand, control, and demonstrate accountability for their AI deployments. QuLab addresses key challenges by:

*   **Centralized Inventory:** Providing a clear, up-to-date registry of all AI systems.
*   **Objective Risk Assessment:** Utilizing a deterministic approach to tier AI systems based on inherent risk factors.
*   **Proactive Risk Management:** Enabling identification, tracking, and mitigation of risks throughout an AI system's operational lifecycle.
*   **Audit Readiness:** Facilitating the generation of traceable evidence packages for regulatory compliance and internal governance.

By the end of this codelab, you will have a solid understanding of how to leverage QuLab to drive responsible AI adoption and robust governance within your organization.

## 2. Navigating QuLab and Initial Setup
Duration: 00:03:00

Upon launching QuLab, you'll see a clean, intuitive interface designed for efficiency. The application is divided into several key sections, accessible via the sidebar navigation.

1.  **Sidebar Navigation:**
    On the left side of the screen, you'll find the navigation panel. This is where you switch between different core functionalities of QuLab. The available sections are:
    *   **Inventory Management:** To add, view, edit, and delete AI systems.
    *   **Risk Tiering:** To assess the inherent risk level of an AI system.
    *   **Lifecycle Risk Register:** To manage specific risks associated with an AI system over its operational lifetime.
    *   **Exports & Evidence:** To generate audit-ready evidence packages.

2.  **Selected AI System:**
    Below the main navigation, there's a section for "Selected AI System". This area will display the name and a short description of the AI system you are currently focusing on. Many functionalities, such as Risk Tiering and Lifecycle Risk Register, operate on the currently selected system.

3.  **Loading Sample Data (Recommended):**
    To quickly get started and explore the features without manually entering data, let's load some sample AI systems.

    *   Navigate to the **Inventory Management** section using the sidebar.
    *   Look for the "Load Sample Systems" button and click it.
    *   You will see a success message, and the "Current Inventory" table will populate with example AI systems.

    <aside class="positive">
    Loading sample data is a great way to familiarize yourself with the application before you start inputting your own enterprise data. It provides ready-made examples for tiering and risk management.
    </aside>

    Now that you have sample systems, you can select any of them from the "Selected AI System" dropdown in the sidebar to view its details across different sections.

## 3. Managing Your AI System Inventory
Duration: 00:10:00

The "Inventory Management" section is your central hub for all AI systems in your organization. As Alex, it's crucial to keep this inventory accurate and complete.

### 3.1. Viewing Current Inventory

*   Once you've loaded sample systems (or added your own), the "Current Inventory" table will display a summary of all registered AI systems.
*   Each row represents an AI system, showing key attributes like Name, Domain, AI Type, Owner Role, Decision Criticality, and when it was last updated.

### 3.2. Adding a New AI System

Let's imagine your team is deploying a new AI system and you need to register it in QuLab.

1.  Click the "Add New System" button.
2.  A form titled "Add New AI System" will appear.
3.  Fill in the details for your new AI system. Pay attention to the following fields, as they are crucial for subsequent risk assessments:
    *   **Name & Description:** Basic identification.
    *   **Domain & Owner Role:** Organizational context.
    *   **AI Type:** What kind of AI is it (e.g., Machine Learning, Generative AI)?
    *   **Deployment Mode:** Where is it deployed (e.g., internal, external)?
    *   **Decision Criticality:** How critical are the decisions made by this AI (e.g., Low, Medium, High, Life-Critical)?
    *   **Automation Level:** What level of human oversight does it have (e.g., Advisory, Semi-Autonomous, Fully Autonomous)?
    *   **Data Sensitivity:** What kind of data does it process (e.g., Public, Confidential, Restricted, Sensitive)?
    *   **External Dependencies:** Any other systems or data sources it relies on.
4.  Once all fields are filled, click "Save System".
5.  You'll see a success message, and the new system will appear in the "Current Inventory" table.

<aside class="positive">
The values chosen for **Decision Criticality**, **Automation Level**, and **Data Sensitivity** are particularly important, as they directly influence the system's inherent risk tier later in the "Risk Tiering" section.
</aside>

### 3.3. Editing an Existing AI System

Suppose an existing AI system's ownership changes, or its deployment mode is updated.

1.  From the "Current Inventory" section, use the "Select System to Edit/Delete" dropdown to choose the system you wish to modify.
2.  Click the "Edit Selected" button.
3.  The "Edit System" form will appear, pre-populated with the system's current details.
4.  Make the necessary changes.
5.  Click "Save System". The inventory will update with your modifications.

### 3.4. Deleting an AI System

If an AI system is decommissioned or no longer in use, you can remove it from the inventory.

1.  From the "Current Inventory" section, use the "Select System to Edit/Delete" dropdown to choose the system.
2.  Click the "Delete Selected" button.
3.  Confirm the deletion. The system will be removed from the inventory.

## 4. Understanding Deterministic Risk Tiering
Duration: 00:08:00

The "Risk Tiering" section allows Alex to determine the inherent risk tier for a selected AI system. QuLab employs a **deterministic tiering algorithm** to classify AI systems objectively into Tier 1 (High Risk), Tier 2 (Medium Risk), or Tier 3 (Low Risk).

### 4.1. Selecting a System for Tiering

*   First, ensure you have a system selected in the sidebar's "Selected AI System" dropdown. If not, go back to "Inventory Management" or "Load Sample Systems", then select a system.
*   Once a system is selected, navigate to the "Risk Tiering" section. You'll see the name of the selected system at the top.

### 4.2. The Tiering Algorithm Concept

The core idea is to assign numerical points to different attributes of an AI system (like its criticality, automation level, and data sensitivity). The sum of these points ($S$) determines the final risk tier.

$$S = \sum_{d \in D} \text{points}(d)$$

Where $D$ is the set of relevant risk dimensions (e.g., Decision Criticality, Automation Level, Data Sensitivity), and $\text{points}(d)$ is the score assigned to the system's characteristic within that dimension. A higher total score indicates a higher inherent risk.

### 4.3. Computing the Risk Tier

1.  With your desired AI system selected, click the "Compute Risk Tier" button.
2.  QuLab will run the deterministic algorithm based on the system's attributes you entered in the inventory.
3.  A success message will confirm that the tier has been calculated and saved. The page will then update to show the result.

### 4.4. Interpreting the Tiering Result

After computation, you'll see:

*   **Risk Tier:** The assigned tier (e.g., "Tier 1: High Risk", "Tier 2: Medium Risk").
*   **Total Score:** The calculated score $S$ that led to this tier.
*   **Score Breakdown:** A table showing how points were assigned for each dimension (e.g., Decision Criticality, Automation Level, Data Sensitivity). This provides transparency into *why* a particular tier was assigned.

### 4.5. Adding Justification and Controls

Below the tiering result, you'll find a form to add important context:

*   **Justification:** This field is for Alex to provide a narrative explaining why this tier is appropriate or any specific considerations.
*   **Required Controls:** Here, you can list the necessary controls or safeguards that should be implemented for systems of this risk tier (one per line).

1.  Enter your justification and list the required controls.
2.  Click "Save Changes to Tiering Result" to record this information.

<aside class="negative">
Remember, the deterministic risk tiering provides an **inherent** risk assessment. It's crucial to document **required controls** to manage this inherent risk, which moves toward a **residual** risk understanding.
</aside>

## 5. Managing Lifecycle Risks
Duration: 00:12:00

The "Lifecycle Risk Register" allows Alex to identify, document, and manage specific risks that emerge at various stages of an AI system's lifecycle. Each risk is categorized by its lifecycle phase and risk vector, and its severity is calculated.

### 5.1. Selecting a System for Risk Management

*   As with Risk Tiering, ensure you have an AI system selected in the sidebar.
*   Navigate to the "Lifecycle Risk Register" section.

### 5.2. Understanding Risk Severity

QuLab calculates risk severity based on two key factors: Impact and Likelihood.

$$\text{Severity} = \text{Impact} \times \text{Likelihood}$$

*   **Impact:** How severe would the consequences be if the risk materializes (on a scale of 1=Low to 5=High)?
*   **Likelihood:** How probable is it that the risk will occur (on a scale of 1=Rare to 5=Frequent)?

The severity score helps prioritize risks, with higher scores indicating more critical risks.

### 5.3. Adding a New Lifecycle Risk

1.  Click the "Add New Risk" button.
2.  A form will appear for adding a new risk entry.
3.  Fill in the details:
    *   **Lifecycle Phase:** At which stage of the AI system's life does this risk apply (e.g., Inception, Design, Development, Deployment, Monitoring, Decommissioning)?
    *   **Risk Vector:** What is the nature of this risk (e.g., Functional, Security, Privacy, Explainability, Fairness, Robustness)?
    *   **Impact (1-5) & Likelihood (1-5):** Use the sliders to rate these. Notice the "Calculated Severity" updates dynamically.
    *   **Risk Owner Role:** Who is responsible for managing this risk?
    *   **Risk Statement:** A clear description of the risk.
    *   **Mitigation Strategy:** What actions are planned or in place to reduce this risk?
    *   **Evidence Links:** Any URLs or references to documentation supporting the risk or mitigation.
4.  Click "Save Risk". The new risk will appear in the "Existing Risks" table.

<aside class="positive">
Documenting risks across different lifecycle phases provides a holistic view, allowing you to anticipate and address challenges proactively rather than reactively.
</aside>

### 5.4. Viewing and Managing Existing Risks

*   The "Existing Risks" table lists all documented lifecycle risks for the currently selected AI system.
*   It provides an overview of the risk statement, phase, vector, impact, likelihood, calculated severity, owner, and mitigation strategy.

### 5.5. Editing or Deleting a Risk

1.  From the "Existing Risks" section, use the "Select a Risk to Edit or Delete" dropdown to choose the specific risk you want to modify or remove.
2.  Click "Edit Selected Risk" to open the form pre-filled with its details, make changes, and save.
3.  Click "Delete Selected Risk" to remove the risk from the register.

### 5.6. The Lifecycle Phase x Risk Vector Matrix

At the bottom of the section, you'll find a matrix that visually summarizes your risks.

*   This table cross-references "Lifecycle Phase" with "Risk Vector".
*   Each cell shows the count of risks for that specific combination. This provides a quick visual overview of where risks are concentrated within the system's lifecycle and by their nature. For example, you might see many "Privacy" risks in the "Development" phase.

## 6. Generating Traceable Evidence Package
Duration: 00:05:00

The "Exports & Evidence" section is where Alex prepares a formal, immutable evidence package for audit and compliance purposes. This package includes all registered AI systems and their associated risk data, secured with SHA-256 hashes for traceability.

### 6.1. The Importance of Evidence Packages

In a regulatory environment, demonstrating due diligence and accountability for AI systems is paramount. An evidence package:

*   **Provides an immutable record:** Cryptographic hashes ensure that the integrity of the data can be verified.
*   **Facilitates Audits:** Gathers all relevant information into a single, organized artifact.
*   **Enhances Trust:** Shows commitment to responsible AI governance.

The core concept is to create a hash of the artifacts (your data) to ensure no tampering has occurred:

$$\text{EvidenceHash} = \text{SHA256}(\text{Artifacts})$$

### 6.2. Generating and Downloading the Package

1.  First, ensure you have some AI systems and risk data entered in the previous sections. If not, the application will issue a warning.
2.  Enter your "Team/User Name" in the provided text input. This name will be included in the evidence package record.
3.  Click the "Generate Evidence Package" button.
4.  QuLab will process all your system inventory, risk tiering results, and lifecycle risk entries. It will compile them into a structured format and create a ZIP archive.
5.  Upon successful generation, you'll see a success message indicating the path where the package was created and a "Download Evidence Package (ZIP)" button.
6.  Click the "Download Evidence Package (ZIP)" button to save the `zip` file to your local machine.

<aside class="positive">
The generated package includes a manifest file. This manifest contains SHA-256 hashes of all individual files within the package, allowing auditors to verify the integrity and authenticity of the evidence provided.
</aside>

Congratulations! You have now completed the QuLab user guide. You can now confidently manage your enterprise AI inventory, assess risks, track them throughout the lifecycle, and generate crucial evidence for responsible AI governance.
