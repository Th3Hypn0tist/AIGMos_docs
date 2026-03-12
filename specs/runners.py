"""
AIGMos v36 — Python-style spec
MODULE: runners

Purpose:
    Define canonical runner identity, runner fields, runner lifecycle,
    status transitions, safe-boundary behavior, execution rules,
    collision policy, resume rules, and loop-runner interaction.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------
# ERROR CODES
# ---------------------------------------------------------------------


class ErrorCode(str, Enum):
    ERR_SYNTAX = "ERR_SYNTAX"
    ERR_TYPE = "ERR_TYPE"
    ERR_STATE = "ERR_STATE"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_TIMEOUT = "ERR_TIMEOUT"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"


# ---------------------------------------------------------------------
# RUNNER STATUS MODEL
# ---------------------------------------------------------------------


class RunnerStatus(str, Enum):
    RUN = "run"
    OK = "ok"
    STOP = "stop"
    CANCEL = "cancel"
    ABORT = "abort"
    ERROR = "error"
    PAUSE = "pause"


RUNNER_STATUS_NUMERIC_COMPAT = {
    "run": 0,
    "ok": 1,
    "stop": 2,
    "error": 3,
    "pause": 4,
    # cancel / abort are canonical symbolic statuses;
    # numeric mapping is intentionally not locked in v36.
}


@dataclass(frozen=True)
class RunnerStatusModelSpec:
    """
    Canonical runner status model.

    Symbolic statuses are canonical.
    Numeric mapping may exist for compatibility/runtime internals.
    """
    canonical_statuses: Tuple[str, ...] = (
        RunnerStatus.RUN.value,
        RunnerStatus.OK.value,
        RunnerStatus.STOP.value,
        RunnerStatus.CANCEL.value,
        RunnerStatus.ABORT.value,
        RunnerStatus.ERROR.value,
        RunnerStatus.PAUSE.value,
    )
    active_state: str = RunnerStatus.RUN.value
    suspend_state: str = RunnerStatus.PAUSE.value


def runner_status_meanings() -> Dict[str, str]:
    return {
        RunnerStatus.RUN.value: "runner is active and eligible to execute steps",
        RunnerStatus.OK.value: "runner completed normally",
        RunnerStatus.STOP.value: "runner halted in controlled stop path and will not continue",
        RunnerStatus.CANCEL.value: "runner received graceful cancellation request and must stop at safe boundary",
        RunnerStatus.ABORT.value: "runner received immediate hard-stop termination request",
        RunnerStatus.ERROR.value: "runner terminated due to failure",
        RunnerStatus.PAUSE.value: "runner is suspended and may later resume",
    }


def runner_terminal_statuses() -> Set[str]:
    return {
        RunnerStatus.OK.value,
        RunnerStatus.STOP.value,
        RunnerStatus.CANCEL.value,
        RunnerStatus.ABORT.value,
        RunnerStatus.ERROR.value,
    }


def runner_nonterminal_statuses() -> Set[str]:
    return {
        RunnerStatus.RUN.value,
        RunnerStatus.PAUSE.value,
    }


# ---------------------------------------------------------------------
# RUNNER IDENTITY / FIELDS
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class RunnerIdentitySpec:
    """
    Canonical runner identity.

    Examples:
        %job
        %cooling.sequence
        %batch:status
    """
    root_prefix: str = "%"
    segment_separator: str = ":"
    dot_is_segment_separator: bool = False


CANONICAL_RUNNER_FIELDS = (
    "status",
    "step",
    "input",
    "output",
    "template",
    "origin",
    "mode",
)


def runner_identity_rules() -> List[str]:
    return [
        "%name identifies a runner/loop root",
        "%name:status is canonical status field",
        "%name:step is canonical step field where step-tracking is exposed",
        "%name:input may be used where runner/loop command family defines input binding",
        "%name:output may be used where runner/loop command family defines output binding",
        "%name:template may be used where loop/template semantics define it",
        "'.' is allowed inside runner name segment and does not split path",
        "':' splits fields/segments",
    ]


def runner_field_rules() -> List[str]:
    return [
        "runner field names are canonical surface fields, not arbitrary implementation leaks",
        "runtime may keep more internal metadata privately, but it must not appear as canonical writable surface unless explicitly specced",
        "unknown runner field write => ERR_STATE or ERR_SYNTAX",
        "runner fields are governed by runner policy, not general free-form tree rules",
    ]


# ---------------------------------------------------------------------
# RUNNER CREATION / COLLISION
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class RunnerCreationSpec:
    """
    Canonical runner creation / activation behavior.
    """
    duplicate_name_allowed: bool = False
    revive_terminal_runner_allowed: bool = False
    implicit_resume_allowed: bool = False


def runner_creation_rules() -> List[str]:
    return [
        "runner identity must be explicit",
        "creating or launching a runner with a name that already exists is an error in V1 unless canonical command explicitly defines attach-to-existing behavior",
        "name collision => ERR_STATE",
        "runtime must not silently overwrite existing runner state",
        "runtime must not silently revive a terminal runner instance",
        "new run instance must be a new runner instance, not a magical reset of old one",
    ]


def runner_existing_name_rules() -> List[str]:
    return [
        "if existing runner is RUN => creating same-name runner is ERR_STATE",
        "if existing runner is PAUSE => creating same-name runner is ERR_STATE",
        "if existing runner is OK => creating same-name runner is ERR_STATE",
        "if existing runner is STOP => creating same-name runner is ERR_STATE",
        "if existing runner is CANCEL => creating same-name runner is ERR_STATE",
        "if existing runner is ABORT => creating same-name runner is ERR_STATE",
        "if existing runner is ERROR => creating same-name runner is ERR_STATE",
        "resume is not done by re-creating same-name runner",
        "resume in V1 is only explicit %runner:status = run from pause state",
    ]


# ---------------------------------------------------------------------
# SAFE BOUNDARY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SafeBoundarySpec:
    """
    Canonical safe boundary model.
    """
    cancel_waits_for_safe_boundary: bool = True
    abort_waits_for_safe_boundary: bool = False


def safe_boundary_definition() -> str:
    return (
        "A safe boundary is the point after the current command finishes normally. "
        "CANCEL is honored at the next safe boundary. "
        "ABORT does not wait for a safe boundary."
    )


def safe_boundary_rules() -> List[str]:
    return [
        "safe boundary occurs after the current command completes normally",
        "safe boundary is not 'one more step later'",
        "CANCEL stops normal forward execution at the next safe boundary",
        "ABORT interrupts as soon as runtime can enforce it",
        "STOP may terminate along controlled stop path without continuing into another normal step",
        "WAIT command end is itself a safe boundary",
    ]


# ---------------------------------------------------------------------
# STATUS TRANSITIONS
# ---------------------------------------------------------------------


def runner_transition_table() -> Dict[str, List[str]]:
    return {
        RunnerStatus.RUN.value: [
            RunnerStatus.OK.value,
            RunnerStatus.STOP.value,
            RunnerStatus.CANCEL.value,
            RunnerStatus.ABORT.value,
            RunnerStatus.ERROR.value,
            RunnerStatus.PAUSE.value,
        ],
        RunnerStatus.PAUSE.value: [
            RunnerStatus.RUN.value,
            RunnerStatus.STOP.value,
            RunnerStatus.CANCEL.value,
            RunnerStatus.ABORT.value,
            RunnerStatus.ERROR.value,
        ],
        RunnerStatus.CANCEL.value: [],
        RunnerStatus.ABORT.value: [],
        RunnerStatus.STOP.value: [],
        RunnerStatus.OK.value: [],
        RunnerStatus.ERROR.value: [],
    }


def runner_transition_rules() -> List[str]:
    return [
        "status transitions must be explicit and valid by transition table",
        "invalid transition => ERR_STATE",
        "terminal status is final in V1",
        "RUN is the only execution-active state",
        "PAUSE suspends execution without finishing runner",
        "CANCEL requests graceful termination at safe boundary",
        "ABORT terminates immediately",
        "STOP is controlled halt/final stop",
        "OK is normal completion/final stop",
        "ERROR is failure/final stop",
    ]


def runner_run_rules() -> List[str]:
    return [
        "RUN means runner may execute current or next eligible step",
        "RUN may transition to PAUSE by explicit status write",
        "RUN may transition to CANCEL by explicit status write",
        "RUN may transition to ABORT by explicit status write",
        "RUN may transition to STOP by explicit status write",
        "RUN may transition to ERROR by runtime failure or explicit failure path",
        "RUN may transition to OK only when runner completes normally",
    ]


def runner_pause_rules() -> List[str]:
    return [
        "PAUSE freezes runner progression",
        "no new normal step begins while paused",
        "blocking WAIT remains frozen while paused",
        "PAUSE may return to RUN",
        "PAUSE may be terminated by STOP, CANCEL, ABORT, or ERROR",
        "PAUSE does not itself imply success or failure",
    ]


def runner_cancel_rules() -> List[str]:
    return [
        "CANCEL is graceful cancellation request",
        "CANCEL must stop normal forward execution at next safe boundary",
        "CANCEL does not allow one more normal step after safe boundary is reached",
        "CANCEL is terminal in V1",
        "CANCEL is not equivalent to ERROR",
        "CANCEL is not equivalent to ABORT",
    ]


def runner_abort_rules() -> List[str]:
    return [
        "ABORT is immediate hard stop",
        "ABORT does not wait for safe boundary",
        "ABORT interrupts current execution path as soon as runtime can enforce it",
        "ABORT is terminal in V1",
        "ABORT is not equivalent to ERROR, though runtime may log related failure context",
    ]


def runner_stop_rules() -> List[str]:
    return [
        "STOP is controlled halt/final stop",
        "STOP is terminal in V1",
        "STOP is not success by itself",
        "STOP is not failure by itself",
        "STOP differs from CANCEL: STOP is direct halt outcome, CANCEL is graceful cancellation request that resolves into terminal cancellation state",
    ]


def runner_ok_rules() -> List[str]:
    return [
        "OK means runner completed its defined execution path normally",
        "OK is terminal in V1",
        "OK may be set only by normal completion path, not by arbitrary external status write in strict production policy",
    ]


def runner_error_rules() -> List[str]:
    return [
        "ERROR means runner failed",
        "ERROR is terminal in V1",
        "ERROR may be caused by command failure, invalid runtime condition, timeout, or explicit error path",
        "ERR_TIMEOUT commonly results in %runner:status = error",
    ]


# ---------------------------------------------------------------------
# EXECUTION MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class RunnerExecutionSpec:
    """
    Canonical runner execution model.

    Core lock:
    - runner executes stepwise
    - one runner step is one command line
    - no hidden parallel step execution inside one runner unless later canonical adds it explicitly
    """
    stepwise_execution: bool = True
    one_step_one_command: bool = True
    implicit_parallelism_inside_runner: bool = False


def runner_execution_rules() -> List[str]:
    return [
        "runner executes stepwise",
        "one normal step corresponds to one command line",
        "step pointer advances only after current step completes normally",
        "pause freezes step progression",
        "cancel stops at safe boundary",
        "abort terminates immediately",
        "runner must not silently skip steps",
        "runner must not silently duplicate steps",
        "runner must not invent hidden steps",
    ]


def runner_step_rules() -> List[str]:
    return [
        "%runner:step is runtime-visible when implementation exposes it",
        "step points to current or next relevant execution position according to runtime policy",
        "step must remain deterministic and auditable",
        "step progression must not depend on hidden parser rewrites",
    ]


def runner_completion_rules() -> List[str]:
    return [
        "runner reaches OK only after full normal completion path",
        "runner reaches STOP/CANCEL/ABORT/ERROR according to explicit control or failure path",
        "terminal status ends runner execution",
        "terminal runner must not continue later in V1",
    ]


# ---------------------------------------------------------------------
# EXTERNAL STATUS WRITE POLICY
# ---------------------------------------------------------------------


def runner_external_write_policy() -> List[str]:
    return [
        "external/control-plane writes to %runner:status are allowed only for valid symbolic statuses",
        "invalid status literal => ERR_TYPE or ERR_STATE",
        "external writes may request RUN, PAUSE, STOP, CANCEL, ABORT",
        "external writes must not forge OK as business success in strict production policy",
        "external writes must not clear terminal state in V1",
    ]


def runner_resume_rules() -> List[str]:
    return [
        "resume in V1 means PAUSE -> RUN only",
        "STOP -> RUN is not allowed in V1",
        "CANCEL -> RUN is not allowed in V1",
        "ABORT -> RUN is not allowed in V1",
        "ERROR -> RUN is not allowed in V1",
        "OK -> RUN is not allowed in V1",
        "restarting a finished runner must be done by creating/launching a new runner instance, not by reviving terminal state",
    ]


# ---------------------------------------------------------------------
# WAIT / TIMEOUT / LOOP INTERACTION
# ---------------------------------------------------------------------


def runner_wait_interaction_rules() -> List[str]:
    return [
        "if runner is in WAIT and status becomes PAUSE, remaining wait time is frozen",
        "if runner is in WAIT and status becomes CANCEL, WAIT ends at safe boundary and runner terminates in cancel state",
        "if runner is in WAIT and status becomes ABORT, WAIT is terminated immediately",
        "if runner is in WAIT and status becomes STOP, WAIT is terminated in controlled stop path",
        "if runner is in WAIT and timeout expires, runner enters ERROR path",
    ]


def runner_timeout_interaction_rules() -> List[str]:
    return [
        "runner-level timeout may transition runner to ERROR on expiry",
        "timeout expiry is failure, not graceful cancel",
        "if runner reaches terminal state before deadline, timeout is cleared with no further effect",
        "timeout policy must not silently downgrade ERROR into STOP/CANCEL",
    ]


def runner_loop_interaction_rules() -> List[str]:
    return [
        "loop-driven runner obeys same status contract as any runner",
        "PAUSE freezes further loop step progression",
        "CANCEL stops loop at safe boundary",
        "ABORT kills loop immediately",
        "terminal status ends loop runner execution",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def runner_status_examples_valid() -> List[str]:
    return [
        "%job:status = run",
        "%job:status = pause",
        "%job:status = cancel",
        "%job:status = abort",
        "%job:status = stop",
    ]


def runner_status_examples_invalid() -> List[str]:
    return [
        "%job:status = finished",
        "%job:status = 123",
        '%job:status = "running"',
        "%job:status = resume",
        "%job:status = unknown",
    ]


def runner_collision_examples_invalid() -> List[str]:
    return [
        "run %job        # invalid if %job already exists",
        "loop %job #tbl  # invalid if %job already exists",
        "%job:status = run   # invalid if %job is terminal and caller expects revive",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


RUNNERS_SUMMARY = {
    "canonical_statuses": [
        RunnerStatus.RUN.value,
        RunnerStatus.OK.value,
        RunnerStatus.STOP.value,
        RunnerStatus.CANCEL.value,
        RunnerStatus.ABORT.value,
        RunnerStatus.ERROR.value,
        RunnerStatus.PAUSE.value,
    ],
    "numeric_compat_locked_subset": RUNNER_STATUS_NUMERIC_COMPAT,
    "active_state": RunnerStatus.RUN.value,
    "suspend_state": RunnerStatus.PAUSE.value,
    "terminal_states": [
        RunnerStatus.OK.value,
        RunnerStatus.STOP.value,
        RunnerStatus.CANCEL.value,
        RunnerStatus.ABORT.value,
        RunnerStatus.ERROR.value,
    ],
    "resume_rule_v1": "only PAUSE -> RUN",
    "duplicate_name_allowed": False,
    "revive_terminal_runner_allowed": False,
    "safe_boundary": "after current command completes normally",
    "cancel_mode": "graceful safe-boundary termination",
    "abort_mode": "immediate hard stop",
    "invalid_transition_error": ErrorCode.ERR_STATE.value,
}
