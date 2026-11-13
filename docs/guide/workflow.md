# Recommended workflow

## Capture real work

Instrument execution with `trace()` and spans. Record usage from the response that actually occurred, then save the run. The quickstart's counts are synthetic; replace them before using its output for cost decisions.

## Inspect and compare

```
agenticlens inspect run.json
agenticlens compare baseline/ candidate/
```

Populate both directories with actual repeated runs of comparable tasks. Inspect changes in success, duration, token use, and variability. Keep task mix and measurement conditions aligned.

## Review improvements

Use optimization recommendations as proposals. Review projected benefit alongside confidence and quality risk, record which change you adopt, and collect new runs to measure the outcome.

## Use existing trace data

```
agenticlens import-otlp --help
```

Follow the supported OTLP contract and inspect the resulting spans. An arbitrary vendor export may require an adapter. Verify attributes before comparing costs or assigning failure ownership.
