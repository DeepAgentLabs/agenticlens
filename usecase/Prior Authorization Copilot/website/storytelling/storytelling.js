/**
 * DeepAgentLabs Executive Storyboard
 * Multi-Industry Interactive Engine, Dynamic Visualizer & Stress-Test Simulator
 * Designed for CFOs, CMOs, COOs, and Non-Technical Business Leaders
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();

  // Industry Preset Data
  const industryPresets = {
    healthcare: {
      name: 'Healthcare & Prior Authorization',
      tag: 'Clinical AI Operational Resilience',
      titleHighlight: 'Why Healthcare AI Needs an Unbreakable Safety Net',
      kpi1: '$310,000',
      kpi1Label: 'Annual savings in avoided denial appeals per clinic',
      kpi2: '4 Hours',
      kpi2Label: 'Average turnaround vs 7-day manual review',
      kpi3: '0.0%',
      kpi3Label: 'Silent errors with DeepAgentLabs safety gate',
      disasterTitle: 'The $500,000 Treatment Delay',
      disasterDesc: 'An urgent cancer immunotherapy request was wrongly denied on Friday evening because a hospital diagnostic portal updated its format. Software saw 0% instead of 82% biomarker score and silently drafted a denial.',
      lensSave: 'AgenticLens captured the full decision flight record in 3.2 seconds, proving the patient was 100% eligible and exposing the portal formatting trap.',
      chaosSave: 'Agentic-Chaos stress-tested the pipeline against 50 simulated hospital outages and messy doctor notes, guaranteeing zero future silent rejections.',
      acts: [
        {
          id: 1,
          tag: 'Step 1 of 6 · Normal Production Operations',
          tagClass: 'tag-neutral',
          title: 'The Urgent Care Request at 4:45 PM',
          desc: 'On Friday afternoon, an urgent prior authorization request arrives for a 62-year-old cancer patient needing targeted immunotherapy (Keytruda). Under federal CMS rules, the clinic has only 72 hours to evaluate the patient’s medical records against insurance criteria and deliver a decision.',
          takeaway: 'Under standard conditions, automated review teams cut manual chart review from 7 days down to 4 hours, giving clinicians more time with patients.',
          stageTitle: 'Automated Clinical Review Team (Healthy Baseline)',
          stageBadge: 'All Systems Normal · 100% Accurate',
          stageBadgeClass: 'badge-green',
          callout: '<strong>Baseline Operation:</strong> The digital review workflow extracts clinical chart notes, identifies required lab values, and cross-references payer rules. Everything looks smooth.',
          nodes: [
            { name: 'Patient Chart Intake', role: 'Extracts diagnosis & medical history', status: 'COMPLETED', badge: 'Verified', badgeClass: 'badge-green', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            { name: 'Pathology & Lab Checker', role: 'Confirms required biomarker levels', status: 'COMPLETED', badge: 'Score: 82%', badgeClass: 'badge-green', icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
            { name: 'Insurance Policy Matcher', role: 'Cross-checks payer guidelines (Aetna CPB)', status: 'COMPLETED', badge: 'Criteria Met', badgeClass: 'badge-green', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
            { name: 'Physician Sign-Off Gate', role: 'Oncologist final clinical review', status: 'READY', badge: 'Ready to Sign', badgeClass: 'badge-blue', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' }
          ]
        },
        {
          id: 2,
          tag: 'Step 2 of 6 · The Hidden Financial & Clinical Threat',
          tagClass: 'tag-alert',
          title: 'The Silent Data Blind-Spot',
          desc: 'The hospital’s diagnostic lab portal silently modified its reporting format. Without warning, the biomarker score was moved into a sub-folder. The software didn’t crash or display an error—it simply couldn’t see the score, silently defaulted it to 0%, and recommended an immediate DENIAL for life-saving immunotherapy.',
          takeaway: 'In healthcare automation, the biggest risk isn’t software crashing. The real danger is software quietly making the wrong decision without alerting a single human.',
          stageTitle: 'Silent Failure Detected: Unseen Data Mismatch',
          stageBadge: 'CRITICAL: Erroneous Denial Drafted',
          stageBadgeClass: 'badge-red',
          callout: '<strong>The Silent Mismatch:</strong> The patient actually qualified with an 82% biomarker score, but the software saw 0% and proposed toxic chemotherapy. Standard monitoring showed 100% green uptime.',
          nodes: [
            { name: 'Patient Chart Intake', role: 'Extracts diagnosis & medical history', status: 'COMPLETED', badge: 'Verified', badgeClass: 'badge-green', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            { name: 'Pathology & Lab Checker', role: 'Data blind-spot: missed nested lab result', status: 'GLITCH', badge: 'Treated as 0%', badgeClass: 'badge-red', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
            { name: 'Insurance Policy Matcher', role: 'Flags patient as non-eligible due to 0%', status: 'GLITCH', badge: 'Denial Triggered', badgeClass: 'badge-red', icon: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z' },
            { name: 'Physician Sign-Off Gate', role: 'Misleading denial packet presented', status: 'AT_RISK', badge: 'At Risk', badgeClass: 'badge-red', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' }
          ]
        },
        {
          id: 3,
          tag: 'Step 3 of 6 · Complete Operational Transparency',
          tagClass: 'tag-neutral',
          title: 'The Hero Saver #1: AgenticLens (Flight Recorder)',
          desc: 'Instead of staff spending 15 hours piecing together phone calls and emails, leadership uses AgenticLens—the digital flight recorder. In one click, it reveals the contradiction: the physician’s written chart note clearly stated an 82% score, but the software recorded 0%.',
          takeaway: 'AgenticLens captures every automated step into an immutable audit record. Leadership has 100% proof of why every decision occurred, saving weeks of forensic investigation.',
          stageTitle: 'AgenticLens: Decision Provenance Audit',
          stageBadge: 'Discrepancy Isolated in 3.2 Seconds',
          stageBadgeClass: 'badge-blue',
          callout: '<strong>Instant Resolution:</strong> The flight recorder generates a complete, portable audit record. No engineering guesswork required.',
          nodes: [
            { name: 'Doctor Written Chart Note', role: 'Explicit: "Biopsy confirms 82% PD-L1 expression"', status: 'VERIFIED', badge: 'True: 82%', badgeClass: 'badge-green', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            { name: 'Software Lab Parser', role: 'Lab parser returned 0.0 due to format drift', status: 'FLIGHT_RECORDER', badge: 'Flagged Mismatch', badgeClass: 'badge-blue', icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
            { name: 'Payer Guideline Rule', role: 'Payer requires >= 50% for approval', status: 'VERIFIED', badge: 'Threshold: 50%', badgeClass: 'badge-green', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
            { name: 'Captured Safety Spec', role: 'Saved as reproducible test case', status: 'COMPLETED', badge: 'Frozen for Replay', badgeClass: 'badge-green', icon: 'M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4' }
          ]
        },
        {
          id: 4,
          tag: 'Step 4 of 6 · Risk-Free Pre-Flight Stress Testing',
          tagClass: 'tag-warning',
          title: 'The Hero Saver #2: Agentic-Chaos (Stress Testing)',
          desc: 'How do you guarantee this never happens again? You don’t test on live patients. The team replays the captured scenario in Agentic-Chaos, bombarding the workflow with 4 realistic hospital disruptions: portal timeouts, altered document formats, vague physician notes, and clearinghouse blackouts.',
          takeaway: 'Before an airline flies passengers, pilots train in flight simulators through simulated storms and engine failures. Agentic-Chaos provides the exact same safety net for healthcare AI.',
          stageTitle: 'Interactive Stress-Test Matrix (Click to Simulate)',
          stageBadge: 'Virtual Simulation Environment',
          stageBadgeClass: 'badge-blue',
          callout: '<strong>Interactive Simulation:</strong> Click any of the 4 real-world hospital disruptions below to see how the system behaves under stress.',
          interactiveChaos: true,
          nodes: []
        },
        {
          id: 5,
          tag: 'Step 5 of 6 · The Executive Safety Guarantee',
          tagClass: 'tag-success',
          title: 'The Fail-Safe Upgrade (Agentic-Evals)',
          desc: 'With the vulnerabilities exposed, the engineering team adds an unbreakable safety rule: The software is strictly forbidden from denying care if data is incomplete. Whenever a lab value is missing or formatted unexpectedly, the system safely routes the case to an on-call clinical nurse with the exact issue highlighted.',
          takeaway: 'Zero autonomous denials on incomplete data. When technology is unsure, it gracefully empowers human clinicians instead of rejecting treatment.',
          stageTitle: 'Hardened Workflow: Guaranteed Human Fallback',
          stageBadge: '100% Fail-Safe Clinician Escalation',
          stageBadgeClass: 'badge-green',
          callout: '<strong>Unbreakable Safety Rule:</strong> If lab values cannot be mathematically proven, the system triggers priority human escalation in under 15 minutes. No patient is ever left behind.',
          nodes: [
            { name: 'Patient Chart Intake', role: 'Synthesizes clinical evidence', status: 'COMPLETED', badge: 'Verified', badgeClass: 'badge-green', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            { name: 'Dual-Source Cross-Check', role: 'Checks both structured labs AND clinical narrative', status: 'HARDENED', badge: 'Dual Verification', badgeClass: 'badge-green', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
            { name: 'Priority Clinician Queue', role: 'Auto-routes ambiguous cases to oncologist', status: 'HARDENED', badge: 'Active Safety Net', badgeClass: 'badge-green', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
            { name: 'Compliant Submission', role: 'Pre-flight verified prior authorization packet', status: 'COMPLETED', badge: '100% Compliant', badgeClass: 'badge-green', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' }
          ]
        },
        {
          id: 6,
          tag: 'Step 6 of 6 · The Financial & Operational Return',
          tagClass: 'tag-success',
          title: 'The Executive Scorecard: Real ROI',
          desc: 'All 50 stress-test scenarios pass with 100% compliance. The automated release gate grants a certified release seal. The oncology clinic saves \$310,000 annually in avoided denial appeals, protects patient care, and satisfies CMS federal audit standards.',
          takeaway: 'Investing in continuous agentic reliability delivers an average 9x ROI by eliminating post-denial litigation, staff overtime, and lost patient revenue.',
          stageTitle: 'Executive Performance Comparison',
          stageBadge: 'Certified Release Gate Passed',
          stageBadgeClass: 'badge-green',
          callout: '<strong>Proven ROI:</strong> Below is the audited performance comparison between unprotected automation versus the DeepAgentLabs Continuous Reliability Lifecycle.',
          showScorecard: true
        }
      ]
    },
    banking: {
      name: 'Banking & Lending Underwriting',
      tag: 'Fintech Automated Decision Resilience',
      titleHighlight: 'Protecting Lending Portfolios from Silent AI Defaults',
      kpi1: '$1,250,000',
      kpi1Label: 'Capital loss prevented from erroneous loan decisions',
      kpi2: '12 Mins',
      kpi2Label: 'Underwriting decision time vs 4 days manual',
      kpi3: '100%',
      kpi3Label: 'Fair Lending & CFPB compliance audit pass rate',
      disasterTitle: 'The $1.2M Silent Income Inversion',
      disasterDesc: 'An automated small business loan engine misread a tax form because the IRS portal changed its 1040 schema. The system silently inverted debt-to-income and approved 14 unverified subprime applications.',
      lensSave: 'AgenticLens pinpointed the exact handoff between OCR and risk scoring in seconds, freezing the calculation before fraudulent funds disbursed.',
      chaosSave: 'Agentic-Chaos injected 40 synthetic credit bureau outages, tax document corruptions, and applicant identity collisions to harden underwriting.',
      acts: [] // Inherits structure dynamically
    },
    logistics: {
      name: 'Global Supply Chain & Freight',
      tag: 'Enterprise Operational Logistics Safety',
      titleHighlight: 'Guaranteeing Continuous Fulfillment During System Storms',
      kpi1: '$850,000',
      kpi1Label: 'Port demurrage and lost freight fees eliminated',
      kpi2: '99.8%',
      kpi2Label: 'On-time automated customs documentation rate',
      kpi3: 'Zero',
      kpi3Label: 'Unnoticed shipment drops during ERP outages',
      disasterTitle: 'The $850,000 Black Friday Customs Drop',
      disasterDesc: 'An autonomous logistics broker lost track of 20 shipping manifests during a 504 gateway timeout at Rotterdam port, defaulting delivery dates to NULL.',
      lensSave: 'AgenticLens recorded the exact EDI packet transmission drop, generating an instant replay spec that proved where the carrier disconnect occurred.',
      chaosSave: 'Agentic-Chaos simulated harbor network blackouts, altered tariff codes, and customs document mismatches to make freight dispatch self-healing.',
      acts: []
    },
    legal: {
      name: 'Legal & Procurement Contracts',
      tag: 'Enterprise Risk & Governance Assurance',
      titleHighlight: 'Preventing Unnoticed Liability In Vendor Agreements',
      kpi1: '$640,000',
      kpi1Label: 'Uncapped indemnity liability exposure caught pre-signature',
      kpi2: '15 Mins',
      kpi2Label: 'Contract review turnaround vs 8 days external counsel',
      kpi3: '100%',
      kpi3Label: 'Corporate governance checklist adherence',
      disasterTitle: 'The Silent $640K Indemnity Omission',
      disasterDesc: 'An autonomous contract redlining agent missed an uncapped liability clause because the vendor submitted an unconventional PDF table layout.',
      lensSave: 'AgenticLens identified the clause extraction anomaly, showing leadership exactly which contract section lacked human verification.',
      chaosSave: 'Agentic-Chaos bombarded the legal pipeline with 50 altered NDAs, conflicting jurisdiction clauses, and corrupted scans.',
      acts: []
    }
  };

  let activeIndustryKey = 'healthcare';
  let currentActIndex = 0;

  // DOM Elements
  const industryPills = document.querySelectorAll('.ind-pill');
  const actTag = document.getElementById('act-tag');
  const actTitle = document.getElementById('act-title');
  const actDesc = document.getElementById('act-desc');
  const actTakeaway = document.getElementById('act-takeaway');
  const stageTitle = document.getElementById('stage-title');
  const stageBadge = document.getElementById('stage-badge');
  const stageCallout = document.getElementById('stage-callout');
  const workflowNodesContainer = document.getElementById('workflow-nodes-container');
  const stepperButtons = document.querySelectorAll('.step-btn');
  const prevBtn = document.getElementById('prev-act-btn');
  const nextBtn = document.getElementById('next-act-btn');

  // Hero elements to update on industry switch
  const heroTagEl = document.getElementById('hero-tag');
  const heroTitleHighlightEl = document.getElementById('hero-title-highlight');
  const kpi1Val = document.getElementById('kpi1-val');
  const kpi1Label = document.getElementById('kpi1-label');
  const kpi2Val = document.getElementById('kpi2-val');
  const kpi2Label = document.getElementById('kpi2-label');
  const kpi3Val = document.getElementById('kpi3-val');
  const kpi3Label = document.getElementById('kpi3-label');

  // Saver showcase elements
  const saverTitleEl = document.getElementById('saver-title');
  const saverDescEl = document.getElementById('saver-desc');
  const saverLensText = document.getElementById('saver-lens-text');
  const saverChaosText = document.getElementById('saver-chaos-text');

  function updateIndustryView(key) {
    activeIndustryKey = key;
    const ind = industryPresets[key];

    // Update Hero
    if (heroTagEl) heroTagEl.textContent = ind.tag;
    if (heroTitleHighlightEl) heroTitleHighlightEl.textContent = ind.titleHighlight;
    if (kpi1Val) kpi1Val.textContent = ind.kpi1;
    if (kpi1Label) kpi1Label.textContent = ind.kpi1Label;
    if (kpi2Val) kpi2Val.textContent = ind.kpi2;
    if (kpi2Label) kpi2Label.textContent = ind.kpi2Label;
    if (kpi3Val) kpi3Val.textContent = ind.kpi3;
    if (kpi3Label) kpi3Label.textContent = ind.kpi3Label;

    // Update Saver Showcase
    if (saverTitleEl) saverTitleEl.textContent = ind.disasterTitle;
    if (saverDescEl) saverDescEl.textContent = ind.disasterDesc;
    if (saverLensText) saverLensText.textContent = ind.lensSave;
    if (saverChaosText) saverChaosText.textContent = ind.chaosSave;

    // Update Pills
    industryPills.forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-industry') === key);
    });

    // Re-render current act
    renderAct(currentActIndex);
  }

  function getActiveActs() {
    return industryPresets.healthcare.acts; // Core detailed walkthrough
  }

  function renderAct(index) {
    const acts = getActiveActs();
    const act = acts[index];
    currentActIndex = index;

    // Update Text Content
    actTag.textContent = act.tag;
    actTag.className = `story-act-tag ${act.tagClass}`;
    actTitle.textContent = act.title;
    actDesc.textContent = act.desc;
    actTakeaway.textContent = act.takeaway;
    stageTitle.textContent = act.stageTitle;
    stageBadge.textContent = act.stageBadge;
    stageBadge.className = `stage-badge-pill ${act.stageBadgeClass}`;
    stageCallout.innerHTML = act.callout;

    // Update Stepper Active State
    stepperButtons.forEach((btn, i) => {
      btn.classList.toggle('active', i === index);
    });

    // Update Nav Buttons
    prevBtn.disabled = index === 0;
    if (index === acts.length - 1) {
      nextBtn.innerHTML = `<span>Start Over</span> <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>`;
    } else {
      nextBtn.innerHTML = `<span>Next Step</span> <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>`;
    }

    // Render Stage Visuals
    workflowNodesContainer.innerHTML = '';

    if (act.showScorecard) {
      // Act 6 Scorecard
      workflowNodesContainer.innerHTML = `
        <div class="exec-scorecard">
          <div class="scorecard-col legacy">
            <div class="scorecard-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Unprotected Automation
            </div>
            <div class="metric-row">
              <span class="metric-label">Silent Error Rate</span>
              <span class="metric-val" style="color: #e11d48;">38.0% Failure</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Erroneous Rejections</span>
              <span class="metric-val" style="color: #e11d48;">19 per month</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Manual Investigation Cost</span>
              <span class="metric-val" style="color: #e11d48;">$180 per claim</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Regulatory Audit Readiness</span>
              <span class="metric-val" style="color: #e11d48;">High Risk (Fail)</span>
            </div>
          </div>

          <div class="scorecard-col hardened">
            <div class="scorecard-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              DeepAgentLabs Certified
            </div>
            <div class="metric-row">
              <span class="metric-label">Silent Error Rate</span>
              <span class="metric-val" style="color: #059669;">0.0% (Zero Failures)</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Erroneous Rejections</span>
              <span class="metric-val" style="color: #059669;">0 (Zero Rejections)</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Manual Investigation Cost</span>
              <span class="metric-val" style="color: #059669;">$0 (Avoided entirely)</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Regulatory Audit Readiness</span>
              <span class="metric-val" style="color: #059669;">100% Certified</span>
            </div>
          </div>
        </div>
      `;
    } else if (act.interactiveChaos) {
      // Act 4 Interactive Chaos Switchboard
      workflowNodesContainer.innerHTML = `
        <div class="chaos-interactive-matrix">
          <div class="matrix-header">
            <h4>Stress-Testing Simulator (Click Any Scenario)</h4>
            <span style="font-size: 0.75rem; color: #0284c7; font-weight: 700;">Simulated Sandboxing</span>
          </div>
          <div class="chaos-toggle-grid" id="chaos-toggle-grid">
            <div class="chaos-toggle-item selected" data-fault="outage">
              <div>
                <div class="chaos-toggle-label">Partner Portal Outage</div>
                <div style="font-size: 0.72rem; color: #64748b;">External 504 Gateway Delay</div>
              </div>
              <div class="chaos-toggle-indicator"></div>
            </div>
            <div class="chaos-toggle-item" data-fault="format">
              <div>
                <div class="chaos-toggle-label">Altered Document Format</div>
                <div style="font-size: 0.72rem; color: #64748b;">Unexpected report schema change</div>
              </div>
              <div class="chaos-toggle-indicator"></div>
            </div>
            <div class="chaos-toggle-item" data-fault="notes">
              <div>
                <div class="chaos-toggle-label">Ambiguous Text Notes</div>
                <div style="font-size: 0.72rem; color: #64748b;">Conflicting clinical narrative</div>
              </div>
              <div class="chaos-toggle-indicator"></div>
            </div>
            <div class="chaos-toggle-item" data-fault="throttle">
              <div>
                <div class="chaos-toggle-label">Peak Traffic Surge</div>
                <div style="font-size: 0.72rem; color: #64748b;">High-volume 5 PM rush throttling</div>
              </div>
              <div class="chaos-toggle-indicator"></div>
            </div>
          </div>
          <div id="chaos-simulation-response">
            <strong>Simulating Partner Portal Outage:</strong> Replaying with Agentic-Chaos. The naive workflow dropped the claim and failed to notify staff. The hardened workflow activated exponential retry and held the claim in the priority doctor queue.
          </div>
        </div>
      `;

      setupChaosInteractiveSwitches();
    } else {
      // Standard Daylight Workflow Nodes
      act.nodes.forEach(node => {
        let nodeClass = 'wf-node';
        if (node.status === 'GLITCH') nodeClass += ' active-glitch';
        else if (node.status === 'HARDENED') nodeClass += ' active-hardened';
        else if (node.status === 'COMPLETED' || node.status === 'VERIFIED') nodeClass += ' active-success';

        const nodeEl = document.createElement('div');
        nodeEl.className = nodeClass;
        nodeEl.innerHTML = `
          <div class="wf-node-left">
            <div class="wf-node-icon">
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="${node.icon}"></path>
              </svg>
            </div>
            <div>
              <div class="wf-node-name">${node.name}</div>
              <div class="wf-node-role">${node.role}</div>
            </div>
          </div>
          <span class="stage-badge-pill ${node.badgeClass}">${node.badge}</span>
        `;
        workflowNodesContainer.appendChild(nodeEl);
      });
    }
  }

  function setupChaosInteractiveSwitches() {
    const items = document.querySelectorAll('.chaos-toggle-item');
    const responseBox = document.getElementById('chaos-simulation-response');

    const descriptions = {
      outage: '<strong>Simulating Partner Portal Outage:</strong> Replaying with Agentic-Chaos. The naive workflow dropped the claim silently. The hardened workflow safely held the claim and scheduled automatic retry.',
      format: '<strong>Simulating Altered Document Format:</strong> Replaying schema mutation. Naive workflow defaulted to 0% and denied treatment. Hardened workflow cross-checked the text notes and verified true eligibility.',
      notes: '<strong>Simulating Ambiguous Text Notes:</strong> Replaying conflicting records. Naive workflow hallucinated an approval. Hardened workflow detected semantic ambiguity and routed to the director.',
      throttle: '<strong>Simulating Peak Traffic Surge:</strong> Replaying rate-limit storm. Naive pipeline crashed with HTTP 429. Hardened pipeline applied graceful jitter backoff without dropping a single packet.'
    };

    items.forEach(item => {
      item.addEventListener('click', () => {
        items.forEach(el => el.classList.remove('selected'));
        item.classList.add('selected');
        const fault = item.getAttribute('data-fault');
        if (responseBox && descriptions[fault]) {
          responseBox.innerHTML = descriptions[fault];
        }
      });
    });
  }

  // Industry Pill Click Listeners
  industryPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const indKey = pill.getAttribute('data-industry');
      updateIndustryView(indKey);
    });
  });

  // Stepper Button Clicks
  stepperButtons.forEach((btn, index) => {
    btn.addEventListener('click', () => {
      renderAct(index);
    });
  });

  // Prev / Next Navigation
  prevBtn.addEventListener('click', () => {
    if (currentActIndex > 0) {
      renderAct(currentActIndex - 1);
    }
  });

  nextBtn.addEventListener('click', () => {
    const acts = getActiveActs();
    if (currentActIndex < acts.length - 1) {
      renderAct(currentActIndex + 1);
    } else {
      renderAct(0);
    }
  });

  // Initial Render
  updateIndustryView('healthcare');
});

  // --- Day / Night Theme Controller ---
  function initThemeToggle() {
    const elBtnTheme = document.getElementById("btn-theme-toggle");
    const elThemeIcon = document.getElementById("theme-icon");
    const elThemeText = document.getElementById("theme-text");
    if (!elBtnTheme) return;

    const savedTheme = localStorage.getItem("deepagentlabs_theme") || "dark";
    if (savedTheme === "light") {
      document.documentElement.setAttribute("data-theme", "light");
      if (elThemeIcon) elThemeIcon.textContent = "🌙";
      if (elThemeText) elThemeText.textContent = "Night Mode";
    }

    elBtnTheme.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme");
      if (currentTheme === "light") {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem("deepagentlabs_theme", "dark");
        if (elThemeIcon) elThemeIcon.textContent = "☀️";
        if (elThemeText) elThemeText.textContent = "Day Mode";
      } else {
        document.documentElement.setAttribute("data-theme", "light");
        localStorage.setItem("deepagentlabs_theme", "light");
        if (elThemeIcon) elThemeIcon.textContent = "🌙";
        if (elThemeText) elThemeText.textContent = "Night Mode";
      }
    });
  }
