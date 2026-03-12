"""
AIGMos v36 — Python-style spec
MODULE: spec_manifest

Purpose:
    Define the canonical module grouping for the split Python-style spec.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SpecManifestIdentity:
    spec_name: str = "AIGMos v36 Python-style spec"
    format_name: str = "split python modules"
    production_runtime_code: bool = False


SPEC_MODULES: Dict[str, List[str]] = {
    "core": [
        "identity",
        "core_model",
        "parser_and_grammar",
        "commands",
        "assignment_and_state",
    ],
    "runtime": [
        "triggers",
        "events",
        "runners",
        "loops",
        "time_control",
    ],
    "integration": [
        "q_and_claims",
        "io_and_adapters",
    ],
    "policy": [
        "errors",
        "summary",
    ],
}


def spec_manifest_rules() -> List[str]:
    return [
        "module grouping is documentation structure, not alternate parser behavior",
        "module names are stable canonical identifiers for the split spec",
        "all modules remain part of one canonical spec set",
        "a module may reference another module's rules, but must not silently contradict them",
        "summary is the final aggregate view and should be generated/maintained only after the other modules are aligned",
    ]


def spec_group_rules() -> Dict[str, List[str]]:
    return {
        "core": [
            "defines identity, high-level model, grammar, command surface, and assignment/state rules",
            "core establishes canonical surface rules used by all other modules",
        ],
        "runtime": [
            "defines trigger, event, runner, loop, and time-control behavior",
            "runtime modules must follow core grammar and command-surface rules",
        ],
        "integration": [
            "defines governed command access, Q/Qc/$CH behavior, and adapter/IO boundaries",
            "integration modules must not weaken governance or ownership rules from core/policy",
        ],
        "policy": [
            "defines cross-cutting failure/error model and final summary view",
            "policy modules do not create new runtime behaviors silently",
        ],
    }


def spec_load_order() -> List[str]:
    """
    Recommended human/read order for the split spec.
    """
    return [
        "identity",
        "core_model",
        "parser_and_grammar",
        "commands",
        "assignment_and_state",
        "triggers",
        "events",
        "runners",
        "loops",
        "time_control",
        "q_and_claims",
        "io_and_adapters",
        "errors",
        "summary",
    ]


def spec_dependency_notes() -> Dict[str, List[str]]:
    return {
        "identity": [
            "stands alone",
        ],
        "core_model": [
            "depends conceptually on identity",
        ],
        "parser_and_grammar": [
            "depends on core_model surface philosophy",
        ],
        "commands": [
            "depends on parser_and_grammar command grammar",
            "depends on core_model explicit command-surface philosophy",
        ],
        "assignment_and_state": [
            "depends on parser_and_grammar path grammar",
            "depends on commands for structural state ops vocabulary",
        ],
        "triggers": [
            "depends on parser_and_grammar for trig grammar",
            "depends on assignment_and_state for readable state refs",
        ],
        "events": [
            "depends on triggers",
            "depends on commands/runtime dispatch rules",
        ],
        "runners": [
            "depends on commands and assignment/state field semantics",
        ],
        "loops": [
            "depends on runners",
            "depends on parser_and_grammar sortable-context rules",
        ],
        "time_control": [
            "depends on runners status model",
            "depends on commands runtime-control family",
        ],
        "q_and_claims": [
            "depends on commands governance family",
            "depends on assignment_and_state protected-root/ownership rules",
        ],
        "io_and_adapters": [
            "depends on commands integration family",
            "depends on assignment_and_state protected roots",
        ],
        "errors": [
            "cross-cuts all modules",
        ],
        "summary": [
            "depends on every other module being aligned first",
        ],
    }


def spec_consistency_rules() -> List[str]:
    return [
        "no module may redefine a canonical root prefix differently from another module",
        "no module may broaden expression scope beyond what parser_and_grammar and triggers allow",
        "no module may create hidden commands or hidden result channels",
        "no integration module may bypass gateway/governance rules",
        "no runtime module may bypass ownership/protected-root policy",
        "runner/loop/time-control semantics must stay mutually consistent",
        "summary must reflect other modules, not invent extra behavior",
    ]


def manifest_examples() -> List[str]:
    return [
        "core -> parser_and_grammar",
        "runtime -> runners",
        "integration -> q_and_claims",
        "policy -> errors",
    ]


SPEC_MANIFEST_SUMMARY = {
    "spec_name": "AIGMos v36 Python-style spec",
    "split": True,
    "production_runtime_code": False,
    "groups": SPEC_MODULES,
    "recommended_read_order": spec_load_order(),
}
