"""
AIGMos v36 — Python-style spec
MODULE: identity

Purpose:
    Define the canonical identity block for the split Python-style spec.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SpecIdentity:
    """
    Canonical identity of this spec artifact.
    """
    system_name: str = "AIGMos"
    system_expansion: str = "AI Realtime OS"
    system_role: str = "HGI Interface"
    spec_name: str = "AIGMos v36 Python-style spec"
    spec_format: str = "split python modules"
    production_runtime_code: bool = False
    canonical_language: str = "Python-style specification"


@dataclass(frozen=True)
class SystemPurposeSpec:
    """
    Canonical high-level purpose of AIGMos.
    """
    coordinates: Tuple[str, ...] = (
        "humans",
        "AI models",
        "sensors",
        "machines",
        "software systems",
        "nodes",
    )
    deterministic: bool = True
    explicit_command_surface: bool = True
    explicit_state_surface: bool = True


def identity_rules() -> List[str]:
    return [
        "AIGMos means AI Realtime OS",
        "AIGMos acts as an HGI Interface",
        "AIGMos is a runtime and command surface, not merely a protocol adapter",
        "AIGMos coordinates humans, AI models, sensors, machines, software systems, and nodes",
        "the system is deterministic by design",
        "the system exposes explicit symbolic state and explicit governed command execution",
    ]


def spec_identity_rules() -> List[str]:
    return [
        "this artifact is a Python-style specification",
        "this artifact is not production runtime code",
        "the split-module form is documentation structure, not alternate runtime behavior",
        "module boundaries exist for clarity and maintenance, not for changing canonical semantics",
    ]


def naming_rules() -> List[str]:
    return [
        "system name is AIGMos",
        "system expansion is AI Realtime OS",
        "system role is HGI Interface",
        "spec name is AIGMos v36 Python-style spec",
        "module names inside the split spec are stable canonical identifiers",
    ]


def scope_rules() -> List[str]:
    return [
        "identity module defines only canonical identity and scope metadata",
        "identity module does not define parser rules",
        "identity module does not define runtime execution behavior",
        "identity module does not define command contracts",
        "those belong to their dedicated modules",
    ]


def valid_identity_examples() -> List[str]:
    return [
        "AIGMos = AI Realtime OS",
        "AIGMos = HGI Interface",
        "AIGMos v36 Python-style spec = split python modules",
    ]


def invalid_identity_interpretations() -> List[str]:
    return [
        "AIGMos is only an OSC/HTTP bridge",
        "AIGMos is a free-form shell language",
        "this spec file is production runtime implementation",
    ]


IDENTITY_SUMMARY = {
    "system": {
        "name": "AIGMos",
        "expansion": "AI Realtime OS",
        "role": "HGI Interface",
    },
    "spec": {
        "name": "AIGMos v36 Python-style spec",
        "format": "split python modules",
        "production_runtime_code": False,
        "language": "Python-style specification",
    },
    "coordinates": [
        "humans",
        "AI models",
        "sensors",
        "machines",
        "software systems",
        "nodes",
    ],
    "deterministic": True,
    "explicit_command_surface": True,
    "explicit_state_surface": True,
}
