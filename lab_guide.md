### Case Context

**Aperture Analytics Corp** is a rapidly scaling fintech startup that has grown from 15 employees to over 200 in just 18 months. The company now operates AI systems across consumer lending, fraud detection, customer service, operations, and marketing. However, this explosive growth has created a critical problem: **no centralized visibility into AI systems**, escalating regulatory pressures from the EU AI Act, and urgent requirements to demonstrate robust AI governance to Series C investors conducting due diligence.

Last month, the Board learned that a competitor faced a $50M regulatory fine due to an AI system failure. The CEO immediately tasked the Chief Risk Officer with implementing a comprehensive AI risk management framework within 60 days. Without systematic oversight, Aperture Analytics faces potential model failures, bias incidents, regulatory penalties, and the collapse of its $150M funding round. The stakes could not be higher.

---

### Your Role

You are Alex, the newly hired **AI Product Engineer** brought in to build and operationalize the company's first AI inventory and risk management system. You report directly to the CRO and are responsible for establishing the single source of truth for all AI systems across the enterprise. The executive team is watching your progress closely, as your success will determine whether Aperture can scale responsibly while securing critical funding.

Your work will create transparency where none exists, implement objective risk classification using deterministic algorithms, systematically document lifecycle risks from design through monitoring, and generate immutable audit evidence with cryptographic integrity verification. Today's lab simulates your first 90 days on the job, during which you must operationalize the complete AI governance lifecycle before investors arrive.

---
### What You Will Do

- Build a comprehensive inventory of AI systems including credit approval, fraud detection, and customer service chatbots
- Calculate deterministic risk tiers using a scoring algorithm based on decision criticality, automation level, and data sensitivity
- Document specific lifecycle risks across design, data, development, deployment, and monitoring phases
- Generate traceable evidence packages with SHA-256 hashes for audit and compliance verification
- Update risk profiles as mitigations are implemented and threat landscapes evolve

---

## Step-by-Step Instructions

**Step 1: Build the AI Inventory**

- Navigate to **Inventory Management** and add three systems: 
    1. Credit Approval System (Consumer Lending, Fully Automated, Highly Sensitive data)
    2. Real-Time Fraud Monitor (Fraud Prevention, Human in the Loop)
    3. Customer Service AI Assistant (Customer Experience, Assisted mode). 
- Use realistic technical specifications including AI type, deployment mode, and external dependencies. 
- Edit the Credit Approval System to add TransUnion API as a new dependency.

*Key Question: Why is maintaining an up-to-date inventory the foundation of effective AI governance?*

**Step 2: Calculate Risk Tiers**

- Navigate to **Risk Tiering** and compute the risk tier for each system. 
- Review the score breakdown showing how each dimension contributes points to the total score. 
- Document justification statements explaining why each system received its tier assignment. 
- Add required controls such as bias testing, human review thresholds, model validation schedules, and incident response plans.

*Key Question: How does deterministic scoring create objectivity and consistency compared to subjective risk assessments?*

**Step 3: Document Lifecycle Risks**
- Navigate to **Lifecycle Risk Register** and add specific risks across all phases. 
- For the** Credit Approval System**, document a data bias risk with Impact=5 and Likelihood=4. 
- For the **Fraud Monitor**, add a performance risk about false positives during seasonal shopping spikes. 
- For the **Chatbot**, document a privacy risk involving PII exposure. Add compliance and security risks to build comprehensive risk profiles.

*Key Question: Why must risk documentation span the entire AI lifecycle rather than focusing only on deployment?*

**Step 4: Update Risk Profiles**
- After documenting initial risks, simulate implementing a mitigation by editing the Fraud Monitor performance risk. 
- Reduce the likelihood from 3 to 2 and update the mitigation strategy to reflect that real-time monitoring dashboards have been deployed. 
- Observe how the severity score automatically recalculates.

*Key Question: How do living risk registers reflect the evolving state of deployed AI systems?*

**Step 5: Generate Audit Evidence**

- Navigate to **Exports and Evidence** and generate a complete evidence package including system inventory JSON files, risk tiering results, lifecycle risk maps, model inventory CSV, executive summary, and evidence manifest with SHA-256 hashes. 
- Review the executive summary showing systems breakdown by tier, risk coverage metrics, and compliance readiness. - 
- Examine the cryptographic hashes that prove integrity.

*Key Question: Why are immutable audit trails with cryptographic verification essential for regulated industries?*

## What This Lab Is Really Teaching

- **Enterprise AI governance is systematic, not ad hoc** - Effective oversight requires structured processes, repeatable workflows, and centralized systems rather than scattered spreadsheets and informal knowledge
- **Risk management operates at multiple levels** - High-level risk tiering enables proportional governance while detailed lifecycle risk registers identify specific threats requiring targeted mitigations
- **Transparency creates accountability** - Inventory systems establish ownership, trigger appropriate oversight based on risk tiers, and ensure that no AI system operates in the shadows
- **Audit readiness is operational, not episodic** - Generating evidence packages on demand requires maintaining up-to-date records continuously rather than scrambling when auditors arrive
- **AI governance is cross-functional** - Successful implementation requires collaboration between data scientists, legal teams, security engineers, product managers, and business stakeholders

--- 
### Discussion

1. How would you prioritize governance efforts if you inherited 50 AI systems tomorrow with limited resources? What criteria would determine which systems receive immediate attention versus lighter-touch oversight, and how would you communicate these trade-offs to executive leadership?
2. When should risk tier assignments trigger automatic controls versus human review of context? Consider scenarios where a Medium Risk system operates in a highly regulated domain versus a High Risk system with mature mitigations already in place.
3. How will the AI governance landscape evolve over the next five years as regulations mature, organizational AI literacy increases, and automated monitoring capabilities advance? What capabilities should you build today to prepare for tomorrow's requirements?

---
### Takeaway

You have operationalized a complete AI risk management system that transforms governance from aspiration into executable process. By establishing inventory transparency, implementing deterministic risk classification, documenting lifecycle risks systematically, and generating cryptographically verified evidence, you have positioned Aperture Analytics to scale AI responsibly while satisfying investors, regulators, and auditors that the company takes AI governance seriously.