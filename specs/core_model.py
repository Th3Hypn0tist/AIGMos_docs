"""
AIGMos v36 — Python-style spec
MODULE: core_model

Purpose:
    Define the canonical high-level model of AIGMos:
    identity, runtime chain, primitive families, execution philosophy,
    deterministic surface rules, and system-wide invariants.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------
# SYSTEM IDENTITY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SystemIdentitySpec:
    """
    Canonical system identity.

    AIGMos is a realtime runtime / command surface for coordinating:
    - humans
    - AI models
    - sensors
    - machines
    - software systems
    - nodes

    Canonical positioning:
    - AI Realtime OS
    - HGI Interface
    """
    system_name: str = "AIGMos"
    system_expansion: str = "AI Realtime OS"
    interface_role: str = "HGI Interface"


def identity_rules() -> List[str]:
    return [
        "AIGMos is a runtime and command surface, not just a hardware protocol adapter",
        "AIGMos coordinates humans, AI, sensors, machines, software systems, and nodes",
        "AIGMos is deterministic by design",
        "AIGMos exposes explicit symbolic state and governed command execution",
        "AIGMos is not a hidden-agent orchestration black box",
    ]


# ---------------------------------------------------------------------
# HIGH-LEVEL EXECUTION CHAIN
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class RuntimeChainSpec:
    """
    Canonical runtime chain.

    signals
    -> state
    -> events
    -> execution
    -> actions
    -> signals
    """
    chain: Tuple[str, ...] = (
        "signals",
        "state",
        "events",
        "execution",
        "actions",
        "signals",
    )


def runtime_chain_rules() -> List[str]:
    return [
        "signals enter the system as observable input or generated output feedback",
        "signals become canonical state through explicit writes or adapter ingestion",
        "events observe trigger state/pulse over canonical state",
        "execution dispatches explicit command/runner behavior",
        "actions produce explicit state changes or outbound effects",
        "resulting actions may generate new signals and continue the cycle",
        "the chain is explicit and auditable",
        "the runtime must not insert hidden stages into the canonical model",
    ]


# ---------------------------------------------------------------------
# CORE ARCHITECTURAL PRINCIPLES
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CoreArchitectureSpec:
    """
    Canonical architectural principles.
    """
    deterministic: bool = True
    explicit_state_surface: bool = True
    explicit_command_surface: bool = True
    hidden_memory_allowed: bool = False
    hidden_side_effects_allowed: bool = False
    implicit_magic_allowed: bool = False


def architecture_rules() -> List[str]:
    return [
        "all meaningful behavior happens through explicit state, explicit commands, explicit runtime control, or explicit adapter boundaries",
        "hidden magic is not part of canonical design",
        "no hidden memory is assumed at command-surface level",
        "no hidden side-effect channel is allowed",
        "no implicit fallback/autocorrect/autowiring is allowed unless later canonical explicitly adds it",
        "behavior must remain auditable and replayable in principle",
    ]


def determinism_rules() -> List[str]:
    return [
        "same valid input in same visible state should produce same canonical interpretation",
        "parser must reject ambiguity instead of guessing",
        "runtime must not silently rewrite user intent",
        "execution ordering must remain explicit and stable",
        "generated state must remain attributable to explicit source action",
    ]


# ---------------------------------------------------------------------
# PRIMITIVE FAMILIES
# ---------------------------------------------------------------------


class PrimitiveFamily(str, Enum):
    KV = "$"
    LIST = "&"
    TREE = "#"
    TRIGGER = "!"
    EVENT = "@"
    RUNNER = "%"


@dataclass(frozen=True)
class PrimitiveModelSpec:
    """
    Canonical primitive-family model.

    There are six canonical root families:
    - $
    - &
    - #
    - !
    - @
    - %
    """
    primitive_roots: Tuple[str, ...] = (
        PrimitiveFamily.KV.value,
        PrimitiveFamily.LIST.value,
        PrimitiveFamily.TREE.value,
        PrimitiveFamily.TRIGGER.value,
        PrimitiveFamily.EVENT.value,
        PrimitiveFamily.RUNNER.value,
    )


def primitive_family_rules() -> Dict[str, List[str]]:
    return {
        PrimitiveFamily.KV.value: [
            "$ is keyed symbolic scalar/state space",
            "$ canonical write shape is fielded, such as $UM.sensor:temp",
            "$ is the primary symbolic KV namespace",
        ],
        PrimitiveFamily.LIST.value: [
            "& is ordered item/list space",
            "& stores step lists, command lists, and other ordered payloads",
            "& is data until explicit execution consumes it",
        ],
        PrimitiveFamily.TREE.value: [
            "# is recursive structured branch space",
            "# supports rows, cells, properties, logs, adapter payloads, and general nested output",
            "#cell:property = value must remain valid",
        ],
        PrimitiveFamily.TRIGGER.value: [
            "! identifies triggers",
            "trigger namespace is governed runtime-definition space",
            "trigger indicates condition/pulse only; it does not execute commands directly",
        ],
        PrimitiveFamily.EVENT.value: [
            "@ identifies events",
            "event namespace is governed runtime-binding space",
            "event binds trigger observation to explicit body dispatch",
        ],
        PrimitiveFamily.RUNNER.value: [
            "% identifies runners and loop-owned runner state",
            "%runner:status is canonical control/status field",
            "loop uses % namespace and is not a separate root family",
        ],
    }


def primitive_global_rules() -> List[str]:
    return [
        "primitive family is determined by root prefix",
        "families must not silently collapse into each other",
        "family-specific semantics are explicit",
        "parser/runtime must not reinterpret one family as another without explicit command contract",
    ]


# ---------------------------------------------------------------------
# STRING-FIRST SYMBOLIC SURFACE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SymbolicSurfaceSpec:
    """
    Canonical data-surface model.

    Core lock:
    - canonical surface is symbolic and string-first
    - runtime may interpret values by context
    - hidden implementation objects must not leak into canonical surface
    """
    string_first_surface: bool = True
    hidden_runtime_objects_exposed: bool = False
    implicit_json_object_magic: bool = False


def symbolic_surface_rules() -> List[str]:
    return [
        "canonical surface is symbolic and string-first",
        "stored values may represent text, paths, command lines, status literals, or structured content by context",
        "runtime may keep richer private implementation structures internally",
        "those private structures must not leak directly into canonical surface unless explicitly canonicalized",
        "parser and command contracts decide interpretation; there is no universal hidden object coercion layer",
    ]


# ---------------------------------------------------------------------
# COMMAND SURFACE PHILOSOPHY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommandSurfacePhilosophySpec:
    """
    Canonical command-surface philosophy.
    """
    explicit_governed_surface: bool = True
    shell_language: bool = False
    freeform_dsl: bool = False
    hidden_command_registration: bool = False


def command_surface_philosophy_rules() -> List[str]:
    return [
        "AIGMos command surface is explicit and governed",
        "it is not a general-purpose shell",
        "it is not a hidden macro engine",
        "it is not a free-form expression language",
        "commands do exactly what their contract says and nothing more",
        "command invocation remains traceable through one governed surface",
    ]


# ---------------------------------------------------------------------
# STATE / EVENT / EXECUTION SEPARATION
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SeparationOfConcernsSpec:
    """
    Canonical separation of concerns.
    """
    trigger_executes_commands: bool = False
    event_dispatches_actions: bool = True
    runner_executes_steps: bool = True
    adapter_bypasses_runtime: bool = False


def separation_rules() -> List[str]:
    return [
        "triggers evaluate condition/pulse only",
        "events bind trigger observation to explicit body dispatch",
        "runners execute stepwise command flow",
        "loops expand into runner-owned step execution",
        "adapters move signals/data across boundaries but do not bypass runtime governance",
        "assignment writes state but does not itself become a general computation engine",
    ]


# ---------------------------------------------------------------------
# EXPLICITNESS / NO HIDDEN MAGIC
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ExplicitnessSpec:
    """
    Canonical explicitness model.
    """
    hidden_autowiring: bool = False
    hidden_retry: bool = False
    hidden_scheduler: bool = False
    hidden_macro_expansion: bool = False
    hidden_parallelism: bool = False


def explicitness_rules() -> List[str]:
    return [
        "no hidden autowiring",
        "no hidden retry policy by default",
        "no hidden scheduler semantics beyond explicit time-control commands",
        "no hidden macro expansion",
        "no hidden command chaining",
        "no hidden parallel step execution inside one runner in V1",
        "no hidden output channels",
    ]


# ---------------------------------------------------------------------
# AUDITABILITY / REPLAYABILITY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class AuditabilitySpec:
    """
    Canonical auditability model.
    """
    auditable: bool = True
    attributable: bool = True
    replay_or_reconstruct_in_principle: bool = True


def auditability_rules() -> List[str]:
    return [
        "state changes should be attributable to explicit commands, runtime actions, or adapter writes",
        "runner status transitions must be observable",
        "error handling must be explicit",
        "governed aliases and claims must remain auditable",
        "system should be replayable or reconstructable in principle from canonical state and execution history",
    ]


# ---------------------------------------------------------------------
# GOVERNANCE / OWNERSHIP / POLICY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class GovernanceSpec:
    """
    Canonical governance model.
    """
    protected_roots_exist: bool = True
    ownership_model_exists: bool = True
    single_choke_point: bool = True


def governance_rules() -> List[str]:
    return [
        "protected roots exist",
        "ownership model exists for writes and governed actions",
        "command surface has one choke point",
        "aliases and claims are governance constructs, not parser accidents",
        "usermodules do not bypass governed command surface when invoking commands",
        "policy controls write access to protected and special namespaces",
    ]


# ---------------------------------------------------------------------
# TIME / CONTROL / STATUS PHILOSOPHY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ControlPhilosophySpec:
    """
    Canonical control philosophy.
    """
    runner_status_driven_control: bool = True
    explicit_time_control: bool = True
    time_unit_ms: bool = True


def control_rules() -> List[str]:
    return [
        "runner control is primarily expressed through %runner:status contract",
        "cancel/abort/stop are statuses/control outcomes, not separate canonical command family in V36",
        "time control is explicit through wait/delay/timeout",
        "time control uses integer milliseconds at canonical surface",
        "time semantics must never run earlier than requested",
    ]


# ---------------------------------------------------------------------
# NONFEATURES / EXPLICIT LIMITS
# ---------------------------------------------------------------------


def nonfeatures_v1() -> List[str]:
    return [
        "no global expression language",
        "no hidden agent mesh",
        "no implicit AI orchestration semantics",
        "no free-form shell compatibility layer",
        "no automatic background task model outside explicit runtime/time-control constructs",
        "no uncontrolled adapter command tunneling",
        "no implicit cross-namespace write privilege",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID INTERPRETATION EXAMPLES
# ---------------------------------------------------------------------


def valid_interpretation_examples() -> List[str]:
    return [
        "signal arrives through adapter -> canonical state write -> trigger observes -> event dispatches -> runner executes",
        "$ stores symbolic state",
        "& stores ordered data/steps",
        "# stores structured branches and properties",
        "! indicates trigger",
        "@ indicates event binding",
        "% indicates runner/loop execution identity",
    ]


def invalid_interpretation_examples() -> List[str]:
    return [
        "trigger executes command directly without event layer",
        "assignment is treated as universal arithmetic language",
        "loop creates a seventh root family",
        "adapter bypasses command/runtime governance through hidden backdoor execution",
        "parser silently invents commands or aliases",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


CORE_MODEL_SUMMARY = {
    "system_identity": {
        "name": "AIGMos",
        "expansion": "AI Realtime OS",
        "role": "HGI Interface",
    },
    "runtime_chain": [
        "signals",
        "state",
        "events",
        "execution",
        "actions",
        "signals",
    ],
    "architecture": {
        "deterministic": True,
        "explicit_state_surface": True,
        "explicit_command_surface": True,
        "hidden_memory_allowed": False,
        "hidden_side_effects_allowed": False,
        "implicit_magic_allowed": False,
    },
    "primitive_roots": ["$", "&", "#", "!", "@", "%"],
    "symbolic_surface": {
        "string_first_surface": True,
        "hidden_runtime_objects_exposed": False,
    },
    "separation": {
        "trigger_executes_commands": False,
        "event_dispatches_actions": True,
        "runner_executes_steps": True,
        "adapter_bypasses_runtime": False,
    },
    "governance": {
        "protected_roots_exist": True,
        "ownership_model_exists": True,
        "single_choke_point": True,
    },
    "control": {
        "runner_status_driven_control": True,
        "explicit_time_control": True,
        "time_unit": "ms",
    },
}
