import requests,json,time
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 (dmtatlas research)"})
queries=["dimethyltryptamine thesis","ayahuasca dissertation","ayahuasca thesis","dimethyltryptamine dissertation","yage thesis","N,N-dimethyltryptamine thesis"]
allhits={}
notes=[]
for q in queries:
    for attempt in range(3):
        try:
            r=S.post("https://api.core.ac.uk/v3/search/works",json={"q":q,"limit":100},timeout=150)
            if r.status_code==200:
                d=r.json(); hits=d.get("results",[])
                for h in hits:
                    allhits[h.get("id") or (h.get("title","")+str(h.get("yearPublished")))]=h
                print("%-34s -> %d (total=%s)"%(q,len(hits),d.get("totalHits")),flush=True); break
            else:
                print("%s status %s"%(q,r.status_code),flush=True)
                if r.status_code in (401,403): break
        except Exception as e:
            print("%s attempt %d %s"%(q,attempt,type(e).__name__),flush=True); time.sleep(8)
    time.sleep(2)
print("CORE unique raw:",len(allhits),flush=True)
json.dump(list(allhits.values()),open("data/research/raw/theses_core_raw.json","w",encoding="utf-8"))
if allhits:
    s=list(allhits.values())[0]; print("KEYS:",sorted(s.keys()),flush=True)
