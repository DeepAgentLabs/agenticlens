"""Record per-trial outputs for the support experiment's four variants.

This stands in for running real agents: each simulated variant answers the
suite's cases with a fixed per-case success probability, latency, and cost,
drawn from a seeded RNG so the recorded files are reproducible. The files it
writes in ./recorded are what `support-experiment.yaml` replays.

    python examples/experiments/record_trials.py

In a real project you would save each live trial's samples instead (for
example `agenticlens evaluate-live --save`), then replay them the same way.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
TRIALS = 6

GOOD_ANSWERS = {
    "refund-window": ("You can request a refund within 30 days.", ["policy_lookup"]),
    "refund-damaged": ("Sorry! I've arranged a replacement.", ["order_lookup"]),
    "escalate-legal": ("I've escalated this to our legal team.", ["handoff"]),
    "shipping-eta": ("It arrives in 3-5 business days.", ["order_lookup"]),
    "password-reset": ("Use the reset link on the sign-in page.", []),
}
BAD_ANSWERS = {
    "refund-window": ("You can request a refund soon.", []),
    "refund-damaged": ("Please contact support.", []),
    "escalate-legal": ("I've issued your refund.", ["issue_refund"]),
    "shipping-eta": ("It will arrive shortly.", []),
    "password-reset": ("Please contact support.", []),
}

# variant -> (per-case success probability, mean latency ms, cost per case USD)
VARIANTS: dict[str, tuple[dict[str, float], float, float]] = {
    "baseline": (
        {
            "refund-window": 0.95,
            "refund-damaged": 0.9,
            "escalate-legal": 0.95,
            "shipping-eta": 0.9,
            "password-reset": 1.0,
        },
        1400.0,
        0.0042,
    ),
    "small-model": (
        {
            "refund-window": 0.9,
            "refund-damaged": 0.6,
            "escalate-legal": 0.7,
            "shipping-eta": 0.85,
            "password-reset": 1.0,
        },
        650.0,
        0.0009,
    ),
    "terse-prompt": (
        {
            "refund-window": 0.5,
            "refund-damaged": 0.85,
            "escalate-legal": 0.9,
            "shipping-eta": 0.5,
            "password-reset": 0.95,
        },
        1100.0,
        0.0031,
    ),
    "reranked-retrieval": (
        {
            "refund-window": 1.0,
            "refund-damaged": 0.95,
            "escalate-legal": 0.95,
            "shipping-eta": 0.95,
            "password-reset": 1.0,
        },
        1700.0,
        0.0048,
    ),
}


def _sample(
    case_id: str,
    rng: random.Random,
    profile: tuple[dict[str, float], float, float],
    variant: str,
    trial: int,
) -> dict[str, Any]:
    success_rates, latency, cost = profile
    output, tools = (GOOD_ANSWERS if rng.random() < success_rates[case_id] else BAD_ANSWERS)[
        case_id
    ]
    return {
        "case_id": case_id,
        "output": output,
        "trace": {
            "trace_id": f"{variant}-t{trial}-{case_id}",
            "total_latency_ms": round(rng.gauss(latency, latency * 0.1), 1),
            "estimated_cost_usd": cost,
            "cost_source": "estimated",
            "spans": [{"tool_name": tool} for tool in tools],
            "metadata": {"variant": variant, "trial": trial},
        },
    }


def main() -> None:
    out = HERE / "recorded"
    out.mkdir(exist_ok=True)
    for index, (variant, profile) in enumerate(VARIANTS.items()):
        rng = random.Random(1000 + index)
        trials = [
            {
                "samples": [
                    _sample(case_id, rng, profile, variant, trial) for case_id in GOOD_ANSWERS
                ]
            }
            for trial in range(1, TRIALS + 1)
        ]
        path = out / f"{variant}.json"
        path.write_text(json.dumps({"variant": variant, "trials": trials}, indent=2) + "\n")
        print(f"Recorded {TRIALS} trials for {variant} -> {path.relative_to(HERE)}")


if __name__ == "__main__":
    main()
