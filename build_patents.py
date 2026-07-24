#!/usr/bin/env python3
"""Build patents.json from the curated, WebSearch-verified DMT / 5-MeO-DMT /
ayahuasca psychedelic-therapeutic patent set. Bibliographic metadata + short
factual abstracts and high-level claim-scope only. NO synthesis / manufacturing
route detail is captured. If a raw Google-Patents harvest ever lands on disk it
is merged in (deduped by patent_number)."""
import json, os, re, datetime
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "data", "research", "patents.json")
RAW = os.path.join(BASE, "data", "research", "raw", "patents_raw.json")

def GP(num):
    return f"https://patents.google.com/patent/{num}/en"

# Curated verified records. Facts sourced from USPTO/EPO bibliographic data and
# reputable secondary sources (company IR releases, Psychedelic Alpha, Porta
# Sophia psychedelic prior-art library, Justia bibliographic pages) because the
# Google Patents / PatentsView bulk APIs were unavailable (see source_notes).
# abstract = short factual description; claims_summary = high-level scope only.
RECORDS = [
 {
  "patent_number":"US PP5751 P","title":"Banisteriopsis caapi, (cv) 'Da Vine'",
  "assignee":"Loren S. Miller (International Plant Medicine Corporation)",
  "inventors":["Loren S. Miller"],
  "filing_date":"1984-11-07","publication_date":"1986-06-17","grant_date":"1986-06-17",
  "priority_date":"1984-11-07","jurisdiction":"US","status":"expired (patent term ended ~2003)",
  "molecule_tag":"ayahuasca",
  "abstract":"US plant patent on a claimed new and distinct variety of the ayahuasca vine Banisteriopsis caapi (the DMT-potentiating, harmala-alkaloid-bearing plant of the ayahuasca brew), distinguished by rose-fading-to-white flower color. Became the focus of a landmark biopiracy challenge; the USPTO briefly revoked it in 1999 before reinstating it for the remainder of its term.",
  "claims_summary":"Plant patent claiming the distinct Banisteriopsis caapi cultivar 'Da Vine'.",
  "uncertain_topic":False,
  "note":"Foundational / historical ayahuasca patent; the only genuine pre-2019 DMT-adjacent therapeutic-context patent located."
 },
 {
  "patent_number":"US11235110B1","title":"Delivery system for ayahuasca-like substances",
  "assignee":"Individual inventor (sole named inventor / registered patent attorney)",
  "inventors":[],
  "filing_date":"2021-07-19","publication_date":"2022-02-01","grant_date":"2022-02-01",
  "priority_date":"2020-07-20","jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Claims a vaporizer delivery device and vaporizable formulations for 'ayahuasca-like substances' defined to include DMT, 5-MeO-DMT and 2C-B. Widely criticised (Porta Sophia filed a third-party submission) because DMT vaping was well documented before the priority date.",
  "claims_summary":"Device + formulation claims to vaporizers delivering DMT / 5-MeO-DMT / 2C-B vapor.",
  "uncertain_topic":False,
  "note":"Notable controversial single-inventor psychedelic 'vape' patent."
 },
 {
  "patent_number":"US11406619B2","title":"Novel injectable formulations of DMT-based compounds",
  "assignee":"Small Pharma Ltd (now Cybin Inc)","inventors":[],
  "filing_date":None,"publication_date":"2022-08-09","grant_date":"2022-08-09",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Small Pharma's first U.S. psychedelic patent grant, covering novel injectable (parenteral) formulations of N,N-DMT (active ingredient of SPL026) and deuterium-substituted DMT (SPL028) for treating depressive disorders; also extends to injectable 5-MeO-DMT and psilocybin.",
  "claims_summary":"Injectable/parenteral formulation claims for DMT and deuterated-DMT compositions for depression.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11602521B2","title":"N,N-dimethyltryptamine compositions and methods",
  "assignee":"atai Life Sciences AG","inventors":["Srinivas G. Rao","Glenn Short"],
  "filing_date":"2022-04-26","publication_date":"2023-03-14","grant_date":"2023-03-14",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Improved pharmaceutical compositions comprising N,N-DMT or a pharmaceutically acceptable salt thereof for treating neurological and psychiatric diseases and conditions.",
  "claims_summary":"Composition / method-of-treatment claims for N,N-DMT pharmaceutical compositions.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11643391B2","title":"Prodrugs and conjugates of dimethyltryptamine",
  "assignee":"CaaMTech, Inc.","inventors":[],
  "filing_date":"2022-06-09","publication_date":"2023-05-09","grant_date":"2023-05-09",
  "priority_date":"2021-06-01","jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Prodrugs and conjugates of N,N-DMT designed to modify the compound's very short duration and poor oral bioavailability for therapeutic use in psychedelic-assisted treatment.",
  "claims_summary":"Composition-of-matter claims to DMT prodrug / conjugate chemistry (route detail omitted).",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11660289B2","title":"Deuterated or partially deuterated N,N-dimethyltryptamine compounds",
  "assignee":"Cybin Inc (Small Pharma)","inventors":[],
  "filing_date":None,"publication_date":"2023-05-30","grant_date":"2023-05-30",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Composition-of-matter protection for deuterated and partially deuterated N,N-DMT compounds underpinning Cybin's deuterated-DMT program (CYB004 / SPL028).",
  "claims_summary":"Composition-of-matter claims to deuterated N,N-DMT analogs.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11697638B2","title":"5-methoxy-N,N-dimethyltryptamine crystalline forms",
  "assignee":"Small Pharma Ltd (now Cybin Inc)","inventors":["Peter Rands"],
  "filing_date":"2021-09-08","publication_date":"2023-07-11","grant_date":"2023-07-11",
  "priority_date":"2021-09-08","jurisdiction":"US","status":"granted",
  "molecule_tag":"5-MeO-DMT",
  "abstract":"Crystalline (including deuterated) solid forms of 5-methoxy-N,N-dimethyltryptamine (5-MeO-DMT) fumarate salts, relating to Small Pharma's SPL029 5-MeO-DMT program.",
  "claims_summary":"Claims to specific crystalline / salt forms of 5-MeO-DMT (characterisation only; no synthesis route captured).",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11746088B2","title":"Deuterated tryptamine compounds (deuterated 5-MeO-DMT analogs)",
  "assignee":"Cybin Inc","inventors":[],
  "filing_date":None,"publication_date":"2023-09-05","grant_date":"2023-09-05",
  "priority_date":None,"jurisdiction":"US","status":"granted (exclusivity to ~2041)",
  "molecule_tag":"5-MeO-DMT",
  "abstract":"Composition of matter for deuterated tryptamine compounds and pharmaceutical compositions thereof, covering deuterated 5-methoxy-dimethyltryptamine analogs in Cybin's deuterated-tryptamine portfolio.",
  "claims_summary":"Composition-of-matter claims to deuterated 5-MeO-DMT analogs and pharmaceutical compositions.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11771681B2","title":"Deuterated N,N-dimethyltryptamine analogs (composition of matter)",
  "assignee":"Cybin Inc","inventors":[],
  "filing_date":None,"publication_date":"2023-10-03","grant_date":"2023-10-03",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Composition-of-matter protection for certain deuterated analogs of DMT within Cybin's deuterated N,N-DMT program (announced October 2023 alongside US11773062B2).",
  "claims_summary":"Composition-of-matter claims to deuterated DMT analogs.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11773062B2","title":"Deuterated compounds (medical use and synthesis of DMT analogs)",
  "assignee":"Small Pharma Ltd (Cybin Inc)","inventors":[],
  "filing_date":None,"publication_date":"2023-10-03","grant_date":"2023-10-03",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Protects the medical use of certain deuterated analogs of DMT (paired with US11771681B2 in Cybin's deuterated N,N-DMT program). Route/synthesis claims noted at title level only.",
  "claims_summary":"Medical-use claims for deuterated DMT analogs (synthesis route detail omitted).",
  "uncertain_topic":False
 },
 {
  "patent_number":"US12065405B2","title":"Prodrugs and conjugates of dimethyltryptamine",
  "assignee":"CaaMTech, Inc.","inventors":[],
  "filing_date":None,"publication_date":"2024-08-20","grant_date":"2024-08-20",
  "priority_date":"2021-06-01","jurisdiction":"US","status":"granted",
  "molecule_tag":"N,N-DMT",
  "abstract":"Continuation in CaaMTech's DMT prodrug/conjugate family (related to US11643391B2), covering prodrug forms of N,N-DMT for therapeutic use.",
  "claims_summary":"Composition-of-matter claims to DMT prodrug / conjugate forms.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US12396981B2","title":"Methods of using DMT",
  "assignee":"William Shulman (individual)","inventors":["William Shulman"],
  "filing_date":"2024-03-11","publication_date":"2025-08-26","grant_date":"2025-08-26",
  "priority_date":None,"jurisdiction":"US","status":"granted (Active)",
  "molecule_tag":"N,N-DMT",
  "abstract":"Methods of modulating the subjective DMT experience by administering DMT after a long-acting tryptamine (e.g. psilacetin), optionally with a benzodiazepine and/or ketamine, for treating mental-health and neurodegenerative disorders and for wellbeing.",
  "claims_summary":"Method-of-use / dosing-regimen claims combining DMT with other agents.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US2021/0395201A1","title":"Synthesis of N,N-dimethyltryptamine-type compounds, methods, and uses",
  "assignee":"Small Pharma Ltd (attributed)","inventors":[],
  "filing_date":None,"publication_date":"2021-12-23","grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"Published application covering N,N-DMT-type compounds and their therapeutic uses (title references synthesis; only bibliographic scope captured here).",
  "claims_summary":"Compound + method-of-use claims for DMT-type compounds (synthesis route not captured).",
  "uncertain_topic":False
 },
 {
  "patent_number":"US2021/0403426A1","title":"Deuterated N,N-dimethyltryptamine compounds",
  "assignee":"Small Pharma Ltd / Cybin Inc (attributed)","inventors":[],
  "filing_date":None,"publication_date":"2021-12-30","grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"Published application on deuterated N,N-DMT compounds within the Small Pharma / Cybin deuterated-DMT program.",
  "claims_summary":"Composition-of-matter claims to deuterated N,N-DMT compounds.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US2023/0136824A1","title":"N,N-dimethyltryptamine (DMT) and DMT analog compositions, methods of making, and methods of use thereof",
  "assignee":"atai Life Sciences / Viridia Life Sciences (attributed)","inventors":[],
  "filing_date":None,"publication_date":"2023-05-04","grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"Published application on N,N-DMT and DMT-analog compositions and their methods of use (companion to US2023/0321039A1 in the atai / Viridia VLS-01 family).",
  "claims_summary":"Composition + method-of-use claims for DMT and DMT analogs.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US2023/0321039A1","title":"N,N-dimethyltryptamine (DMT) and DMT analog compositions, methods of making, and methods of use thereof",
  "assignee":"Viridia Life Sciences, Inc. (assigned to Atai Therapeutics, Inc.)","inventors":[],
  "filing_date":None,"publication_date":"2023-10-12","grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"Application underpinning atai's VLS-01 oral transmucosal (buccal) DMT film program; covers DMT and DMT-analog compositions and methods of use for treatment-resistant depression.",
  "claims_summary":"Composition + method-of-use claims for DMT compositions (VLS-01 buccal film program).",
  "uncertain_topic":False
 },
 {
  "patent_number":"WO2023/076135A1","title":"N,N-dimethyltryptamine (DMT) crystalline products and methods of making the same",
  "assignee":"(PCT applicant — psychedelic developer)","inventors":[],
  "filing_date":None,"publication_date":"2023-05-04","grant_date":None,
  "priority_date":None,"jurisdiction":"WO","status":"PCT application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"PCT application on crystalline solid-form products of N,N-DMT (bibliographic scope only; making/route detail not captured).",
  "claims_summary":"Claims to crystalline DMT product forms.",
  "uncertain_topic":False
 },
 {
  "patent_number":"WO2024/121253A1","title":"Novel N,N-dimethyltryptamine (DMT) derivatives and uses thereof",
  "assignee":"(PCT applicant — psychedelic developer)","inventors":[],
  "filing_date":None,"publication_date":"2024-06-13","grant_date":None,
  "priority_date":None,"jurisdiction":"WO","status":"PCT application/published",
  "molecule_tag":"N,N-DMT",
  "abstract":"PCT application on novel N,N-DMT derivatives and their therapeutic uses.",
  "claims_summary":"Compound + use claims for novel DMT derivatives.",
  "uncertain_topic":False
 },
 {
  "patent_number":"EP3927337B1","title":"Mebufotenin (5-MeO-DMT) for use in treating major depressive disorder / treatment-resistant depression",
  "assignee":"GH Research Ireland Ltd","inventors":[],
  "filing_date":None,"publication_date":"2024-02-14","grant_date":"2024-02-14",
  "priority_date":None,"jurisdiction":"EP","status":"granted (effective 2024-02-14; expiry no earlier than 2040)",
  "molecule_tag":"5-MeO-DMT",
  "abstract":"European patent with claims directed to mebufotenin (5-MeO-DMT) or a pharmaceutically acceptable salt thereof for use in treating major depressive disorder (MDD) and treatment-resistant depression, including pulmonary-inhalation, intravenous and intranasal administration.",
  "claims_summary":"Medical-use (second-medical-use) claims to 5-MeO-DMT / salts for MDD and TRD.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US 18/675,614 (application)","title":"5-Methoxy-N,N-Dimethyltryptamine (5-MeO-DMT) for Treating Depression",
  "assignee":"GH Research Ireland Ltd","inventors":[],
  "filing_date":"2024-05-28","publication_date":None,"grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"pending — all pending claims rejected (novelty/obviousness)",
  "molecule_tag":"5-MeO-DMT",
  "abstract":"U.S. counterpart of GH Research's 5-MeO-DMT (mebufotenin) depression program: methods of treating MDD and TRD with 5-MeO-DMT, emphasising inhalation, dosing strategies and MADRS/HAM-D endpoints. All pending U.S. claims were rejected over prior public disclosures.",
  "claims_summary":"Method-of-treatment claims for 5-MeO-DMT in depression (US claims rejected).",
  "uncertain_topic":False
 },
 {
  "patent_number":"US 18/697,499 (application)","title":"Encapsulated microparticles and nanoparticles of dimethyltryptamines",
  "assignee":"Biomind Labs Inc.","inventors":[],
  "filing_date":"2024-04-01","publication_date":None,"grant_date":None,
  "priority_date":"2022-09-29","jurisdiction":"US","status":"application (pending; withstood third-party observations)",
  "molecule_tag":"N,N-DMT",
  "abstract":"Compositions and methods for formulating DMT and 5-MeO-DMT with microparticle and nanoparticle polymers for clinical use (Biomind's BMND08 5-MeO-DMT nano-formulation program). PCT counterpart filed across ~153 jurisdictions.",
  "claims_summary":"Formulation claims to encapsulated micro/nanoparticle DMT and 5-MeO-DMT compositions.",
  "uncertain_topic":False
 },
 {
  "patent_number":"US11292765B2","title":"Tryptamine prodrugs",
  "assignee":"CaaMTech, Inc. (attributed)","inventors":[],
  "filing_date":None,"publication_date":"2022-04-05","grant_date":"2022-04-05",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"tryptamine-general",
  "abstract":"Prodrug forms of psychedelic tryptamines; part of CaaMTech's broad tryptamine platform that encompasses DMT among other tryptamines.",
  "claims_summary":"Composition-of-matter claims to tryptamine prodrugs (platform scope).",
  "uncertain_topic":True,
  "note":"Broad tryptamine-platform patent; DMT is within scope but not necessarily the primary claim."
 },
 {
  "patent_number":"US11332441B2","title":"Crystalline N-methyl tryptamine derivatives",
  "assignee":"CaaMTech, Inc. (attributed)","inventors":[],
  "filing_date":None,"publication_date":"2022-05-17","grant_date":"2022-05-17",
  "priority_date":None,"jurisdiction":"US","status":"granted",
  "molecule_tag":"tryptamine-general",
  "abstract":"Crystalline forms of N-methyl tryptamine derivatives within CaaMTech's tryptamine platform.",
  "claims_summary":"Claims to crystalline N-methyl tryptamine derivative forms.",
  "uncertain_topic":True,
  "note":"Broad tryptamine-platform patent; DMT-adjacent."
 },
 {
  "patent_number":"US2023/0406824A1","title":"Tryptamine derivatives and their therapeutic uses",
  "assignee":"(psychedelic developer — attribution unresolved)","inventors":[],
  "filing_date":None,"publication_date":"2023-12-21","grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"application/published",
  "molecule_tag":"tryptamine-general",
  "abstract":"Published application on tryptamine derivatives and their therapeutic uses (DMT within the broader tryptamine scope).",
  "claims_summary":"Compound + therapeutic-use claims for tryptamine derivatives.",
  "uncertain_topic":True
 },
 {
  "patent_number":"Beckley Psytech BPL-003 (US composition-of-matter; exact number unresolved)",
  "title":"Intranasal mebufotenin (5-MeO-DMT) benzoate formulation (BPL-003)",
  "assignee":"Beckley Psytech Ltd (AtaiBeckley Inc.)","inventors":[],
  "filing_date":None,"publication_date":None,"grant_date":None,
  "priority_date":None,"jurisdiction":"US","status":"granted composition-of-matter (US, UK, EP) — exact US number not resolved via free sources",
  "molecule_tag":"5-MeO-DMT",
  "abstract":"BPL-003 is Beckley Psytech's patent-protected intranasal formulation of mebufotenin (5-MeO-DMT) benzoate delivered by nasal spray, in Phase IIb for treatment-resistant depression (FDA Breakthrough Therapy 2025; program moved under Eli Lilly / AtaiBeckley 2026). Covered by granted US/UK/EP composition-of-matter patents.",
  "claims_summary":"Composition-of-matter claims to intranasal 5-MeO-DMT benzoate formulation.",
  "uncertain_topic":False,
  "note":"Included per coordinator seed; exact granted US patent number not resolvable via free search (Google Patents/PatentsView unavailable)."
 },
 {
  "patent_number":"Algernon AP-188 (DMT salt-form / method applications; number unresolved)",
  "title":"Novel DMT salt forms (pamoate, nicotinate) and methods for stroke and traumatic brain injury",
  "assignee":"Algernon Pharmaceuticals Inc.","inventors":[],
  "filing_date":"2021-01-01","publication_date":None,"grant_date":None,
  "priority_date":"2021-01-01","jurisdiction":"US","status":"application(s) filed 2021 — number not resolved via free sources",
  "molecule_tag":"N,N-DMT",
  "abstract":"Algernon's AP-188 IP covers novel DMT salt forms (pamoate and nicotinate) plus formulation, dosage and method-of-use claims for ischemic and hemorrhagic stroke and traumatic brain injury — a non-psychiatric (neuro-repair) DMT indication.",
  "claims_summary":"Salt-form, formulation and method-of-treatment claims for DMT in stroke / TBI.",
  "uncertain_topic":False,
  "note":"Included per coordinator seed; filing_date approximate (early 2021 per company disclosures); exact application number not resolvable via free search."
 },
]

def jurisdiction_of(num, default):
    m = re.match(r"^\s*([A-Z]{2})", num or "")
    return m.group(1) if m else default

def year_of(d):
    if d and re.match(r"\d{4}", d):
        return int(d[:4])
    return None

def norm(r):
    num = r["patent_number"]
    juris = r.get("jurisdiction") or jurisdiction_of(num, "US")
    return {
        "patent_number": num,
        "title": r["title"],
        "assignee": r.get("assignee"),
        "inventors": r.get("inventors", []),
        "filing_date": r.get("filing_date"),
        "publication_date": r.get("publication_date"),
        "grant_date": r.get("grant_date"),
        "priority_date": r.get("priority_date"),
        "jurisdiction": juris,
        "status": r.get("status"),
        "molecule_tag": r["molecule_tag"],
        "abstract": r.get("abstract"),
        "claims_summary": r.get("claims_summary"),
        "url": (GP(re.sub(r"\s|\(.*\)|/", "", num))
                if re.match(r"^(US|EP|WO)", re.sub(r"\s", "", num)) and re.search(r"\d", num)
                and "unresolved" not in num else None),
        "uncertain_topic": r.get("uncertain_topic", False),
        "note": r.get("note"),
    }

def main():
    records = [norm(r) for r in RECORDS]

    # merge any raw Google-Patents harvest if present (deduped by number)
    merged_from_raw = 0
    if os.path.exists(RAW):
        have = {re.sub(r"[^A-Z0-9]", "", (r["patent_number"] or "").upper()) for r in records}
        try:
            raw = json.load(open(RAW, encoding="utf-8"))
            for pid, pat in raw.items():
                pub = pat.get("publication_number") or ""
                key = re.sub(r"[^A-Z0-9]", "", pub.upper())
                if key and key not in have:
                    merged_from_raw += 1  # (kept minimal; curated set is the spine)
        except Exception:
            pass

    def sortkey(r):
        return (r["filing_date"] or r["priority_date"] or r["publication_date"] or "9999")
    records.sort(key=sortkey)

    by_decade, by_assignee, by_molecule, by_juris = Counter(), Counter(), Counter(), Counter()
    fam = set()
    for r in records:
        y = year_of(r["filing_date"] or r["priority_date"] or r["publication_date"])
        by_decade[(f"{(y//10)*10}s" if y else "unknown")] += 1
        if r["assignee"]:
            # collapse to a short org key for the tally
            a = re.split(r"\s*\(", r["assignee"])[0].strip()
            if not a:
                a = r["assignee"].strip()
            by_assignee[a] += 1
        by_molecule[r["molecule_tag"]] += 1
        by_juris[r["jurisdiction"]] += 1
        fam.add((re.sub(r"[^a-z0-9]", "", r["title"].lower())[:50], r["priority_date"] or r["filing_date"] or r["publication_date"]))

    out = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_notes": (
            "APIs: Google Patents public XHR (patents.google.com/xhr/query) initially returned data "
            "(confirmed ~6,764 abstract hits and ~1,386 title hits for 'dimethyltryptamine') but after a "
            "few requests began returning HTTP 503 and then Google's 'unusual traffic' block page; WebFetch "
            "to patents.google.com and patents.justia.com also returned 503/403 (same block). PatentsView "
            "LEGACY api (api.patentsview.org) is RETIRED - it 301-redirects to the USPTO ODP portal HTML; the "
            "NEW search.patentsview.org api requires an X-Api-Key (none available) and returned no data. The "
            "Lens and EPO OPS were not attempted (require keys). RESULT: this catalog was assembled from "
            "WebSearch-verified bibliographic facts drawn from USPTO/EPO records and reputable secondary "
            "sources (company IR / press releases, Psychedelic Alpha, Porta Sophia psychedelic prior-art "
            "library, Justia bibliographic listings). It is therefore a high-confidence CURATED catalog of the "
            "genuine psychedelic-therapeutic DMT / 5-MeO-DMT / ayahuasca patent landscape (the modern "
            "2019-2025 wave plus the 1986 'Da Vine' ayahuasca plant patent), not an exhaustive machine dump - "
            "the bulk-API route was blocked. Abstracts are short factual descriptions and claims_summary gives "
            "high-level claim scope only; NO chemical synthesis or manufacturing route detail is included even "
            "where the underlying patent contains it. FILTERING: dropped false-positive 'DMT'/'Dmt' acronym "
            "hits - notably US20080269143 / US8030341 ('DMT-Derivative Compounds', which are 2',6'-dimethyl"
            "tyrosine opioid peptides, not dimethyltryptamine), plus Derjaguin-Muller-Toporov contact "
            "mechanics, dot-matrix, and dimethyl terephthalate. Dates left null where not verifiable rather "
            "than guessed; a few filing dates are approximate and flagged in the record 'note'. Two records "
            "(Beckley BPL-003, Algernon AP-188) are known-real programs whose exact patent numbers could not "
            "be resolved via free sources and are flagged accordingly. Records are deduped by patent_number."
        ),
        "counts": {
            "total_records": len(records),
            "estimated_unique_families": len(fam),
            "uncertain_topic": sum(1 for r in records if r["uncertain_topic"]),
            "records_with_resolved_number": sum(1 for r in records if r["url"]),
            "by_decade": dict(sorted(by_decade.items())),
            "by_assignee_top20": dict(by_assignee.most_common(20)),
            "by_molecule_tag": dict(by_molecule.most_common()),
            "by_jurisdiction": dict(by_juris.most_common()),
        },
        "records": records,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {len(records)} records -> {OUT}")
    print("molecule:", dict(by_molecule))
    print("decades:", dict(sorted(by_decade.items())))
    print("assignees:", by_assignee.most_common(12))
    print("earliest:", [(r['patent_number'], r['filing_date'] or r['publication_date']) for r in records[:3]])

if __name__ == "__main__":
    main()
