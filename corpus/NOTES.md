# NOTES — corpus pipeline, run 2 (extractor repair)

Run 1 notes are in NOTES-run1.md (pilot failed: 6 empty records, $2.28). Read CORPUS2.md for the diagnosis and the repair.

## Last section (rewrite every turn, under 40 lines)
Report2 turn 3/3 COMPLETE — 2026-09-06. CORPUS2 scoped delivery closed.
Read CORPUS2 active/hard lines, phases2 report2 (2 used, IN_PROGRESS), last NOTES.
README final disposition now closes repair, pilots, aggregate2 and report2;
removed interim closing-turn language and separated future work from delivered scope.
Final documentation checks PASS: closure wording, required gate/cost/command details,
full-pass authorization blockers and consumer compatibility limitations retained.
Turn 1 verified links/fences/cost arithmetic, CLI help and pre-API guard rejections.
Turn 2 reconciled saved records, cohort, source joins, aggregate counts and phase ledger.
200 accepted v0.4 records; 144 trip-classified; 56 non-reports; 431 scenes;
167 being entries; 287 adjacencies; 152 flagged reports. Six legacy rows excluded untouched.
1,230/1,231 quotes anchored; one weak retained; every scene has an anchored quote.
Places: 7 canonical, 308 unmapped, 116 unspecified. All links sampling_eligible false.
Dwell/episodes/abruptness/order confidence uncollected. Sparse format 3.1.0 documented.
Pilot20 PASS 16/20 against 14/20; pilot200 accepted 180/180 within $3 cap.
201 v0.4 JSON-schema attempts: 200 accepted, one unbilled provider error, retry successful.
No structural rejection/fallback. Retry $0.027693250 included in measured costs.
Audit unchanged: wrong place 0/10, missed stage 2/10, invented detail 1/10,
classification error 1/10, redaction miss 1/10, temporal/qualification concerns 5/10.
Additional 180 not reading-audited; no rendered/blind fidelity certification.
Pilot20 $0.208577375; pilot200 $1.867267375; combined $2.075844750.
Lifetime $4.358262625; zero reservations; 200 distinct batch IDs, five realtime slots.
Current limits remain $10 cumulative, 400 batch IDs, ten realtime slots, pinned pilots.
Cost/report $0.01037922375; fresh equivalent 14,297-report pass $148.39;
14,097-report remainder $146.32; projected ending ledger after pilot reuse $150.67.
README exact target: extract.py --phase full --ids full-joined-ids.txt
--limit 14297 --budget-usd 180 (absolute interpreter/-B in README); PROPOSED, DO NOT RUN.
Full mode and manifest absent; $180 not approved. Written owner go and reviewed
selection/checkpoint/limit/budget implementation are prerequisites; never bypass guards.
Future scope: broader reading audit, v3 sampler/fidelity migration, renderer integration
and evaluation, guarded authorized full extraction, separately validated refresh ingestion.
No API calls/spend, record/state/code changes, rebuilds, refresh or persistent tests this turn.
Completion marks CORPUS2 delivery only, not full extraction or achieved world fidelity.
<<CORPUS2_DONE>>
