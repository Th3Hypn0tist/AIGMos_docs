"""
AIGMos v36 — Python-style spec
MODULE: summary

Purpose:
    Provide the final aggregate summary of the canonical split spec
    without introducing any new behavior.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SummaryIdentity:
    spec_name: str = "AIGMos v36 Python-style spec"
    system_name: str = "AIGMos"
    system_role: str = "AI Realtime OS / HGI Interface"
    production_runtime_code: bool = False


def summary_positioning() -> List[str]:
    return [
        "AIGMos is a deterministic runtime and command surface",
        "AIGMos coordinates humans, AI models, sensors, machines, software systems, and nodes",
        "AIGMos is not a hidden-agent black box",
        "all meaningful behavior is expressed through explicit commands, explicit state, explicit runtime bindings, and explicit adapter boundaries",
    ]


@dataclass(frozen=True)
class SummaryRuntimeChain:
    chain: Tuple[str, ...] = (
        "signals",
        "state",
        "events",
        "execution",
        "actions",
        "signals",
    )


def summary_runtime_rules() -> List[str]:
    return [
        "signals enter the system",
        "state stores the canonical observable symbolic model",
        "triggers evaluate conditions or changes over state",
        "events bind trigger observation to explicit body dispatch",
        "runners execute explicit command payloads step by step",
        "actions update state or emit governed outbound effects",
        "resulting actions may generate new signals",
    ]


SUMMARY_PRIMITIVES: Dict[str, str] = {
    "$": "keyed symbolic state",
    "&": "ordered list space",
    "#": "recursive structured space",
    "!": "trigger namespace",
    "@": "event namespace",
    "%": "runner namespace",
}


def summary_primitive_rules() -> List[str]:
    return [
        "$ is fielded symbolic state",
        "& is ordered payload/list data until consumed",
        "# is recursive structured branch space and supports cell properties",
        "! only indicates trigger state/pulse and does not execute by itself",
        "@ binds trigger observation to explicit dispatch",
        "% is runner state/control space; loops use % and do not create a seventh root family",
    ]


SUMMARY_COMMAND_SURFACE = {
    "philosophy": [
        "all state changes happen through the command surface",
        "parser rejects ambiguity instead of guessing",
        "no hidden commands, no hidden result channels, no silent fallbacks",
    ],
    "command_families": [
        "assignment",
        "structural state operations",
        "trigger declarations",
        "event declarations",
        "runner control",
        "time control",
        "Q / claim / governed integration commands",
        "adapter / IO commands",
        "log and clear operations where canonically defined",
    ],
}


def summary_command_rules() -> List[str]:
    return [
        "commands are explicit and grammar-bound",
        "run %name is valid; run % without target is invalid",
        "list payloads remain data until explicit execution consumes them",
        "quoted command bodies remain canonical where body grammar requires them",
        "no multi-command magic outside canonically defined structures",
    ]


SUMMARY_STATE_MODEL = {
    "ownership": [
        "writes are governed by namespace ownership rules",
        "user modules write only to their own allowed namespace",
        "protected roots remain protected",
    ],
    "shape": [
        "$ prefers fielded symbolic values",
        "# supports structured nested content such as rows, cells, logs, and adapter payloads",
        "& stores ordered items",
    ],
}


def summary_state_rules() -> List[str]:
    return [
        "$UM.sensor:temp is valid fielded state",
        "$UM.sensor = 1 is invalid when a field/key is required by canonical grammar",
        "#SYSTEM:error:log is valid structured-address space",
        "#cell:property = value remains valid canonical syntax",
        "state is explicit, attributable, and auditable",
    ]


SUMMARY_RUNTIME_COMPONENTS = {
    "triggers": [
        "support direct value, range/comparison, and onchange-style observation",
        "trigger represents condition/pulse only",
        "trigger does not itself execute",
    ],
    "events": [
        "bind named trigger observation to explicit body dispatch",
        "event body is explicit command or explicit runner dispatch",
        "event can start runners and loop-owned runners",
    ],
    "runners": [
        "runner is explicit executable runtime payload",
        "runner status/control lives in %runner:status and related fields",
        "runner execution is governed and attributable",
    ],
    "loops": [
        "loop is a runner-oriented execution pattern, not a separate primitive family",
        "loop commonly resets to start/wait/go style behavior",
        "loop-owned state is represented under %",
    ],
}


def summary_runtime_component_rules() -> List[str]:
    return [
        "triggers pulse; events observe; runners execute",
        "events do not replace runners",
        "loops are implemented through runner semantics",
        "runtime components must remain mutually consistent",
    ]


SUMMARY_INTEGRATION_MODEL = {
    "governance": [
        "external and model-facing access goes through governed command surfaces",
        "gateway/choke-point behavior is intentional and canonical",
        "integration must not bypass ownership or policy rules",
    ],
    "q_family": [
        "Q is the current query/model-facing surface",
        "Q aliases may map governed model endpoints",
        "claim/Qc-style behavior remains explicit and attributable",
    ],
    "adapters": [
        "adapters translate external IO into canonical state/actions",
        "adapters do not redefine core semantics",
        "OSC/HTTP/other integrations stay subordinate to canonical command/state rules",
    ],
}


def summary_integration_rules() -> List[str]:
    return [
        "integration expands reach, not authority",
        "adapter traffic must land in canonical symbolic structures",
        "governed surfaces remain the single choke point for accepted command execution",
    ]


SUMMARY_POLICY = {
    "error_model": [
        "errors must be attributable to the causing address or source",
        "syntax errors are rejected explicitly",
        "policy modules do not invent hidden runtime behavior",
    ],
    "logging": [
        "structured logs may be exposed through canonical # paths",
        "error log targets are canonical structured-address objects",
        "clear/show behavior must follow canonical command rules",
    ],
}


def summary_policy_rules() -> List[str]:
    return [
        "error handling must preserve traceability",
        "logging is explicit, not hidden",
        "summary reflects policy; it does not weaken it",
    ]


def summary_invariants() -> List[str]:
    return [
        "deterministic by design",
        "explicit command surface",
        "explicit symbolic state",
        "no hidden memory at command-surface level",
        "no silent fallbacks or parser guessing",
        "no hidden side-effect channels",
        "ownership and protected-root rules must hold everywhere",
        "integration cannot bypass governance",
        "summary cannot invent behavior absent from other modules",
    ]


SUMMARY = {
    "identity": SummaryIdentity(),
    "positioning": summary_positioning(),
    "runtime_chain": SummaryRuntimeChain(),
    "runtime_rules": summary_runtime_rules(),
    "primitives": SUMMARY_PRIMITIVES,
    "primitive_rules": summary_primitive_rules(),
    "command_surface": SUMMARY_COMMAND_SURFACE,
    "command_rules": summary_command_rules(),
    "state_model": SUMMARY_STATE_MODEL,
    "state_rules": summary_state_rules(),
    "runtime_components": SUMMARY_RUNTIME_COMPONENTS,
    "runtime_component_rules": summary_runtime_component_rules(),
    "integration_model": SUMMARY_INTEGRATION_MODEL,
    "integration_rules": summary_integration_rules(),
    "policy": SUMMARY_POLICY,
    "policy_rules": summary_policy_rules(),
    "invariants": summary_invariants(),
}


def summary_guard_rules() -> List[str]:
    return [
        "this module is an aggregate view only",
        "if any detail here conflicts with a canonical source module, the source module wins",
        "summary must be regenerated whenever canonical lower modules change",
        "summary should help human reading, auditing, and implementation alignment",
    ]
