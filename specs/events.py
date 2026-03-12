"""
AIGMos v36 — Python-style spec
MODULE: events

Purpose:
    Define canonical event identity, event declaration model,
    trigger-to-event binding, event body contract, persistence rules,
    and event execution boundaries.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------
# ERROR CODES
# ---------------------------------------------------------------------


class ErrorCode(str, Enum):
    ERR_SYNTAX = "ERR_SYNTAX"
    ERR_TYPE = "ERR_TYPE"
    ERR_STATE = "ERR_STATE"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_OWNERSHIP = "ERR_OWNERSHIP"


# ---------------------------------------------------------------------
# EVENT IDENTITY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class EventIdentitySpec:
    """
    Canonical event identity.

    Examples:
        @cooling.start
        @alarm:shutdown
        @log.sensor.hot
    """
    root_prefix: str = "@"
    segment_separator: str = ":"
    dot_is_segment_separator: bool = False


def event_identity_rules() -> List[str]:
    return [
        "@name identifies an event",
        "'.' is allowed inside event segment text and does not split the path",
        "':' splits event path segments",
        "event identity must be explicit",
        "duplicate event identity is an error unless canonical update mode is explicitly defined",
    ]


# ---------------------------------------------------------------------
# EVENT DECLARATION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class EventDeclarationSpec:
    """
    Canonical event declaration.

    Canonical form:
        on <trigger> <event> <body>

    Example:
        on !sensor.hot @cooling.start "run %runner.cooling"
    """
    declaration_keyword: str = "on"
    explicit_trigger_required: bool = True
    explicit_event_name_required: bool = True
    explicit_body_required: bool = True


def event_declaration_rules() -> List[str]:
    return [
        "event declaration begins with literal keyword 'on'",
        "canonical form is on <trigger> <event> <body>",
        "trigger reference must be explicit",
        "event identity must be explicit",
        "event body must be explicit",
        "event declaration binds one trigger to one event identity and one event body",
        "duplicate event declaration with same identity is ERR_STATE unless explicit replace/update semantics are later defined",
    ]


def event_reference_rules() -> List[str]:
    return [
        "trigger reference in event declaration must resolve to a valid trigger identity or be a valid trigger path awaiting later definition per runtime policy",
        "unknown or invalid trigger reference => ERR_NOT_FOUND or ERR_SYNTAX depending on layer",
        "event declaration does not itself evaluate trigger expression text",
        "event declaration stores binding metadata; it does not execute body immediately",
    ]


# ---------------------------------------------------------------------
# EVENT BODY CONTRACT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class EventBodySpec:
    """
    Canonical event body contract.

    Core lock:
    - event body is explicit executable content
    - event body is either one command line or one explicit state command target,
      according to canonical event rules
    - event body is not a hidden multi-command script
    """
    one_event_one_body: bool = True
    body_is_explicit: bool = True
    hidden_multicommand_expansion: bool = False


def event_body_rules() -> List[str]:
    return [
        "event body must be explicit",
        "event body may be quoted command text when literal command body is intended",
        "event body may reference explicit state/runner command target according to canonical event-body forms",
        "event body must resolve to exactly one executable unit in V1",
        "event body is not a semicolon-chained script",
        "event body is not a free-form expression language",
        "event body must remain auditable and deterministic",
    ]


def event_body_allowed_shapes() -> List[str]:
    return [
        "quoted single command line",
        "explicit single canonical command body",
        "explicit state command target such as $target or &tasklist only when event execution contract for that shape is already canonical",
        "event may start a runner by body command such as run %job",
        "event may write state by explicit body command such as $UM.cooling:state = on",
    ]


def event_body_disallowed_shapes() -> List[str]:
    return [
        "multiple executable commands on one line",
        "implicit command chains",
        "free-form arithmetic expression as event body",
        "hidden macro expansion",
        "side-effecting parser shortcuts not defined canonically",
    ]


# ---------------------------------------------------------------------
# EVENT EXECUTION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class EventExecutionSpec:
    """
    Canonical event execution model.

    Core lock:
    - event does not poll triggers by itself
    - event engine observes trigger pulse/state
    - when firing conditions are met, event dispatches its body
    """
    trigger_observed_externally: bool = True
    body_dispatched_on_fire: bool = True
    hidden_body_rewrite: bool = False


def event_execution_rules() -> List[str]:
    return [
        "event engine observes trigger state/pulse",
        "when firing condition is met, event dispatches its explicit body",
        "event dispatch is deterministic",
        "event dispatch must not rewrite body into hidden extra commands",
        "event does not mutate trigger definition",
        "event firing does not redefine itself",
    ]


def event_dispatch_rules() -> List[str]:
    return [
        "event dispatch produces exactly the effect defined by its body contract",
        "if body launches a runner, that launch is explicit",
        "if body writes state, that write is explicit",
        "event dispatch must pass through normal command-surface/runtime governance",
        "event dispatch must remain auditable",
    ]


def event_fire_condition_rules() -> List[str]:
    return [
        "event fires only when observed trigger condition/pulse meets firing policy",
        "trigger itself does not execute event body directly",
        "event layer is the binding and dispatch layer between trigger and action",
        "multiple events may observe same trigger unless later governance narrows that",
    ]


# ---------------------------------------------------------------------
# PERSISTENCE / LIFECYCLE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class EventLifecycleSpec:
    """
    Canonical event lifecycle model.
    """
    persistent_by_default: bool = True
    self_deletes_after_fire: bool = False
    explicit_remove_required: bool = True


def event_lifecycle_rules() -> List[str]:
    return [
        "event is persistent by default in V1 unless canonical command explicitly creates one-shot semantics later",
        "event does not disappear after execution by default",
        "event removal must be explicit if event removal command family exists",
        "runtime must not silently delete persistent event after firing",
        "event may fire multiple times across multiple trigger pulses according to trigger/event policy",
    ]


def event_redefinition_rules() -> List[str]:
    return [
        "redefining an existing event identity without explicit replace/update mode is ERR_STATE",
        "runtime must not silently merge two event bodies under same event identity",
        "event identity remains stable until explicitly removed or replaced by canonical update command",
    ]


# ---------------------------------------------------------------------
# EVENT / RUNNER / LOOP INTERACTION
# ---------------------------------------------------------------------


def event_runner_interaction_rules() -> List[str]:
    return [
        "event may launch a runner through explicit body command",
        "event may target existing controlled runner state only through explicit canonical commands or %runner:status policy",
        "event must not silently attach hidden commands to a runner body",
        "runner collision rules still apply when event body launches a runner",
    ]


def event_loop_interaction_rules() -> List[str]:
    return [
        "event may launch a loop/runner through explicit body command",
        "loop execution obeys same runner governance and status model",
        "event does not gain special privilege to bypass loop collision/status rules",
    ]


# ---------------------------------------------------------------------
# EVENT / OWNERSHIP / POLICY INTERACTION
# ---------------------------------------------------------------------


def event_policy_rules() -> List[str]:
    return [
        "event body writes are still subject to ownership rules",
        "event body writes to protected roots remain policy-governed",
        "event dispatch does not bypass gateway/choke-point governance",
        "event existence in @ namespace does not grant arbitrary write privilege",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def event_examples_valid() -> List[str]:
    return [
        'on !sensor.hot @cooling.start "run %runner.cooling"',
        'on !sensor.hot @flag.cooling "$UM.cooling:state = on"',
        'on !sensor.changed @log.sensor "delay 100 Q.sensor hot"',
        'on !alarm @shutdown "timeout 5000 %shutdown.sequence"',
    ]


def event_examples_invalid() -> List[str]:
    return [
        "on !sensor.hot",
        "on @cooling.start !sensor.hot run %runner.cooling",
        "on !sensor.hot @cooling.start run %a ; run %b",
        "on !sensor.hot @cooling.start $UM.a + $UM.b",
        "on !sensor.hot @cooling.start",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


EVENTS_SUMMARY = {
    "identity_prefix": "@",
    "declaration_keyword": "on",
    "canonical_form": "on <trigger> <event> <body>",
    "explicit_trigger_required": True,
    "explicit_event_name_required": True,
    "explicit_body_required": True,
    "persistent_by_default": True,
    "self_delete_after_fire": False,
    "trigger_executes_event_directly": False,
    "event_layer_dispatches_body": True,
    "hidden_multicommand_expansion": False,
}
