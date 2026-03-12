"""
AIGMos v36 — Python-style spec
MODULE: triggers

Purpose:
    Define canonical trigger identity, trigger declaration model,
    trigger evaluation behavior, trigger expression scope,
    onchange / direct / range semantics, pulse behavior,
    and trigger-event interaction boundaries.

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
    ERR_EVAL = "ERR_EVAL"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_STATE = "ERR_STATE"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"


# ---------------------------------------------------------------------
# TRIGGER IDENTITY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TriggerIdentitySpec:
    """
    Canonical trigger identity.

    Examples:
        !sensor.hot
        !mode.auto
        !system:alarm.high
    """
    root_prefix: str = "!"
    segment_separator: str = ":"
    dot_is_segment_separator: bool = False


def trigger_identity_rules() -> List[str]:
    return [
        "!name identifies a trigger",
        "'.' is allowed inside trigger segment text and does not split the path",
        "':' splits trigger path segments",
        "trigger identity must be explicit",
        "duplicate trigger identity is an error unless canonical update mode is explicitly defined",
    ]


# ---------------------------------------------------------------------
# TRIGGER DECLARATION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TriggerDeclarationSpec:
    """
    Canonical trigger declaration model.

    Canonical form:
        trig !name <expr>

    Trigger expressions are allowed only in trig declarations.
    """
    declaration_keyword: str = "trig"
    expression_scope_only: bool = True
    one_trigger_one_expression: bool = True


def trigger_declaration_rules() -> List[str]:
    return [
        "trigger declaration begins with literal keyword 'trig'",
        "canonical form is trig !name <expression>",
        "trigger name must be explicit",
        "one trigger has exactly one canonical expression definition in V1",
        "trigger redefinition without explicit update semantics => ERR_STATE",
        "trigger declaration stores trigger logic; it does not itself execute event bodies",
    ]


def trigger_storage_rules() -> List[str]:
    return [
        "trigger definition is canonical runtime metadata",
        "trigger storage belongs to governed trigger namespace",
        "trigger is not general-purpose data row",
        "trigger definition must remain auditable and explicit",
    ]


# ---------------------------------------------------------------------
# TRIGGER EVALUATION PURPOSE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TriggerEvaluationSpec:
    """
    Canonical trigger evaluation model.

    Core lock:
    - trigger evaluates to boolean/pulse state
    - trigger does not execute commands by itself
    - events observe trigger state/pulse
    """
    result_type: str = "boolean/pulse"
    side_effects: bool = False
    command_invocation_allowed: bool = False
    state_write_allowed: bool = False


def trigger_evaluation_rules() -> List[str]:
    return [
        "trigger evaluates condition to boolean result",
        "trigger may produce pulse/active indication according to runtime policy",
        "trigger does not execute commands by itself",
        "trigger does not mutate state by itself",
        "trigger does not create hidden command output",
        "events observe trigger state/pulse and may launch runner/action through explicit event bindings",
    ]


# ---------------------------------------------------------------------
# TRIGGER TYPES / MODES
# ---------------------------------------------------------------------


class TriggerMode(str, Enum):
    DIRECT = "direct"
    RANGE = "range"
    ONCHANGE = "onchange"
    EXPR = "expr"


def trigger_mode_rules() -> Dict[str, List[str]]:
    return {
        TriggerMode.DIRECT.value: [
            "direct trigger fires/evaluates based on direct comparison to one condition",
            "examples: ==, !=, >=, <=, >, <",
        ],
        TriggerMode.RANGE.value: [
            "range trigger means expression checks a bounded condition",
            "range is still represented through canonical boolean expression, not separate hidden engine magic",
        ],
        TriggerMode.ONCHANGE.value: [
            "onchange trigger reacts to value change",
            "onchange may pulse immediately when change is detected",
            "onchange trigger still does not execute commands directly",
        ],
        TriggerMode.EXPR.value: [
            "expr trigger uses canonical trigger expression grammar",
            "expr mode is the general V36 form and subsumes direct/range logic through expression syntax",
        ],
    }


# ---------------------------------------------------------------------
# PULSE MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TriggerPulseSpec:
    """
    Canonical pulse model.
    """
    default_pulse_ms: int = 100
    onchange_may_be_immediate: bool = True
    trigger_executes_nothing: bool = True


def trigger_pulse_rules() -> List[str]:
    return [
        "trigger itself does nothing except expose condition/pulse state",
        "default trigger pulse is 100ms unless canonical subtype overrides it explicitly",
        "onchange may produce immediate/0ms-style detection boundary according to runtime policy already discussed in canonical history",
        "event engine reads trigger state/pulse and decides event firing",
        "pulse visibility must remain deterministic and auditable",
    ]


def trigger_pulse_interaction_rules() -> List[str]:
    return [
        "event bound to trigger may fire when pulse is 1/active according to event policy",
        "trigger pulse does not itself queue commands directly",
        "trigger reset/return-to-idle is runtime state behavior, not command execution",
    ]


# ---------------------------------------------------------------------
# TRIGGER EXPRESSION / EXACT SCOPE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TriggerExpressionSpec:
    """
    Canonical purpose:
        Evaluate a trigger condition to a boolean result.

    Canonical rule:
        Trigger expressions are allowed only inside trig declarations.
        They never write state and never invoke commands.
    """
    scope: str = "trig declarations only"
    result_type: str = "boolean"
    side_effects: bool = False
    command_invocation_allowed: bool = False
    assignment_allowed: bool = False


def trigger_expr_scope_rules() -> List[str]:
    return [
        "allowed only in trig declarations",
        "not allowed as assignment RHS",
        "not allowed in event body",
        "not allowed in runner command flow",
        "not allowed in loop body as expression language",
        "not allowed inside delay/timeout/wait arguments except as plain command text outside expression parsing",
    ]


def trigger_expr_result_rules() -> List[str]:
    return [
        "expression result must be boolean",
        "expression never returns structured data",
        "expression never writes state",
        "expression never mutates runtime",
        "expression never emits command output",
        "expression never creates hidden commands",
    ]


def trigger_expr_operand_rules() -> List[str]:
    return [
        "allowed operands: numeric literals",
        "allowed operands: numeric $ refs",
        "V1: # refs are not allowed unless later explicitly enabled",
        "string literals are not allowed",
        "boolean literals are not required in V1",
        "missing ref during evaluation => ERR_EVAL",
        "non-numeric ref in numeric context => ERR_TYPE or ERR_EVAL",
    ]


def trigger_expr_operator_rules() -> Dict[str, List[str]]:
    return {
        "arithmetic": ["+", "-", "*", "/"],
        "comparison": ["==", "!=", "<", "<=", ">", ">="],
        "boolean": ["AND", "OR", "XOR", "NOT"],
        "grouping": ["(", ")"],
    }


def trigger_expr_precedence_rules() -> List[str]:
    return [
        "parentheses have highest explicit grouping priority",
        "NOT binds tighter than AND/OR/XOR",
        "arithmetic is evaluated before comparison",
        "comparison is evaluated before boolean composition",
        "AND binds tighter than OR",
        "XOR is evaluated at boolean-composition level",
        "if precedence would be ambiguous to human reader, parentheses are recommended",
    ]


def trigger_expr_arithmetic_rules() -> List[str]:
    return [
        "arithmetic operators are allowed only for numeric operands",
        "division by zero => ERR_EVAL",
        "runtime may evaluate using float-capable numeric semantics",
        "V1 does not guarantee integer-preserving division",
        "implicit string-to-number coercion is not allowed",
        "implicit boolean-to-number coercion is not allowed",
    ]


def trigger_expr_comparison_rules() -> List[str]:
    return [
        "comparison operators return boolean",
        "numeric comparison requires numeric operands",
        "V1 does not define lexicographic string comparison inside trigger expressions",
        "equality/inequality in V1 is intended for numeric results only",
    ]


def trigger_expr_boolean_rules() -> List[str]:
    return [
        "boolean operators compose boolean subexpressions only",
        "AND requires boolean left and right operands",
        "OR requires boolean left and right operands",
        "XOR requires boolean left and right operands",
        "NOT requires one boolean operand",
        "truthiness coercion from arbitrary values is not allowed",
    ]


def trigger_expr_ref_rules() -> List[str]:
    return [
        "$ refs are resolved at evaluation time",
        "ref resolution uses current runtime-visible state",
        "unresolved ref => ERR_EVAL",
        "protected-root read rules still apply normally",
        "trigger expression may read but never write",
    ]


def trigger_expr_failure_behavior_rules() -> List[str]:
    return [
        "syntax failure while defining trigger => ERR_SYNTAX",
        "type mismatch during evaluation => ERR_TYPE or ERR_EVAL",
        "unresolved ref during evaluation => ERR_EVAL",
        "division by zero during evaluation => ERR_EVAL",
        "runtime evaluator failure => ERR_RUNTIME",
        "failed evaluation does not silently become false unless later canonical explicitly chooses that policy",
    ]


def trigger_expr_nonfeatures_v1() -> List[str]:
    return [
        "no function calls",
        "no assignment inside expression",
        "no command invocation",
        "no string concatenation",
        "no arrays",
        "no dictionaries",
        "no regex",
        "no implicit casts",
        "no custom operators",
    ]


# ---------------------------------------------------------------------
# ONCHANGE MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class OnChangeSpec:
    """
    Canonical onchange trigger model.
    """
    compares_against_previous_value: bool = True
    writes_previous_value_hidden_to_surface: bool = False


def onchange_rules() -> List[str]:
    return [
        "onchange means trigger condition is based on value change between previous and current observed state",
        "onchange may pulse immediately when change is detected",
        "previous-value tracking is runtime-internal metadata unless later explicitly exposed",
        "onchange does not itself execute event body",
        "event engine observes onchange trigger pulse like any other trigger pulse",
    ]


# ---------------------------------------------------------------------
# DIRECT / RANGE CONVERGENCE
# ---------------------------------------------------------------------


def trigger_direct_range_convergence_rules() -> List[str]:
    return [
        "direct and range logic are represented through canonical trigger expressions in V36",
        "there is no need for separate hidden comparison engine outside trigger expression grammar",
        "simple threshold examples remain valid through expression form",
        "range examples remain valid through boolean composition and comparisons",
    ]


# ---------------------------------------------------------------------
# TRIGGER / EVENT BOUNDARY
# ---------------------------------------------------------------------


def trigger_event_boundary_rules() -> List[str]:
    return [
        "trigger indicates state/pulse only",
        "event binds trigger to action path",
        "event may launch runner or write state according to event body contract",
        "trigger never directly runs event body by itself without event binding layer",
        "multiple events may observe same trigger unless event-governance policy narrows that later",
    ]


# ---------------------------------------------------------------------
# TRIGGER LIFECYCLE / REDEFINITION
# ---------------------------------------------------------------------


def trigger_lifecycle_rules() -> List[str]:
    return [
        "trigger exists as named runtime definition once declared",
        "duplicate trigger declaration with same identity is ERR_STATE unless explicit replace/update command exists",
        "trigger removal must be explicit if canonical command family provides it",
        "runtime must not silently mutate declared trigger expression",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def trigger_examples_valid() -> List[str]:
    return [
        "trig !sensor.hot $UM.sensor:temp >= 40",
        "trig !sensor.cold $UM.sensor:temp <= 5",
        "trig !delta.big ($UM.a - $UM.b) > 20",
        "trig !power.high ($UM.voltage * $UM.current) > 1000",
        "trig !tank.low ($UM.tank:level / $UM.tank:max) < 0.2",
        "trig !alarm (($UM.temp > 80) AND ($UM.pressure > 120))",
    ]


def trigger_examples_invalid() -> List[str]:
    return [
        'trig !foo $UM.mode == "auto"',
        "trig !foo run %job",
        "trig !foo $UM.x = 5",
        "trig !foo #table:0 > 10",
        "trig !foo ($UM.a / 0) > 1",
        "trig !foo $UM.a + $UM.b",
    ]


def onchange_examples() -> List[str]:
    return [
        "onchange semantics are allowed as trigger mode/policy",
        "event fires only because event observes trigger pulse/state, not because trigger executes command",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


TRIGGERS_SUMMARY = {
    "identity_prefix": "!",
    "declaration_keyword": "trig",
    "trigger_executes_commands": False,
    "trigger_writes_state": False,
    "default_pulse_ms": 100,
    "onchange_may_be_immediate": True,
    "expression": {
        "scope": "trig declarations only",
        "result_type": "boolean",
        "allowed_refs_v1": ["$ numeric refs only"],
        "disallowed_refs_v1": ["# refs", "string refs in expr context"],
        "arithmetic": ["+", "-", "*", "/"],
        "comparison": ["==", "!=", "<", "<=", ">", ">="],
        "boolean": ["AND", "OR", "XOR", "NOT"],
        "grouping": ["(", ")"],
        "side_effects": False,
        "command_invocation": False,
        "assignment_inside_expr": False,
        "implicit_coercion": False,
    },
    "boundary": {
        "trigger_only_indicates": True,
        "event_layer_executes": True,
    },
}
