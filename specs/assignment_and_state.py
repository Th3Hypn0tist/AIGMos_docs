"""
AIGMos v36 — Python-style spec
MODULE: assignment_and_state

Purpose:
    Define canonical assignment semantics, state-write rules,
    primitive data behavior, protected roots, ownership boundaries,
    and structural state movement rules.

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
    ERR_OWNERSHIP = "ERR_OWNERSHIP"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_RUNTIME = "ERR_RUNTIME"


# ---------------------------------------------------------------------
# CORE TYPE MODEL
# ---------------------------------------------------------------------


class PrimitiveFamily(str, Enum):
    KV = "$"
    LIST = "&"
    TREE = "#"
    TRIGGER = "!"
    EVENT = "@"
    RUNNER = "%"


class StoredValueType(str, Enum):
    STRING = "string"
    SYMBOLIC_PATH = "symbolic_path"
    COMMAND_LINE = "command_line"
    STRUCTURED_BRANCH = "structured_branch"
    LIST_ITEM = "list_item"
    STATUS_LITERAL = "status_literal"


@dataclass(frozen=True)
class TypeModelSpec:
    """
    Canonical state model.

    Core lock:
    - stored values are string-first symbolic values
    - parser/runtime may interpret them by context
    - there is no hidden typed object system at canonical surface level
    """
    canonical_storage_model: str = "string-first"
    hidden_object_storage: bool = False
    implicit_runtime_object_leakage: bool = False


def type_model_rules() -> List[str]:
    return [
        "canonical state surface is symbolic and string-first",
        "a stored value may represent text, command line, path reference, status literal, or structured content by context",
        "runtime must not expose hidden implementation objects at command surface",
        "type validation is command- and context-specific",
        "there is no implicit JSON object magic at assignment surface unless explicit import/export rules apply",
    ]


# ---------------------------------------------------------------------
# ASSIGNMENT MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class AssignmentModelSpec:
    """
    Canonical assignment model.

    Form:
        <target> = <rhs>
    """
    operator: str = "="
    target_count: int = 1
    rhs_required: bool = True
    expression_language_enabled: bool = False


def assignment_global_rules() -> List[str]:
    return [
        "canonical assignment form is <target> = <rhs>",
        "assignment requires exactly one writable target",
        "assignment requires a non-empty RHS",
        "empty RHS => ERR_SYNTAX",
        "assignment is not a general expression language",
        "arithmetic is not allowed in assignment RHS unless later canonical explicitly enables it",
        "assignment never implies hidden command execution",
    ]


def assignment_target_rules() -> List[str]:
    return [
        "assignment target must be a writable canonical path",
        "target writability depends on primitive family, protected-root policy, and ownership rules",
        "non-writable target => ERR_OWNERSHIP or ERR_STATE",
        "unknown target family => ERR_SYNTAX",
        "assignment target is parsed before RHS semantic interpretation",
    ]


def assignment_rhs_rules() -> List[str]:
    return [
        "RHS may be literal text",
        "RHS may be a symbolic path copied as value when command semantics say literal assignment",
        "RHS may be treated as reference source in commands that explicitly perform copy/move/merge behavior",
        "RHS is not evaluated as free-form math expression",
        "RHS is not evaluated as command invocation",
        "quoted text preserves literal spaces and operator characters",
    ]


def assignment_resolution_rules() -> List[str]:
    return [
        "plain assignment stores the RHS as canonical value according to target context",
        "assignment itself does not recursively dereference arbitrary paths unless command semantics explicitly say so",
        "copying data from one path to another belongs to cp/mv/merge/import/export semantics, not implicit '=' magic",
        "assignment parser must not guess whether RHS is intended as literal or source command",
    ]


def assignment_side_effect_rules() -> List[str]:
    return [
        "assignment writes only the specified target",
        "assignment must not create hidden sibling writes",
        "assignment must not launch runner/event/trigger execution by itself",
        "state-driven downstream effects happen only through trigger/event/runtime logic after write is complete",
    ]


# ---------------------------------------------------------------------
# PRIMITIVE BEHAVIOR
# ---------------------------------------------------------------------


def primitive_behavior_rules() -> Dict[str, List[str]]:
    return {
        "$": [
            "$ stores scalar/keyed symbolic state",
            "$ canonical writable target is fielded shape such as $UM.sensor:temp",
            "$ root-only assignment without field key is invalid in strict canonical mode",
            "$ is the primary symbolic KV namespace",
        ],
        "&": [
            "& stores ordered items",
            "& numeric child keys are used in sortable contexts",
            "& may contain command lines as data",
            "& is data until executed by runner/loop semantics",
        ],
        "#": [
            "# stores recursive structured branches",
            "# supports rows, cells, properties, logs, adapter payloads, and general nested branches",
            "#cell:property = value is valid and property addressing must remain preserved",
            "# is not limited to tables only",
        ],
        "!": [
            "! identifies trigger definitions and trigger state",
            "! is not general business-data storage",
            "trigger writes happen through trigger-definition/runtime mechanics, not arbitrary free-form use",
        ],
        "@": [
            "@ identifies event definitions and event state",
            "@ is not general business-data storage",
            "event writes happen through event-definition/runtime mechanics, not arbitrary free-form use",
        ],
        "%": [
            "% identifies runner/loop roots and their fields",
            "%runner:status is canonical control/status field",
            "% fields are governed by runner model and must not be treated as arbitrary free-form tree without runner policy",
        ],
    }


# ---------------------------------------------------------------------
# WRITABLE / NON-WRITABLE SURFACE
# ---------------------------------------------------------------------


def writable_surface_rules() -> List[str]:
    return [
        "$ writable by assignment when target path is valid and ownership policy allows it",
        "& writable by assignment/add/copy/import semantics when target path is valid",
        "# writable by assignment/add/copy/merge/import semantics when target path is valid",
        "! writable through trigger-definition commands and trigger runtime policy",
        "@ writable through event-definition commands and event runtime policy",
        "% writable through runner-definition/runtime control policy",
    ]


def nonwritable_surface_rules() -> List[str]:
    return [
        "protected system roots may reject direct user writes",
        "read-only runtime reflections must not accept direct assignment",
        "unknown path family is never writable",
        "implementation-private storage must never leak as writable canonical path",
    ]


# ---------------------------------------------------------------------
# PROTECTED ROOTS
# ---------------------------------------------------------------------


PROTECTED_ROOTS = (
    "$SYSTEM",
    "$CH",
    "#SYSTEM",
    "#HTTP",
    "#OSC",
)


@dataclass(frozen=True)
class ProtectedRootPolicySpec:
    """
    Canonical protected-root model.

    Note:
    - 'protected' does not always mean fully read-only
    - it means writes are policy-governed and not open free-for-all
    """
    protected_roots: Tuple[str, ...] = PROTECTED_ROOTS
    unrestricted_user_write: bool = False


def protected_root_rules() -> List[str]:
    return [
        "$SYSTEM is protected",
        "$CH is protected",
        "#SYSTEM is protected",
        "#HTTP is protected as inbound/runtime/integration branch family",
        "#OSC is protected as inbound/runtime/integration branch family",
        "protected roots may allow specific canonical writes by specific commands or ownership domains",
        "general arbitrary write into protected roots is not allowed by default",
        "protected-root violation => ERR_OWNERSHIP or ERR_STATE",
    ]


def protected_root_examples() -> Dict[str, List[str]]:
    return {
        "allowed_by_policy_examples": [
            "$SYSTEM:error.log = ...    # only if canonical/system policy explicitly allows that write path",
            "%job:status = cancel       # runner control write, governed by runner policy",
            "#HTTP:in:req:1 = ...       # integration/runtime-managed, not arbitrary user write",
        ],
        "rejected_examples": [
            "$CH = foo                  # direct protected-root overwrite is not open by default",
            "#SYSTEM = something        # protected root overwrite",
            "#HTTP = raw                # protected integration root overwrite",
        ],
    }


# ---------------------------------------------------------------------
# OWNERSHIP MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class OwnershipModelSpec:
    """
    Canonical ownership boundary model.
    """
    usermodule_write_scope_prefix: str = "$UM."
    cross_module_direct_write_allowed: bool = False
    read_across_modules_allowed: bool = True


def ownership_rules() -> List[str]:
    return [
        "usermodule may write only inside its own $UM.<module> namespace",
        "usermodule must not directly write to another module's $UM.<other> namespace",
        "cross-module read is allowed unless later policy narrows it",
        "protected-root write still requires explicit policy even if module owns nearby namespace",
        "ownership violation => ERR_OWNERSHIP",
    ]


def ownership_examples_valid() -> List[str]:
    return [
        "$UM.weather:temp = 21",
        "$UM.weather:status = ok",
        "$UM.audio.mixer:scene = live",
    ]


def ownership_examples_invalid() -> List[str]:
    return [
        "# module 'weather' writing to another module:",
        "$UM.audio:gain = 5   # invalid if issued by non-audio module",
        "$SYSTEM:name = foo   # invalid unless protected policy explicitly allows writer",
    ]


# ---------------------------------------------------------------------
# STRING / SYMBOL / LITERAL RULES
# ---------------------------------------------------------------------


def literal_storage_rules() -> List[str]:
    return [
        "canonical storage preserves literal intent unless command explicitly transforms structure",
        "quoted text remains literal text content",
        "command-looking text may be stored as plain data",
        "path-looking text may be stored as plain data",
        "parser/runtime must not auto-execute stored strings",
    ]


def symbolic_reference_rules() -> List[str]:
    return [
        "a symbolic path may be stored as literal string value",
        "a stored path string does not become active reference unless a command explicitly interprets it as source/target reference",
        "runtime must avoid hidden dereference magic",
    ]


# ---------------------------------------------------------------------
# REMOVE / COPY / MOVE / ADD / MERGE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class StructuralStateOpsSpec:
    """
    Canonical structural movement model.
    """
    implicit_recursive_merge_on_assignment: bool = False
    implicit_copy_on_assignment: bool = False
    implicit_delete_on_move: bool = False


def rm_rules() -> List[str]:
    return [
        "rm removes the addressed canonical target",
        "rm on $ removes the addressed keyed scalar target, not the whole family",
        "rm on & removes the addressed list or list item according to target shape",
        "rm on # removes the addressed branch/cell/property according to target shape",
        "rm on protected roots is policy-governed",
        "removing missing target may be ERR_NOT_FOUND or idempotent no-op only if canonical later defines it explicitly",
    ]


def cp_rules() -> List[str]:
    return [
        "cp copies data from explicit source to explicit target",
        "cp does not delete source",
        "cp must preserve source content semantics according to primitive shape",
        "cp must not invent hidden transformations outside canonical conversion rules",
        "cp into protected roots remains policy-governed",
    ]


def mv_rules() -> List[str]:
    return [
        "mv moves data from explicit source to explicit target",
        "mv = copy then source removal as one canonical operation",
        "mv must not partially succeed silently",
        "mv failure semantics must be explicit in implementation/runtime policy",
        "mv into or out of protected roots remains policy-governed",
    ]


def add_rules() -> List[str]:
    return [
        "add.item on # target appends a new numerically named child entry",
        "new child index is greater than the current greatest numeric sibling key",
        "numeric indexing begins from 0 when branch is empty",
        "add.item on & appends new next numeric item",
        "add.item stores payload as data; execution happens only if later run/loop uses it",
        "add.item must not overwrite existing child key",
    ]


def merge_rules() -> List[str]:
    return [
        "merge means structural combine, not JSON text concatenation",
        "merge combines branch structures by canonical shape rules",
        "merge must remain explicit command behavior, never implicit '=' behavior",
        "merge conflict policy must be explicit in command/runtime spec",
        "merge into protected roots remains policy-governed",
    ]


def import_export_rules() -> List[str]:
    return [
        "import is explicit structural load operation",
        "import may reset and overwrite target according to import mode",
        "export is explicit structural serialization/output operation",
        "import/export are command-level behaviors, not implicit parser behaviors",
        "file/code/json shape handling must be explicit per import/export command family",
    ]


# ---------------------------------------------------------------------
# COMMAND RESULT CONTRACT
# ---------------------------------------------------------------------


def command_result_contract_rules() -> List[str]:
    return [
        "commands produce effects only through explicit target writes, runtime-defined status changes, or explicit output branches",
        "no command may rely on hidden result channels",
        "commands that write output must define exact output target contract",
        "commands that do not define output target must not invent one silently unless canonical command family explicitly says so",
    ]


# ---------------------------------------------------------------------
# STATE SHAPE CLARIFICATIONS
# ---------------------------------------------------------------------


def state_shape_clarification_rules() -> List[str]:
    return [
        "$ is for keyed symbolic state",
        "& is for ordered items/lists",
        "# is for structured branches and cell/property addressing",
        "general # namespaces may be non-numeric outside sortable contexts",
        "numeric sort rule applies only where a command/runtime context explicitly treats children as sortable indices",
        "state model must preserve ability to address #cell:property paths exactly",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID ASSIGNMENT EXAMPLES
# ---------------------------------------------------------------------


def valid_assignment_examples() -> List[str]:
    return [
        "$UM.sensor:temp = 40",
        "$UM.mode:state = auto",
        "&tasks:0 = run %job.cooling",
        "#table:0:cmd = run %job",
        "#cell:property = value",
        "%job:status = pause",
    ]


def invalid_assignment_examples() -> List[str]:
    return [
        "$UM.sensor = 1",
        "$UM.sensor:temp = ",
        "$SYSTEM = raw",
        "$UM.sensor:temp = 1 + 2",
        "$UM.sensor:temp = run %job",
        "#SYSTEM = overwrite",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


ASSIGNMENT_AND_STATE_SUMMARY = {
    "assignment_form": "<target> = <rhs>",
    "rhs_required": True,
    "general_expression_language": False,
    "implicit_copy_on_assignment": False,
    "implicit_merge_on_assignment": False,
    "implicit_command_execution": False,
    "canonical_storage_model": "string-first symbolic surface",
    "protected_roots": list(PROTECTED_ROOTS),
    "ownership": {
        "module_write_scope": "$UM.<module>",
        "cross_module_direct_write": False,
        "cross_module_read": True,
    },
    "state_families": {
        "$": "keyed symbolic scalar state",
        "&": "ordered items / lists",
        "#": "recursive structured branches",
        "!": "trigger identities/state",
        "@": "event identities/state",
        "%": "runner identities/fields",
    },
    "structural_ops": {
        "rm": "explicit remove",
        "cp": "explicit copy",
        "mv": "explicit move",
        "add.item": "explicit append/create numeric child",
        "merge": "explicit structural combine",
        "import_export": "explicit command behavior",
    },
}
