# CASE STUDY: Enterprise Credit Decision System
## Lab 1 — Enterprise AI Lifecycle Risk Mapper

**Course:** AI Design & Deployment Risks (Spring 2026)  
**Session:** 1 — Enterprise AI Risk & Lifecycle Foundations  
**Use Case:** Finance — ML-Based Consumer Credit Approval  
**Version:** 1.0  
**Last Updated:** 2026-01-20

---

## Executive Overview

**Meridian National Bank** is replacing its legacy rules-based credit approval workflow with an ML-powered decision system. This case study provides the full context needed for students to complete Lab 1's Lifecycle Risk Mapper exercise.

The case is designed to surface risks across all lifecycle stages, multiple risk categories, and varying severity levels — ensuring students can practice the complete risk identification and scoring workflow.

---

## 1. Organization Context

### 1.1 Company Profile

| Attribute | Value |
|-----------|-------|
| **Organization** | Meridian National Bank |
| **Type** | Regional commercial bank (FDIC-insured) |
| **Assets** | $48 billion |
| **Employees** | 4,200 |
| **Branches** | 187 locations across 6 states (Mid-Atlantic region) |
| **Primary Regulators** | OCC, Federal Reserve, CFPB |
| **Applicable Regulations** | SR 11-7, ECOA, Fair Housing Act, FCRA, UDAAP |

### 1.2 Business Unit

| Attribute | Value |
|-----------|-------|
| **Division** | Consumer Lending |
| **Products** | Personal loans, auto loans, credit cards, HELOCs |
| **Annual Originations** | $6.2 billion |
| **Active Accounts** | 1.4 million |
| **Business Owner** | Sarah Chen, SVP Consumer Lending |
| **Technical Owner** | Marcus Williams, VP Data Science & Analytics |

### 1.3 Current State (Legacy System)

The existing credit decisioning process uses a **rules-based expert system** deployed in 2014:

- **Decision Logic:** 847 hard-coded rules maintained by a 3-person team
- **Average Decision Time:** 4.2 minutes per application
- **Manual Review Rate:** 38% of applications require human underwriter review
- **Approval Rate:** 52%
- **Default Rate (12-month):** 3.8%
- **Primary Pain Points:**
  - Rules are brittle and difficult to update
  - Cannot capture complex, non-linear relationships
  - High manual review rate increases operational costs
  - Competitive disadvantage vs. fintech lenders with instant decisioning

---

## 2. System Description

### 2.1 Project Charter

**Project Name:** APEX (Automated Predictive EXcellence) Credit Decision System

**Business Objective:**  
Deploy an ML-based credit decisioning system to:
1. Reduce average decision time from 4.2 minutes to <30 seconds
2. Reduce manual review rate from 38% to <15%
3. Maintain or improve current default rate (≤3.8%)
4. Ensure full compliance with fair lending regulations

**Target Go-Live:** Q3 2026 (pilot), Q4 2026 (full production)

### 2.2 System Metadata (Lab 1 Input)

```json
{
  "system_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "APEX Credit Decision System",
  "domain": "Finance",
  "description": "Automate consumer credit approval decisions for personal loans, auto loans, and credit cards with real-time ML scoring, fair lending compliance layer, and SHAP-based adverse action explanations",
  "ai_type": "ML",
  "owner_role": "Sarah Chen, SVP Consumer Lending",
  "deployment_mode": "HUMAN_IN_LOOP",
  "decision_criticality": "HIGH",
  "automation_level": "HUMAN_APPROVAL",
  "data_sensitivity": "REGULATED_PII",
  "external_dependencies": ["Experian API", "TransUnion API", "Core Banking System"],
  "updated_at": "2026-01-20T00:00:00+00:00"
}
```

### 2.3 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APEX CREDIT DECISION SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Digital   │    │   Branch    │    │    API      │    │   Partner   │  │
│  │  Channels   │    │   Systems   │    │   Gateway   │    │  Integrations│  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │          │
│         └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      APPLICATION INTAKE LAYER                         │   │
│  │   • Data validation  • Identity verification  • Fraud screening      │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      DATA ENRICHMENT LAYER                            │   │
│  │   • Bureau data pull  • Internal history  • Alternative data         │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         FEATURE STORE                                 │   │
│  │   • 847 engineered features  • Real-time computation  • Caching      │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ML SCORING ENGINE (Core)                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │  XGBoost     │  │  Fair Lending │  │  Explanation │                │   │
│  │  │  Ensemble    │  │  Compliance   │  │  Generator   │                │   │
│  │  │  Model       │  │  Layer        │  │  (SHAP)      │                │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      DECISION OUTPUT LAYER                            │   │
│  │   • Approve/Decline/Review  • Pricing tier  • Adverse action reasons │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────┐         ┌─────────────────┐         ┌─────────────┐       │
│  │  Straight-  │         │     Human       │         │   Decline   │       │
│  │  Through    │         │   Underwriter   │         │   Queue     │       │
│  │  Approval   │         │     Queue       │         │             │       │
│  │   (65%)     │         │     (15%)       │         │    (20%)    │       │
│  └─────────────┘         └─────────────────┘         └─────────────┘       │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                          MONITORING & GOVERNANCE                             │
│   • Model performance dashboards  • Drift detection  • Fairness metrics     │
│   • Override tracking  • Audit logging  • Incident response                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Key System Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Decision Volume** | 520,000 decisions/month | ~17,300/day average |
| **Portfolio Exposure** | $52 billion | Total outstanding balance |
| **Target SLA** | <500ms (P95) | End-to-end decision time |
| **Model Type** | XGBoost Ensemble | Gradient-boosted decision trees |
| **Features Used** | 847 | Engineered from raw data |
| **Training Data Period** | 2019-2024 | 5 years of historical decisions |
| **Training Samples** | 4.2 million | Historical applications |
| **Refresh Cycle** | Quarterly | Full retrain with champion-challenger |
| **Explanation Method** | SHAP values | For adverse action reasons |

---

## 3. Data Inventory

### 3.1 Training Data Sources

| Source | Type | Records | Refresh | Data Quality Concerns |
|--------|------|---------|---------|----------------------|
| **Internal Application Data** | Structured | 4.2M applications | Real-time | Selection bias from previous rules |
| **Credit Bureau (Experian)** | Structured | 4.2M pulls | Real-time | Reporting lags, disputes |
| **Credit Bureau (TransUnion)** | Structured | 4.2M pulls | Real-time | Coverage gaps for thin-file |
| **Internal Account History** | Structured | 18M account-months | Daily | Survivorship bias |
| **Employment Verification** | Semi-structured | 2.1M records | On-demand | Gig economy coverage gaps |
| **Alternative Data (bank txns)** | Structured | 890K records | Opt-in | Consent/privacy concerns |

### 3.2 Feature Categories

| Category | Count | Examples | Risk Concerns |
|----------|-------|----------|---------------|
| **Credit History** | 124 | Delinquency count, utilization, age of accounts | Reflects historical access disparities |
| **Payment Behavior** | 156 | On-time payment rate, payment volatility | Economic stress sensitivity |
| **Debt Profile** | 98 | DTI, total balances, revolving vs. installment | May disadvantage certain demographics |
| **Application Data** | 87 | Loan amount, purpose, term requested | Self-selection bias |
| **Geographic** | 42 | State, MSA, zip code density | **HIGH RISK: Proxy for race** |
| **Employment** | 78 | Employment length, income stability, industry | Gig economy disadvantage |
| **Banking Relationship** | 112 | Account age, product count, avg balance | Excludes underbanked |
| **Alternative Data** | 150 | Cash flow patterns, utility payments | Consent and coverage issues |

### 3.3 Known Data Quality Issues

1. **Historical Bias:** Training data reflects decisions made by the rules-based system, which may have embedded historical discrimination patterns.

2. **COVID-19 Anomaly:** 2020-2021 data includes forbearance programs, stimulus effects, and abnormal default patterns that may not generalize.

3. **Thin-File Underrepresentation:** Applicants with limited credit history (young adults, recent immigrants, unbanked populations) are underrepresented in training data.

4. **Geographic Concentration:** 78% of training data comes from 3 states; model may perform poorly in recently expanded markets.

5. **Label Quality:** "Default" definition changed in 2022 from 90 days past due to 60 days, creating label inconsistency.

---

## 4. Regulatory & Compliance Context

### 4.1 Applicable Regulations

| Regulation | Relevance | Key Requirements |
|------------|-----------|------------------|
| **SR 11-7** | Model Risk Management | Independent validation, ongoing monitoring, governance framework |
| **ECOA** | Fair Lending | Cannot discriminate on race, color, religion, national origin, sex, marital status, age |
| **Fair Housing Act** | Housing Credit | Applies to HELOCs; prohibits geographic discrimination (redlining) |
| **FCRA** | Consumer Reporting | Accurate data use, adverse action notices, dispute handling |
| **UDAAP** | Consumer Protection | No unfair, deceptive, or abusive acts or practices |
| **State Laws** | Varies by state | Additional fair lending requirements in NY, CA, IL |

### 4.2 Regulatory Examination History

| Date | Examiner | Finding | Status |
|------|----------|---------|--------|
| Q2 2024 | OCC | MRA: Inadequate model documentation | Remediated Q4 2024 |
| Q3 2023 | CFPB | MRBA: Incomplete adverse action reasons | Open |
| Q1 2023 | State (NY) | Observation: Geographic feature monitoring | Remediated |

### 4.3 Fair Lending Analysis Requirements

Per regulatory guidance, the bank must demonstrate:

1. **No Disparate Treatment:** Protected class status cannot directly influence decisions
2. **No Disparate Impact:** Facially neutral practices cannot disproportionately harm protected classes without business justification
3. **No Proxy Discrimination:** Features that serve as proxies for protected characteristics must be justified or removed

**Protected Classes (ECOA):**
- Race
- Color
- Religion
- National origin
- Sex
- Marital status
- Age (if applicant has capacity to contract)
- Receipt of public assistance
- Exercise of Consumer Credit Protection Act rights

---

## 5. Stakeholder Map

### 5.1 Internal Stakeholders

| Stakeholder | Role | Interest | Concern |
|-------------|------|----------|---------|
| **Sarah Chen** | SVP Consumer Lending | Business outcomes | Revenue impact, customer experience |
| **Marcus Williams** | VP Data Science | Technical delivery | Model performance, scalability |
| **Janet Morrison** | Chief Risk Officer | Enterprise risk | Regulatory compliance, credit losses |
| **David Park** | Chief Compliance Officer | Regulatory compliance | Fair lending, UDAAP |
| **Linda Tran** | Head of Model Validation | Independent validation | SR 11-7 compliance |
| **Operations Team** | Underwriters | Daily workflow | Override rates, queue management |
| **IT Security** | Infrastructure | System security | Data protection, access control |

### 5.2 External Stakeholders

| Stakeholder | Role | Interest | Concern |
|-------------|------|----------|---------|
| **OCC** | Primary Regulator | Safety & soundness | Model risk, fair lending |
| **CFPB** | Consumer Protection | Consumer outcomes | Discrimination, transparency |
| **Consumers** | Applicants | Fair treatment | Accurate decisions, explanations |
| **Community Groups** | Advocacy | Fair access | Lending disparities |
| **External Auditors** | Annual Audit | Controls | Documentation, testing |

---

## 6. Lifecycle Risk Scenarios

This section provides detailed risk scenarios for each lifecycle stage. Students should use these as a starting point for Lab 1 risk identification.

---

### 6.1 DESIGN_BUILD Phase Risks

#### RISK-DESIGN-001: Proxy Variable Discrimination (CRITICAL)

**Description:**  
The model uses "zip code density" and "distance to nearest branch" as features. Analysis shows these features correlate strongly with race and ethnicity (r = 0.42 and r = 0.38 respectively) due to historical residential segregation patterns.

**Risk Vector:** BIAS_FAIRNESS

**Impact Analysis:**
- Regulatory: Fair lending violation, potential enforcement action
- Financial: Potential restitution, fines ($10M+ range)
- Reputational: Public disclosure, community backlash

**Impact Score:** 5 (Catastrophic)  
**Likelihood Score:** 4 (Likely — features currently in production design)  
**Severity Score:** 20 (CRITICAL)

**Evidence Type:** DESIGN_DOC  
**Evidence Reference:** Feature correlation analysis v2.3, Fair Lending Impact Assessment (pending)

---

#### RISK-DESIGN-002: Scope Creep to High-Risk Decisions (HIGH)

**Description:**  
Initial scope was personal loans only. Business stakeholders have requested expansion to auto loans and HELOCs during design phase, each with different risk profiles and regulatory requirements (HELOC triggers Fair Housing Act).

**Risk Vector:** COMPLIANCE

**Impact Score:** 4 (Major)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** ASSUMPTION  
**Evidence Reference:** Project Change Request #PCR-2026-047

---

#### RISK-DESIGN-003: Insufficient Stakeholder Representation (MEDIUM)

**Description:**  
Design workshops did not include representation from compliance, model validation, or operations. Requirements may miss critical regulatory and operational constraints.

**Risk Vector:** COMPLIANCE

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 9 (MEDIUM)

**Evidence Type:** ASSUMPTION  
**Evidence Reference:** Design Workshop Attendance Records

---

### 6.2 DATA Phase Risks

#### RISK-BUILD-001: Historical Bias in Training Labels (CRITICAL)

**Description:**  
Training data includes 5 years of decisions from the legacy rules-based system. Analysis indicates the legacy system had a 12% lower approval rate for applicants in majority-minority zip codes, even after controlling for creditworthiness factors. The ML model may learn and amplify this historical discrimination.

**Risk Vector:** BIAS_FAIRNESS

**Impact Score:** 5 (Catastrophic)  
**Likelihood Score:** 4 (Likely — data reflects legacy decisions)  
**Severity Score:** 20 (CRITICAL)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Historical Disparate Impact Analysis v1.2

---

#### RISK-BUILD-002: COVID-19 Data Contamination (HIGH)

**Description:**  
Training data from 2020-2022 includes anomalous patterns due to forbearance programs, stimulus payments, and economic disruption. Models trained on this data may not generalize to normal economic conditions.

**Risk Vector:** FUNCTIONAL

**Impact Score:** 4 (Major)  
**Likelihood Score:** 4 (Likely — data is included)  
**Severity Score:** 16 (CRITICAL)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Data Quality Assessment Report Section 4.2

---

#### RISK-BUILD-003: Label Leakage from Future Information (HIGH)

**Description:**  
Feature engineering pipeline inadvertently includes post-application data (account behavior after approval) in training features, creating temporal leakage. Model performance in production will be significantly worse than validation metrics suggest.

**Risk Category:** FUNCTIONAL

**Impact Score:** 4 (Major)  
**Likelihood Score:** 3 (Possible — pipeline review pending)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** TBD  
**Evidence Reference:** Feature Pipeline Audit (scheduled)

---

#### RISK-BUILD-004: Thin-File Population Exclusion (HIGH)

**Description:**  
Applicants with limited credit history ("thin-file" consumers) represent only 8% of training data but 22% of target population. Model may perform poorly or unfairly disadvantage young adults, recent immigrants, and unbanked populations.

**Risk Vector:** BIAS_FAIRNESS

**Impact Score:** 4 (Major)  
**Likelihood Score:** 4 (Likely)  
**Severity Score:** 16 (CRITICAL)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Training Data Demographic Analysis

---

#### RISK-BUILD-005: Third-Party Data Dependency (MEDIUM)

**Description:**  
Model relies on credit bureau data from Experian and TransUnion. Bureau data quality, coverage, and pricing changes are outside bank control. Bureau API downtime would halt all credit decisions.

**Risk Category:** OPERATIONAL

**Impact Score:** 4 (Major)  
**Likelihood Score:** 2 (Unlikely)  
**Severity Score:** 8 (MEDIUM)

**Evidence Type:** DESIGN_DOC  
**Evidence Reference:** Vendor Risk Assessment — Experian, TransUnion

---

### 6.3 VALIDATION Phase Risks

#### RISK-VALIDATE-001: Subgroup Performance Blindspot (CRITICAL)

**Description:**  
Initial validation achieved 94.2% overall accuracy (AUC = 0.89). However, stratified analysis reveals:
- Majority population: 95.1% accuracy
- Hispanic applicants: 86.3% accuracy  
- Black applicants: 84.7% accuracy
- Age 18-25: 81.2% accuracy

Validation team initially signed off on overall metrics without subgroup analysis.

**Risk Vector:** BIAS_FAIRNESS

**Impact Score:** 5 (Catastrophic)  
**Likelihood Score:** 4 (Likely — gaps confirmed)  
**Severity Score:** 20 (CRITICAL)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Model Validation Report v1.0, Appendix C (Subgroup Analysis)

---

#### RISK-VALIDATE-002: Validation Independence Compromise (HIGH)

**Description:**  
Due to resource constraints, two members of the validation team previously worked on model development. SR 11-7 requires validation to be performed by staff independent from development.

**Risk Vector:** COMPLIANCE

**Impact Score:** 4 (Major)  
**Likelihood Score:** 4 (Likely — staffing confirmed)  
**Severity Score:** 16 (CRITICAL)

**Evidence Type:** ASSUMPTION  
**Evidence Reference:** Model Validation Team Roster

---

#### RISK-VALIDATE-003: Inadequate Stress Testing (HIGH)

**Description:**  
Validation tested model under normal conditions but did not include stress scenarios (recession, interest rate shock, regional economic downturn). Model behavior under adverse conditions is unknown.

**Risk Category:** FUNCTIONAL

**Impact Score:** 4 (Major)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** TBD  
**Evidence Reference:** Stress Testing Plan (not yet developed)

---

#### RISK-VALIDATE-004: Explainability Gap (MEDIUM)

**Description:**  
SHAP-based explanations are technically accurate but not meaningful to consumers. Example adverse action reason: "Feature_427 contributed -0.23 to score." Regulatory requirement is for explanations consumers can understand and act upon.

**Risk Vector:** INTERPRETABILITY

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 4 (Likely)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Adverse Action Reason Audit

---

### 6.4 DEPLOYMENT Phase Risks

#### RISK-DEPLOY-001: A/B Test Statistical Validity (MEDIUM)

**Description:**  
Pilot deployment plan uses A/B testing with 5% traffic to new model. At current volumes, this provides only 850 decisions/day, requiring 60+ days to achieve statistical significance for key metrics. Business pressure to expand before significance achieved.

**Risk Category:** FUNCTIONAL

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 9 (MEDIUM)

**Evidence Type:** DESIGN_DOC  
**Evidence Reference:** Pilot Deployment Plan v2.1

---

#### RISK-DEPLOY-002: Integration Failure with Core Banking (HIGH)

**Description:**  
APEX integrates with legacy core banking system via batch interface. Testing revealed that high-volume periods cause queue backlogs, resulting in decisions not being recorded in core system for up to 4 hours. Customer-facing systems may show inconsistent information.

**Risk Category:** OPERATIONAL

**Impact Score:** 4 (Major)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** TEST_RESULT  
**Evidence Reference:** Integration Test Report — Core Banking

---

#### RISK-DEPLOY-003: Rollback Procedure Untested (MEDIUM)

**Description:**  
Deployment plan includes rollback procedure to legacy system, but procedure has not been tested under production load. Rollback may take 2-4 hours, during which credit decisions would be delayed.

**Risk Category:** OPERATIONAL

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 2 (Unlikely)  
**Severity Score:** 6 (MEDIUM)

**Evidence Type:** TBD  
**Evidence Reference:** Rollback Test (scheduled)

---

### 6.5 OPERATIONS Phase Risks

#### RISK-OPERATE-001: Economic Drift Undetected (CRITICAL)

**Description:**  
Model trained on 2019-2024 data. Economic conditions (interest rates, unemployment, inflation) may shift significantly post-deployment. Without robust drift detection, model performance may degrade silently for months before detection.

Example: Model deployed January 2020 would have failed catastrophically by March 2020 without drift detection.

**Risk Category:** OPERATIONAL

**Impact Score:** 5 (Catastrophic)  
**Likelihood Score:** 4 (Likely — economic cycles are certain)  
**Severity Score:** 20 (CRITICAL)

**Evidence Type:** ASSUMPTION  
**Evidence Reference:** Drift Monitoring Requirements (in development)

---

#### RISK-OPERATE-002: Override Rate Creep (HIGH)

**Description:**  
Underwriters may systematically override model decisions based on factors the model doesn't capture. If override rate exceeds 20%, it indicates model is not fit for purpose. Currently no override monitoring dashboard exists.

Per SR 11-7: "If the rate of overrides is high, or if the override process consistently improves model performance, it is often a sign that the underlying model needs revision."

**Risk Vector:** COMPLIANCE

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 4 (Likely)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** TBD  
**Evidence Reference:** Override Monitoring Dashboard (not yet built)

---

#### RISK-OPERATE-003: Feedback Loop Amplification (HIGH)

**Description:**  
Approved applicants become training data for future models. If model is biased against certain groups, those groups receive fewer approvals, generating less positive training data, reinforcing the bias in future iterations.

**Risk Vector:** BIAS_FAIRNESS

**Impact Score:** 4 (Major)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 12 (HIGH)

**Evidence Type:** ASSUMPTION  
**Evidence Reference:** Retraining Strategy Document

---

#### RISK-OPERATE-004: Incident Response Gap (MEDIUM)

**Description:**  
No documented incident response procedure exists for AI-specific incidents (e.g., model producing discriminatory outcomes, drift detection alert, adversarial attack). IT incident response procedures do not cover AI/ML scenarios.

**Risk Vector:** COMPLIANCE

**Impact Score:** 3 (Moderate)  
**Likelihood Score:** 3 (Possible)  
**Severity Score:** 9 (MEDIUM)

**Evidence Type:** TBD  
**Evidence Reference:** AI Incident Response Playbook (not yet created)

---

## 7. Seeded Lab Data Files

### 7.1 System Metadata File

**Filename:** `sample_system_credit_decision.json`

```json
{
  "system_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "APEX Credit Decision System",
  "description": "Automate consumer credit approval decisions for personal loans, auto loans, and credit cards with real-time ML scoring, fair lending compliance layer, and SHAP-based adverse action explanations",
  "domain": "Finance",
  "ai_type": "ML",
  "owner_role": "Sarah Chen, SVP Consumer Lending",
  "deployment_mode": "HUMAN_IN_LOOP",
  "decision_criticality": "HIGH",
  "automation_level": "HUMAN_APPROVAL",
  "data_sensitivity": "REGULATED_PII",
  "external_dependencies": ["Experian API", "TransUnion API", "Core Banking System"],
  "updated_at": "2026-01-20T00:00:00+00:00"
}
```

### 7.2 Lifecycle Risks File

**Filename:** `sample_lifecycle_risks_credit.json`

```json
{
  "risks": [
    {
      "risk_id": "11111111-1111-1111-1111-111111111111",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "DESIGN_BUILD",
      "risk_vector": "BIAS_FAIRNESS",
      "risk_statement": "Zip code density and branch distance features correlate strongly with race/ethnicity (r=0.42, r=0.38) due to historical residential segregation. May constitute proxy discrimination under ECOA.",
      "impact": 5,
      "likelihood": 4,
      "severity": 20,
      "mitigation": "Remove geographic proxy features and conduct fair lending impact assessment before deployment.",
      "owner_role": "David Park, Chief Compliance Officer",
      "evidence_type": "DESIGN_DOC",
      "evidence_reference": "Feature Correlation Analysis v2.3; Fair Lending Impact Assessment pending",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "22222222-2222-2222-2222-222222222222",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "DATA",
      "risk_vector": "BIAS_FAIRNESS",
      "risk_statement": "Training data (2019-2024) reflects legacy rules-based decisions with 12% lower approval rate for majority-minority zip codes. ML model may learn and amplify historical discrimination patterns.",
      "impact": 5,
      "likelihood": 4,
      "severity": 20,
      "mitigation": "Conduct bias audit on training data, apply fairness constraints during training, and monitor for disparate impact.",
      "owner_role": "Marcus Williams, VP Data Science",
      "evidence_type": "TEST_RESULT",
      "evidence_reference": "Historical Disparate Impact Analysis v1.2",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "33333333-3333-3333-3333-333333333333",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "DATA",
      "risk_vector": "FUNCTIONAL",
      "risk_statement": "COVID-19 period (2020-2022) data includes anomalous forbearance, stimulus, and default patterns that may not generalize to normal economic conditions.",
      "impact": 4,
      "likelihood": 4,
      "severity": 16,
      "mitigation": "Weight or exclude COVID-era data, perform temporal validation splits, and implement drift detection for economic regime shifts.",
      "owner_role": "Marcus Williams, VP Data Science",
      "evidence_type": "TEST_RESULT",
      "evidence_reference": "Data Quality Assessment Report Section 4.2",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "44444444-4444-4444-4444-444444444444",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "VALIDATION",
      "risk_vector": "BIAS_FAIRNESS",
      "risk_statement": "Overall accuracy 94.2% masks significant subgroup disparities: Hispanic 86.3%, Black 84.7%, Age 18-25 81.2%. Initial validation signed off without stratified analysis.",
      "impact": 5,
      "likelihood": 4,
      "severity": 20,
      "mitigation": "Mandate stratified performance analysis for all protected classes before validation approval. Set minimum performance thresholds per subgroup.",
      "owner_role": "Linda Tran, Head of Model Validation",
      "evidence_type": "TEST_RESULT",
      "evidence_reference": "Model Validation Report v1.0, Appendix C",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "55555555-5555-5555-5555-555555555555",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "VALIDATION",
      "risk_vector": "COMPLIANCE",
      "risk_statement": "Two validation team members previously worked on model development, compromising SR 11-7 independence requirement.",
      "impact": 4,
      "likelihood": 4,
      "severity": 16,
      "mitigation": "Replace validation team members with independent staff who have no prior involvement in model development.",
      "owner_role": "Janet Morrison, Chief Risk Officer",
      "evidence_type": "ASSUMPTION",
      "evidence_reference": "Model Validation Team Roster",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "66666666-6666-6666-6666-666666666666",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "DEPLOYMENT",
      "risk_vector": "OPERATIONAL",
      "risk_statement": "Integration with legacy core banking via batch interface causes 4-hour recording delays during high-volume periods, creating customer-facing inconsistencies.",
      "impact": 4,
      "likelihood": 3,
      "severity": 12,
      "mitigation": "Implement real-time API integration with core banking system or add queuing buffer to handle peak loads.",
      "owner_role": "IT Operations Lead",
      "evidence_type": "TEST_RESULT",
      "evidence_reference": "Integration Test Report — Core Banking",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "77777777-7777-7777-7777-777777777777",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "OPERATIONS",
      "risk_vector": "OPERATIONAL",
      "risk_statement": "No robust drift detection mechanism to identify when economic conditions diverge from training data distribution. Model could degrade silently for months.",
      "impact": 5,
      "likelihood": 4,
      "severity": 20,
      "mitigation": "Implement automated drift detection for input features and model performance, with alerting thresholds and retraining triggers.",
      "owner_role": "Marcus Williams, VP Data Science",
      "evidence_type": "ASSUMPTION",
      "evidence_reference": "Drift Monitoring Requirements (in development)",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    },
    {
      "risk_id": "88888888-8888-8888-8888-888888888888",
      "system_id": "550e8400-e29b-41d4-a716-446655440001",
      "lifecycle_phase": "OPERATIONS",
      "risk_vector": "BIAS_FAIRNESS",
      "risk_statement": "Feedback loop risk: Biased approvals generate biased training data, reinforcing discrimination in future model iterations.",
      "impact": 4,
      "likelihood": 3,
      "severity": 12,
      "mitigation": "Implement fairness monitoring in production, use counterfactual outcomes for retraining, and maintain diverse training data sources.",
      "owner_role": "David Park, Chief Compliance Officer",
      "evidence_type": "ASSUMPTION",
      "evidence_reference": "Retraining Strategy Document",
      "evidence_links": [],
      "last_reviewed": "2026-01-20T00:00:00+00:00",
      "created_at": "2026-01-20T00:00:00+00:00"
    }
  ]
}
```

---

## 8. Lab 1 Exercise Instructions

### 8.1 Task Overview

Using the APEX Credit Decision System case study, complete the following in the Lab 1 Streamlit application:

1. **Create System Metadata** — Enter the system information in the left panel
2. **Document Architecture** — Describe the system architecture in your own words
3. **Identify Lifecycle Risks** — Add at least 5 risks across 3+ lifecycle stages
4. **Score Severity** — Apply Impact × Likelihood scoring consistently
5. **Assign Ownership** — Identify who should own each risk
6. **Link Evidence** — Reference available evidence or note gaps
7. **Export Package** — Generate the evidence-grade export bundle

### 8.2 Minimum Requirements

| Requirement | Threshold |
|-------------|-----------|
| System metadata complete | All fields populated |
| Lifecycle coverage | Risks in ≥3 stages |
| Risk categories | ≥3 different categories used |
| HIGH risks identified | ≥1 risk with severity 11-15 |
| CRITICAL risks identified | ≥1 risk with severity 16-25 |
| Evidence types | Mix of available and TBD |
| Export generated | ZIP file with all artifacts |

### 8.3 Discussion Questions

After completing the lab, consider:

1. Which lifecycle stage has the highest concentration of CRITICAL risks? Why?
2. How would you prioritize remediation given limited resources?
3. What additional evidence would strengthen your risk register?
4. How would the risk profile differ for Use Case B (Healthcare Triage)?
5. What governance structure would you recommend to manage these risks?

---

## 9. Reference: Risk Scoring Guide

### Impact Score Definitions

| Score | Label | Financial | Operational | Regulatory | Reputational |
|-------|-------|-----------|-------------|------------|--------------|
| **1** | Negligible | <$100K | <1 hour delay | Observation | Internal only |
| **2** | Minor | $100K-$1M | 1-4 hour delay | MRA | Local media |
| **3** | Moderate | $1M-$10M | 4-24 hour delay | MRBA | Regional media |
| **4** | Major | $10M-$100M | 1-7 day impact | Enforcement | National media |
| **5** | Catastrophic | >$100M | >7 day impact | Consent order | Congressional |

### Likelihood Score Definitions

| Score | Label | Probability | Timeframe |
|-------|-------|-------------|-----------|
| **1** | Rare | <5% | May occur in exceptional circumstances |
| **2** | Unlikely | 5-20% | Could occur but not expected |
| **3** | Possible | 20-50% | May occur at some point |
| **4** | Likely | 50-80% | Will probably occur |
| **5** | Almost Certain | >80% | Expected to occur in most circumstances |

### Severity Bands

| Severity Score | Band | Required Action |
|----------------|------|-----------------|
| 1-5 | LOW | Monitor; address in normal course |
| 6-10 | MEDIUM | Documented mitigation plan required |
| 11-15 | HIGH | Senior management review; accelerated timeline |
| 16-25 | CRITICAL | Executive escalation; immediate action required |

---

## 10. Appendix: Regulatory Reference

### SR 11-7 Key Principles (Summary)

1. **Model Risk Definition:** "The potential for adverse consequences from decisions based on incorrect or misused model outputs and reports"

2. **Three Lines of Defense:**
   - First: Model development and use
   - Second: Model validation (independent)
   - Third: Internal audit

3. **Effective Challenge:** "Critical analysis by objective, informed parties who can identify model limitations and assumptions and produce appropriate changes"

4. **Documentation:** "Without adequate documentation, model risk assessment and management will be ineffective"

5. **Ongoing Monitoring:** "Models should be subject to ongoing monitoring... to confirm that they are performing properly"

### ECOA Protected Classes

Creditors may not discriminate against any applicant based on:
- Race
- Color
- Religion
- National origin
- Sex
- Marital status
- Age (provided the applicant has the capacity to contract)
- Receipt of income from public assistance programs
- Good faith exercise of any right under the Consumer Credit Protection Act

### Disparate Impact Standard

A facially neutral practice that has a disproportionate adverse effect on a protected class is unlawful unless:
1. The practice is necessary to achieve a legitimate business objective
2. The objective cannot reasonably be achieved by less discriminatory means

---

*End of Case Study Document*

**Document Version:** 1.0  
**Classification:** Educational Use  
**Course:** AI Design & Deployment Risks — George Mason University — Spring 2026
