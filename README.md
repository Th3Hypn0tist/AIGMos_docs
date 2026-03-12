# AIGMos

**AIGMos** is a deterministic runtime and governed command surface for coordinating humans, AI models, sensors, machines, software systems, and nodes.

This repository is the **public Python-style specification** for AIGMos.
It is intentionally published as a **spec repo first**: explicit structure, explicit semantics, explicit constraints.

It is **not** the production runtime implementation.

## Positioning

AIGMos is specified as:

- **AI Realtime OS**
- **HGI Interface**

At a high level, AIGMos is designed around one strict principle:

> meaningful system behavior must remain explicit.

That means:

- explicit commands
- explicit symbolic state
- explicit trigger/event/runner separation
- explicit ownership boundaries
- explicit adapter boundaries
- no hidden fallbacks
- no silent command injection
- no hidden orchestration magic

## Canonical runtime chain

```text
signals
→ state
→ events
→ execution
→ actions
→ signals
```

This is the core mental model of the system.

## Core primitive families

AIGMos uses six canonical primitive families:

```text
$ = keyed symbolic state
& = ordered list space
# = recursive structured space
! = trigger namespace
@ = event namespace
% = runner namespace
```

Important notes:

- `!` indicates trigger state/pulse only; it does not execute by itself.
- `@` binds trigger observation to explicit dispatch.
- `%` is the runtime execution/runner space.
- loops are modeled through runner semantics and do **not** introduce a seventh primitive family.
- `#cell:property = value` is valid canonical syntax.

## What makes AIGMos distinct

AIGMos is not framed as a generic automation toy or hidden-agent orchestration layer.
The spec is built around deterministic governance and strict surface clarity.

Key differences in the architecture:

- **single governed command surface**
- **parser determinism**
- **state ownership rules**
- **trigger / event / runner separation**
- **adapter boundaries that cannot bypass governance**
- **spec-first canonical model before implementation sprawl**

## Repository structure

```text
README.md
specs/
  __init__.py
  identity.py
  spec_manifest.py
  core_model.py
  parser_and_grammar.py
  commands.py
  assignment_and_state.py
  triggers.py
  events.py
  runners.py
  loops.py
  time_control.py
  q_and_claims.py
  io_and_adapters.py
  errors.py
  summary.py
```

## Module map

### Core

- `identity.py` — canonical identity and scope
- `core_model.py` — high-level runtime model and invariants
- `parser_and_grammar.py` — parser contracts, path grammar, quoting and command shape rules
- `commands.py` — locked command surface
- `assignment_and_state.py` — state rules, ownership, symbolic assignment model

### Runtime

- `triggers.py` — trigger model and pulse semantics
- `events.py` — event binding and dispatch rules
- `runners.py` — runner execution model and status semantics
- `loops.py` — loop behavior expressed through runner semantics
- `time_control.py` — explicit time-based control rules

### Integration

- `q_and_claims.py` — command claims, aliases, Q/Qc, choke-point governance
- `io_and_adapters.py` — adapter boundary, OSC/HTTP contracts, inbound/outbound policy

### Policy

- `errors.py` — canonical error taxonomy and logging boundaries
- `summary.py` — final aggregate summary of the spec set

## Spec status

This repo should be read as:

- **public draft spec**
- **architecture preview**
- **canonical semantics reference**

This repo should **not** be read as:

- finished production runtime
- frozen implementation details
- a promise that all syntax and internal APIs are forever unchanged

The intended purpose is to make the architecture visible early, lock the core ideas publicly, and give implementation work a clean canonical base.

## Reading order

Recommended order:

1. `specs/identity.py`
2. `specs/core_model.py`
3. `specs/parser_and_grammar.py`
4. `specs/commands.py`
5. `specs/assignment_and_state.py`
6. `specs/triggers.py`
7. `specs/events.py`
8. `specs/runners.py`
9. `specs/loops.py`
10. `specs/time_control.py`
11. `specs/q_and_claims.py`
12. `specs/io_and_adapters.py`
13. `specs/errors.py`
14. `specs/summary.py`

## Design commitments

The spec strongly commits to the following:

- deterministic behavior over hidden convenience
- explicitness over magic
- governance over silent bypasses
- symbolic clarity over opaque orchestration
- auditable state/action flow over implicit side effects

## Current publication goal

The goal of this repository is simple:

- make the architecture public
- establish the canonical model early
- make implementation alignment easier
- invite serious technical reading before the runtime is presented as “finished”

## License

License is intentionally not assumed in this README.
Add the repository license explicitly when publishing.

## Notes

This repository contains **Python-style specification files**.
They are written in Python syntax for readability, structure, and maintainability.
That does **not** mean these files are the runtime implementation.
