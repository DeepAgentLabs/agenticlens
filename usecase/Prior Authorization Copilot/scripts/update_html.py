import re

HTML_PATH = r'd:\DeepAgentlabs\Prior Authorization Copilot\frontend\index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

new_cards = """            <div class="scenario-cards-list" id="scenario-cards">
              <div class="scenario-card" data-scenario="token_timeout">
                <div class="scenario-header">
                  <span class="scenario-title">LLM / Payer Token Timeout</span>
                  <span class="tag tag-danger">TokenTimeoutFault</span>
                </div>
                <p class="scenario-desc">agentic-chaos: Hangs call 5s then raises TokenTimeoutError. Verifies agent escalates to human without crashing.</p>
                <button class="btn btn-sm btn-warning btn-inject-scenario" data-scenario="token_timeout">Inject &amp; Test</button>
              </div>

              <div class="scenario-card" data-scenario="rate_limit_storm">
                <div class="scenario-header">
                  <span class="scenario-title">Payer API Rate Limit Burst (429)</span>
                  <span class="tag tag-warning">RateLimitStormFault</span>
                </div>
                <p class="scenario-desc">agentic-chaos: Simulates 3 consecutive 429 responses. Verifies agent backs off gracefully.</p>
                <button class="btn btn-sm btn-warning btn-inject-scenario" data-scenario="rate_limit_storm">Inject &amp; Test</button>
              </div>

              <div class="scenario-card" data-scenario="handoff_corruption">
                <div class="scenario-header">
                  <span class="scenario-title">Agent Handoff Payload Corruption</span>
                  <span class="tag tag-info">HandoffCorruptionFault</span>
                </div>
                <p class="scenario-desc">agentic-chaos: Corrupts JSON payload between agents. Verifies downstream agent flags case.</p>
                <button class="btn btn-sm btn-warning btn-inject-scenario" data-scenario="handoff_corruption">Inject &amp; Test</button>
              </div>

              <div class="scenario-card" data-scenario="silent_degradation">
                <div class="scenario-header">
                  <span class="scenario-title">Silent Response Quality Drop</span>
                  <span class="tag tag-danger">SilentDegradationFault</span>
                </div>
                <p class="scenario-desc">agentic-chaos: Returns degraded response silently. Verifies low confidence auto-routes to human review.</p>
                <button class="btn btn-sm btn-warning btn-inject-scenario" data-scenario="silent_degradation">Inject &amp; Test</button>
              </div>

              <div class="scenario-card" data-scenario="tool_call_failure">
                <div class="scenario-header">
                  <span class="scenario-title">Payer API Tool Call Failure</span>
                  <span class="tag tag-danger">ToolCallFailureFault</span>
                </div>
                <p class="scenario-desc">agentic-chaos: Hard failure on payer_api tool call. Verifies submission agent escalates without data loss.</p>
                <button class="btn btn-sm btn-warning btn-inject-scenario" data-scenario="tool_call_failure">Inject &amp; Test</button>
              </div>
            </div>"""

updated = re.sub(
    r'<div class="scenario-cards-list" id="scenario-cards">.*?</div>(?=\s*\n\s*\n\s*<div class="chaos-global-actions)',
    new_cards,
    content,
    flags=re.DOTALL
)

if updated != content:
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(updated)
    print("SUCCESS")
else:
    print("No match - checking content around scenario-cards...")
    idx = content.find('scenario-cards')
    print(repr(content[idx:idx+300]))
