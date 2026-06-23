# The DMT Atlas — saturation / demand backlog

Source: 3 parallel demand-mines (Tue Jun 23 2026) — community questions (r/DMT, DMT-Nexus, Bluelight, Shroomery, Quora), search demand (autocomplete, People-Also-Ask, YouTube titles, related searches), and a responsible-content/resource spec. All three converged.

## What people actually want (dominant intent)
The DMT-experience audience is overwhelmingly **"what is X / is it real / why does everyone see it / is this normal"** — *explainer and reassurance* intent, **not** how-to. That's the moat: most competing pages overclaim one side of "are they real"; honest, cited, no-verdict wins.

## Ranked backlog
| # | Demand | Signal | Status |
|---|--------|--------|--------|
| 1 | "Are the entities real, or just my brain?" | HIGH (all 3 mines) | ✅ Built — `questions.html` (4-position spectrum, no verdict) |
| 2 | "Why do strangers see the same beings?" | HIGH | ✅ `questions.html` |
| 3 | Searchable entity/realm lookup ("anyone meet THIS being?") | HIGH | ✅ Core Atlas (`index.html`) + `identify.html` encounter matcher |
| 4 | Stage/vocabulary explainers (chrysanthemum, waiting room, breakthrough vs sub-breakthrough, carrier wave, ego death, cosmic joke) | HIGH | ✅ The Journey view + `questions.html` "Is it normal that…?" FAQ |
| 5 | "I'm shaken / changed / questioning reality — is this normal? How do I integrate?" | HIGH | ✅ Built — `grounding.html` (support + verified crisis/integration resources) |
| 6 | DMT vs the Near-Death Experience | HIGH | ✅ `questions.html` (Timmermann 2018 + honest disanalogy) |
| 7 | DMT vs ayahuasca (same molecule, different vehicle) | MED-HIGH | ✅ `questions.html` (mechanism only, risks flagged) |
| 8 | "Does the brain release DMT when you die?" | HIGH | ✅ `questions.html` — labeled UNPROVEN |
| 9 | "Do people meet God on DMT?" | MED | ✅ `questions.html` (Hopkins belief-shift + caveat) |
| 10 | "Felt watched / judged / banned" (guardian motif) | MED | ✅ `questions.html` FAQ + Guardians entry in Atlas |
| 11 | Geometry / "is it a language?" | MED | ◻ Partly in Atlas (geometries); could add a dedicated explainer |
| 12 | 5-MeO-DMT vs N,N-DMT | MED | ◻ Not built — candidate next (distinct molecule; keep scope clear) |
| 13 | Per-entity SEO landing pages (machine elves, mantis, jester…) | MED (long-tail) | ◻ Candidate — crawlable per-entity pages from the same DB would capture the long tail |

## REFUSE list (real, high demand — deliberately NOT built)
Logged for honesty; these are the boundary, not an oversight:
- **Dosing** — "how much DMT to breakthrough," "breakthrough dose mg," "how many vape hits," "threshold dose."
- **Extraction / synthesis** — "how to make/extract DMT," "extraction tek," "DMT at home."
- **Sourcing / use mechanics** — "where to buy," "how to smoke/use a cart/vape."
- **MAOI / substance combinations** — ayahuasca "recipes," combos.
The "bad trip / scary entities" cluster is the gray edge — served ONLY as phenomenology + harm-reduction aftercare on `grounding.html`, never as use instructions.

## Built this pass
- **`questions.html`** — "Questions from Hyperspace": are-they-real spectrum, why-the-same, DMT vs NDE, DMT vs ayahuasca, DMT-at-death (unproven), meet-God, and an "Is it normal that…?" FAQ. Cited, no-verdict.
- **`identify.html`** — "What Did I Meet?" encounter identifier: maps a described encounter → the reported archetypes (with frequencies + sources + deep-link into the Atlas). Phenomenology lookup, not diagnosis.
- **`grounding.html`** — "After the experience": validating, non-medical support; crisis resources above the fold (Fireside Project 623-473-7433, 988, Crisis Text Line, international), integration directories, explicit boundaries.
- 4-page nav + intro links + deep-linking (`index.html#entity:slug`).

## Honesty guardrails honored across everything
Stay ontologically neutral (never assert entities are literally real or fake); label community-lore vs studied findings; cite sources; "DMT at death" flagged unproven; support content includes a clear "seek professional help / crisis" path; zero dosing/sourcing/how-to.

## Next candidates (not yet built)
Per-entity crawlable landing pages (long-tail SEO), 5-MeO vs N,N-DMT explainer, a geometry/"is it a language" page, and (on deploy) GA4 + bot radar + IndexNow/GSC submission.
