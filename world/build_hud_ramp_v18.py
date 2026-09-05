"""One-shot isolated deterministic HUD ramp candidate; live CSS remains untouched."""
from pathlib import Path
import ast
import hashlib
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-hud-ramp-v18'
asset = HERE / 'hud-alpha-ramp-v18.png'
target = HERE / 'probe_hud_ramp_v18.py'
assert not asset.exists() and not target.exists()
# Explicit endpoint samples; standard browser image interpolation provides scaling.
# No random data, noise, colour profile, procedural CSS raster or AI imagery.
t = np.arange(4097, dtype=np.float64) / 4096
alpha = np.where(t <= .75, t * 112 / .75, 112 + (t - .75) * 64 / .25)
rgba = np.empty((4097, 1, 4), dtype=np.uint8)
rgba[:, 0, :3] = (4, 2, 10)
rgba[:, 0, 3] = np.floor(alpha + .5).astype(np.uint8)
assert rgba[0, 0, 3] == 0 and rgba[3072, 0, 3] == 112 and rgba[-1, 0, 3] == 176
Image.fromarray(rgba).save(asset)
source = (HERE / 'probe_static_compositor_v18r2.py').read_text()
def replace(old, new):
    global source
    assert source.count(old) == 1, old[:100]
    source = source.replace(old, new)
replace('diagnostic-static-compositor-v18r2', PREFIX)
replace("for mode in ['present','absent']:", "for mode in ['ramp']:")
replace("html = html.replace('</body>',", "html = html.replace('</head>', '<style>#hud::before{background: url(hud-alpha-ramp-v18.png) center / 100% 100% no-repeat}</style></head>')\nhtml = html.replace('</body>',")
replace("'purpose':'Static diagnostic, not live acceptance or correction'", "'purpose':'Changed deterministic HUD PNG fixture; not live acceptance', 'asset_sha256':digest(HERE/'hud-alpha-ramp-v18.png')")
replace("if mode=='present':page.screenshot(path=str(HERE/f'{PREFIX}.png'))", """page.screenshot(path=str(HERE/f'{PREFIX}.png'))
        desktop_clip = clip
        page.set_viewport_size({'width':390,'height':844});settled()
        clip = {'x':40,'y':410,'width':300,'height':50}
        pair('mobile:baseline')
        page.set_viewport_size({'width':410,'height':844});settled()
        page.set_viewport_size({'width':390,'height':844});settled()
        pair('mobile:resize-restored')
        page.locator('#detail').click();page.locator('#detail').click()
        pair('mobile:detail-restored')
        page.screenshot(path=str(HERE/f'{PREFIX}-mobile.png'))
        case['mobile_final']=page.evaluate('staticProbe()')
        clip = desktop_clip""")
replace("f'{PREFIX}.js',f'{PREFIX}.png'", "f'{PREFIX}.js',f'{PREFIX}.png',f'{PREFIX}-mobile.png','hud-alpha-ramp-v18.png'")
replace("print('Static isolation completed; no live runtime changes.',flush=True)", "assert all(c['changed_pixels']==0 for case in receipt['cases'] for c in case['comparisons']), 'Strict candidate stillness failed'\nprint('Changed HUD ramp fixture passed; no live runtime changes.',flush=True)")
ast.parse(source)
target.write_text(source)
(HERE / 'hud-ramp-v18-build.json').write_text(json.dumps({
    'asset': asset.name, 'dimensions': [1,4097], 'rgb': [4,2,10],
    'alpha_stops': [[0,0],[.75,112],[1,176]], 'bytes': asset.stat().st_size,
    'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(),
    'fixture_parent': 'probe_static_compositor_v18r2.py',
    'live_files_modified': False,
}, indent=2)+'\n')
print('Built isolated HUD PNG candidate and changed-only fixture.')
