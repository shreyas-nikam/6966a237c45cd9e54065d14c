# Student Lab Guide
## Enterprise AI Risk Management System

---

## 📋 Case Study: Aperture Analytics Corp.

### Company Background

**Aperture Analytics Corp.** is a rapidly growing fintech startup that has experienced explosive growth over the past 18 months. What started as a small team of 15 people building credit risk models has now expanded to 200+ employees across multiple business units including:

- **Consumer Lending** - AI-powered credit decisioning systems
- **Fraud Detection** - Real-time transaction monitoring
- **Customer Service** - AI chatbots and recommendation engines
- **Operations** - Document processing and workflow automation
- **Marketing** - Predictive analytics and personalization engines

### The Challenge

As Aperture Analytics scaled, the company deployed AI systems at an unprecedented pace. Different teams built and launched AI models independently, each solving their own business problems. However, this rapid growth created significant challenges:

1. **No Central Visibility**: Leadership has no comprehensive view of what AI systems exist across the organization
2. **Regulatory Pressure**: The EU AI Act and other emerging regulations require systematic risk management of AI systems
3. **Compliance Gaps**: The upcoming Series C funding round requires demonstrating robust AI governance to investors
4. **Audit Readiness**: External auditors need traceable evidence of AI risk management practices
5. **Operational Risk**: Without proper oversight, the company faces potential model failures, bias incidents, and regulatory penalties

### The Board Meeting

Last month, the Board of Directors raised serious concerns after learning about a competitor's AI system failure that resulted in a $50M regulatory fine and significant reputational damage. The CEO tasked the Chief Risk Officer (CRO) with implementing a comprehensive AI risk management framework within 60 days.

The CRO immediately established an AI Governance team and hired **you** as the **AI Product Engineer** (Alex) to build and operationalize the company's first AI inventory and risk management system.

### Your Mission

As **Alex, the AI Product Engineer**, you are responsible for:

1. **Building the AI Inventory** - Create a single source of truth for all AI systems across the enterprise
2. **Implementing Risk Tiering** - Classify each AI system by inherent risk level using a deterministic algorithm
3. **Documenting Lifecycle Risks** - Identify and track risks across each system's development and deployment lifecycle
4. **Generating Audit Evidence** - Produce traceable, immutable records for compliance and audit purposes

The executive team is watching closely. Your success in implementing this system will determine whether Aperture Analytics can scale responsibly, secure its Series C funding, and maintain its competitive edge while managing AI risk.

**Today's lab session simulates your first 90 days on the job.** You'll work through the complete AI risk management lifecycle using the tools you've built for Aperture Analytics.

---

## 🎯 Lab Objectives

By the end of this lab, you will:

1. ✅ Build a comprehensive AI system inventory
2. ✅ Calculate deterministic risk tiers for AI systems
3. ✅ Document lifecycle risks across different phases
4. ✅ Generate traceable evidence packages for audit
5. ✅ Understand the operational workflow of enterprise AI governance

---

## 🚀 Getting Started

### Prerequisites

- Access to the Streamlit application (provided by your instructor)
- Basic understanding of AI/ML concepts
- Familiarity with risk management terminology

### Accessing the Application

1. Open your web browser
2. Navigate to the URL provided by your instructor
3. You should see the main dashboard: **"QuLab: Enterprise AI Inventory + Risk Tiering + Lifecycle Risk Map"**

### Interface Overview

The application has **four main sections** accessible from the left sidebar:

1. **Inventory Management** - Add, view, edit, and delete AI systems
2. **Risk Tiering** - Calculate risk tiers using a deterministic algorithm
3. **Lifecycle Risk Register** - Document risks across the AI lifecycle
4. **Exports & Evidence** - Generate audit-ready evidence packages

---

## 📖 Part 1: Building the AI Inventory

### Scenario Context

It's your first week at Aperture Analytics. The CRO has asked you to interview business unit leaders and document all existing AI systems. You've scheduled meetings with:

- **Sarah (VP of Lending)** - Runs the credit decisioning platform
- **Marcus (Head of Fraud)** - Manages real-time fraud detection
- **Priya (Customer Experience Lead)** - Oversees the AI chatbot

Your job is to translate these conversations into structured inventory records.

---

### Exercise 1.1: Add Your First AI System - Credit Decisioning Platform

**Background**: You just finished your meeting with Sarah. She explained that the lending team built an automated credit approval system that processes 10,000+ loan applications daily. The system makes high-stakes decisions with minimal human oversight and uses sensitive financial data.

**Instructions**:

1. Navigate to **Inventory Management** from the sidebar
2. Click on the **➕ Add** tab
3. Fill in the following information:

   **Basic Information**:
   - **Name**: `Credit Approval System`
   - **Domain**: `Consumer Lending`
   - **Owner Role**: `VP of Lending Operations`
   - **Description**: `Automated credit decisioning system that evaluates loan applications using machine learning models to predict default risk and determine approval decisions`

   **Technical Characteristics**:
   - **AI Type**: Select `Predictive Model`
   - **Deployment Mode**: Select `Production`
   - **Decision Criticality**: Select `High` (affects people's access to credit)
   - **Automation Level**: Select `Fully Automated` (no human in the loop)
   - **Data Sensitivity**: Select `Highly Sensitive` (uses personal financial data)
   - **External Dependencies**: `Equifax API, Experian API, AWS SageMaker`

4. Click **Add System**
5. Verify the success message appears

**✅ Checkpoint**: Navigate to the **📋 View** tab and confirm your system appears in the inventory table.

---

### Exercise 1.2: Add the Fraud Detection System

**Background**: Marcus described their real-time fraud detection system that monitors every transaction across the platform. It flags suspicious activity and can automatically block transactions above a certain risk threshold.

**Instructions**:

1. Stay in **Inventory Management** section
2. Click the **➕ Add** tab
3. Add the following system:

   - **Name**: `Real-Time Fraud Monitor`
   - **Domain**: `Fraud Prevention`
   - **Owner Role**: `Head of Risk & Security`
   - **Description**: `ML-based transaction monitoring system that detects fraudulent patterns in real-time and automatically blocks high-risk transactions`
   - **AI Type**: `Anomaly Detection`
   - **Deployment Mode**: `Production`
   - **Decision Criticality**: `High` (false positives harm customers, false negatives cost money)
   - **Automation Level**: `Human in the Loop` (analysts review flagged transactions)
   - **Data Sensitivity**: `Highly Sensitive` (transaction data, user behavior)
   - **External Dependencies**: `Stripe API, DataDog, Redis Cache`

4. Click **Add System**

---

### Exercise 1.3: Add the Customer Service Chatbot

**Background**: Priya's team launched an AI chatbot six months ago that handles 70% of customer inquiries. It provides product recommendations and account information but always offers to escalate to human agents.

**Instructions**:

1. Add a third system with these details:

   - **Name**: `Customer Service AI Assistant`
   - **Domain**: `Customer Experience`
   - **Owner Role**: `Customer Experience Team`
   - **Description**: `Conversational AI chatbot that handles customer inquiries, provides product recommendations, and assists with account information requests`
   - **AI Type**: `Generative AI`
   - **Deployment Mode**: `Production`
   - **Decision Criticality**: `Medium` (impacts customer experience but not critical decisions)
   - **Automation Level**: `Assisted` (AI suggests, human can override)
   - **Data Sensitivity**: `Moderate` (customer inquiries, account data)
   - **External Dependencies**: `OpenAI API, Zendesk, PostgreSQL`

2. Click **Add System**

**✅ Checkpoint**: You should now have **3 AI systems** in your inventory. Check the **📋 View** tab to confirm.

---

### Exercise 1.4: Edit an Existing System

**Scenario**: You just received an email from Sarah (VP of Lending). She mentioned that the Credit Approval System now also uses the TransUnion API, which was added last month. You need to update the inventory.

**Instructions**:

1. Navigate to the **✏️ Edit** tab in Inventory Management
2. Select **Credit Approval System** from the dropdown
3. Find the **External Dependencies** field
4. Update it to: `Equifax API, Experian API, TransUnion API, AWS SageMaker`
5. Click **Update System**
6. Verify the success message

**💡 Insight**: In real enterprise environments, AI systems constantly evolve. Maintaining up-to-date inventory records is crucial for effective governance.

---

### Exercise 1.5: Review Your Complete Inventory

**Instructions**:

1. Go to the **📋 View** tab
2. Review the table showing all your registered systems
3. Observe the columns: name, domain, AI type, owner, decision criticality, and last update timestamp

**🤔 Reflection Questions** (discuss with your team):
- Which systems appear to have the highest inherent risk?
- What patterns do you notice across different domains?
- Why is "Decision Criticality" an important attribute?

---

## 📊 Part 2: Deterministic Risk Tiering

### Scenario Context

The CRO reviewed your inventory and was impressed by your thoroughness. Now comes the critical next step: **risk classification**. 

Aperture Analytics uses a **deterministic risk tiering algorithm** that objectively classifies AI systems into three tiers:

- **Tier 1 (High Risk)**: Systems requiring the most stringent controls and oversight
- **Tier 2 (Medium Risk)**: Systems needing moderate controls and regular review
- **Tier 3 (Low Risk)**: Systems with lighter-touch governance requirements

The algorithm calculates a **total risk score** based on multiple dimensions:
- AI Type
- Decision Criticality
- Automation Level
- Data Sensitivity
- Deployment Mode

**Formula**: $S = \sum_{d \in D} \text{points}(d)$

Each dimension contributes points to the total score, which is then compared to predefined thresholds to assign the tier.

---

### Exercise 2.1: Calculate Risk Tier for Credit Approval System

**Instructions**:

1. Navigate to **Risk Tiering** from the sidebar
2. Ensure **Credit Approval System** is selected in the sidebar system selector (it should auto-select if you added it first)
3. Click the **Compute Risk Tier** button
4. Wait for the calculation to complete
5. Review the results:
   - **Risk Tier** assignment (Tier 1, 2, or 3)
   - **Total Score** calculated
   - **Score Breakdown** table showing points from each dimension

**✅ Checkpoint**: What tier was the Credit Approval System assigned? Does this match your intuition?

---

### Exercise 2.2: Document Justification and Controls

**Scenario**: For audit purposes, every risk tier assignment must include written justification and a list of required controls.

**Instructions**:

1. After computing the risk tier, scroll down to the **Controls & Justification** section
2. In the **Justification** field, write:
   ```
   This system is classified as high risk due to its fully automated decision-making on credit applications affecting consumers' access to financial services. The system processes highly sensitive financial data and operates with minimal human oversight, creating significant potential for adverse impacts.
   ```

3. In the **Required Controls** field, add the following (one per line):
   ```
   Monthly bias testing and fairness audits
   Human review for applications above $50K
   Quarterly model performance validation
   Annual third-party model audit
   Explainability reports for all denials
   Incident response plan with 24hr SLA
   ```

4. Click **Save Changes to Tiering Result**
5. Confirm the success message

---

### Exercise 2.3: Calculate Risk Tiers for Remaining Systems

**Instructions**:

1. Use the **sidebar system selector** to switch to **Real-Time Fraud Monitor**
2. Click **Compute Risk Tier**
3. Review the results and compare to the Credit Approval System
4. Add appropriate justification and controls (use your judgment based on the system characteristics)
5. Switch to **Customer Service AI Assistant**
6. Repeat the process

**🤔 Discussion Questions**:
- How do the risk tiers differ across the three systems?
- Which dimensions contribute most to higher risk scores?
- Why might a Generative AI chatbot have different risk considerations than a predictive model?

---

## 🗺️ Part 3: Lifecycle Risk Register

### Scenario Context

Risk tiering tells you **what** level of inherent risk a system poses. The Lifecycle Risk Register helps you identify and track **specific risks** across the entire AI lifecycle.

At Aperture Analytics, every AI system must have documented risks across multiple lifecycle phases:

- **Design**: Requirements, use case definition, ethical considerations
- **Data**: Collection, quality, bias, privacy
- **Development**: Model selection, training, validation
- **Deployment**: Integration, monitoring, rollback procedures
- **Monitoring**: Performance drift, fairness metrics, incident detection

Each risk is categorized by **Risk Vector** (e.g., Bias, Privacy, Security, Performance, Compliance) and assigned:
- **Impact** (1-5): Severity of consequences if the risk materializes
- **Likelihood** (1-5): Probability the risk will occur
- **Severity** = Impact × Likelihood (calculated automatically)

---

### Exercise 3.1: Document a Data Bias Risk

**Scenario**: During your conversation with Sarah (VP of Lending), she mentioned that the Credit Approval System was trained primarily on historical loan data. You're concerned about potential bias, since historical lending practices may have discriminated against certain protected groups.

**Instructions**:

1. Navigate to **Lifecycle Risk Register** from the sidebar
2. Ensure **Credit Approval System** is selected in the sidebar
3. Click on the **➕ Add** tab
4. Fill in the risk form:

   - **Lifecycle Phase**: `Data`
   - **Risk Vector**: `Bias & Fairness`
   - **Impact**: `5` (could result in discriminatory lending practices)
   - **Likelihood**: `4` (historical data likely contains bias)
   - **Risk Statement**: `Training data reflects historical lending patterns that may contain systematic bias against protected classes, potentially resulting in discriminatory credit decisions`
   - **Owner Role**: `ML Engineering Lead`
   - **Mitigation Strategy**: `Conduct fairness audit using demographic parity and equalized odds metrics. Implement bias correction techniques. Establish monthly monitoring for disparate impact. Create appeals process for denied applicants.`
   - **Evidence Links**: `https://example.com/fairness-audit-q4-2025`

5. Click **Add Risk**
6. Verify success message

**✅ Checkpoint**: Navigate to the **📋 View** tab and confirm your risk appears in the register. Note the **Severity** score (should be 20 = 5×4).

---

### Exercise 3.2: Document a Model Performance Risk

**Scenario**: Marcus (Head of Fraud) mentioned that the fraud detection system occasionally generates false positives during holiday shopping seasons when transaction patterns change dramatically.

**Instructions**:

1. Switch to **Real-Time Fraud Monitor** using the sidebar selector
2. Navigate to the **➕ Add** tab in Lifecycle Risk Register
3. Add this risk:

   - **Lifecycle Phase**: `Monitoring`
   - **Risk Vector**: `Performance & Accuracy`
   - **Impact**: `4` (false positives harm customer experience and revenue)
   - **Likelihood**: `3` (happens during seasonal spikes)
   - **Risk Statement**: `Model performance degrades during high-volume periods and seasonal shopping events, leading to increased false positive rates that block legitimate customer transactions`
   - **Owner Role**: `Fraud Detection Team Lead`
   - **Mitigation Strategy**: `Implement adaptive thresholds during known high-traffic periods. Deploy automated retraining pipeline triggered by performance metrics. Establish 15-minute SLA for model rollback. Create escalation path for customer support.`
   - **Evidence Links**: `https://example.com/performance-dashboard`

4. Click **Add Risk**

---

### Exercise 3.3: Document a Privacy Risk

**Scenario**: The Customer Service AI Assistant accesses customer account information to answer questions. You're concerned about potential data exposure or privacy violations.

**Instructions**:

1. Switch to **Customer Service AI Assistant**
2. Add this risk to the register:

   - **Lifecycle Phase**: `Deployment`
   - **Risk Vector**: `Privacy & Data Protection`
   - **Impact**: `4` (potential PII exposure and regulatory violations)
   - **Likelihood**: `2` (access controls exist but vulnerabilities possible)
   - **Risk Statement**: `AI assistant may inadvertently expose sensitive customer information through unintended prompt patterns or fail to properly redact PII in conversation logs, creating privacy violations`
   - **Owner Role**: `Data Privacy Officer`
   - **Mitigation Strategy**: `Implement PII redaction in all logs. Deploy prompt filtering to prevent information leakage. Limit chatbot access to minimum necessary data fields. Conduct quarterly privacy impact assessments. Enable customer data deletion requests.`
   - **Evidence Links**: `https://example.com/privacy-controls`

3. Click **Add Risk**

**✅ Checkpoint**: Each system should now have at least one documented risk in its register.

---

### Exercise 3.4: Add Multiple Risks Across Lifecycle Phases

**Scenario**: You're building a comprehensive risk profile for the Credit Approval System. Add risks for other lifecycle phases.

**Instructions**: Add the following two additional risks for the **Credit Approval System**:

**Risk #1 - Compliance Risk**:
- **Lifecycle Phase**: `Design`
- **Risk Vector**: `Compliance & Legal`
- **Impact**: `5`
- **Likelihood**: `3`
- **Risk Statement**: `System may not comply with emerging AI regulations (EU AI Act, GDPR) regarding automated decision-making and right to explanation for credit denials`
- **Owner Role**: `Legal & Compliance Team`
- **Mitigation Strategy**: `Engage legal counsel for regulatory review. Implement explanation capabilities for all decisions. Document compliance controls. Establish regulatory change monitoring process.`
- **Evidence Links**: `https://example.com/legal-review`

**Risk #2 - Security Risk**:
- **Lifecycle Phase**: `Deployment`
- **Risk Vector**: `Security & Adversarial`
- **Impact**: `5`
- **Likelihood**: `2`
- **Risk Statement**: `Model could be vulnerable to adversarial attacks where malicious actors manipulate input features to receive fraudulent loan approvals`
- **Owner Role**: `Security Engineering Team`
- **Mitigation Strategy**: `Implement input validation and anomaly detection. Deploy adversarial robustness testing. Establish rate limiting and fraud detection on application submissions. Create security incident response plan.`
- **Evidence Links**: `https://example.com/security-audit`

**✅ Checkpoint**: Credit Approval System should now have **3 total risks** documented across Design, Data, and Deployment phases.

---

### Exercise 3.5: View the Risk Matrix

**Scenario**: The CRO wants a visual summary showing risk coverage across all lifecycle phases and risk vectors.

**Instructions**:

1. Ensure you're viewing the Lifecycle Risk Register for **Credit Approval System**
2. Click on the **📊 Matrix** tab
3. Observe the heatmap showing:
   - **Rows**: Lifecycle Phases (Design, Data, Development, Deployment, Monitoring)
   - **Columns**: Risk Vectors (Bias, Privacy, Security, Performance, Compliance, etc.)
   - **Cell Colors**: Indicate severity (darker = higher severity)

4. Repeat for the other two systems to see their risk profiles

**🤔 Discussion Questions**:
- Which lifecycle phase has the most risks documented?
- Are there any gaps in risk coverage that should be addressed?
- How does the risk profile differ between a predictive model and a generative AI system?

---

### Exercise 3.6: Edit an Existing Risk

**Scenario**: After implementing new monitoring dashboards, the likelihood of the fraud detection performance risk has decreased.

**Instructions**:

1. Switch to **Real-Time Fraud Monitor**
2. Navigate to the **✏️ Edit** tab
3. Select the **performance risk** you created earlier (about false positives during holiday seasons)
4. Change the **Likelihood** from `3` to `2`
5. Update the **Mitigation Strategy** to include: `IMPLEMENTED: Real-time performance dashboard with automated alerting. Reduced likelihood from 3 to 2.`
6. Click **Update Risk**
7. Note that the **Severity** automatically recalculates (should now be 8 = 4×2 instead of 12)

**💡 Insight**: Risk registers are living documents. As you implement controls and mitigations, risk levels should be updated to reflect the current state.

---

## 📦 Part 4: Generate Audit Evidence Package

### Scenario Context

**The Big Moment**: The Series C investors are conducting due diligence next week. The CFO and CRO need to provide auditors with a complete, traceable record of all AI systems, their risk tiers, and documented risks.

You need to generate an **Evidence Package** that includes:
1. **Complete AI System Inventory** (JSON)
2. **Risk Tiering Results** for all systems
3. **Lifecycle Risk Map** for all systems
4. **Model Inventory** (CSV format for auditors)
5. **Executive Summary** (Markdown report)
6. **Configuration Snapshot** (for reproducibility)
7. **Evidence Manifest** with SHA-256 hashes (cryptographic proof of integrity)

The SHA-256 hashes create an **immutable audit trail** - any tampering with the files can be detected by recomputing and comparing hashes.

**Formula**: $\text{EvidenceHash} = \text{SHA256}(\text{Artifacts})$

---

### Exercise 4.1: Generate the Evidence Package

**Instructions**:

1. Navigate to **Exports & Evidence** from the sidebar
2. In the **Team/User Name** field, enter: `Alex Chen - AI Product Engineer`
3. Click **Generate Evidence Package**
4. Wait for the process to complete (may take 10-20 seconds)
5. Observe the success message showing the case ID and export directory

**What Just Happened?**:
The system created a complete evidence package containing:
- All your inventory data
- All risk tier calculations
- All lifecycle risks
- Cryptographic hashes for integrity verification

---

### Exercise 4.2: Review the Executive Summary

**Instructions**:

1. After generation completes, click the **View/Download** buttons that appear
2. Open the **Executive Summary** (Markdown file)
3. Review the contents:
   - Systems count and breakdown by tier
   - Risk metrics and coverage
   - Compliance readiness indicators
   - Recommended actions

**✅ Checkpoint**: The executive summary should show:
- Total systems: 3
- Systems by tier (based on your earlier calculations)
- Total risks documented
- Timestamp and generator name

---

### Exercise 4.3: Examine the Evidence Manifest

**Scenario**: The auditors need to verify that the evidence package hasn't been tampered with.

**Instructions**:

1. Open/download the **Evidence Manifest** JSON file
2. Observe the structure:
   - List of artifacts (files)
   - SHA-256 hash for each file
   - File sizes and timestamps
   - Package metadata

**💡 Security Concept**: These hashes provide cryptographic proof. If anyone modifies even a single character in any file, the hash will change completely, proving tampering occurred.

**🤔 Discussion Question**: Why is immutability important for audit evidence in regulated industries?

---

### Exercise 4.4: Review the Model Inventory CSV

**Instructions**:

1. Open/download the **Model Inventory** CSV file
2. Notice it contains a tabular view of all AI systems with key attributes
3. This format is often required by auditors and regulators who prefer spreadsheets

**Purpose**: Different stakeholders need different formats. The evidence package provides multiple views of the same data for different audiences:
- **Technical teams**: JSON files
- **Auditors**: CSV spreadsheets  
- **Executives**: Markdown summaries

---

## 🎓 Part 5: Reflection and Discussion

### Scenario Conclusion

**90 Days Later...**

You've successfully implemented Aperture Analytics' AI risk management system. The Series C due diligence went smoothly - investors were impressed by the systematic approach to AI governance. The company closed its $150M funding round, with the lead investor specifically citing "mature AI risk management practices" as a key factor.

The CRO promoted you to **Senior AI Governance Engineer** and tasked you with:
- Scaling the system to cover 50+ additional AI systems across the company
- Implementing automated monitoring and alerting for risk thresholds
- Building integration with the company's existing GRC (Governance, Risk, Compliance) platform
- Training other teams on the AI risk management framework

Your work has positioned Aperture Analytics as an industry leader in responsible AI development.

---

### Key Takeaways

Through this lab, you've learned how to:

1. ✅ **Build a structured AI inventory** - The foundation of AI governance is knowing what systems exist and their characteristics

2. ✅ **Apply deterministic risk tiering** - Objective, reproducible risk classification enables proportional governance without bias or inconsistency

3. ✅ **Document lifecycle risks systematically** - Comprehensive risk identification across all phases of the AI lifecycle prevents blind spots

4. ✅ **Generate audit-ready evidence** - Traceable, immutable records satisfy regulatory requirements and investor due diligence

5. ✅ **Operationalize AI governance** - Governance isn't just policy documents - it requires systematic processes and tooling

---

### Real-World Applications

The patterns you practiced today are used by:

- **Financial institutions** implementing model risk management under SR 11-7
- **Healthcare organizations** managing AI medical devices under FDA regulations
- **Technology companies** preparing for EU AI Act compliance
- **Government agencies** deploying AI systems under the White House AI Bill of Rights
- **Any organization** seeking ISO 42001 (AI Management System) certification

---

### Discussion Questions

**Technical**:
1. How would you extend this system to support continuous monitoring of deployed models?
2. What additional risk vectors should be considered for different types of AI systems?
3. How could automation reduce the manual effort in maintaining the inventory?

**Process**:
4. What organizational changes are needed to ensure inventory records stay up-to-date?
5. How should risk tier assignments trigger different control requirements?
6. What role should business stakeholders play vs. technical teams in risk documentation?

**Strategic**:
7. How does systematic AI risk management create competitive advantage?
8. What are the costs of NOT implementing these governance practices?
9. How will AI regulations continue to evolve over the next 5 years?

---

### Optional Advanced Exercises

If you finish early and want to explore further:

**Exercise A: Simulate a Model Failure Incident**
1. Document a new risk describing a hypothetical model failure
2. Set Impact=5 and Likelihood=5 (highest severity)
3. Develop a detailed incident response and mitigation plan
4. Generate a new evidence package showing the incident documentation

**Exercise B: Build a Complete System Profile**
1. Add a new AI system of your choosing (e.g., resume screening, dynamic pricing, content moderation)
2. Calculate its risk tier
3. Document at least 5 risks across all lifecycle phases
4. Ensure all risk vectors are covered
5. Generate evidence and review the risk matrix

**Exercise C: Cross-System Analysis**
1. Compare risk profiles across all three systems
2. Identify common risks that appear in multiple systems
3. Propose organization-wide controls that could address shared risks
4. Draft an executive memo recommending governance improvements

---

## 📚 Additional Resources

### Frameworks & Standards
- **NIST AI Risk Management Framework (AI RMF)** - US national standard for AI risk management
- **ISO 42001** - International standard for AI management systems
- **EU AI Act** - European regulatory framework for high-risk AI systems
- **SR 11-7** - Federal Reserve guidance on model risk management

### Industry Best Practices
- **Model Cards** - Documentation standard for ML models
- **Datasheets for Datasets** - Transparency framework for training data
- **AI Incident Database** - Real-world examples of AI failures and harms

### Tools & Technologies
- **MLflow** - ML lifecycle management and model registry
- **Weights & Biases** - Experiment tracking and model monitoring
- **Evidently AI** - Data drift and model performance monitoring
- **Fairlearn** - Bias assessment and mitigation toolkit

---

## ✉️ Questions or Issues?

If you encounter any technical issues during the lab:
1. Check that all required fields are filled before submitting forms
2. Verify you've selected a system in the sidebar before navigating to Risk Tiering or Lifecycle Risk Register
3. Ensure you have at least one system in the inventory before generating evidence packages

For conceptual questions about AI risk management, ask your instructor or discuss with your team.

---

## 📝 Lab Completion Checklist

Before leaving today's session, ensure you have:

- [ ] Added at least 3 AI systems to the inventory
- [ ] Calculated risk tiers for all systems
- [ ] Documented at least 5 total lifecycle risks across systems
- [ ] Generated at least one evidence package
- [ ] Reviewed the executive summary and evidence manifest
- [ ] Participated in group discussion and reflection

---

**Congratulations on completing the AI Risk Management Lab!**

You've developed practical skills in AI governance that are increasingly critical across all industries. These capabilities will serve you well whether you pursue careers in AI engineering, risk management, compliance, product management, or leadership roles in technology companies.

Remember: **Responsible AI isn't just about avoiding harms - it's about building systems that create value while earning trust.**

---

*This lab was designed for educational purposes as part of the QuantUniversity AI Risk Management curriculum.*
