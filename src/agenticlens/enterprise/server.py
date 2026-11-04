"""Uvicorn factory: configuration is loaded only from an operator-provided local file."""

import os
from pathlib import Path

from agentic_evals import GateConfig
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from agenticlens.enterprise.http import create_enterprise_app
from agenticlens.enterprise.models import Credential, StoragePolicy
from agenticlens.enterprise.store import EnterpriseStore


class ServiceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    credentials: list[Credential] = Field(min_length=1)
    storage_policy: StoragePolicy = Field(default_factory=StoragePolicy)
    gate_policy: GateConfig = Field(default_factory=GateConfig)


def create_app() -> FastAPI:
    config = ServiceConfig.model_validate_json(Path(os.environ["LENS_CONFIG"]).read_bytes())
    store = EnterpriseStore(Path(os.environ["LENS_DATABASE"]))
    return create_enterprise_app(
        store,
        config.credentials,
        storage_policy=config.storage_policy,
        gate_policy=config.gate_policy,
    )
