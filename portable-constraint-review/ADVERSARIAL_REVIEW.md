# Portable Constraint Evaluator — adversarial review

Verdict: **H1_FAILS_STOP**

Review date: 2026-10-13. Input: portable_constraint_evaluator_poc.zip.

## Scope and method

The user's request authorized reading ADVERSARIAL_BRIEF.md, running the full suite, and performing its review. The attached RESULTS.md was treated as a claim to investigate, not as evidence that its conclusion was correct. Both verifiers, the loader and package validator, all five JSON modules, and all supplied tests were inspected. No interpreter, module, opcode, schema, or architecture was repaired.

Baseline command: `python3 run_tests.py`. Result: **14 tests, OK**, before and after the adversarial probes. Several baseline tests intentionally pass when weaknesses exist.

Run the accompanying reproductions from the extracted project directory:

```sh
python3 adversarial_reproduce.py
```

Only Python's standard library is required. The script prints observed outcomes for A and B; findings are not regression assertions. It includes an independent exhaustive matching oracle.

## Exact counterexamples

| Attack | Minimal input or construction | A / B outcome | Implication |
|---|---|---|---|
| Overlapping groups | requirements `[A or B:1, A:1]`; line items `[A:1, B:1]` | false / false | Feasible assignment B to first, A to second is rejected. |
| Requirement ordering | Reverse those requirement groups | true / true | Equivalent requirement order changes authorization. |
| Duplicate SKUs | requirement A:1; items `[A:1,A:0]` versus `[A:0,A:1]` | false / false versus true / true | Last-write-wins dictionary construction loses quantity; item ordering matters. |
| Fractional quantity | requirement A:1.9; item A:1 | true / true | `int` silently truncates. No integer-quantity validation. |
| Overflow | requirement quantity `float('inf')` | OverflowError / OverflowError | Runtime does not return a closed denial. Infinity is also accepted by Python JSON parsing/serialization. |
| Malformed opcode | Re-digested package with `program={"lte":[]}` | IndexError / IndexError | Operand arity is not checked; exception escapes Runtime.decide. |
| Recursion | Re-digested package with 1,500 nested `and` nodes | RecursionError / RecursionError | No enforced depth/fuel quota; exception escapes. |
| Negative duration | max_minutes=1, start_minute=100, end_minute=0 | true / true | Missing duration validity rule. |
| String arithmetic | budget="9", amount="0", spent_this_month="100" | true / true | Concatenation and lexicographic comparison replace numeric arithmetic. |
| Forged aggregate | budget=100, amount=1000, spent_this_month=-1000 | true / true | Caller facts widen spending authority. |
| Membership coercion | room_membership={"r":1}, room_id="r" | true / true | Python equality treats integer 1 as boolean true. |
| Null identity | owner_team_by_file={"f":null}, requester_team=null, file_id="f" | true / true | Explicit missing identities compare equal and permit access. |
| Fact absence/forgery | room r with empty facts versus membership r=true | false / false versus true / true | Presence is checked; provenance, requester binding, freshness and authority are not. |
| Extra facts | Valid calendar action plus unrelated nonempty facts | false / false | No-fact modules reject all nonempty facts. This narrows authority, rather than widening it. |
| Package substitution | Change id to other, version to unsupported string, schema to null, program to const true, then recompute digest | true / true | ID, version, schema and trusted code identity are not enforced. Digest is an unkeyed checksum, not a signature. |
| Loader traversal | Existing modules directory; valid sibling outside.json; request `../outside` | true / true | Module IDs can escape the configured package directory. |
| Python type divergence | Calendar action supplied as subclass of dict | true / false | A uses isinstance; B requires exact dict. This case is outside plain JSON objects. |
| Unicode | file_id composed é; ownership key decomposed e + combining accent | false / false | Exact code-point matching; no normalization profile. This is not itself proof normalization is required. |

The independent matching oracle checked **1,080 cases** (one to four unit requirements over A, B, or A/B, with stock capacities zero to two) and found **32 mismatches**. A and B agree on these wrong answers.

The numerical/malformed differential corpus exercised **450 cases** across calendar and payment: null, booleans, negatives, integers, fractions, a 101-digit integer, Infinity, NaN, strings, Unicode, lists and dictionaries. It found **zero A/B divergences and zero uncaught exceptions in that corpus**. This bounded result does not prove cross-language portability; the targeted checkout, malformed-program, and depth probes above do raise uncaught exceptions.

## Canonicalization, capabilities, and resource limits

`canonical(-0.0)` is `b'-0.0'`, while `canonical(0.0)` is `b'0.0'`; `canonical(float('nan'))` is `b'NaN'`. Object keys are sorted and strings are encoded as UTF-8 without Unicode normalization. This is deterministic for ordinary supported Python inputs, but lacks a specified cross-language number and Unicode profile. Python JSON loading silently resolves duplicate object keys before hashing; duplicate checkout SKUs are separately demonstrated above. Repetition tests only establish repeatability on the same Python implementation.

An unknown opcode in an unvisited branch is not statically rejected: `and [const false, unknown true]` returns false without reaching the invalid node. Package validation does not validate the full program. Facts are host objects, not verified capabilities with authority or freshness bindings. Payment evaluates a supplied aggregate; it does not implement atomic state reservation, so a stateful budget guarantee is not demonstrated.

Checkout creates a stock dictionary proportional to input line count and sorts choices for every requirement. Work grows roughly with line count plus the sum of choice-list sorting costs. There is no input-size, integer-size, memory, execution-fuel, or depth limit. Probes with 1,000, 10,000, and 100,000 repeated lines all completed and returned true, with roughly 0.0003, 0.0014, and 0.0113 seconds for both verifiers together in this environment. These are modest local observations, not a claim of production denial-of-service resistance. The recursion probe demonstrates an actual uncontrolled failure.

## Architectural falsification

The calendar package composes subtraction and comparison; matrix membership combines a fact lookup with equality; payment combines aggregate facts and arithmetic; document ownership compares looked-up owner and requester. Their shapes and validity assumptions remain host/module contracts, not validated schemas.

Checkout is stronger evidence: both runtimes implement the `maxflow_match` opcode and its domain shapes `{acceptable_skus, qty}` and `{sku, qty}`. The implementation is greedy matching, not max flow. Avoiding provider-name branches does not eliminate domain coupling. Two independently written implementations sharing Python operators, the same package loader, and the same semantic algorithm establish only bounded agreement.

Correcting the greedy matcher would repair a particular correctness defect but leave checkout semantics in both runtimes. Moving arbitrary evaluator algorithms into module code instead requires an execution language/runtime, confinement for untrusted code, deterministic execution and a capability ABI, resource limits, package identity/trust, and trusted fact integration. The specific technology need not be a custom VM, but those execution and trust functions remain necessary. The POC does not demonstrate H1's promise of arbitrary semantics without that shared layer.

AP2-style typed custom constraints with explicit evaluator support expose this integration boundary more honestly: unknown semantics require supported evaluators instead of implying universal evaluation. This is a boundary comparison, not a verification of any current AP2 specification or deployed implementation; none was supplied or independently examined in this review.

## Decision

**H1_FAILS_STOP.** The five fixture pairs survive as bounded examples. Strong H1 does not: domain semantics have moved into a shared interpreter, and even the hard shared opcode is incorrect for overlapping groups. Package/fact weaknesses reinforce the missing trust boundary but are not the sole basis for the architectural verdict. No new opcode, ontology, VM, sandbox, protocol object, or provider branch was added to make H1 pass.
