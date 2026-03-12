"""
AIGMos v36 — Python-style spec
MODULE: time_control

Purpose:
    Define canonical time-control behavior:
    - wait <ms>
    - delay <ms> <command>
    - timeout <ms> %runner

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


# ---------------------------------------------------------------------
# ERROR CODES
# ---------------------------------------------------------------------


class ErrorCode(str, Enum):
    ERR_SYNTAX = "ERR_SYNTAX"
    ERR_TYPE = "ERR_TYPE"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_TIMEOUT = "ERR_TIMEOUT"
    ERR_STATE = "ERR_STATE"


# ---------------------------------------------------------------------
# RUNNER STATUS REFERENCE
# ---------------------------------------------------------------------


class RunnerStatus(str, Enum):
    RUN = "run"
    OK = "ok"
    STOP = "stop"
    CANCEL = "cancel"
    ABORT = "abort"
    ERROR = "error"
    PAUSE = "pause"


# ---------------------------------------------------------------------
# GLOBAL TIME CONTROL MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TimeControlModelSpec:
    """
    Canonical time-control model.

    Core locks:
    - time control is explicit
    - no hidden retries
    - no hidden scheduler magic
    - no implicit background orchestration beyond what the command defines
    """
    explicit_only: bool = True
    hidden_retry_logic: bool = False
    hidden_scheduler_magic: bool = False
    global_expression_language: bool = False


def time_control_global_rules() -> List[str]:
    return [
        "time control must be explicit",
        "time control commands are part of executable command flow, not free-form expressions",
        "time control must not introduce hidden retries",
        "time control must not introduce hidden command duplication",
        "time control must not invent hidden fallback execution",
        "runtime overhead may delay actual execution, but must never make a command happen earlier than requested",
    ]


def time_control_scope_rules() -> List[str]:
    return [
        "time control commands are allowed in runner step flow",
        "time control commands are allowed in event-dispatched runner bodies",
        "time control commands are allowed in loop-expanded runner bodies",
        "time control commands are not allowed as assignment RHS",
        "time control commands are not allowed inside trigger expressions",
    ]


def time_value_rules() -> List[str]:
    return [
        "time value unit is milliseconds",
        "canonical syntax uses integer millisecond literals",
        "float is invalid in V1",
        "negative value is invalid in V1",
        "quoted numeric string is not an integer literal",
        "0 is valid where command-specific rules allow immediate behavior",
    ]


# ---------------------------------------------------------------------
# WAIT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class WaitCommandSpec:
    """
    Canonical syntax:
        wait <ms>

    Purpose:
        Block the current runner step for a fixed duration in milliseconds.
    """
    command_name: str = "wait"
    arg_count: int = 1
    arg_1_name: str = "ms"
    arg_1_type: str = "integer >= 0"


def wait_scope_rules() -> List[str]:
    return [
        "wait is valid only inside executable command flow",
        "wait is not valid as assignment RHS",
        "wait is not valid inside trigger expressions",
    ]


def wait_argument_rules() -> List[str]:
    return [
        "<ms> must be integer >= 0",
        "float => ERR_SYNTAX",
        "negative => ERR_SYNTAX",
        "non-numeric => ERR_SYNTAX",
        "quoted numeric string is not accepted as integer literal",
    ]


def wait_execution_rules() -> List[str]:
    return [
        "wait blocks only the current runner step",
        "runner remains active while waiting unless status changes",
        "step pointer does not advance during wait",
        "current step is not complete until wait finishes",
        "wait writes no state by itself",
        "wait emits no implicit result payload",
        "wait creates no hidden command",
        "runtime must never resume earlier than requested duration",
        "actual resume may occur later due to scheduler/runtime overhead",
    ]


def wait_completion_rules() -> List[str]:
    return [
        "when duration has elapsed, current step completes normally",
        "runner continues to next step by normal flow",
        "wait completion itself is a safe boundary",
    ]


def wait_status_interaction_rules() -> List[str]:
    return [
        "if %runner:status = cancel during wait: wait ends at safe boundary and runner does not continue to next normal step",
        "if %runner:status = abort during wait: wait is terminated immediately",
        "if %runner:status = stop during wait: wait is terminated in controlled stop path",
        "if %runner:status = pause during wait: remaining wait duration is frozen until status returns to run",
    ]


def wait_error_rules() -> Dict[str, str]:
    return {
        "invalid syntax": ErrorCode.ERR_SYNTAX.value,
        "invalid numeric value": ErrorCode.ERR_SYNTAX.value,
        "runtime timing subsystem failure": ErrorCode.ERR_RUNTIME.value,
    }


def wait_examples_valid() -> List[str]:
    return [
        "wait 0",
        "wait 100",
        "wait 5000",
    ]


def wait_examples_invalid() -> List[str]:
    return [
        "wait -1",
        "wait 1.5",
        'wait "100"',
        "$foo = wait 100",
    ]


# ---------------------------------------------------------------------
# DELAY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class DelayCommandSpec:
    """
    Canonical syntax:
        delay <ms> <command>

    Purpose:
        Schedule exactly one command to be dispatched after a fixed delay
        without blocking the current runner step.
    """
    command_name: str = "delay"
    arg_count_min: int = 2
    arg_1_name: str = "ms"
    arg_1_type: str = "integer >= 0"
    arg_2_name: str = "command"
    arg_2_type: str = "single command line"


def delay_scope_rules() -> List[str]:
    return [
        "delay is valid only inside executable command flow",
        "delay is not valid as assignment RHS",
        "delay is not valid inside trigger expressions",
    ]


def delay_argument_rules() -> List[str]:
    return [
        "<ms> must be integer >= 0",
        "float => ERR_SYNTAX",
        "negative => ERR_SYNTAX",
        "non-numeric => ERR_SYNTAX",
        "quoted numeric string is not accepted as integer literal",
        "<command> must be exactly one valid command line",
        "multi-command payload is not allowed",
        "empty command => ERR_SYNTAX",
    ]


def delay_execution_rules() -> List[str]:
    return [
        "delay schedules one command for future dispatch after <ms>",
        "delay itself completes immediately after successful scheduling",
        "delay does not block the current runner step",
        "step pointer may advance immediately after delay command completes",
        "scheduled command is dispatched as a new execution item",
        "scheduled command is not appended implicitly to the current runner body",
        "scheduled command preserves exact command text after parser normalization",
        "runtime must never dispatch earlier than requested duration",
        "actual dispatch may occur later due to scheduler/runtime overhead",
    ]


def delay_side_effect_rules() -> List[str]:
    return [
        "delay writes no state by itself",
        "delay emits no implicit result payload by itself",
        "only the delayed command may later write state or produce effects",
        "delay creates one explicit deferred execution item and nothing else",
    ]


def delay_status_interaction_rules() -> List[str]:
    return [
        "once delay has completed scheduling, the delayed command exists independently of the issuing step",
        "pause/stop/cancel/abort of the issuing runner after scheduling does not retroactively unschedule the delayed command",
        "abort of the issuing runner before delay command completes prevents scheduling",
        "cancel of the issuing runner before delay command completes prevents scheduling at the safe boundary of the delay command",
    ]


def delay_target_model_rules() -> List[str]:
    return [
        "V1 delayed unit is exactly one command",
        "V1 does not delay an entire runner by name",
        "V1 does not delay an event definition",
        "if a delayed runner launch command is desired, that runner launch is the single delayed command",
        "example: delay 500 run %cooling.sequence",
    ]


def delay_completion_rules() -> List[str]:
    return [
        "delay command is complete immediately after successful scheduling",
        "successful scheduling is the only completion condition of the delay command itself",
        "the later success or failure of the delayed command does not change the already-completed status of the delay command",
    ]


def delay_error_rules() -> Dict[str, str]:
    return {
        "invalid syntax": ErrorCode.ERR_SYNTAX.value,
        "invalid numeric value": ErrorCode.ERR_SYNTAX.value,
        "empty or invalid delayed command": ErrorCode.ERR_SYNTAX.value,
        "scheduler/runtime timing subsystem failure during scheduling": ErrorCode.ERR_RUNTIME.value,
    }


def delay_examples_valid() -> List[str]:
    return [
        "delay 0 run %job",
        "delay 100 wait 50",
        "delay 500 $UM.cooling:state = on",
        "delay 1000 Q.status 'hello'",
    ]


def delay_examples_invalid() -> List[str]:
    return [
        "delay -1 run %job",
        "delay 1.5 run %job",
        'delay "100" run %job',
        "delay 100",
        "delay 100 ",
        "delay 100 cmd1 ; cmd2",
    ]


# ---------------------------------------------------------------------
# TIMEOUT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class TimeoutCommandSpec:
    """
    Canonical syntax:
        timeout <ms> %runner

    Purpose:
        Apply a maximum allowed execution duration to a runner.
        If the runner does not complete before the timeout expires,
        timeout handling is triggered.
    """
    command_name: str = "timeout"
    arg_count: int = 2
    arg_1_name: str = "ms"
    arg_1_type: str = "integer >= 0"
    arg_2_name: str = "target"
    arg_2_type: str = "%runner"


def timeout_scope_rules() -> List[str]:
    return [
        "timeout is valid only inside executable command flow",
        "timeout is not valid as assignment RHS",
        "timeout is not valid inside trigger expressions",
    ]


def timeout_argument_rules() -> List[str]:
    return [
        "<ms> must be integer >= 0",
        "float => ERR_SYNTAX",
        "negative => ERR_SYNTAX",
        "non-numeric => ERR_SYNTAX",
        "quoted numeric string is not accepted as integer literal",
        "target must be exactly one %runner reference",
        "V1 target is runner only",
        "single command target is not allowed in V1",
        "event target is not allowed in V1",
    ]


def timeout_execution_rules() -> List[str]:
    return [
        "timeout applies a deadline to the referenced runner",
        "timeout command itself completes immediately after successful timeout registration",
        "timeout does not block the current runner step",
        "timeout creates one explicit timeout watch and nothing else",
        "timeout does not modify runner body or step order",
        "multiple timeout registrations for the same runner are not allowed in V1",
    ]


def timeout_deadline_rules() -> List[str]:
    return [
        "deadline countdown begins when timeout registration completes",
        "runtime must never fire timeout earlier than requested duration",
        "actual timeout handling may occur later due to scheduler/runtime overhead",
        "if target runner completes before deadline, timeout watch resolves with no effect",
        "if target runner is already in terminal state at registration time, timeout registration has no effect",
    ]


def timeout_failure_behavior_rules() -> List[str]:
    return [
        "on timeout expiry, target runner transitions to %runner:status = error",
        "runtime logs ERR_TIMEOUT",
        "timeout expiry is treated as runner failure, not graceful cancel",
        "timeout does not map implicitly to stop",
        "timeout does not map implicitly to cancel",
        "timeout does not map implicitly to abort unless later policy adds it explicitly",
    ]


def timeout_status_interaction_rules() -> List[str]:
    return [
        "if target runner reaches ok before deadline, timeout is cleared with no effect",
        "if target runner reaches stop before deadline, timeout is cleared with no effect",
        "if target runner reaches cancel before deadline, timeout is cleared with no effect",
        "if target runner reaches abort before deadline, timeout is cleared with no effect",
        "if target runner reaches error before deadline, timeout is cleared with no effect",
        "if target runner is paused, timeout countdown continues in V1 unless later canonical overrides this",
    ]


def timeout_safe_boundary_rules() -> List[str]:
    return [
        "timeout expiry is not a graceful boundary event",
        "timeout handling may interrupt target execution path as failure",
        "if target is in a blocking wait when timeout expires, timeout still wins and runner enters error path",
    ]


def timeout_error_rules() -> Dict[str, str]:
    return {
        "invalid syntax": ErrorCode.ERR_SYNTAX.value,
        "invalid numeric value": ErrorCode.ERR_SYNTAX.value,
        "invalid target type": ErrorCode.ERR_SYNTAX.value,
        "duplicate timeout registration for same runner": ErrorCode.ERR_RUNTIME.value,
        "runtime timeout subsystem failure during registration": ErrorCode.ERR_RUNTIME.value,
        "deadline expired before runner completed": ErrorCode.ERR_TIMEOUT.value,
    }


def timeout_examples_valid() -> List[str]:
    return [
        "timeout 1000 %job",
        "timeout 0 %job",
        "timeout 5000 %cooling.sequence",
    ]


def timeout_examples_invalid() -> List[str]:
    return [
        "timeout -1 %job",
        "timeout 1.5 %job",
        'timeout "100" %job',
        "timeout 100",
        "timeout 100 run %job",
        "timeout 100 @event",
    ]


# ---------------------------------------------------------------------
# CROSS-COMMAND INTERACTION RULES
# ---------------------------------------------------------------------


def time_control_interaction_rules() -> List[str]:
    return [
        "wait is blocking for the current runner step",
        "delay is non-blocking for the current runner step",
        "timeout is non-blocking for the current runner step that registers it",
        "delay and timeout registration complete immediately after successful scheduling/registration",
        "wait completion is a safe boundary",
        "timeout expiry is a failure event, not a safe-boundary completion event",
    ]


def time_control_runner_status_rules() -> List[str]:
    return [
        "pause freezes active wait remaining time",
        "pause does not freeze timeout countdown in V1",
        "cancel honors safe-boundary semantics",
        "abort overrides safe-boundary waiting and interrupts immediately",
        "stop follows controlled halt path",
        "error is terminal and clears relevant time-control watches for the runner",
    ]


def time_control_nonfeatures_v1() -> List[str]:
    return [
        "no cron-like scheduler",
        "no calendar semantics",
        "no recurring delay command",
        "no timeout for single command target",
        "no implicit retry-after-timeout",
        "no backoff policy",
        "no hidden watchdog loops",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


TIME_CONTROL_SUMMARY = {
    "time_unit": "milliseconds",
    "literal_type": "integer >= 0",
    "commands": {
        "wait": {
            "syntax": "wait <ms>",
            "meaning": "blocks current runner step",
            "blocks_current_step": True,
            "writes_state": False,
            "pause_behavior": "freezes remaining wait time",
            "cancel_behavior": "stops at wait boundary",
            "abort_behavior": "cuts immediately",
        },
        "delay": {
            "syntax": "delay <ms> <command>",
            "meaning": "non-blocking deferred dispatch of one command",
            "blocks_current_step": False,
            "step_advances_immediately": True,
            "writes_state": False,
            "unit_of_delay_v1": "single command",
        },
        "timeout": {
            "syntax": "timeout <ms> %runner",
            "meaning": "apply runner-level deadline",
            "blocks_current_step": False,
            "writes_state_directly": False,
            "target_v1": "%runner only",
            "on_expiry_runner_status": RunnerStatus.ERROR.value,
            "on_expiry_error_code": ErrorCode.ERR_TIMEOUT.value,
            "countdown_during_pause_v1": True,
        },
    },
    "hidden_scheduler_magic": False,
    "hidden_retry_logic": False,
}
