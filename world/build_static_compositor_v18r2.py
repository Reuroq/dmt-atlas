"""Preserve first fixture's resize-observer failure; build corrected isolation."""
from pathlib import Path
import ast
import json

here=Path(__file__).resolve().parent
target=here/'probe_static_compositor_v18r2.py'
assert not target.exists()
s=(here/'probe_static_compositor_v18.py').read_text()
s=s.replace("PREFIX = 'diagnostic-static-compositor-v18'", "PREFIX = 'diagnostic-static-compositor-v18r2'")
a="""        def settled():
            page.wait_for_function('!staticProbe().pending')"""
b="""        def settled():
            # A viewport API acknowledgement can precede native resize delivery.
            # Observe actual drawing dimensions, not just the previous fence.
            page.wait_for_function('''() => {const s=staticProbe();const r=Math.min(devicePixelRatio,s.high?1.5:.85);
                return !s.pending && s.width===Math.floor(innerWidth*r) && s.height===Math.floor(innerHeight*r);}''')"""
assert s.count(a)==1
s=s.replace(a,b)
ast.parse(s)
target.write_text(s)
(here/'static-compositor-v18-initial-failure.json').write_text(json.dumps({
    'failure':'Static submission changed during comparison after viewport resize',
    'cause':'Fixture waited for previous pending=false before native resize delivery; dimension guard missing.',
    'scope':'Diagnostic harness error, not screenshot inequality or live application failure.',
    'preserved':['probe_static_compositor_v18.py','diagnostic-static-compositor-v18.js','diagnostic-static-compositor-v18.html','probe-static-compositor-v18.log'],
    'correction':'r2 waits for actual drawing dimensions plus fence retirement; no delay or relaxed equality.'
},indent=2)+'\n')
