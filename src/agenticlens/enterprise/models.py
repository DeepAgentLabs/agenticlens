"""Lens-local candidate contracts; independent of native trace and AIOS schemas."""

from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    organization: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")

    @property
    def key(self) -> str:
        return f"{self.organization}/{self.name}"


class Credential(BaseModel):
    """Configure SHA-256 digests of random bearer tokens, never plaintext tokens."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    subject: str = Field(min_length=1, max_length=100)
    token_sha256: SecretStr
    project: Project
    role: Literal["reader", "writer", "admin"]


class StoragePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    max_age_days: int = Field(default=30, ge=1, le=3650)
    max_traces: int = Field(default=1000, ge=1, le=100000)
    redact: Literal[True] = True


class RegistryEntry(BaseModel):
    """Immutable metadata; prompt bodies and executable evaluators stay outside the registry."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["model", "prompt"]
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    version: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


def digest(value: str) -> str:
    return sha256(value.encode()).hexdigest()
