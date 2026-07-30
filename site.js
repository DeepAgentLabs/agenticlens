const tabs = [...document.querySelectorAll("[data-tab]")];
const copyButton = document.querySelector("#copy-install");
const judgeToggle = document.querySelector("#judge-toggle");
const judgeScore = document.querySelector("#judge-score");
const averageScore = document.querySelector("#average-score");
const threshold = document.querySelector("#gate-threshold");
const thresholdValue = document.querySelector("#threshold-value");
const gateOrb = document.querySelector("#gate-orb");
const gateTitle = document.querySelector("#gate-title");
const gateCopy = document.querySelector("#gate-copy");
const gateBar = document.querySelector("#gate-bar");

function selectTab(name) {
  tabs.forEach((tab) => {
    const active = tab.dataset.tab === name;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
  document.querySelectorAll("[data-output]").forEach((panel) => {
    panel.hidden = panel.dataset.output !== name;
  });
}

function observedScore() {
  return judgeToggle?.checked ? 95 : 100;
}

function updateEvaluation() {
  const enabled = Boolean(judgeToggle?.checked);
  if (judgeScore) judgeScore.hidden = !enabled;
  if (averageScore) averageScore.textContent = enabled ? "0.95" : "1.00";
  updateGate();
}

function updateGate() {
  const required = Number(threshold?.value || 90);
  const observed = observedScore();
  const passed = observed >= required;
  if (thresholdValue) thresholdValue.textContent = `${required}%`;
  if (gateCopy) gateCopy.textContent = `Observed ${observed}% · Required ${required}%`;
  if (gateTitle) gateTitle.textContent = passed ? "Ready to ship" : "Gate blocked";
  if (gateOrb) {
    gateOrb.textContent = passed ? "✓" : "!";
    gateOrb.classList.toggle("passed", passed);
    gateOrb.classList.toggle("failed", !passed);
  }
  if (gateBar) gateBar.style.width = `${observed}%`;
}

tabs.forEach((tab) => tab.addEventListener("click", () => selectTab(tab.dataset.tab)));
judgeToggle?.addEventListener("change", updateEvaluation);
threshold?.addEventListener("input", updateGate);
copyButton?.addEventListener("click", async () => {
  await navigator.clipboard?.writeText("pip install agenticlens");
  copyButton.querySelector("span").textContent = "✓";
  setTimeout(() => { copyButton.querySelector("span").textContent = "⧉"; }, 1400);
});
