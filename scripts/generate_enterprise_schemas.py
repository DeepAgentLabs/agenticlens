"""Generate candidate configuration/registry schemas; run from the repository root."""

import json
from pathlib import Path

from agenticlens.enterprise.models import Project, RegistryEntry, StoragePolicy
from agenticlens.enterprise.server import ServiceConfig

for name, model in (
    ("project", Project),
    ("registry-entry", RegistryEntry),
    ("storage-policy", StoragePolicy),
    ("service-config", ServiceConfig),
):
    schema = model.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"https://deepagentlabs.io/agenticlens/enterprise/1-candidate/{name}.json"
    Path(f"schemas/enterprise/{name}.json").write_text(json.dumps(schema, indent=2) + "\n")
