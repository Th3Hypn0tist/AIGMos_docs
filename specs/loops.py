"""
AIGMos v36 — Python-style spec
MODULE: loops

Purpose:
    Define canonical loop identity, loop creation model,
    template/list/table expansion, row normalization rules,
    loop-runner relationship, and loop execution boundaries.

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


# ---------------------------------------------------------------------
# LOOP IDENTITY / RELATION TO RUNNER
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class LoopIdentitySpec:
    """
    Canonical loop identity model.

    Core lock:
    - loop is implemented through % runner space
    - loop is not a separate root family
    - loop creates/uses a named runner identity
    """
    runner_root_prefix: str = "%"
    separate_loop_root_exists: bool = False
    loop_is_runner: bool = True


def loop_identity_rules() -> List[str]:
    return [
        "loop is a runner-form execution model",
        "loop identity lives under % namespace",
        "loop does not introduce a new root family",
        "loop %jobs and runner %jobs share the same identity space",
        "runner collision rules apply to loop names exactly as to any other runner",
    ]


def loop_runner_equivalence_rules() -> List[str]:
    return [
        "loop produces/uses a named runner instance",
        "loop status is governed by %runner:status contract",
        "loop obeys same run/pause/stop/cancel/abort/error/ok lifecycle",
        "loop may expose %name:step just like other runners where runtime surfaces it",
        "loop is cluster-ready by nature only through explicit runner/event architecture, not through hidden magic",
    ]


# ---------------------------------------------------------------------
# LOOP CREATION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class LoopCreationSpec:
    """
    Canonical loop creation model.

    Canonical concept:
    - loop prepares executable step data from template/list/table input
    - prepared execution is owned by a named runner
    """
    explicit_name_required: bool = True
    implicit_name_generation: bool = False
    duplicate_name_allowed: bool = False


def loop_creation_rules() -> List[str]:
    return [
        "loop name must be explicit",
        "loop must not silently auto-generate canonical runner names in V1",
        "creating loop with existing %name is ERR_STATE",
        "loop creation must not silently overwrite existing runner/loop state",
        "loop creation prepares executable step data but does not bypass runner governance",
    ]


# ---------------------------------------------------------------------
# LOOP INPUT MODEL
# ---------------------------------------------------------------------


class LoopInputKind(str, Enum):
    LIST = "&"
    TABLE = "#"
    TEMPLATE = "$"


@dataclass(frozen=True)
class LoopInputSpec:
    """
    Canonical loop input model.

    Supported concepts:
    - steps from &list
    - steps from #table rows
    - optional $template merged with step rows/items
    """
    supports_list_input: bool = True
    supports_table_input: bool = True
    supports_template_input: bool = True


def loop_input_rules() -> List[str]:
    return [
        "loop input may come from & list data",
        "loop input may come from # structured rows when command/runtime context explicitly treats them as loop rows",
        "loop may use $template in addition to list/table step data",
        "loop input is data until expanded into runner step commands",
        "loop input must remain explicit and auditable",
    ]


def loop_template_rules() -> List[str]:
    return [
        "$template may contain one or more command fragments/constant fields according to loop contract",
        "template is not executed directly at declaration time",
        "template contributes constant structure to each produced step",
        "all template-driven parallel sources must be length-compatible when canonical loop mode requires that",
        "length mismatch in locked same-length mode => ERR_STATE or ERR_RUNTIME",
    ]


# ---------------------------------------------------------------------
# LOOP EXPANSION / NORMALIZATION
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class LoopExpansionSpec:
    """
    Canonical loop expansion model.

    Core lock:
    - each produced loop step resolves to one command line
    - no hidden extra command creation
    """
    one_output_step_one_command: bool = True
    hidden_command_expansion: bool = False
    deterministic_normalization: bool = True


def loop_expansion_rules() -> List[str]:
    return [
        "loop expands data into runner step commands deterministically",
        "each produced output step must be exactly one command line",
        "loop must not silently generate extra hidden steps",
        "loop must not silently drop valid rows/items",
        "loop output is ordered and auditable",
    ]


def loop_list_rules() -> List[str]:
    return [
        "& list input is read in numeric ascending order in sortable contexts",
        "each & item may represent one command line or one step fragment according to loop mode",
        "non-numeric sortable key in list context => ERR_SYNTAX",
    ]


def loop_table_rules() -> List[str]:
    return [
        "# table/row input is valid only where command/runtime explicitly treats branch as loop-table context",
        "row keys are read in numeric ascending order in sortable row contexts",
        "non-numeric key in sortable row context => ERR_SYNTAX",
        "general # namespace remains allowed to have non-numeric names outside sortable loop context",
    ]


def loop_row_normalization_rules() -> List[str]:
    return [
        "when a # row is converted into one command, child cells are read in numeric ascending order",
        "each cell value is trimmed",
        "empty cell values are removed from normalized command assembly",
        "remaining cell fragments are joined with single space",
        "result is exactly one normalized command line",
        "normalization must never reorder cells except by canonical numeric sorting",
    ]


def loop_template_merge_rules() -> List[str]:
    return [
        "template merge is explicit loop behavior, not generic '=' behavior",
        "template constants are applied to each produced step according to loop mode",
        "template and step payloads must merge deterministically",
        "template merge must not invent hidden fields beyond declared loop contract",
    ]


# ---------------------------------------------------------------------
# LOOP OUTPUT / RUNNER BINDING
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class LoopOutputSpec:
    """
    Canonical loop output model.
    """
    output_runner_owned: bool = True
    supports_explicit_output_target: bool = True
    hidden_output_branch: bool = False


def loop_output_rules() -> List[str]:
    return [
        "loop produces execution owned by named %runner",
        "loop may expose output through explicit %name:output or caller-supplied target where command contract allows",
        "loop must not invent hidden output branches",
        "loop-expanded step list remains part of runner-owned execution model",
    ]


def loop_step_visibility_rules() -> List[str]:
    return [
        "runtime may expose active/current step under %name:step",
        "runtime may expose prepared steps in runner-owned storage if command contract allows",
        "exposed step data must remain deterministic and auditable",
        "implementation-private metadata must not leak as arbitrary canonical fields",
    ]


# ---------------------------------------------------------------------
# EXECUTION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class LoopExecutionSpec:
    """
    Canonical loop execution model.

    Core lock:
    - loop executes through runner semantics
    - loop is continuous by nature, but may reset to waiting start state
    """
    executes_through_runner: bool = True
    implicit_parallel_step_execution: bool = False
    may_reset_to_start_state: bool = True


def loop_execution_rules() -> List[str]:
    return [
        "loop executes through normal runner step engine",
        "loop step progression is sequential unless later canonical adds explicit parallel mode",
        "loop may prepare many steps, but executes them through runner governance",
        "loop may reset itself to waiting/start state according to loop control policy",
        "loop does not bypass event/runner/error/status models",
    ]


def loop_reset_rules() -> List[str]:
    return [
        "loop may be designed to reset to start and wait for go/run signal",
        "reset/waiting behavior is represented through runner fields/status, not hidden daemon magic",
        "pause and stop semantics still follow runner contract",
        "loop reset must remain explicit in runtime behavior",
    ]


def loop_status_rules() -> List[str]:
    return [
        "%loop:status = run => active execution",
        "%loop:status = pause => freeze progression",
        "%loop:status = cancel => graceful termination at safe boundary",
        "%loop:status = abort => immediate termination",
        "%loop:status = stop => controlled halt",
        "%loop:status = ok => normal completion",
        "%loop:status = error => failed completion",
    ]


# ---------------------------------------------------------------------
# COLLISION / RESUME RULES
# ---------------------------------------------------------------------


def loop_collision_rules() -> List[str]:
    return [
        "loop name collision with any existing runner/loop of same %name => ERR_STATE",
        "paused loop is resumed by %name:status = run, not by creating same-name loop again",
        "terminal loop is not revived in V1",
        "restarting after terminal state requires a new runner/loop instance, not magical resurrection",
    ]


def loop_resume_rules() -> List[str]:
    return [
        "resume in V1 means PAUSE -> RUN only",
        "STOP/OK/CANCEL/ABORT/ERROR do not resume",
        "loop declaration command must not be reused as hidden resume shortcut",
    ]


# ---------------------------------------------------------------------
# LOOP / TIME CONTROL INTERACTION
# ---------------------------------------------------------------------


def loop_time_control_rules() -> List[str]:
    return [
        "wait inside loop blocks current loop-runner step only",
        "delay inside loop schedules one future command and does not block current step",
        "timeout may apply to loop runner just like any other runner",
        "pause freezes active wait remaining time inside loop",
        "timeout countdown continues during pause in V1",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def loop_examples_valid() -> List[str]:
    return [
        "loop %jobs &tasks",
        "loop %jobs #table",
        "loop %jobs $template &steps",
        "loop %jobs $template #rows",
        "%jobs:status = pause",
        "%jobs:status = run",
    ]


def loop_examples_invalid() -> List[str]:
    return [
        "loop &tasks",
        "loop %jobs",
        "loop %jobs run %other ; wait 100",
        "loop %jobs #rows   # invalid if sortable row keys are non-numeric in loop-row context",
        "loop %jobs        # invalid if %jobs already exists",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


LOOPS_SUMMARY = {
    "separate_loop_root_exists": False,
    "loop_is_runner": True,
    "identity_root": "%",
    "inputs": {
        "supports_list": True,
        "supports_table": True,
        "supports_template": True,
    },
    "expansion": {
        "one_output_step_one_command": True,
        "hidden_command_expansion": False,
        "row_normalization": {
            "sort_numeric": True,
            "trim_cells": True,
            "drop_empty": True,
            "join_with_single_space": True,
        },
    },
    "execution": {
        "through_runner": True,
        "implicit_parallel_step_execution": False,
        "may_reset_to_start_state": True,
    },
    "resume_rule_v1": "only PAUSE -> RUN",
    "collision_policy": "same %name always collides",
}
