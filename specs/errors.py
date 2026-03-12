"""
AIGMos v36 — Python-style spec
MODULE: errors

Purpose:
    Define canonical error taxonomy, error logging contract,
    error propagation expectations, and failure-handling boundaries.

Important:
    This file is a specification artifact written in Python style.
    It is not production runtime code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------
# CANONICAL ERROR CODES
# ---------------------------------------------------------------------


class ErrorCode(str, Enum):
    ERR_SYNTAX = "ERR_SYNTAX"
    ERR_TYPE = "ERR_TYPE"
    ERR_EVAL = "ERR_EVAL"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_ADAPTER = "ERR_ADAPTER"
    ERR_OWNERSHIP = "ERR_OWNERSHIP"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_STATE = "ERR_STATE"
    ERR_TIMEOUT = "ERR_TIMEOUT"


@dataclass(frozen=True)
class ErrorTaxonomySpec:
    """
    Canonical error taxonomy.

    Core lock:
    - error classes are explicit
    - runtime must not collapse all failures into one generic unknown error
    - canonical error names are stable identifiers
    """
    explicit_error_classes: bool = True
    generic_catchall_only_model: bool = False
    stable_error_identifiers: bool = True


def error_taxonomy_rules() -> List[str]:
    return [
        "canonical error codes are explicit and stable",
        "runtime should classify failures into the narrowest correct canonical error code when possible",
        "runtime must not silently collapse all failures into generic runtime error when a more specific canonical code is available",
        "error codes are identifiers, not free-form prose",
        "additional implementation-private detail may exist, but canonical error surface must remain understandable and stable",
    ]


# ---------------------------------------------------------------------
# ERROR MEANINGS
# ---------------------------------------------------------------------


def error_meanings() -> Dict[str, str]:
    return {
        ErrorCode.ERR_SYNTAX.value: (
            "Parser or command-shape error. "
            "The input form itself is invalid, incomplete, malformed, or disallowed by grammar."
        ),
        ErrorCode.ERR_TYPE.value: (
            "Type/shape mismatch. "
            "The provided value exists but is not valid for the expected canonical type/context."
        ),
        ErrorCode.ERR_EVAL.value: (
            "Evaluation failure. "
            "Expression/ref evaluation failed after parsing succeeded."
        ),
        ErrorCode.ERR_RUNTIME.value: (
            "Execution/runtime failure. "
            "The operation was valid in form but failed during execution infrastructure/runtime handling."
        ),
        ErrorCode.ERR_ADAPTER.value: (
            "External adapter/integration failure. "
            "The failure occurred at IO/protocol/network/adapter boundary."
        ),
        ErrorCode.ERR_OWNERSHIP.value: (
            "Ownership/policy violation. "
            "The caller is not allowed to write/invoke/access that governed target/action."
        ),
        ErrorCode.ERR_NOT_FOUND.value: (
            "Referenced entity/path/command/target was not found."
        ),
        ErrorCode.ERR_STATE.value: (
            "Invalid lifecycle/state transition or forbidden operation in current state."
        ),
        ErrorCode.ERR_TIMEOUT.value: (
            "A timeout deadline expired before the target completed."
        ),
    }


# ---------------------------------------------------------------------
# ERROR CLASSIFICATION GUIDANCE
# ---------------------------------------------------------------------


def error_classification_rules() -> List[str]:
    return [
        "ERR_SYNTAX is for malformed input form, missing required parts, invalid grammar shape, invalid command shape, or forbidden parser structure",
        "ERR_TYPE is for valid shape but wrong kind of value, such as string where integer literal is required",
        "ERR_EVAL is for failures during expression/ref evaluation after syntax was already accepted",
        "ERR_RUNTIME is for internal execution failures not better explained by adapter/timeout/state/ownership/type/syntax",
        "ERR_ADAPTER is for external IO/protocol/integration failures",
        "ERR_OWNERSHIP is for protected-root violations, cross-module forbidden writes, or governed surface violations",
        "ERR_NOT_FOUND is for missing named target, missing path, missing claim target, missing trigger/event/runner where lookup is required",
        "ERR_STATE is for invalid transition, duplicate name collision in governed lifecycle, forbidden resume, or invalid operation in current state",
        "ERR_TIMEOUT is specifically for deadline expiry",
    ]


def error_priority_guidance_rules() -> List[str]:
    return [
        "when multiple interpretations seem possible, prefer the most specific canonical error code",
        "syntax errors take precedence when input form is not parse-valid",
        "type errors take precedence when syntax is valid but provided literal/value kind is wrong",
        "ownership errors take precedence when action is structurally valid but forbidden by governance/policy",
        "state errors take precedence when entity exists but requested operation is illegal in current lifecycle/state",
        "adapter errors take precedence over generic runtime error for external integration failures",
        "timeout errors take precedence over generic runtime error for deadline expiry",
    ]


# ---------------------------------------------------------------------
# ERROR LOG CONTRACT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ErrorLogContractSpec:
    """
    Canonical error log contract.

    Core idea from project history:
    - errors are logged explicitly
    - causing address/path should be present
    - log-book style targets are allowed
    """
    explicit_error_logging: bool = True
    cause_address_required_when_available: bool = True
    hidden_silent_failure_allowed: bool = False


ERROR_LOG_FIELDS = (
    "timestamp",
    "level",
    "command",
    "runner_id",
    "error_code",
    "cause_address",
    "message",
    "recovery_action",
)


def error_log_rules() -> List[str]:
    return [
        "errors must be logged explicitly",
        "silent swallow of canonical errors is not allowed",
        "error log entry should include the causing command when available",
        "error log entry should include runner identity when relevant",
        "error log entry should include canonical error_code",
        "error log entry should include cause_address/path when available",
        "error log entry may include recovery_action guidance",
        "error log output must remain auditable and deterministic",
    ]


def error_log_shape_rules() -> List[str]:
    return [
        "canonical log entry may be represented as structured # branch, row/cell property set, or explicit log-book row model",
        "log-book style structures are valid under # namespaces",
        "error-causing address should be stored when available",
        "error log contract must not depend on hidden implementation-only stack traces being user-visible",
        "implementation may store deeper internal diagnostics privately, but canonical error surface remains explicit",
    ]


def error_log_examples() -> List[str]:
    return [
        "timestamp | level | command | runner_id | error_code | cause_address | recovery_action",
        "2026-03-05T12:38:01 | ERROR | mk.#repo | %build.001 | ERR_NOT_FOUND | $missing_cmd | check command claim",
        "#SYSTEM:error:log:0:code = ERR_SYNTAX",
        "#SYSTEM:error:log:0:cause_address = $UM.sensor",
    ]


# ---------------------------------------------------------------------
# ERROR PROPAGATION
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ErrorPropagationSpec:
    """
    Canonical error propagation model.
    """
    explicit_propagation: bool = True
    hidden_retry_or_swallow: bool = False
    terminal_failure_may_update_runner_status: bool = True


def error_propagation_rules() -> List[str]:
    return [
        "canonical errors propagate explicitly through runtime handling",
        "runtime must not silently retry unless a specific command/runtime policy explicitly defines retry behavior",
        "runtime must not silently downgrade ERR_TIMEOUT to OK/STOP/CANCEL",
        "runtime must not silently downgrade ERR_OWNERSHIP to harmless no-op",
        "runtime must not silently reinterpret parse failure as a different valid command",
        "runner-related execution failure may transition %runner:status = error where runner model says so",
    ]


def error_runner_interaction_rules() -> List[str]:
    return [
        "command failure inside active runner may place runner into ERROR path according to runner semantics",
        "ERR_TIMEOUT commonly results in %runner:status = error",
        "ERR_STATE does not always mean runner enters error if the failure occurred outside active execution path, but it must still be surfaced explicitly",
        "ABORT is not itself an error code; it is a status/control outcome",
        "CANCEL is not itself an error code; it is a status/control outcome",
        "STOP is not itself an error code; it is a status/control outcome",
    ]


def error_trigger_interaction_rules() -> List[str]:
    return [
        "trigger definition syntax failure => ERR_SYNTAX",
        "trigger evaluation failure => ERR_EVAL or ERR_TYPE",
        "failed trigger evaluation must not silently become false unless canonical policy explicitly says so",
        "trigger evaluation failure does not equal hidden event execution skip without observable error handling",
    ]


def error_event_interaction_rules() -> List[str]:
    return [
        "invalid event declaration => ERR_SYNTAX",
        "duplicate event identity without explicit replace mode => ERR_STATE",
        "event dispatch failure must remain observable",
        "event does not get silent hidden fallback body execution after failure",
    ]


def error_adapter_interaction_rules() -> List[str]:
    return [
        "HTTP/OSC/integration boundary failures should use ERR_ADAPTER when that is the real failure class",
        "missing caller-supplied output target remains ERR_SYNTAX, not ERR_ADAPTER",
        "protected integration root violation may be ERR_OWNERSHIP, not ERR_ADAPTER",
    ]


# ---------------------------------------------------------------------
# ERROR VS STATUS
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ErrorVsStatusSpec:
    """
    Canonical distinction:
    - error_code classifies failure
    - runner/event/trigger status describes lifecycle/control state
    """
    error_codes_are_not_statuses: bool = True
    statuses_are_not_error_codes: bool = True


def error_vs_status_rules() -> List[str]:
    return [
        "error code and status are different concepts",
        "ERR_TIMEOUT is an error code; error is a runner status",
        "CANCEL/ABORT/STOP/OK/PAUSE/RUN are statuses, not error codes",
        "one failure may produce both an error code and a resulting runner status transition",
        "runtime must not conflate status literals with canonical error identifiers",
    ]


# ---------------------------------------------------------------------
# NONFEATURES / LIMITS
# ---------------------------------------------------------------------


def error_nonfeatures_v1() -> List[str]:
    return [
        "no hidden auto-recovery policy by default",
        "no silent ignore of ownership violations",
        "no 'best effort' parser reinterpretation after syntax failure",
        "no requirement that private implementation stack trace be surfaced canonically",
        "no uncontrolled expansion of unofficial error codes into canonical surface without governance",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID CLASSIFICATION EXAMPLES
# ---------------------------------------------------------------------


def error_examples_classification() -> Dict[str, List[str]]:
    return {
        "ERR_SYNTAX": [
            "wait 1.5",
            "on !sensor.hot",
            "$UM.sensor:temp = ",
        ],
        "ERR_TYPE": [
            '%job:status = 123',
            'timeout "100" %job',
        ],
        "ERR_EVAL": [
            "trig !foo ($UM.a / 0) > 1",
            "trig !foo $UM.missing > 10",
        ],
        "ERR_RUNTIME": [
            "internal scheduler/timing subsystem failed while registering delay",
            "runtime execution engine failed without narrower canonical class",
        ],
        "ERR_ADAPTER": [
            "HTTP.GET valid syntax but network/adapter call failed",
            "OSC transport send/receive failed at adapter boundary",
        ],
        "ERR_OWNERSHIP": [
            "module writes into another module's $UM namespace",
            "arbitrary direct overwrite into protected root",
        ],
        "ERR_NOT_FOUND": [
            "claim.command.alias unknown status",
            "referenced runner/trigger/event/path not found where required",
        ],
        "ERR_STATE": [
            "duplicate runner name collision",
            "STOP -> RUN attempted in V1",
        ],
        "ERR_TIMEOUT": [
            "timeout expired before %job completed",
        ],
    }


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


ERRORS_SUMMARY = {
    "canonical_error_codes": [
        ErrorCode.ERR_SYNTAX.value,
        ErrorCode.ERR_TYPE.value,
        ErrorCode.ERR_EVAL.value,
        ErrorCode.ERR_RUNTIME.value,
        ErrorCode.ERR_ADAPTER.value,
        ErrorCode.ERR_OWNERSHIP.value,
        ErrorCode.ERR_NOT_FOUND.value,
        ErrorCode.ERR_STATE.value,
        ErrorCode.ERR_TIMEOUT.value,
    ],
    "explicit_error_logging": True,
    "silent_failure_allowed": False,
    "cause_address_required_when_available": True,
    "error_codes_are_statuses": False,
    "statuses_are_error_codes": False,
    "specificity_preferred": True,
}
