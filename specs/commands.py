"""
AIGMos v36 — Python-style spec
MODULE: commands

Purpose:
    Define the locked canonical command surface, command families,
    command shape contracts, and command-level nonfeatures.

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
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_OWNERSHIP = "ERR_OWNERSHIP"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_ADAPTER = "ERR_ADAPTER"


# ---------------------------------------------------------------------
# GLOBAL COMMAND SURFACE MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommandSurfaceSpec:
    """
    Canonical command-surface model.

    Core locks:
    - command surface is explicit
    - commands are governed names, not free-form language
    - parser does not invent commands
    - commands do exactly what their contract says
    """
    explicit_surface: bool = True
    hidden_commands_allowed: bool = False
    implicit_macro_language: bool = False
    implicit_shell_features: bool = False


def command_surface_rules() -> List[str]:
    return [
        "canonical command surface is explicit and governed",
        "commands are named operations, not a free-form shell language",
        "parser must not invent commands",
        "unknown command is rejection, not fuzzy interpretation",
        "command contracts must be stable and auditable",
        "command execution must not rely on hidden side channels",
    ]


def command_surface_nonfeatures() -> List[str]:
    return [
        "no semicolon chaining",
        "no pipe operator",
        "no shell substitution",
        "no implicit macro expansion",
        "no hidden expression-language promotion of all arguments",
        "no background magic outside explicitly specced runtime commands",
    ]


# ---------------------------------------------------------------------
# LOCKED COMMAND FAMILIES
# ---------------------------------------------------------------------


LOCKED_COMMAND_FAMILIES = {
    "governance": [
        "claim.root",
        "release.root",
        "claim.command",
        "release.command",
        "claim.command.alias",
        "release.command.alias",
        "claim.Q.alias",
        "release.Q.alias",
    ],
    "runtime_control": [
        "run",
        "loop",
        "wait",
        "delay",
        "timeout",
    ],
    "state_ops": [
        "rm",
        "cp",
        "mv",
        "merge",
        "add.item",
    ],
    "definition_ops": [
        "trig",
        "on",
    ],
    "transport_q": [
        "Q",
        "Qc",
    ],
    "integration_http": [
        "HTTP.GET",
        "HTTP.POST",
        "HTTP.PUT",
        "HTTP.DELETE",
        "HTTP.PATCH",
        "HTTP.HEAD",
    ],
    "serialization": [
        "import",
        "export",
    ],
}


def locked_command_family_rules() -> List[str]:
    return [
        "locked command families define canonical named operations",
        "presence in this module does not imply unrestricted execution; governance/ownership rules still apply",
        "commands outside locked families require explicit later canonical addition",
        "family grouping is documentation structure, not alternate parser behavior",
    ]


# ---------------------------------------------------------------------
# GOVERNANCE COMMANDS
# ---------------------------------------------------------------------


def governance_command_rules() -> Dict[str, List[str]]:
    return {
        "claim.root": [
            "reserves/registers a governed command root",
            "duplicate claim => ERR_STATE",
            "must be explicit",
        ],
        "release.root": [
            "releases a previously claimed command root explicitly",
            "unknown root => ERR_NOT_FOUND",
        ],
        "claim.command": [
            "registers a governed command name",
            "duplicate command => ERR_STATE",
            "no implicit replace in V1",
        ],
        "release.command": [
            "releases a previously claimed command explicitly",
            "unknown command => ERR_NOT_FOUND",
        ],
        "claim.command.alias": [
            "binds alias to already claimed command",
            "base command must exist first",
            "duplicate alias => ERR_STATE",
        ],
        "release.command.alias": [
            "removes a previously claimed alias",
            "unknown alias => ERR_NOT_FOUND",
        ],
        "claim.Q.alias": [
            "registers governed Q alias contract",
            "alias remains part of governed Q family",
        ],
        "release.Q.alias": [
            "removes governed Q alias contract explicitly",
        ],
    }


# ---------------------------------------------------------------------
# RUNTIME CONTROL COMMANDS
# ---------------------------------------------------------------------


def runtime_control_command_rules() -> Dict[str, List[str]]:
    return {
        "run": [
            "launches/creates runner execution through explicit %runner identity",
            "same-name collision => ERR_STATE",
            "does not silently revive terminal runner",
        ],
        "loop": [
            "creates loop execution through %runner identity",
            "loop is runner-form execution, not separate root family",
            "same-name collision => ERR_STATE",
        ],
        "wait": [
            "syntax: wait <ms>",
            "blocks current runner step",
            "does not write state by itself",
        ],
        "delay": [
            "syntax: delay <ms> <command>",
            "schedules one future command dispatch",
            "non-blocking for current step",
        ],
        "timeout": [
            "syntax: timeout <ms> %runner",
            "registers runner-level deadline",
            "on expiry => ERR_TIMEOUT + %runner:status = error",
        ],
    }


# ---------------------------------------------------------------------
# STATE OPS COMMANDS
# ---------------------------------------------------------------------


def state_ops_command_rules() -> Dict[str, List[str]]:
    return {
        "rm": [
            "removes addressed canonical target explicitly",
            "does not imply broader recursive deletion unless target/command contract says so",
            "protected-root removal remains policy-governed",
        ],
        "cp": [
            "copies from explicit source to explicit target",
            "does not delete source",
            "no hidden transform beyond canonical shape rules",
        ],
        "mv": [
            "moves from explicit source to explicit target",
            "equivalent to governed copy + source removal as one canonical operation",
            "must not partially succeed silently",
        ],
        "merge": [
            "explicit structural combine",
            "not text concatenation by default",
            "not implicit behavior of '='",
        ],
        "add.item": [
            "adds next numeric child/item to # or & target according to family rules",
            "new key is greater than current greatest numeric sibling",
            "starts from 0 when branch/list is empty",
        ],
    }


# ---------------------------------------------------------------------
# DEFINITION COMMANDS
# ---------------------------------------------------------------------


def definition_command_rules() -> Dict[str, List[str]]:
    return {
        "trig": [
            "syntax: trig !name <expression>",
            "defines named trigger",
            "expression scope exists only inside trig declarations",
        ],
        "on": [
            "syntax: on <trigger> <event> <body>",
            "defines named event binding",
            "body must be explicit and single-unit in V1",
        ],
    }


# ---------------------------------------------------------------------
# Q COMMANDS
# ---------------------------------------------------------------------


def q_command_rules() -> Dict[str, List[str]]:
    return {
        "Q": [
            "writes to governed $CH default branch",
            "append-like numeric growth",
            "may also be used as Q.<alias> under governed alias contract",
        ],
        "Qc": [
            "requires explicit output target",
            "does not silently default to $CH when explicit target is required",
        ],
    }


def q_command_examples() -> List[str]:
    return [
        "Q hello",
        "Q.status ok",
        "Qc hello #out:chat",
    ]


# ---------------------------------------------------------------------
# HTTP COMMANDS
# ---------------------------------------------------------------------


def http_command_rules() -> Dict[str, List[str]]:
    return {
        "HTTP.GET": [
            "syntax: HTTP.GET <url> <output>",
            "writes to caller-supplied # output branch",
        ],
        "HTTP.POST": [
            "syntax: HTTP.POST <url> <body> <output>",
            "writes to caller-supplied # output branch",
        ],
        "HTTP.PUT": [
            "syntax: HTTP.PUT <url> <body> <output>",
            "writes to caller-supplied # output branch",
        ],
        "HTTP.DELETE": [
            "syntax: HTTP.DELETE <url> <output>",
            "writes to caller-supplied # output branch",
        ],
        "HTTP.PATCH": [
            "syntax: HTTP.PATCH <url> <body> <output>",
            "writes to caller-supplied # output branch",
        ],
        "HTTP.HEAD": [
            "syntax: HTTP.HEAD <url> <output>",
            "writes to caller-supplied # output branch",
        ],
    }


# ---------------------------------------------------------------------
# IMPORT / EXPORT
# ---------------------------------------------------------------------


def serialization_command_rules() -> Dict[str, List[str]]:
    return {
        "import": [
            "explicit structural load operation",
            "may reset/overwrite target according to import mode",
            "not implicit parser behavior",
        ],
        "export": [
            "explicit structural serialization/output operation",
            "shape/format must be explicit per command contract",
            "not implicit parser behavior",
        ],
    }


# ---------------------------------------------------------------------
# COMMAND RESULT CONTRACT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommandResultContractSpec:
    """
    Canonical command result contract.

    Core lock:
    - command effects are explicit
    - outputs are written only where contract says
    - no hidden result channels
    """
    hidden_result_channels: bool = False
    explicit_output_contract_required: bool = True
    implicit_unrelated_writes_allowed: bool = False


def command_result_rules() -> List[str]:
    return [
        "commands produce effects only through explicit target writes, explicit output branches, or explicit runtime state transitions",
        "commands must not invent hidden output channels",
        "commands must not write unrelated state silently",
        "when command family defines output target contract, that exact contract must be followed",
        "when command family does not define default output, runtime must not invent one silently",
    ]


# ---------------------------------------------------------------------
# COMMAND-SHAPE VALIDATION
# ---------------------------------------------------------------------


def command_shape_validation_rules() -> List[str]:
    return [
        "each command validates its own required argument count and argument kinds",
        "missing required argument => ERR_SYNTAX",
        "wrong target family/kind => ERR_TYPE or ERR_SYNTAX depending on layer",
        "policy/ownership violation => ERR_OWNERSHIP",
        "duplicate governed identity => ERR_STATE",
        "unknown referenced entity => ERR_NOT_FOUND",
    ]


# ---------------------------------------------------------------------
# COMMAND INTERACTION BOUNDARIES
# ---------------------------------------------------------------------


def command_boundary_rules() -> List[str]:
    return [
        "commands do not redefine parser grammar",
        "commands do not create global expression-language semantics unless their own contract explicitly defines a narrow expression scope",
        "trigger math remains inside trig declarations only",
        "time-control commands do not imply scheduler framework beyond their explicit contract",
        "Q output contract is separate from HTTP output contract",
        "runner control is primarily through %runner:status contract, not separate stop/cancel/abort commands",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def command_examples_valid() -> List[str]:
    return [
        "run %job",
        "loop %jobs &tasks",
        "wait 100",
        "delay 500 run %cooling.sequence",
        "timeout 5000 %job",
        "rm $CH.status:00001",
        "cp #src:0 #dst:0",
        "mv &tasks:0 #archive:0",
        "merge #a #b",
        "add.item #table:row $UM.sensor:temp",
        "trig !sensor.hot $UM.sensor:temp >= 40",
        'on !sensor.hot @cooling.start "run %runner.cooling"',
        "Q hello",
        "Qc hello #out:chat",
        "HTTP.GET https://example.com #out:http:0",
        "import file.json #cfg",
        "export #cfg file.json",
    ]


def command_examples_invalid() -> List[str]:
    return [
        "stop %job",
        "cancel %job",
        "abort %job",
        "run %job ; wait 100",
        "delay 100 cmd1 ; cmd2",
        "timeout 100 run %job",
        "HTTP.GET https://example.com",
        "Qc hello",
        "trig !foo $UM.a + $UM.b",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


COMMANDS_SUMMARY = {
    "explicit_surface": True,
    "hidden_commands_allowed": False,
    "implicit_macro_language": False,
    "families": LOCKED_COMMAND_FAMILIES,
    "result_contract": {
        "hidden_result_channels": False,
        "explicit_output_contract_required": True,
        "implicit_unrelated_writes_allowed": False,
    },
    "nonfeatures": [
        "semicolon chaining",
        "pipe operator",
        "shell substitution",
        "hidden macro expansion",
        "global expression language",
    ],
}
