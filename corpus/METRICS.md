# Tokens per phase — measured from Codex's own session logs

Updated 2026-09-06T03:07:59 UTC. Source: one `token_count` event per API request in ~/.codex/sessions (rows from: codex; 'usage' = the dashboard's usage.jsonl fallback, which under-reports). Tokens = input + output + reasoning; cached is a share of input.

- Turns: **38** (38 productive)
- Total tokens: **21,375,033**
- Phases closed: **5** of 5
- Tokens per closed phase: **2,122,548**
- Median tokens per productive turn: **335,798**
- Cached share of input: **94%**

| phase | turns | productive | tokens | cached | output+reasoning | outcome |
|---|---|---|---|---|---|---|
| repair | 3 | 3 | 1,505,390 | 92% | 48,942 | IN_PROGRESS |
| pilot20 | 3 | 3 | 2,571,101 | 96% | 20,894 | IN_PROGRESS |
| pilot200 | 3 | 3 | 4,331,371 | 96% | 34,066 | IN_PROGRESS |
| aggregate2 | 3 | 3 | 1,063,462 | 93% | 29,786 | IN_PROGRESS |
| report2 | 3 | 3 | 1,141,417 | 90% | 14,044 | IN_PROGRESS |

## Curve — cumulative tokens per closed unit, in closing order

| closed | unit | tokens this unit | cumulative tokens | tokens per closed unit so far |
|---|---|---|---|---|
| 1 | repair | 1,505,390 | 1,505,390 | 1,505,390 |
| 2 | pilot20 | 2,571,101 | 4,076,491 | 2,038,245 |
| 3 | pilot200 | 4,331,371 | 8,407,862 | 2,802,620 |
| 4 | aggregate2 | 1,063,462 | 9,471,324 | 2,367,831 |
| 5 | report2 | 1,141,417 | 10,612,741 | 2,122,548 |

## Per turn

| ts | turn | unit | k | productive | requests | tokens | cached | output+reasoning |
|---|---|---|---|---|---|---|---|---|
| 22:09 | 1 | schema | 1 | yes | 11 | 221,008 | 168,064 | 8,027 |
| 22:16 | 2 | schema | 2 | yes | 12 | 503,685 | 461,824 | 15,080 |
| 22:20 | 3 | schema | 3 | yes | 7 | 422,753 | 401,024 | 8,245 |
| 22:27 | 4 | harness | 1 | yes | 12 | 350,838 | 304,384 | 12,725 |
| 22:33 | 5 | harness | 2 | yes | 7 | 300,119 | 274,560 | 12,469 |
| 22:45 | 1 | pilot | 1 | yes | 20 | 500,787 | 461,568 | 6,713 |
| 22:56 | 0 | pilot | 2 | yes | 22 | 1,107,923 | 1,064,704 | 17,818 |
| 23:19 | 1 | pilot | 3 | yes | 35 | 2,408,902 | 2,289,152 | 35,170 |
| 23:25 | 2 | aggregate | 1 | yes | 12 | 353,980 | 288,512 | 11,500 |
| 23:29 | 3 | aggregate | 2 | yes | 7 | 284,282 | 269,440 | 6,522 |
| 23:35 | 4 | aggregate | 3 | yes | 12 | 602,106 | 574,592 | 13,570 |
| 23:40 | 5 | sampler | 1 | yes | 7 | 239,941 | 184,320 | 9,191 |
| 23:47 | 6 | sampler | 2 | yes | 10 | 581,894 | 546,048 | 15,711 |
| 23:52 | 7 | sampler | 3 | yes | 8 | 221,777 | 184,192 | 8,244 |
| 23:58 | 8 | fidelity | 1 | yes | 7 | 195,907 | 149,248 | 11,238 |
| 00:02 | 9 | fidelity | 2 | yes | 7 | 311,421 | 286,976 | 7,752 |
| 00:06 | 10 | fidelity | 3 | yes | 9 | 513,406 | 492,800 | 7,751 |
| 00:11 | 11 | refresh | 1 | yes | 11 | 263,850 | 224,384 | 8,933 |
| 00:15 | 12 | refresh | 2 | yes | 5 | 192,222 | 173,824 | 8,752 |
| 00:21 | 13 | refresh | 3 | yes | 9 | 429,459 | 407,680 | 10,025 |
| 00:24 | 14 | report | 1 | yes | 9 | 229,609 | 175,360 | 6,594 |
| 00:26 | 15 | report | 2 | yes | 7 | 291,556 | 279,680 | 2,952 |
| 00:28 | 16 | report | 3 | yes | 5 | 234,867 | 227,328 | 2,953 |
| 00:50 | 1 | repair | 1 | yes | 10 | 248,600 | 176,384 | 11,621 |
| 00:57 | 2 | repair | 2 | yes | 13 | 625,579 | 584,960 | 13,736 |
| 01:07 | 3 | repair | 3 | yes | 9 | 631,211 | 573,824 | 23,585 |
| 01:29 | 4 | pilot20 | 1 | yes | 53 | 2,204,790 | 2,113,408 | 15,090 |
| 01:31 | 5 | pilot20 | 2 | yes | 11 | 205,351 | 177,920 | 3,890 |
| 01:33 | 6 | pilot20 | 3 | yes | 6 | 160,960 | 154,112 | 1,914 |
| 02:39 | 7 | pilot200 | 1 | yes | 86 | 3,967,624 | 3,809,792 | 27,263 |
| 02:42 | 8 | pilot200 | 2 | yes | 11 | 235,051 | 201,984 | 4,332 |
| 02:43 | 9 | pilot200 | 3 | yes | 4 | 128,696 | 121,984 | 2,471 |
| 02:52 | 10 | aggregate2 | 1 | yes | 12 | 439,127 | 372,480 | 16,718 |
| 02:57 | 11 | aggregate2 | 2 | yes | 8 | 439,618 | 414,592 | 10,987 |
| 02:59 | 12 | aggregate2 | 3 | yes | 3 | 184,717 | 179,072 | 2,081 |
| 03:03 | 13 | report2 | 1 | yes | 12 | 320,758 | 234,624 | 7,793 |
| 03:06 | 14 | report2 | 2 | yes | 9 | 401,524 | 374,016 | 4,314 |
| 03:07 | 15 | report2 | 3 | yes | 8 | 419,135 | 406,016 | 1,937 |
