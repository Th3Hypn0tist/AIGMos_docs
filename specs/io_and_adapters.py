"""
AIGMos v36 — Python-style spec
MODULE: io_and_adapters

Purpose:
    Define canonical adapter boundary behavior, inbound/outbound IO policy,
    OSC / HTTP contracts, output-target rules, protected integration roots,
    and integration-side execution constraints.

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
    ERR_ADAPTER = "ERR_ADAPTER"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_OWNERSHIP = "ERR_OWNERSHIP"


# ---------------------------------------------------------------------
# ADAPTER MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class AdapterModelSpec:
    """
    Canonical adapter boundary model.

    Core lock:
    - adapters move data/signals across the boundary
    - adapters do not bypass command-surface governance
    - adapter payloads are represented canonically through explicit roots/targets
    """
    boundary_explicit: bool = True
    hidden_bypass_allowed: bool = False
    adapter_executes_hidden_commands: bool = False


def adapter_global_rules() -> List[str]:
    return [
        "adapter boundary is explicit",
        "adapters move data/signals across boundary; they do not redefine canonical parser semantics",
        "adapters must not bypass gateway/choke-point governance for executable commands",
        "adapters must not inject hidden commands",
        "adapter payload shapes must be represented through explicit canonical targets/branches",
        "adapter failures must be observable through explicit error model",
    ]


def adapter_direction_rules() -> List[str]:
    return [
        "inbound adapter flow brings external data into canonical state surface",
        "outbound adapter flow sends explicit canonical data/commands outward",
        "inbound and outbound directions must remain distinguishable and auditable",
        "runtime must not silently reinterpret outbound data as inbound state or vice versa",
    ]


# ---------------------------------------------------------------------
# PROTECTED INTEGRATION ROOTS
# ---------------------------------------------------------------------


PROTECTED_INTEGRATION_ROOTS = (
    "#HTTP",
    "#OSC",
)


@dataclass(frozen=True)
class IntegrationRootsSpec:
    """
    Canonical protected integration roots.
    """
    protected_roots: Tuple[str, ...] = PROTECTED_INTEGRATION_ROOTS
    arbitrary_user_write_allowed: bool = False


def integration_root_rules() -> List[str]:
    return [
        "#HTTP is protected integration/runtime root",
        "#OSC is protected integration/runtime root",
        "protected integration roots are not open arbitrary write space by default",
        "specific canonical commands/adapters may write there by explicit policy",
        "general direct overwrite of protected integration roots is not allowed",
    ]


# ---------------------------------------------------------------------
# HTTP MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class HttpModelSpec:
    """
    Canonical HTTP command family model.

    Canonical command shapes discussed:
        HTTP.GET    <url> <output>
        HTTP.POST   <url> <body> <output>
        HTTP.PUT    <url> <body> <output>
        HTTP.DELETE <url> <output>
        HTTP.PATCH  <url> <body> <output>
        HTTP.HEAD   <url> <output>

    Core lock:
    - HTTP output writes into caller-supplied # output target
    - HTTP does not silently force output to #HTTP:<id>:...
    """
    output_target_required: bool = True
    output_target_family: str = "#"
    implicit_output_root: str = ""
    writes_to_caller_supplied_hash_branch: bool = True


HTTP_COMMANDS = (
    "HTTP.GET",
    "HTTP.POST",
    "HTTP.PUT",
    "HTTP.DELETE",
    "HTTP.PATCH",
    "HTTP.HEAD",
)


def http_global_rules() -> List[str]:
    return [
        "HTTP command family is explicit adapter-facing command family",
        "HTTP command names are governed command-surface names",
        "HTTP output target is caller-supplied # branch",
        "HTTP command must not silently redirect output into hidden default branch",
        "HTTP does not use #HTTP as mandatory caller output target",
        "#HTTP may still exist as protected inbound/runtime/integration branch family where runtime/adapters keep HTTP-related state",
    ]


def http_argument_rules() -> List[str]:
    return [
        "HTTP.GET requires <url> <output>",
        "HTTP.DELETE requires <url> <output>",
        "HTTP.HEAD requires <url> <output>",
        "HTTP.POST requires <url> <body> <output>",
        "HTTP.PUT requires <url> <body> <output>",
        "HTTP.PATCH requires <url> <body> <output>",
        "<output> must be caller-supplied # target",
        "missing required output target => ERR_SYNTAX",
        "output target outside allowed # family => ERR_TYPE or ERR_SYNTAX",
    ]


def http_output_rules() -> List[str]:
    return [
        "HTTP.* writes response data into caller-supplied # output branch",
        "exact output branch is the one the caller provided",
        "HTTP command must not silently choose #HTTP:<id>:... as output contract",
        "output data shape must remain explicit and stable per HTTP command family contract",
        "HTTP response metadata/body separation may exist, but must be stored under the explicit caller-supplied output branch if surfaced canonically",
    ]


def http_body_rules() -> List[str]:
    return [
        "HTTP.POST/PUT/PATCH body argument is explicit",
        "body may be literal payload text or explicit canonical source according to command contract",
        "body semantics must not be guessed silently by parser",
        "quoted body preserves literal spaces and symbols",
    ]


def http_error_rules() -> Dict[str, str]:
    return {
        "invalid command syntax": ErrorCode.ERR_SYNTAX.value,
        "missing or invalid output target": ErrorCode.ERR_SYNTAX.value,
        "adapter/network failure": ErrorCode.ERR_ADAPTER.value,
        "runtime integration subsystem failure": ErrorCode.ERR_RUNTIME.value,
    }


def http_examples_valid() -> List[str]:
    return [
        "HTTP.GET https://example.com #out:http:0",
        "HTTP.DELETE https://example.com/resource #out:http:1",
        'HTTP.POST https://example.com/api "{\\"x\\":1}" #out:http:2',
        "HTTP.HEAD https://example.com #out:http:3",
    ]


def http_examples_invalid() -> List[str]:
    return [
        "HTTP.GET https://example.com",
        "HTTP.POST https://example.com/api #out:http:0",
        "HTTP.GET https://example.com #HTTP",
        "HTTP.GET https://example.com $UM:http",
    ]


# ---------------------------------------------------------------------
# OSC MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class OscModelSpec:
    """
    Canonical OSC adapter model.

    Core ideas from canonical discussion:
    - OSC is fast namespace/datafeed style IO
    - #OSC can represent structured inbound/outbound addressing
    - ':' path style must preserve #cell:property addressing capability
    """
    protected_root: str = "#OSC"
    canonical_surface_uses_hash_namespace: bool = True
    slash_style_is_adapter_side_representation: bool = True


def osc_global_rules() -> List[str]:
    return [
        "OSC is adapter/integration/datafeed style IO",
        "#OSC is protected integration root family",
        "canonical structured addressing may represent OSC endpoints under #OSC using ':' segments",
        "adapter-side slash-style path such as /button/1 may map to canonical #OSC:... addressing by explicit adapter policy",
        "OSC integration must preserve ability to use #cell:property style addressing elsewhere; ':' cannot be globally consumed only as transport separator magic",
    ]


def osc_mapping_rules() -> List[str]:
    return [
        "canonical representation may use forms such as #OSC:in:button:1",
        "adapter-side transport path may correspond to /button/1",
        "in/out direction may be represented explicitly in canonical branch layout",
        "mapping between canonical branch and transport path must be explicit and deterministic",
        "runtime must not silently collapse unrelated canonical segments into ambiguous OSC transport paths",
    ]


def osc_state_rules() -> List[str]:
    return [
        "OSC inbound values may be stored under protected #OSC branches",
        "OSC outbound values may be sourced from explicit canonical targets/commands",
        "OSC value storage is data until explicit event/command logic acts on it",
        "OSC adapter does not itself bypass trigger/event/runner layers",
    ]


def osc_examples_valid() -> List[str]:
    return [
        "#OSC:in:button:1 = 256",
        "#OSC:out:led:on = 1",
        "#OSC:button:1 = 256    # valid if adapter policy defines that branch shape",
    ]


def osc_examples_invalid() -> List[str]:
    return [
        "#OSC = raw overwrite",
        "#OSC::button = 1",
    ]


# ---------------------------------------------------------------------
# ADAPTER OUTPUT / RESULT CONTRACTS
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class AdapterOutputContractSpec:
    """
    Canonical adapter output contract.

    Core lock:
    - output targets must be explicit per command family
    - commands outside a family must not assume the same defaults
    """
    explicit_contract_required: bool = True
    hidden_result_channels: bool = False


def adapter_output_contract_rules() -> List[str]:
    return [
        "adapter-facing command families must define exact output target contract",
        "no hidden result channels",
        "if command requires explicit output target, missing target is error",
        "commands outside same family must not assume that family's output defaults",
        "HTTP output contract and Q output contract are separate and must not be conflated",
    ]


def adapter_output_target_rules() -> List[str]:
    return [
        "caller-supplied output targets must be writable by policy",
        "protected integration roots remain policy-governed even when adapter family uses nearby namespaces",
        "explicit output target family/type must match command contract",
    ]


# ---------------------------------------------------------------------
# INBOUND / OUTBOUND EXECUTION BOUNDARIES
# ---------------------------------------------------------------------


def inbound_boundary_rules() -> List[str]:
    return [
        "inbound adapter payload arrival does not itself equal hidden command execution",
        "inbound data may update canonical state branches according to adapter policy",
        "trigger/event logic may later react to those writes through normal runtime flow",
        "adapter must not smuggle arbitrary executable multi-command payload through inbound state write path",
    ]


def outbound_boundary_rules() -> List[str]:
    return [
        "outbound adapter action must originate from explicit canonical command or explicit runtime-governed dispatch",
        "outbound adapter action must remain auditable",
        "outbound action must not silently mutate unrelated canonical state unless command contract says so",
    ]


# ---------------------------------------------------------------------
# POLICY / OWNERSHIP INTERACTION
# ---------------------------------------------------------------------


def adapter_policy_rules() -> List[str]:
    return [
        "adapter commands remain subject to governance and command-surface policy",
        "protected-root writes remain policy-governed",
        "integration adapters do not weaken ownership model",
        "usermodules interacting with adapters still use governed command surface",
    ]


# ---------------------------------------------------------------------
# NONFEATURES / EXPLICIT LIMITS
# ---------------------------------------------------------------------


def adapter_nonfeatures_v1() -> List[str]:
    return [
        "no hidden auto-discovery contract in canonical surface",
        "no implicit protocol translation without explicit adapter mapping policy",
        "no arbitrary executable payload tunneling through adapter data fields",
        "no silent fallback output target selection",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


IO_AND_ADAPTERS_SUMMARY = {
    "protected_integration_roots": list(PROTECTED_INTEGRATION_ROOTS),
    "adapter_boundary_explicit": True,
    "hidden_bypass_allowed": False,
    "HTTP": {
        "commands": list(HTTP_COMMANDS),
        "output_target_required": True,
        "output_target_family": "#",
        "writes_to": "caller-supplied # output branch",
        "forced_output_root": False,
    },
    "OSC": {
        "protected_root": "#OSC",
        "canonical_hash_namespace": True,
        "transport_path_mapping_explicit": True,
    },
    "hidden_result_channels": False,
}
