"""
AIGMos v36 — Python-style spec
MODULE: q_and_claims

Purpose:
    Define canonical command claiming, alias ownership, Q / Qc behavior,
    $CH contract, gateway / choke-point policy, and command-surface control.

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
# COMMAND CLAIM MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommandClaimModelSpec:
    """
    Canonical command-surface governance model.

    Core lock:
    - command surface is explicit
    - commands must be claimed before aliasing
    - usermodules and integrations go through the same choke point
    """
    explicit_claim_required: bool = True
    implicit_alias_creation: bool = False
    hidden_command_registration: bool = False
    single_choke_point: bool = True


def claim_global_rules() -> List[str]:
    return [
        "command surface is explicit and governed",
        "commands must be claimed before aliasing",
        "alias creation without claimed base command is invalid",
        "runtime must not silently auto-register commands",
        "usermodules do not bypass command-surface governance",
        "single choke point applies to usermodule command access and alias-dispatched execution",
    ]


def claim_root_rules() -> List[str]:
    return [
        "claim.root defines or reserves a command root for governed use",
        "claim.root is explicit governance action, not implicit side effect",
        "claim.root must not silently overwrite an existing claimed root",
        "duplicate claimed root => ERR_STATE",
        "release.root removes governance reservation only by explicit action",
    ]


def claim_command_rules() -> List[str]:
    return [
        "claim.command registers a command name into governed command surface",
        "claimed command identity is explicit and stable",
        "claim.command must fail if command already exists unless canonical later adds explicit replace mode",
        "duplicate claimed command => ERR_STATE",
        "release.command removes that claimed command identity explicitly",
    ]


def claim_alias_rules() -> List[str]:
    return [
        "claim.command.alias binds an alias to an already claimed command",
        "base command must exist before alias is created",
        "alias must not silently shadow an existing alias or command",
        "duplicate alias => ERR_STATE",
        "release.command.alias removes that alias explicitly",
        "alias is governance metadata, not parser magic",
    ]


def claim_validation_rules() -> List[str]:
    return [
        "claim validation happens at governance layer before runtime dispatch",
        "unknown claimed target => ERR_NOT_FOUND",
        "ownership/policy violation => ERR_OWNERSHIP",
        "invalid claim syntax => ERR_SYNTAX",
    ]


# ---------------------------------------------------------------------
# GATEWAY / CHOKE-POINT POLICY
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class GatewayPolicySpec:
    """
    Canonical gateway model.

    Core lock:
    - usermodule-visible commands must pass through governed gateway surface
    - direct hidden execution paths are not allowed
    """
    single_choke_point: bool = True
    hidden_bypass_allowed: bool = False
    alias_dispatch_allowed: bool = True


def gateway_rules() -> List[str]:
    return [
        "all governed command execution passes through command surface gateway",
        "usermodules may use only commands exposed through claimed/aliased command surface",
        "no hidden execution bypass around gateway",
        "no private magical command channel outside governance policy",
        "alias dispatch is explicit and traceable",
        "gateway must remain auditable",
    ]


def usermodule_gateway_rules() -> List[str]:
    return [
        "usermodule writes only to its owned namespace remain separate from command governance",
        "but when a usermodule invokes a command, it must use the governed command surface",
        "usermodule must not invoke arbitrary hidden internal runtime functions directly through canonical surface",
        "UM-prefixed commands still require explicit command-surface registration if exposed canonically",
    ]


# ---------------------------------------------------------------------
# Q / QC MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class QModelSpec:
    """
    Canonical Q / Qc model.

    Intent:
    - Q writes to canonical chat/output buffer space
    - Q.alias writes to alias-specific buffer branch
    - Qc requires explicit output target
    """
    q_requires_explicit_output: bool = False
    qc_requires_explicit_output: bool = True
    q_default_output_root: str = "$CH"


def q_global_rules() -> List[str]:
    return [
        "Q is governed command-surface command family",
        "Q uses canonical chat/output buffer contract rooted at $CH",
        "Q.<alias> uses alias-scoped branch under $CH",
        "Qc requires explicit output target",
        "Q/Qc behavior must remain explicit and auditable",
        "Q/Qc must not invent hidden side-channel outputs",
    ]


def q_rules() -> List[str]:
    return [
        "Q writes to $CH by default",
        "Q with no alias uses canonical default branch in $CH",
        "Q may create a new numeric item in its governed output branch",
        "Q result growth is append-like by numeric ordering",
        "Q must not overwrite unrelated existing branches silently",
    ]


def q_alias_rules() -> List[str]:
    return [
        "Q.<alias> writes to $CH.<alias>",
        "alias must be claimed/governed before use if canonical governance policy requires it",
        "each Q alias has its own output branch scope",
        "Q.<alias> append behavior follows same numeric growth contract as Q",
    ]


def qc_rules() -> List[str]:
    return [
        "Qc requires explicit output target",
        "Qc does not default silently to $CH when explicit target is required",
        "Qc output target must be writable by policy",
        "Qc may write to explicit canonical target allowed by command contract",
        "missing explicit output target => ERR_SYNTAX",
    ]


# ---------------------------------------------------------------------
# $CH CONTRACT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CHContractSpec:
    """
    Canonical $CH contract.

    $CH is protected.
    It is not open arbitrary overwrite space.
    It is governed append/output space used by Q-family behavior.
    """
    protected: bool = True
    default_append_numeric: bool = True
    fixed_width_id_locked: bool = True
    fixed_width_digits: int = 5


def ch_global_rules() -> List[str]:
    return [
        "$CH is protected",
        "$CH is governed output/chat buffer root",
        "$CH may contain default branch and alias-specific branches",
        "$CH growth is append-like using numeric ordering",
        "append item IDs are fixed-width 5-digit strings in canonical contract",
        "runtime must not silently change width once locked canonically",
    ]


def ch_shape_rules() -> List[str]:
    return [
        "$CH default branch may hold indexed items",
        "$CH.<alias> branch may hold indexed items for that alias scope",
        "indexed children use fixed-width numeric string IDs such as 00001",
        "index ordering is numeric ascending by canonical interpretation",
        "new item index is greater than current greatest existing numeric item in that branch",
        "empty branch starts from canonical first index defined by implementation policy, but width remains fixed",
    ]


def ch_append_rules() -> List[str]:
    return [
        "Q appends into governed $CH branch",
        "Q.<alias> appends into governed $CH.<alias> branch",
        "append does not overwrite previous items",
        "append target branch is explicit by Q contract, not inferred by unrelated command",
        "manual direct writes to protected $CH remain policy-governed",
    ]


def ch_clear_rules() -> List[str]:
    return [
        "rm $CH clears/removes default $CH branch according to protected policy",
        "rm $CH.alias clears/removes alias branch according to protected policy",
        "rm $CH.alias:00001 removes exactly that indexed item",
        "/clear ch and related aliases are governance/alias conveniences, not parser primitives by themselves",
        "clear behavior must map to explicit canonical remove semantics, not hidden magic",
    ]


def ch_examples_valid() -> List[str]:
    return [
        "Q hello",
        "Q.status system ok",
        "Qc hello #out:chat",
        "rm $CH.status",
        "rm $CH.status:00001",
    ]


def ch_examples_invalid() -> List[str]:
    return [
        "$CH = raw overwrite",
        "$CH.status = force",
        "Qc hello",
    ]


# ---------------------------------------------------------------------
# CLAIM + Q ALIAS COUPLING
# ---------------------------------------------------------------------


def q_claim_rules() -> List[str]:
    return [
        "claim.Q.alias registers a governed Q alias contract where supported by canonical command family",
        "release.Q.alias removes that governed alias contract explicitly",
        "Q aliasing is governance action, not ad hoc parser shortcut",
        "Q alias must not silently exist without explicit governance definition if canonical governance requires it",
    ]


def q_dispatch_rules() -> List[str]:
    return [
        "Q and Q.<alias> dispatch through same governed command surface as other commands",
        "Q alias dispatch remains auditable and attributable",
        "Q-family command use must not bypass gateway/choke-point policy",
    ]


# ---------------------------------------------------------------------
# RESULT / OUTPUT CONTRACT
# ---------------------------------------------------------------------


def q_output_contract_rules() -> List[str]:
    return [
        "Q output target is implicit only within its own canonical contract: $CH or $CH.<alias>",
        "Qc output target is explicit and caller-supplied",
        "commands outside Q-family must not assume $CH as hidden default output unless their own contract says so",
        "output contract must be exact and documented per command family",
    ]


def q_data_storage_rules() -> List[str]:
    return [
        "Q-family outputs are stored as canonical string/symbolic data",
        "Q-family must not leak hidden implementation objects into $CH",
        "stored output may later be read, listed, removed, or routed by explicit commands only",
    ]


# ---------------------------------------------------------------------
# OWNERSHIP / POLICY INTERACTION
# ---------------------------------------------------------------------


def q_policy_rules() -> List[str]:
    return [
        "$CH is protected, so general arbitrary writes remain disallowed by default",
        "Q/Q.<alias>/Qc may write where command contract explicitly permits",
        "manual cp/mv/merge into $CH remains policy-governed",
        "governed aliases do not weaken protected-root policy outside their exact contract",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID EXAMPLES
# ---------------------------------------------------------------------


def claim_examples_valid() -> List[str]:
    return [
        "claim.root Q",
        "claim.command Q",
        "claim.command.alias Q status",
        "claim.Q.alias status",
        "release.Q.alias status",
    ]


def claim_examples_invalid() -> List[str]:
    return [
        "claim.command.alias unknown status",
        "claim.command Q    # invalid if already claimed",
        "claim.command.alias Q status   # invalid if status already exists",
    ]


def gateway_examples() -> List[str]:
    return [
        "UM module invokes only claimed/exposed commands",
        "alias-dispatched Q.status still passes through gateway",
        "no hidden runtime backdoor command invocation",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


Q_AND_CLAIMS_SUMMARY = {
    "governance": {
        "explicit_claim_required": True,
        "implicit_alias_creation": False,
        "single_choke_point": True,
        "hidden_command_registration": False,
    },
    "Q": {
        "default_output": "$CH",
        "alias_output": "$CH.<alias>",
        "append_like_growth": True,
    },
    "Qc": {
        "explicit_output_required": True,
    },
    "$CH": {
        "protected": True,
        "fixed_width_ids": True,
        "fixed_width_digits": 5,
        "append_branching": ["$CH", "$CH.<alias>"],
    },
    "gateway": {
        "bypass_allowed": False,
        "alias_dispatch_allowed": True,
        "usermodule_must_use_governed_surface": True,
    },
}
