# V0.5 closure-fix results

Final recommendation: **CLOSE_WITH_EXPLICIT_LIMITATIONS**.

The user's request establishes this task's scope. The user explicitly selected the attached implementation brief as the specification and the supplied closure-review archive as the baseline. The review documents are defect evidence; earlier closure verdicts are historical claims, not instructions to close. This is not V0.6.

The implementation repairs contract-requiredness propagation, adds exact unit dependency/update projection and predecessor lineage, replaces the false total order with explicit independent properties, binds strong contexts to complete deterministic security scopes, authenticates them through registered source capabilities, rejects identity conflicts and critical extensions, and converts malformed state structures to DENY. Source-level changes are available in `closure_fix_logs/core_changes.patch`.

## Actual runs

Run from the implementation directory with Python and standard library only. `closure_fix_logs/commands.json` records the exact executable, arguments, environment and exit codes. `PYTHONPATH=src:. python tools/run_closure_fix.py` reproduces all final runs. No preserved test is deleted, skipped, rewritten or marked expected-failure.

| Run | Actual result | Exit | Raw log |
|---|---|---:|---|
| All preserved V0–V0.5 tests | 351 tests; FAILED (failures=2, errors=1) | 1 | closure_fix_logs/baseline.txt |
| Separate preserved V0–V0.4 suite | 311 tests; OK | 0 | closure_fix_logs/legacy_through_v04.txt |
| Preserved closure adversarial tests | 19 tests; FAILED (failures=12, errors=2) | 1 | closure_fix_logs/adversarial.txt |
| New closure-fix controls | 39 tests; OK | 0 | closure_fix_logs/closure_fix.txt |
| Complete discovery | 409 tests; FAILED (failures=15, errors=3) | 1 | closure_fix_logs/full_suite.txt |
| Isolated legacy GC finding | 1 tests; OK | 0 | closure_fix_logs/legacy_gc.txt |
| Required closure-fix mutations plus provider validation mutation | 9/9 detected by security assertions; selected tests pass before mutation | 0 | closure_fix_logs/mutations_fix.txt |
| Preserved mutation definitions on repaired implementation | 89/89 detected | 0 | closure_fix_logs/preserved_mutations.txt and individual mutant logs |

Full discovery is **not green**. Counts of failures include subtests. The listed errors are obsolete test harness assumptions about an available grant, not malformed-input exceptions escaping the verifier.

## Every remaining historical failure

* V0.5 C3/C5 expect strong authorization from unregistered, unscoped adapter assertions. They now receive DENY. C8 then dereferences a nonexistent grant; it also assumes an undeclared individual property may be inferred from an atomic claim. Corrected authenticated positives are Guarantees.test_snapshot/test_atomic/test_additional.
* Closure `CompositeAttacks` uses multi-state units without explicit dependency/update scopes and returns a full aggregate binding without the required predecessor envelope. Authorization rejects that incomplete contract. Its valid and eight attack subtests consequently fail their old ALLOW expectations; its port and removed-unit tests dereference an absent grant. This old test family no longer proves selective handoff security. New Handoffs.test_positive/test_attacks/test_subject/test_port, Receipts controls and ArchitectureControls.test_prior_update_survives_another_handoff exercise the corrected representation at the real boundary. Required-unit-removal remains covered by the unchanged V0.4 suite.
* The old conflict test explicitly expects the core to accept contradictory tokens and leave rejection to the provider. It now receives DENY; Malformed.test_conflict verifies core rejection with no effect.
* The old context replay test demands an initial ALLOW with an already mismatched grant identifier, no authenticated source and no complete scope. Its initial premise is now denied. New Contexts controls start from valid authenticated contexts and separately attack dependency, subject, intent, authorization and execution scope.
* The old provider-omission/lying-validator method still succeeds in its hidden-dependency half, preserving the contract-truth limitation. Its atomic-lie half supplies no trusted scoped context and is denied before the malicious executor. New TrustBoundaries.test_compromised_trusted_enforcement_does_not_manufacture_truth starts with authenticated strong scope, deliberately compromises trusted enforcement, and demonstrates execution can lie while the receipt remains UNVERIFIED.
* The unchanged Mode B GC escape finding fails in combined discovery (extra balance expected 100000, observed 0), while its isolated run and the separate legacy suite succeed. Its process-global object search can select stale fixture instances depending on ordering/GC. This reproduces the archived runtime-sensitive limitation. No isolation repair is claimed and the failure is not hidden.

## Positive controls

| Brief | Actual boundary evidence |
|---|---|
| P1 legacy single state | Preserved legacy provider and single-state conditional execution tests in the passing 311-test V0–V0.4 run |
| P2 A+B authorization/effect | AdditionalControls.test_AB_authorization_execution |
| P3 U1(A+B) → authoritative B2 → U2(B2+C) | Handoffs.test_positive plus Receipts.test_verified_composition: exact dependency checks, both effects and VERIFIED independent evidence |
| P4 authoritative scoped snapshot-only | Guarantees.test_snapshot |
| P5 authoritative atomic-only | Guarantees.test_atomic; fixture reads and conditional predicate/effect boundary use a common lock |
| P6 snapshot+atomic | Guarantees.test_both, with test_both_needs_both selectively rejecting either incomplete claim |
| P7 explicit reusable immutable context | Contexts.test_reusable executes two distinct actions/executions included in the authenticated scope list |

## Negative controls

| Brief | Actual authorization/execution evidence |
|---|---|
| N1 required downgrade | Requirements.test_downgrade, with a provider race that would otherwise skip B |
| N2 stale B1 | Handoffs.test_attacks(stale): U1 remains, U2 has no effect |
| N3 wrong subject | Handoffs.test_subject: uses a substituted subject with a token valid for that subject, isolating core identity protection |
| N4 wrong issuer | Handoffs.test_attacks(issuer) |
| N5 wrong execution/predecessor | Handoffs.test_attacks(execution, predecessor) |
| N6 failed/partial/unknown U1 | Handoffs.test_attacks(failed, partial, unknown) |
| N7 atomic cannot imply snapshot | Guarantees.test_atomic_not_snapshot with an authentic atomic context |
| N8 snapshot cannot imply atomic | Guarantees.test_snapshot_not_atomic with an authentic snapshot context |
| N9 local snapshots cannot be global | Contexts.test_local_not_global: authentic source lacks second-issuer capability |
| N10 bare cross-provider Boolean | Contexts.test_bare_boolean |
| N11 changed subject context replay | Contexts.test_subject |
| N12 changed issuer scope replay | Contexts.test_dependency_scope, even after allowing issuer capability, isolating scope binding |
| N13 changed security intent | Contexts.test_lineage(intent) |
| N14 changed authorization/execution lineage | Contexts.test_lineage(grant, execution) |
| N15 duplicate ID | Malformed.test_duplicate/test_duplicate_subject |
| N16 conflicting subject | Malformed.test_conflict |
| N17 malformed covers | Malformed.test_bad_context, including None, scalar, dict and invalid list |
| N18 unknown critical context extension | Contexts.test_critical; source authenticates it deliberately so the core rule is tested independently |
| N19 missing/forged/incapable/unavailable authority | Contexts.test_authority_failures |
| N20 required dependency unavailable | Malformed.test_bad_dependency(missing issuer/empty value); preserved provider-disappearance control |

Additional controls reject changed representation, false B2 versus authoritative current state, missing B2, stale aggregate reuse, changed C, unit ordering/injection/wrong execution, uncovered required unit dependencies, and malformed guarantee/dependency/extension structures. Receipt evidence disagreement yields VIOLATION. Safe optional narrowing, explicit independent claims, noncritical inert metadata, registered common cross-issuer authority, another handoff and settled-partial replay have positive controls.

## Mutation evidence

The eight requested regression classes are independently detected: offered requiredness weakening; B2 handoff identity validation removal; atomic→snapshot implication; dependency-scope omission; intent/authorization/execution scope omission; bare cross-provider Boolean acceptance; duplicate-ID acceptance; unknown critical extension acceptance. A ninth mutation disables the trusted provider's U2 token check and causes stale/false B2 and changed-C effects. Every selected test passes unmodified, and detection requires a failing security assertion rather than import/structure errors.

All 29 V0.3 and 55 V0.4 mutation definitions execute against passing relevant suites in disposable copies. The five prior closure definitions are also rerun: three are rebased to repaired coverage/guarantee/lineage paths and passing new boundary controls, explicitly recorded in the JSON. Original mutation tools remain byte-identical. A prior partial-result mutation survived the older tests because lookup returned no result; the retained preliminary JSON records that evidence. ResultsTransition.test_partial_is_settled_without_lookup supplies a misleading lookup result after a real partial outcome and catches the regression. No unrelated failing full-suite assertion is counted as a kill.

## Audit and decision limits

New lifecycle objects 0; binding categories 0; generic-core modules 0; provider-specific generic branches 0; transaction coordinator 0; ontology/domain semantics 0. Exact core lines: 3501 → 3718 (+217). StateBinding fields: 7 → 9. All preserved tests, original mutation tools, review logs and historical review findings are byte-identical according to `closure_fix_logs/audit.json`.

The supported composite envelope currently carries individual claims and trusted conditional enforcement. Strong contexts for projected multi-state composite units are explicitly denied before execution. Strong standalone actions require registered authoritative infrastructure; global provider consistency is not manufactured. Honest complete contracts, honest authoritative validators and actual Mode B isolation remain explicit boundaries. The field/schema growth and dictionary-based dual representation are discussed candidly in CLOSURE_FIX_REVIEW.md; stable object count is not treated as sufficient closure evidence.

The ordinary composition counterexample is repaired without a new primitive. No known core security counterexample remains within the tested supported envelope, but the strong-composite/infrastructure/isolation limits justify the qualified recommendation above.
