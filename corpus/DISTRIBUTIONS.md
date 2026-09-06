# Corpus distributions — v0.4 pilot

## Aggregate2 — final disposition, turn 3/3, 2026-09-06

**COMPLETE.** The v0.4 aggregate contains 200 unique records, 144 trip-classified
reports, 431 scenes, 167 being entries and 287 consecutive-scene adjacencies.
All 1,231 quotes remain retained, including one weak anchor. Six historical
v0.3 rows remain on disk and outside these measurements.

Free-text descriptors use the local vocabulary normaliser; mapping coverage,
counts, denominators and supporting IDs are explicit. Only 7 scenes map to
canonical realms; 308 retain unmapped places and 116 have unspecified places.
Sparse format 3.1.0 preserves observed evidence and defines canonical zero-bin
reconstruction. Turn 2 verified unchanged nonzero measures/provenance and
14,297-report synthetic capacity; the size and fidelity limitations below stand.

Turn 3 rechecked saved totals, selected-ID count, realm reconciliation, baseline
verification flags and ineligible adjacency traversal. No extraction, record
changes or added spend occurred. Old v2 sampler/fidelity consumers still require
migration. Report2 is the next separately assigned phase; it was not started.
**Full extraction remains unauthorized.**

Generated offline by `aggregate.py`; extraction and stored records are unchanged.

## Current evidence

**200 unique v0.4 records; 144 trip-classified; 431 trip scenes.** 6 legacy rows are excluded and retained on disk. 0 older/duplicate v0.4 rows were superseded.

| Measure | n / denominator |
| --- | ---: |
| Trip-classified reports | 144 / 200 reports |
| Non-reports | 56 / 200 reports |
| Scene-bearing trip reports | 144 / 144 trip reports |
| Being entries | 167 across 431 scenes |
| Flagged reports (retained) | 152 / 200 reports |
| Anchored quotes | 1230 / 1231 quotes |
| Weak quotes (retained) | 1 / 1231 quotes |
| Unknown anchor scores | 0 / 1231 quotes |
| Canonical realm-mapped scenes | 7 / 431 scenes |
| Unmapped nonempty places (`other:*`) | 308 / 431 scenes |
| Unspecified places | 116 / 431 scenes |
| Consecutive-scene adjacencies | 287 across 144 trip reports |
| Adjacencies with an outgoing trigger | 269 / 287 adjacencies |
| Nonsequential order labels | 0 / 144 trip reports |

Pilot20 passed its numerical gate **16/20**. Its fixed ten-record audit reported wrong place 0/10, missed scene/stage 2/10, invented detail 1/10, classification error 1/10, redaction miss 1/10, and temporal/qualification concerns 5/10 (overlapping). The additional 180 were not reading-audited. These are descriptive counts on a nonrandom pilot, not population prevalence or fidelity certification. See `PILOT2.md`.

## Run and evidence contract

```sh
/home/clawd/corpus-venv/bin/python -B aggregate.py
```

- Format **3.1.0** uses sparse histograms and is deliberately incompatible with the old v2 sampler/fidelity contract; those consumers are not migrated by this aggregate phase.
- Inputs are `records/*.jsonl`, never examples or rejected outputs. Only structurally accepted v0.4 records enter the selected cohort, highest `_extraction.attempt` per ID. Conflicting ties fail explicitly. Legacy and superseded files are not modified.
- Every measure in `distributions.json` has `n` and unique sorted supporting `report_ids`. `frequency` uses an inline denominator, JSON `denominator_ref`, or enclosing histogram denominator. Empty denominators yield null. Repeated scenes/beings count separately.
- `selected_records` resolves each ID to its file, line, attempt, job and original flags. Joint-profile and adjacency observations point into these unchanged records. Profiles contain normalized co-occurring bundles; their weights are `n`, not independent draws.
- The existing local normaliser's vocabulary maps and synonym rules are applied anew to raw descriptors. Nonempty unmapped words remain `other:<text>`; blank is missing. Repeated labels/aliases count once per observational unit. `values` stores observed bins only; `vocabulary_ref` points to a shared canonical domain. An absent canonical bin has `n: 0`, `report_ids: []`, and frequency 0 for a nonempty denominator or null for an empty denominator. Nonempty `other:*` bins stay explicit. Multi-label frequencies may sum above one.
- Flags and weak anchors never remove or downgrade evidence. Original flags remain available per selected record; prefix rates are diagnostic, not error rates. Neither mapped nor unflagged means reading-verified.
- Realm denominators are scenes in that normalized place, or all trip reports for report prevalence. Being denominators are entries, not individual counts; grouping by form is multi-label and does not infer entity identity. Ordinary companions may be coded as beings. No being coded is not demonstrated absence.
- Scene-count and order measures use trip-classified records. Any non-trip scenes are counted separately and retained in `global.non_trip_scene_profiles`.
- Transitions are **array-neighbor adjacencies**, with the outgoing trigger on the source scene. They are not confirmed same-episode transitions. No reordering occurs. Episode boundaries, dwell, abruptness and order confidence were removed in v0.4; they are explicitly not collected, never zero/imputed. All links have `sampling_eligible: false` because the former qualification cannot be established.

## Scenes per trip report

| Scenes | n / trip reports |
| ---: | ---: |
| 1 | 36 / 144 |
| 2 | 31 / 144 |
| 3 | 31 / 144 |
| 4 | 23 / 144 |
| 5 | 8 / 144 |
| 6 | 7 / 144 |
| 7 | 6 / 144 |
| 11 | 1 / 144 |
| 13 | 1 / 144 |

## Normalization coverage

Each row partitions observational units into mapped-only, unmapped-only, mixed (both), and missing. All cells are n; the final column is the shared denominator n. These are lexical mapping rates, not accuracy rates. Unmapped evidence is retained. JSON supplies each cell's report IDs and frequency.

| Unit / field | Mapped only n | Unmapped only n | Mixed n | Missing n | Denominator n |
| --- | ---: | ---: | ---: | ---: | ---: |
| scene / place | 7 | 308 | 0 | 116 | 431 |
| scene / light | 3 | 104 | 4 | 320 | 431 |
| scene / colour | 28 | 106 | 12 | 285 | 431 |
| scene / motion | 3 | 249 | 25 | 154 | 431 |
| scene / geometry | 4 | 191 | 5 | 231 | 431 |
| scene / material | 2 | 94 | 2 | 333 | 431 |
| scene / density | 1 | 49 | 0 | 381 | 431 |
| scene / scale | 6 | 101 | 1 | 323 | 431 |
| scene / affect | 14 | 300 | 62 | 55 | 431 |
| being entry / form | 2 | 155 | 9 | 1 | 167 |
| being entry / behaviour | 2 | 151 | 1 | 13 | 167 |
| being entry / communication | 0 | 91 | 0 | 76 | 167 |
| being entry / affect | 1 | 49 | 0 | 117 | 167 |

## Descriptor coverage

Top values are scene occurrence counts, not shares of descriptor mentions. Full per-realm values, missing counts and evidence IDs are in JSON.

| Field | Observed n / scenes | Most frequent values (n) |
| --- | ---: | --- |
| light | 111 / 431 | glowing (3); other:darkness (3); other:neon (3); dark (2); other:blackness (2) |
| colour | 146 / 431 | white (9); blue (8); green (8); purple (7); orange (5) |
| motion | 277 / 431 | rotating (10); morphing (7); other:melting (6); other:dancing (5); other:swirling (5) |
| geometry | 200 / 431 | other:fractals (13); other:patterns (13); other:geometric patterns (7); other:fractal (4); other:shapes (4) |
| material | 98 / 431 | other:energy (7); other:grass (5); crystalline (3); other:[redacted]-like (2); other:cartoon (2) |
| density | 50 / 431 | other:overwhelming (3); other:complex (2); other:mass (2); empty (1); other:Sensory overload (1) |
| scale | 108 / 431 | other:infinite (6); vast (5); other:universe (4); other:eternity (3); other:forever (3) |
| affect | 376 / 431 | awe (17); fear (14); other:beautiful (12); other:beauty (11); calm (10) |

## Being mix

| Field | Observed n / being entries | Most frequent values (n) |
| --- | ---: | --- |
| form | 166 / 167 | self-transforming-machine-elves (5); other:a being (3); other:beings (3); other:entities (3); other:enities (2) |
| behaviour | 154 / 167 | other:smiled (3); guiding (2); other:holding hands (2); other:looking at me (2); other:observing me (2) |
| communication | 91 / 167 | other:I heard him say “it's okay, it's ok, you're safe.” (2); other:called "not yet, stay a bit longer" (2); other:difficult to communicate (2); other:"And now you know." (1); other:"Do it" (1) |
| affect | 50 / 167 | other:welcoming (3); other:friendly (2); other:laughing (2); other:warm (2); calm (1) |

## Most frequent adjacency pairs

Top 12; all pairs and supporting source/destination pointers are in JSON. Counts include missing triggers, self-links and unknown places.

| From → to | n / all adjacencies | With trigger n / pair adjacencies |
| --- | ---: | ---: |
| __unknown__ → __unknown__ | 16 / 287 | 14 / 16 |
| other:room with music playing → other:vortex | 2 / 287 | 2 / 2 |
| other:vortex → other:another planet | 2 / 287 | 2 / 2 |
| __unknown__ → hyperspace | 1 / 287 | 1 / 1 |
| __unknown__ → other:a "true" eternal reality / mental hell | 1 / 287 | 1 / 1 |
| __unknown__ → other:a sickly colored room | 1 / 287 | 1 / 1 |
| __unknown__ → other:a wall of lies | 1 / 287 | 0 / 1 |
| __unknown__ → other:a wild carnival | 1 / 287 | 1 / 1 |
| __unknown__ → other:another world / felt like I was in space | 1 / 287 | 1 / 1 |
| __unknown__ → other:apartment (felt like back in February) | 1 / 287 | 1 / 1 |
| __unknown__ → other:at the computer | 1 / 287 | 1 / 1 |
| __unknown__ → other:back in the room | 1 / 287 | 1 / 1 |

## Keyword baseline comparison

Baseline IDs are reconstructed by ID from `reports.jsonl` tags and counts verified against `summary.json`. The 14,309 tagged reports include twelve missing raw joins. Keyword mentions are not experienced scene settings. The first-200 nonrandom pilot also differs from that population; the matched-trip-cohort column separates part of this selection difference. Conservative lexical mapping leaves free-text places unmapped rather than forcing realm identity. These differences cannot establish extraction accuracy. All columns have numerator/denominator IDs in JSON.

| Realm | Keyword n / tagged reports | Keyword n / pilot trip reports | Coded n / pilot trip reports | Scenes n |
| --- | ---: | ---: | ---: | ---: |
| Hyperspace | 2163 / 14309 | 24 / 144 | 5 / 144 | 5 |
| The Waiting Room | 815 / 14309 | 2 / 144 | 1 / 144 | 1 |
| The Domed Cathedral | 395 / 14309 | 11 / 144 | 0 / 144 | 0 |
| The Throne Room | 4 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Void | 697 / 14309 | 10 / 144 | 0 / 144 | 0 |
| The Workshop / Factory / Market | 76 / 14309 | 1 / 144 | 0 / 144 | 0 |
| Geometric Palaces &amp; the Lattice | 66 / 14309 | 1 / 144 | 0 / 144 | 0 |
| The Circus / Playroom | 29 / 14309 | 1 / 144 | 0 / 144 | 0 |
| Tunnels &amp; Corridors | 1204 / 14309 | 11 / 144 | 0 / 144 | 0 |
| The Membrane / Veil | 1750 / 14309 | 24 / 144 | 0 / 144 | 0 |
| The In-Between | 5 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Deeper Realms | 34 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Hospital / Operating Theater | 80 / 14309 | 2 / 144 | 0 / 144 | 0 |
| The Testing Laboratory | 446 / 14309 | 6 / 144 | 0 / 144 | 0 |
| The Control Room / Cockpit | 36 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Hive | 3 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Nursery / Incubation Chamber | 63 / 14309 | 1 / 144 | 0 / 144 | 0 |
| The Library / Hall of Records | 7 / 14309 | 1 / 144 | 1 / 144 | 1 |
| The Garden | 27 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The City of Lights / Alien Metropolis | 255 / 14309 | 4 / 144 | 0 / 144 | 0 |
| The Court / Council Chamber | 1 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Mesoamerican Temple Complex | 1 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Egyptian Hall | 272 / 14309 | 5 / 144 | 0 / 144 | 0 |
| The Theater / Grand Stage | 3 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Grid Plain | 75 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Ocean / Underwater Realm | 333 / 14309 | 5 / 144 | 0 / 144 | 0 |
| The Space Station / Docking Bay | 2 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The White Room | 14 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Bardo Crossing / Hall of Judgment | 291 / 14309 | 6 / 144 | 0 / 144 | 0 |
| The Carnival Midway / Fairground Machinery | 4 / 14309 | 0 / 144 | 0 / 144 | 0 |
| The Uncanny Interior | 78 / 14309 | 3 / 144 | 0 / 144 | 0 |

## Noncanonical places

Exact normalized labels are retained; descriptive phrases are not semantically merged.

| Place | Scenes n / all scenes | Reports n / trip reports |
| --- | ---: | ---: |
| __unknown__ | 116 / 431 | 86 / 144 |
| other:"dimensional classroom" | 1 / 431 | 1 / 144 |
| other:5th or 6th dimension space of brown cubes | 1 / 431 | 1 / 144 |
| other:Chinese palace with cherry blossom trees (closed-eye vision) | 1 / 431 | 1 / 144 |
| other:Mexico, historical vision | 1 / 431 | 1 / 144 |
| other:a "true" eternal reality / mental hell | 1 / 431 | 1 / 144 |
| other:a beautiful green field | 1 / 431 | 1 / 144 |
| other:a completely different world | 1 / 431 | 1 / 144 |
| other:a different world / hyperspace | 1 / 431 | 1 / 144 |
| other:a garden | 1 / 431 | 1 / 144 |
| other:a park at night | 1 / 431 | 1 / 144 |
| other:a room of elves | 1 / 431 | 1 / 144 |
| other:a room with other people | 1 / 431 | 1 / 144 |
| other:a sickly colored room | 1 / 431 | 1 / 144 |
| other:a soft pink room | 1 / 431 | 1 / 144 |
| other:a spherical room with a single large dimple | 1 / 431 | 1 / 144 |
| other:a supermarket / shopping centre | 1 / 431 | 1 / 144 |
| other:a therapists' office, lying in a chair | 1 / 431 | 1 / 144 |
| other:a type of white room | 1 / 431 | 1 / 144 |
| other:a vast open space | 1 / 431 | 1 / 144 |
| other:a wall of lies | 1 / 431 | 1 / 144 |
| other:a wild carnival | 1 / 431 | 1 / 144 |
| other:above earth, out of solar system, reaches of the multiverse | 1 / 431 | 1 / 144 |
| other:above his own body in his room | 1 / 431 | 1 / 144 |
| other:all of existence | 1 / 431 | 1 / 144 |
| other:alone, a week later | 1 / 431 | 1 / 144 |
| other:an Egyptian tomb | 1 / 431 | 1 / 144 |
| other:an empty place | 1 / 431 | 1 / 144 |
| other:another planet | 2 / 431 | 2 / 144 |
| other:another reality | 1 / 431 | 1 / 144 |
| other:another room with a table | 1 / 431 | 1 / 144 |
| other:another world / felt like I was in space | 1 / 431 | 1 / 144 |
| other:apartment (felt like back in February) | 1 / 431 | 1 / 144 |
| other:apartment, brown carpet | 1 / 431 | 1 / 144 |
| other:at home | 1 / 431 | 1 / 144 |
| other:at my computer / walking around room | 1 / 431 | 1 / 144 |
| other:at the computer | 1 / 431 | 1 / 144 |
| other:back at the river | 1 / 431 | 1 / 144 |
| other:back in body | 1 / 431 | 1 / 144 |
| other:back in my room | 1 / 431 | 1 / 144 |
| other:back in reality | 1 / 431 | 1 / 144 |
| other:back in reality, seeing own body | 1 / 431 | 1 / 144 |
| other:back in recognized surroundings | 1 / 431 | 1 / 144 |
| other:back in the room | 2 / 431 | 2 / 144 |
| other:back in the room with the fan | 1 / 431 | 1 / 144 |
| other:back on earth, bedroom | 1 / 431 | 1 / 144 |
| other:back on the couch | 1 / 431 | 1 / 144 |
| other:back outdoors, coming down | 1 / 431 | 1 / 144 |
| other:back to reality by the river | 1 / 431 | 1 / 144 |
| other:back with friend | 1 / 431 | 1 / 144 |
| other:back with the family | 1 / 431 | 1 / 144 |
| other:basement couch, then looking out the window | 1 / 431 | 1 / 144 |
| other:bathroom | 1 / 431 | 1 / 144 |
| other:bathroom mirror | 1 / 431 | 1 / 144 |
| other:bed | 1 / 431 | 1 / 144 |
| other:bedroom | 2 / 431 | 2 / 144 |
| other:bedroom filled with spirit objects | 1 / 431 | 1 / 144 |
| other:bedroom melting into colour | 1 / 431 | 1 / 144 |
| other:bedroom near speakers | 1 / 431 | 1 / 144 |
| other:bedroom walls | 1 / 431 | 1 / 144 |
| other:bedroom, eyes open | 1 / 431 | 1 / 144 |
| other:bedroom, lying in bed | 1 / 431 | 1 / 144 |
| other:bedroom, lying on bed | 1 / 431 | 1 / 144 |
| other:bedroom, sitting on bed | 1 / 431 | 1 / 144 |
| other:behind closed eyelids, a new world | 1 / 431 | 1 / 144 |
| other:being born back into the room | 1 / 431 | 1 / 144 |
| other:below a tree in a grove, outdoors | 1 / 431 | 1 / 144 |
| other:beyond the lake | 1 / 431 | 1 / 144 |
| other:beyond the membrane / behind eyelids | 1 / 431 | 1 / 144 |
| other:black space with fractals | 1 / 431 | 1 / 144 |
| other:black void / death darkness | 1 / 431 | 1 / 144 |
| other:brightly lit living room | 1 / 431 | 1 / 144 |
| other:brother's room, sunny day | 1 / 431 | 1 / 144 |
| other:by a river at dusk (observing friend) | 1 / 431 | 1 / 144 |
| other:candyland | 1 / 431 | 1 / 144 |
| other:chair in a room | 1 / 431 | 1 / 144 |
| other:chair in the room | 1 / 431 | 1 / 144 |
| other:clearing of brown and blue | 1 / 431 | 1 / 144 |
| other:climbing out of a canyon in the dark | 1 / 431 | 1 / 144 |
| other:closed-eye field of view after coming down | 1 / 431 | 1 / 144 |
| other:closed-eye visions on bed | 1 / 431 | 1 / 144 |
| other:closed-eye visual field at the computer | 1 / 431 | 1 / 144 |
| other:closed-eye visuals | 1 / 431 | 1 / 144 |
| other:comedown, with cat on lap | 1 / 431 | 1 / 144 |
| other:comfy bed and cool room with friend in a chair | 1 / 431 | 1 / 144 |
| other:complete dark | 1 / 431 | 1 / 144 |
| other:couch at my house | 1 / 431 | 1 / 144 |
| other:couch, eyes closed | 2 / 431 | 2 / 144 |
| other:couch, losing vision | 1 / 431 | 1 / 144 |
| other:cubed universe | 1 / 431 | 1 / 144 |
| other:cubic room of cris-crossed triangle pattern | 1 / 431 | 1 / 144 |
| other:cubic shaped room, green like | 1 / 431 | 1 / 144 |
| other:cycle of the universe | 1 / 431 | 1 / 144 |
| other:dark bedroom | 1 / 431 | 1 / 144 |
| other:dark bedroom with candle, chair by window | 1 / 431 | 1 / 144 |
| other:dark bedroom, curtains pulled | 1 / 431 | 1 / 144 |
| other:dark room, only light from a router | 1 / 431 | 1 / 144 |
| other:dark space with pink blob | 1 / 431 | 1 / 144 |
| other:darkness with a fractal wall | 1 / 431 | 1 / 144 |
| other:debris in another world | 1 / 431 | 1 / 144 |
| other:dimly lit back room, sitting on bed | 1 / 431 | 1 / 144 |
| other:dimly lit room, reclined on futon | 1 / 431 | 1 / 144 |
| other:dream | 1 / 431 | 1 / 144 |
| other:dream, sitting down | 1 / 431 | 1 / 144 |
| other:dreamland | 1 / 431 | 1 / 144 |
| other:dreams in bed, "the matrix" | 1 / 431 | 1 / 144 |
| other:endless rooms and hallways | 1 / 431 | 1 / 144 |
| other:entity filling entire vision | 1 / 431 | 1 / 144 |
| other:everyday life, months after | 1 / 431 | 1 / 144 |
| other:eyes closed | 1 / 431 | 1 / 144 |
| other:eyes closed on bed | 1 / 431 | 1 / 144 |
| other:eyes closed on the blanket | 1 / 431 | 1 / 144 |
| other:eyes closed, falling/flying into everything | 1 / 431 | 1 / 144 |
| other:eyes closed, later attempt | 1 / 431 | 1 / 144 |
| other:eyes open | 1 / 431 | 1 / 144 |
| other:eyes open, in room | 1 / 431 | 1 / 144 |
| other:eyes-closed aztec temple | 1 / 431 | 1 / 144 |
| other:eyes-closed visual field | 1 / 431 | 1 / 144 |
| other:eyes-closed visual field (previous low-[redacted] trips) | 1 / 431 | 1 / 144 |
| other:eyes-closed visual space | 1 / 431 | 1 / 144 |
| other:facing the blinded window | 1 / 431 | 1 / 144 |
| other:floor of some surface, in darkness | 1 / 431 | 1 / 144 |
| other:flying above the planet | 1 / 431 | 1 / 144 |
| other:forest by my house | 1 / 431 | 1 / 144 |
| other:fractal city with skyscrapers and gates | 1 / 431 | 1 / 144 |
| other:friend's apartment, lying under a ceiling fan | 1 / 431 | 1 / 144 |
| other:friend's basement | 1 / 431 | 1 / 144 |
| other:friend's bedroom, red blinking Christmas lights | 1 / 431 | 1 / 144 |
| other:friend's house | 1 / 431 | 1 / 144 |
| other:friend's living room | 1 / 431 | 1 / 144 |
| other:friend's place, before onset | 1 / 431 | 1 / 144 |
| other:friend's room | 2 / 431 | 1 / 144 |
| other:friend's room with laser light show and blacklight | 1 / 431 | 1 / 144 |
| other:friend's room, cartoon-like | 1 / 431 | 1 / 144 |
| other:friend's trip (observed and described) | 1 / 431 | 1 / 144 |
| other:grassy field by a calm lake | 1 / 431 | 1 / 144 |
| other:higher dimension / hyperspace | 1 / 431 | 1 / 144 |
| other:his apartment | 1 / 431 | 1 / 144 |
| other:his bed / room | 1 / 431 | 1 / 144 |
| other:his bedroom, facing Bob Marley poster | 1 / 431 | 1 / 144 |
| other:his car / ordinary world | 1 / 431 | 1 / 144 |
| other:his room | 2 / 431 | 1 / 144 |
| other:his room again | 1 / 431 | 1 / 144 |
| other:his room at desk | 1 / 431 | 1 / 144 |
| other:his room, body vibrating | 1 / 431 | 1 / 144 |
| other:his room, coming down | 2 / 431 | 2 / 144 |
| other:his room, eyes open with light on | 1 / 431 | 1 / 144 |
| other:his session, last night | 1 / 431 | 1 / 144 |
| other:huge round room of energy | 1 / 431 | 1 / 144 |
| other:hyper ultra colourful fractal landscape | 1 / 431 | 1 / 144 |
| other:hyperspace vortex | 1 / 431 | 1 / 144 |
| other:hyperspace, electric cubes | 1 / 431 | 1 / 144 |
| other:identity merged with the rower | 1 / 431 | 1 / 144 |
| other:in front of the mirror | 1 / 431 | 1 / 144 |
| other:in space without a body | 1 / 431 | 1 / 144 |
| other:inside a bright yellow sphere | 1 / 431 | 1 / 144 |
| other:inside my head | 1 / 431 | 1 / 144 |
| other:intergalactic mall | 1 / 431 | 1 / 144 |
| other:judgement room, dark reality that's not quite reality | 1 / 431 | 1 / 144 |
| other:jungle planet with golden structures | 1 / 431 | 1 / 144 |
| other:kitchen | 2 / 431 | 2 / 144 |
| other:kitchen floor | 1 / 431 | 1 / 144 |
| other:laying on couch facing a long hallway | 1 / 431 | 1 / 144 |
| other:laying on the floor listening to music | 1 / 431 | 1 / 144 |
| other:leaning back against a wall | 1 / 431 | 1 / 144 |
| other:living room couch | 1 / 431 | 1 / 144 |
| other:living room of the house | 1 / 431 | 1 / 144 |
| other:living room with TV, looking at ceiling | 1 / 431 | 1 / 144 |
| other:long hallway with a door | 1 / 431 | 1 / 144 |
| other:looking out the window at the moon | 1 / 431 | 1 / 144 |
| other:looking out window | 1 / 431 | 1 / 144 |
| other:looking through two semicircle windows | 1 / 431 | 1 / 144 |
| other:low lit basement room with candles | 1 / 431 | 1 / 144 |
| other:lying back in bed | 1 / 431 | 1 / 144 |
| other:lying down after taking hit | 1 / 431 | 1 / 144 |
| other:lying down, cosmic space | 1 / 431 | 1 / 144 |
| other:lying down, eyes closed | 1 / 431 | 1 / 144 |
| other:lying on bed reading | 1 / 431 | 1 / 144 |
| other:lying on makeshift bed / flying through space | 1 / 431 | 1 / 144 |
| other:lying underneath a tree, sunny with green grass | 1 / 431 | 1 / 144 |
| other:medical feeling, like a hospital bed or lab | 1 / 431 | 1 / 144 |
| other:middle of a street surrounded by houses | 1 / 431 | 1 / 144 |
| other:middle of my bed, with a sitter | 1 / 431 | 1 / 144 |
| other:my bathroom, only bathroom light on | 1 / 431 | 1 / 144 |
| other:my bedroom reassembling | 1 / 431 | 1 / 144 |
| other:my bedroom with a small light on | 1 / 431 | 1 / 144 |
| other:my bedroom, sunny day, window open with birdsong | 1 / 431 | 1 / 144 |
| other:my faintly lit bedroom | 1 / 431 | 1 / 144 |
| other:my garden (in the dream) | 1 / 431 | 1 / 144 |
| other:my room | 6 / 431 | 5 / 144 |
| other:my room / bed | 1 / 431 | 1 / 144 |
| other:my room / outside apartment | 1 / 431 | 1 / 144 |
| other:my room returning | 1 / 431 | 1 / 144 |
| other:my room with adventure time poster | 1 / 431 | 1 / 144 |
| other:my room, alone | 1 / 431 | 1 / 144 |
| other:my room, eyes open | 2 / 431 | 2 / 144 |
| other:my room, overlaid with patterns | 1 / 431 | 1 / 144 |
| other:no self, all things | 1 / 431 | 1 / 144 |
| other:odd bubble with shifting walls, like a hospital emergency room | 1 / 431 | 1 / 144 |
| other:on bed | 1 / 431 | 1 / 144 |
| other:on his bed, eyes closed, with SO present | 1 / 431 | 1 / 144 |
| other:on my bed | 1 / 431 | 1 / 144 |
| other:on the floor / rug in the room | 1 / 431 | 1 / 144 |
| other:original surroundings transformed | 1 / 431 | 1 / 144 |
| other:outdoors with two companions, looking at the moon | 1 / 431 | 1 / 144 |
| other:outdoors, heavy mushroom trip surroundings | 1 / 431 | 1 / 144 |
| other:outside a temple surrounded by yellow desert | 1 / 431 | 1 / 144 |
| other:outside on a blanket under some trees | 1 / 431 | 1 / 144 |
| other:own room looking at a poster | 1 / 431 | 1 / 144 |
| other:own solitary bedroom | 1 / 431 | 1 / 144 |
| other:part of space | 1 / 431 | 1 / 144 |
| other:passenger seat of a parked car in a hockey rink parking lot | 1 / 431 | 1 / 144 |
| other:pink bubblegum room | 1 / 431 | 1 / 144 |
| other:pit of chaos / deepest subconscious mind | 1 / 431 | 1 / 144 |
| other:place of perfect geometry | 1 / 431 | 1 / 144 |
| other:planet re-entered | 1 / 431 | 1 / 144 |
| other:planet surface with hills and pyramids | 1 / 431 | 1 / 144 |
| other:planet with hills and pyramids | 1 / 431 | 1 / 144 |
| other:psychonaut bedroom | 1 / 431 | 1 / 144 |
| other:realm of darkness | 1 / 431 | 1 / 144 |
| other:riverside, eyes open | 1 / 431 | 1 / 144 |
| other:room | 1 / 431 | 1 / 144 |
| other:room after opening eyes | 1 / 431 | 1 / 144 |
| other:room of energy again | 1 / 431 | 1 / 144 |
| other:room reassembling | 1 / 431 | 1 / 144 |
| other:room walls becoming space / interstellar dogfight | 1 / 431 | 1 / 144 |
| other:room with a TV show on | 1 / 431 | 1 / 144 |
| other:room with eyes open, looking at hands | 1 / 431 | 1 / 144 |
| other:room with music playing | 2 / 431 | 2 / 144 |
| other:room with plain white walls and an Alex Grey painting | 1 / 431 | 1 / 144 |
| other:room with sitter | 1 / 431 | 1 / 144 |
| other:room, eyes open, seeing friend | 1 / 431 | 1 / 144 |
| other:room, looking at carpet and oven | 1 / 431 | 1 / 144 |
| other:room, looking at ceiling | 1 / 431 | 1 / 144 |
| other:room, looking at his hands | 1 / 431 | 1 / 144 |
| other:rooms with faces on cubes | 1 / 431 | 1 / 144 |
| other:same chair, new video playing (Africa footage) | 1 / 431 | 1 / 144 |
| other:same room, inside the writer's head | 1 / 431 | 1 / 144 |
| other:seated on bed in dim candle-lit room with fan | 1 / 431 | 1 / 144 |
| other:second trip | 1 / 431 | 1 / 144 |
| other:shower at home | 1 / 431 | 1 / 144 |
| other:sitting down attempting to meditate, closed eyes | 1 / 431 | 1 / 144 |
| other:sitting on floor of his room, eyes closed | 1 / 431 | 1 / 144 |
| other:sitting outdoors/room with friends | 1 / 431 | 1 / 144 |
| other:sky / infinite toroidal energy field | 1 / 431 | 1 / 144 |
| other:small cedar wood closet, completely dark | 1 / 431 | 1 / 144 |
| other:some type of valley | 1 / 431 | 1 / 144 |
| other:space behind the "false bottom" of the bookshelf | 1 / 431 | 1 / 144 |
| other:space-like visual space, no body awareness | 1 / 431 | 1 / 144 |
| other:spot by the river just before sunset | 1 / 431 | 1 / 144 |
| other:standing on the rim of a cornea, looking through | 1 / 431 | 1 / 144 |
| other:strange yet familiar world | 1 / 431 | 1 / 144 |
| other:surrounded by family, music playing | 1 / 431 | 1 / 144 |
| other:suspended in "computer code?" | 1 / 431 | 1 / 144 |
| other:that realm | 1 / 431 | 1 / 144 |
| other:the "pre-chamber" | 1 / 431 | 1 / 144 |
| other:the cosmos / hyperspace | 1 / 431 | 1 / 144 |
| other:the land of everything | 1 / 431 | 1 / 144 |
| other:the room | 2 / 431 | 2 / 144 |
| other:the room around me | 1 / 431 | 1 / 144 |
| other:the room with TV, curtains, sitter friend, cat | 1 / 431 | 1 / 144 |
| other:the room, coming out | 1 / 431 | 1 / 144 |
| other:the room, eyes open | 1 / 431 | 1 / 144 |
| other:the room, looking at a picture on the wall | 1 / 431 | 1 / 144 |
| other:the second dimension | 1 / 431 | 1 / 144 |
| other:the void / imploding universe | 1 / 431 | 1 / 144 |
| other:the world seen from outside; digging holes through it | 1 / 431 | 1 / 144 |
| other:third person view | 1 / 431 | 1 / 144 |
| other:this white space I was now in | 1 / 431 | 1 / 144 |
| other:tunnel of fractals | 1 / 431 | 1 / 144 |
| other:tunnel of life | 1 / 431 | 1 / 144 |
| other:two-week ayahuasca retreat in Peru | 1 / 431 | 1 / 144 |
| other:under a vast dome | 1 / 431 | 1 / 144 |
| other:universe / being birthed | 1 / 431 | 1 / 144 |
| other:universe of fractal cities | 1 / 431 | 1 / 144 |
| other:unknown, not the kitchen | 1 / 431 | 1 / 144 |
| other:vast black infinitness | 1 / 431 | 1 / 144 |
| other:vast white kitchen like room | 1 / 431 | 1 / 144 |
| other:vent airway shaped like space | 1 / 431 | 1 / 144 |
| other:vent shaped space | 1 / 431 | 1 / 144 |
| other:view of whole universe as an egg on a rowboat | 1 / 431 | 1 / 144 |
| other:vision of two ribbons | 1 / 431 | 1 / 144 |
| other:visions mixed with childhood memories | 1 / 431 | 1 / 144 |
| other:vortex | 2 / 431 | 2 / 144 |
| other:vortex/planet again | 1 / 431 | 1 / 144 |
| other:waking at home the next morning | 1 / 431 | 1 / 144 |
| other:white background | 1 / 431 | 1 / 144 |
| other:with a group of friends | 1 / 431 | 1 / 144 |
| other:with friend, early morning | 1 / 431 | 1 / 144 |
| other:with music | 1 / 431 | 1 / 144 |
| other:woods along the river bank | 1 / 431 | 1 / 144 |
| other:woods, resting against a hill | 1 / 431 | 1 / 144 |

## Offline capacity check — 2026-09-06

Turn 2 verified that sparse storage preserves every prior nonzero measure, denominator, profile and provenance pointer. The 103,852 canonical zero bins are reconstructible from shared domains; 13 coverage rows partition their observational units exactly. Pilot JSON decreased from 8,697,818 to 2,943,046 bytes.

A separate in-memory synthetic check aggregated 14,297 distinct report IDs with one scene, one unique noncanonical place and one unique profile each. Report, scene, realm and profile totals passed; aggregation took 2.999 seconds on this machine. Compact serialization was 61,655,498 bytes, excluding the file/line registry (synthetic inputs had no files). Process peak RSS was 381,368 KiB, including prior verification work. No synthetic record or distribution was written to disk or mixed with pilot evidence.

This checks report-count capacity and high place diversity, not full-extraction fidelity or a size bound. Multiple scenes, beings, longer labels and richer profiles can increase size and memory. No full extraction was run or authorized.
