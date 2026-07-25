import requests, json, sys, time

OUT = {}
terms = ["dimethyltryptamine", "ayahuasca", "hoasca", "N,N-dimethyltryptamine", "psychotropic substances"]
base = "https://www.federalregister.gov/api/v1/documents.json"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (research; dmtatlas archive)"})

for term in terms:
    params = {
        "conditions[term]": term,
        "per_page": 100,
        "order": "oldest",
        "fields[]": ["title","type","abstract","document_number","publication_date","agencies","html_url","action","citation"],
    }
    try:
        r = session.get(base, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        docs = data.get("results", [])
        OUT[term] = {"count": data.get("count"), "docs": docs}
        print(f"[OK] {term}: total_count={data.get('count')} pulled={len(docs)}")
    except Exception as e:
        OUT[term] = {"error": str(e)}
        print(f"[FAIL] {term}: {e}")
    time.sleep(0.5)

with open("fedreg_raw.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, indent=2)
print("wrote fedreg_raw.json")
