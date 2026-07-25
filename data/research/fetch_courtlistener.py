import requests, json, time

OUT = {}
queries = [
    'O Centro Espirita',
    'hoasca',
    'ayahuasca',
    'dimethyltryptamine',
    'Santo Daime',
    'Uniao do Vegetal',
    'Church of the Holy Light of the Queen',
]
base = "https://www.courtlistener.com/api/rest/v4/search/"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (research; dmtatlas archive)"})

for q in queries:
    params = {"q": q, "type": "o"}  # o = case law opinions
    try:
        r = session.get(base, params=params, timeout=30)
        status = r.status_code
        if status == 200:
            data = r.json()
            results = data.get("results", [])
            slim = []
            for res in results[:15]:
                slim.append({
                    "caseName": res.get("caseName"),
                    "court": res.get("court"),
                    "court_citation_string": res.get("court_citation_string"),
                    "dateFiled": res.get("dateFiled"),
                    "citation": res.get("citation"),
                    "docketNumber": res.get("docketNumber"),
                    "absolute_url": res.get("absolute_url"),
                })
            OUT[q] = {"status": status, "count": data.get("count"), "results": slim}
            print(f"[OK] {q}: count={data.get('count')} shown={len(slim)}")
        else:
            OUT[q] = {"status": status, "body": r.text[:300]}
            print(f"[HTTP {status}] {q}: {r.text[:150]}")
    except Exception as e:
        OUT[q] = {"error": str(e)}
        print(f"[FAIL] {q}: {e}")
    time.sleep(1.0)

with open("courtlistener_raw.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, indent=2)
print("wrote courtlistener_raw.json")
