"""
AIGMos v36 — Python-style spec
MODULE: parser_and_grammar

Purpose:
    Define the canonical parser contracts, command-line grammar locks,
    path grammar, quoting rules, parser order, and sortable-context rules.

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


# ---------------------------------------------------------------------
# CANONICAL IDENTIFIERS / GRAMMAR TOKENS
# ---------------------------------------------------------------------


COMMAND_NAME_RULE = r"[a-zA-Z0-9._]+"
FIELD_NAME_RULE = r"[a-zA-Z0-9._]+"
SEGMENT_RULE = r"[A-Za-z0-9._-]+"

ROOT_PREFIXES = ("$", "&", "#", "!", "@", "%")

ASSIGNMENT_OPERATOR = "="

BOOLEAN_OPERATORS = ("AND", "OR", "XOR", "NOT")
COMPARISON_OPERATORS = ("==", "!=", "<", "<=", ">", ">=")
ARITHMETIC_OPERATORS = ("+", "-", "*", "/")

SORTABLE_NUMERIC_KEY_RULE = r"0|[1-9][0-9]*"


# ---------------------------------------------------------------------
# PARSER MODEL
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ParserModelSpec:
    """
    Canonical parser model.

    Key locks:
    - one line = one command
    - one command = one parse target
    - no implicit multi-command expansion
    - all state-changing behavior must remain explicit
    """
    one_line_one_command: bool = True
    implicit_multi_command: bool = False
    parser_is_deterministic: bool = True
    hidden_commands_allowed: bool = False
    hidden_state_writes_allowed: bool = False


def parser_global_rules() -> List[str]:
    return [
        "one line = one command",
        "one parsed command line must resolve to exactly one command form",
        "no semicolon-based command chaining",
        "no shell-style piping",
        "no implicit macro expansion in parser layer",
        "no hidden command injection",
        "all parser behavior must be deterministic",
        "parser must reject ambiguous forms rather than guessing intent",
    ]


def parser_whitespace_rules() -> List[str]:
    return [
        "leading whitespace is ignored",
        "trailing whitespace is ignored",
        "internal whitespace separates tokens",
        "multiple consecutive whitespace characters collapse as separators outside quoted text",
        "quoted text preserves internal whitespace content",
        "empty line is not a command",
    ]


def parser_line_rules() -> List[str]:
    return [
        "parser input unit is one logical line",
        "one logical line may define one assignment, one command, one trig declaration, or one event declaration",
        "line must not contain multiple executable commands",
        "multi-line composition belongs to list/table primitives, not parser chaining",
    ]


def parser_order_rules() -> List[str]:
    """
    Canonical parse-order lock.

    This order is important and must remain stable unless canonical changes.
    """
    return [
        "1) trim outer whitespace",
        "2) detect 'on <trigger> <event> <body>' event declaration form",
        "3) detect assignment form using '='",
        "4) otherwise parse as command form",
        "parser must not reinterpret an already-matched earlier form as a later form",
    ]


def parser_assignment_detection_rules() -> List[str]:
    return [
        "assignment detection happens before generic command parsing",
        "assignment requires exactly one assignment target on left side",
        "assignment target must be a writable canonical path",
        "assignment operator is plain '='",
        "assignment must not be inferred if line is already matched as event declaration",
    ]


def parser_event_detection_rules() -> List[str]:
    return [
        "event declaration begins with literal token 'on'",
        "event declaration form is parsed before generic assignment/command ambiguity resolution finishes",
        "event body must be explicit",
        "event body may be quoted command text or explicit state command target according to canonical event rules",
    ]


# ---------------------------------------------------------------------
# QUOTING / ESCAPE RULES
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class QuoteModelSpec:
    """
    Canonical quote model.

    V1 goal:
    - keep quoting simple
    - avoid shell-like complexity
    - preserve deterministic parsing
    """
    supports_double_quotes: bool = True
    supports_single_quotes: bool = True
    nested_quotes: bool = False
    implicit_unescape_magic: bool = False


def quote_rules() -> List[str]:
    return [
        "single-quoted and double-quoted strings are allowed where literal text is required",
        "quoted text is treated as one token for parser splitting purposes",
        "quotes are used to preserve spaces and literal operator characters",
        "unclosed quote => ERR_SYNTAX",
        "nested quoting is not required in V1",
        "parser must not silently repair broken quoting",
    ]


def escape_rules() -> List[str]:
    return [
        "escape behavior must remain minimal and explicit",
        "parser must not invent shell-style escape semantics unless later canonical defines them",
        "if backslash escaping is supported in implementation, it must be documented 1:1 and remain deterministic",
        "unknown escape sequence must not be silently normalized into something else",
    ]


def quoting_usage_rules() -> List[str]:
    return [
        "numbers do not require quotes",
        "simple command names do not require quotes",
        "paths do not require quotes unless embedded as literal text in another command argument position",
        "text containing spaces should be quoted when intended as one literal argument",
        "event command bodies may require quotes depending on declaration form",
    ]


# ---------------------------------------------------------------------
# COMMAND GRAMMAR
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CommandGrammarSpec:
    """
    Canonical command grammar.

    Command names are intentionally locked to a restricted pattern.
    """
    command_name_rule: str = COMMAND_NAME_RULE
    case_sensitive: bool = True
    hidden_alias_inference: bool = False


def command_grammar_rules() -> List[str]:
    return [
        "command name must match [a-zA-Z0-9._]+",
        "command name does not contain whitespace",
        "command name does not contain ':'",
        "command name does not contain '#' '$' '&' '!' '@' '%'",
        "command parsing is case-sensitive unless canonical later changes that explicitly",
        "unknown command => ERR_SYNTAX or command-surface rejection depending on layer",
    ]


def command_argument_rules() -> List[str]:
    return [
        "arguments are whitespace-delimited unless preserved by quotes",
        "command-specific argument validation belongs to the command spec",
        "parser only splits and preserves literal structure; semantic validation happens later",
        "multi-command payload is not allowed unless canonical command explicitly accepts one command line as literal text",
    ]


# ---------------------------------------------------------------------
# FIELD / PATH GRAMMAR
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class PathGrammarSpec:
    """
    Canonical path model.

    Core idea:
    - root prefix indicates primitive family / runtime namespace
    - ':' separates path segments
    - '.' is allowed inside a segment and does NOT segment the path
    """
    segment_separator: str = ":"
    dot_is_segment_separator: bool = False
    empty_segment_allowed: bool = False
    leading_separator_allowed: bool = False
    trailing_separator_allowed: bool = False


def general_path_rules() -> List[str]:
    return [
        "canonical paths begin with one of: $, &, #, !, @, %",
        "':' is the only path segment separator",
        "'.' never segments a path by itself",
        "'.' is part of the segment text when present",
        "empty path segment => ERR_SYNTAX",
        "leading ':' after root => ERR_SYNTAX",
        "trailing ':' => ERR_SYNTAX",
        "double separator '::' creates empty segment => ERR_SYNTAX",
    ]


def path_segment_rules() -> List[str]:
    return [
        "each segment must be non-empty",
        "segment text may include letters, digits, dot, underscore, and hyphen according to canonical segment rule",
        "parser must not normalize or lowercase segments implicitly",
        "segment meaning depends on primitive family and field name, not parser guessing",
    ]


def protected_shape_rules() -> List[str]:
    return [
        "$ paths represent scalar / key-value symbolic state references",
        "& paths represent ordered command or item lists",
        "# paths represent recursive structured branches, rows, and cells",
        "! paths represent trigger identities",
        "@ paths represent event identities",
        "% paths represent runner / loop identities and fields",
    ]


def dollar_path_rules() -> List[str]:
    return [
        "canonical writable scalar target form is $subject:key",
        "$ target without field key is not a valid value assignment target in strict canonical mode",
        "$ path may contain dots inside a segment, e.g. $UM.sensor:temp",
        "$UM.module:field is a normal valid shape",
    ]


def ampersand_path_rules() -> List[str]:
    return [
        "&name identifies a list root",
        "&name:index addresses a list item in contexts that access explicit indices",
        "sortable list indices are numeric in sortable contexts",
        "& payload may hold multiple command lines as data, not as already-executing parser chain",
    ]


def hash_path_rules() -> List[str]:
    return [
        "# is a general recursive structured namespace",
        "#branch:child:leaf is valid structured addressing",
        "#cell:property = value is valid and property addressing must remain possible",
        "# paths are not limited to tables only",
        "# may store rows, cells, properties, logs, inbound adapter payloads, and structured output branches",
    ]


def bang_path_rules() -> List[str]:
    return [
        "!name identifies a trigger",
        "!name.subname is valid because '.' is part of segment text",
        "! path segments still split only on ':'",
    ]


def at_path_rules() -> List[str]:
    return [
        "@name identifies an event",
        "@name.subname is valid because '.' is part of segment text",
        "@ path segments still split only on ':'",
    ]


def percent_path_rules() -> List[str]:
    return [
        "%name identifies a runner/loop root",
        "%name:status addresses runner status field",
        "%name:step addresses runner step field where defined by canonical runner model",
        "% path segments still split only on ':'",
    ]


# ---------------------------------------------------------------------
# FIELD GRAMMAR
# ---------------------------------------------------------------------


def field_grammar_rules() -> List[str]:
    return [
        "field names inside command semantics may use [a-zA-Z0-9._]+ unless narrower command rules override them",
        "field grammar does not override path segment grammar",
        "field names are semantic identifiers, not separate parser roots",
    ]


# ---------------------------------------------------------------------
# SORT RULE / SCOPE
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SortScopeSpec:
    """
    Canonical clarification for numeric sorting.

    Important:
    - numeric sort is NOT a global restriction on all # segments
    - numeric sort applies only in sortable contexts
    """
    global_numeric_sort: bool = False
    sortable_contexts_only: bool = True


def sortable_context_rules() -> List[str]:
    return [
        "numeric sort rule applies only in sortable contexts",
        "sortable contexts include list-like row iteration, loop row expansion, indexed log-book traversal, and other explicitly sortable branches",
        "in sortable contexts, keys must be numeric strings",
        "non-numeric key in sortable context => ERR_SYNTAX",
        "numeric sorting is ascending unless canonical command overrides it explicitly",
    ]


def nonsortable_context_rules() -> List[str]:
    return [
        "general # namespace is not restricted to numeric child names",
        "general structured addressing may use non-numeric segment names normally",
        "adapter payload branches, named fields, and structured properties are valid even when not numeric",
        "parser must not reject non-numeric # segments outside sortable contexts",
    ]


def sort_examples_valid() -> List[str]:
    return [
        "#log:0",
        "#log:1",
        "#table:rowA:cell",
        "#OSC:in:button:1",
        "&tasks:0",
        "&tasks:1",
    ]


def sort_examples_invalid_in_sortable_context() -> List[str]:
    return [
        "&tasks:alpha    # invalid if used as sortable list index",
        "#row:foo        # invalid if parser/command expects numeric sortable row index here",
    ]


# ---------------------------------------------------------------------
# TRIGGER EXPRESSION PARSER BOUNDARY
# ---------------------------------------------------------------------


def trigger_expression_parser_boundary_rules() -> List[str]:
    return [
        "trigger expression parsing is separate from general command parsing",
        "math/comparison/boolean operators are allowed only inside trig declaration expression scope",
        "general command surface must not become a global expression language",
        "assignment RHS is not an expression language by default",
        "event bodies are not expression language by default",
        "runner steps are command lines, not free-form arithmetic expressions",
    ]


# ---------------------------------------------------------------------
# VALID / INVALID SHAPE EXAMPLES
# ---------------------------------------------------------------------


def valid_examples() -> List[str]:
    return [
        "$UM.sensor:temp = 40",
        "$SYSTEM:error.log = #log:error",
        "&tasks:0 = run %job",
        "#OSC:in:button:1 = 256",
        "#SYSTEM:clear:alias:clear = rm $CH",
        "trig !sensor.hot $UM.sensor:temp >= 40",
        "on !sensor.hot @cooling.start \"run %runner.cooling\"",
        "%cooling:status = pause",
        "wait 100",
    ]


def invalid_examples() -> List[str]:
    return [
        "$UM.sensor = 1",
        "$UM::temp = 1",
        "$UM.sensor: = 1",
        "cmd:name arg",
        "trig !foo $UM.mode + \"auto\"",
        "#foo::bar = 1",
        "on !sensor.hot @cooling.start run %runner ; wait 100",
        "wait 1.5",
    ]


# ---------------------------------------------------------------------
# SUMMARY BLOCK
# ---------------------------------------------------------------------


PARSER_AND_GRAMMAR_SUMMARY = {
    "one_line_one_command": True,
    "parser_order": [
        "trim",
        "event declaration",
        "assignment",
        "command",
    ],
    "command_name_rule": COMMAND_NAME_RULE,
    "path_segment_separator": ":",
    "dot_is_segment_separator": False,
    "empty_segments_allowed": False,
    "quote_model": {
        "single_quotes": True,
        "double_quotes": True,
        "nested_quotes": False,
    },
    "sortable_context_numeric_only": True,
    "global_numeric_only_namespace": False,
    "general_expression_language": False,
    "trigger_expression_scope_only": True,
}
