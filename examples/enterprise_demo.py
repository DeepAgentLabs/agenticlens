"""Offline project storage, registry and audit export. No server or external tools run."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agenticlens.enterprise import EnterpriseStore, Project, RegistryEntry, StoragePolicy, digest
from agenticlens.models.trace import Run


def main() -> None:
    with TemporaryDirectory() as directory:
        store = EnterpriseStore(Path(directory) / "lens.db")
        project = Project(organization="demo", name="support")
        policy = StoragePolicy(max_traces=10)
        store.put_run(
            project,
            "offline-example",
            Run(
                application_name="support",
                trace_id="recorded-1",
                run_id="run-1",
                metadata={"email": "example@example.com", "password": "never-store"},
            ),
            policy,
        )
        store.register(
            project,
            "offline-example",
            RegistryEntry(
                kind="prompt",
                name="support",
                version="1",
                content_sha256=digest("synthetic prompt"),
            ),
        )
        exported = store.compliance_export(project, policy)
        assert exported["audit"]["integrity"] == "not_verified"
        assert store.runs(project, policy)[0].metadata["password"] == "[REDACTED]"
        print(
            json.dumps(
                {
                    "project": exported["project"],
                    "traces": len(exported["trace_digests"]),
                    "registry": len(exported["registry"]),
                    "certification": exported["certification"],
                }
            )
        )


if __name__ == "__main__":
    main()
