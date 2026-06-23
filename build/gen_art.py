"""Generate the Atlas's atmospheric art with gpt-image-2 (per standing rule: always gpt-image-2)."""
import os, base64, sys
from openai import OpenAI

key = os.environ.get("OPENAI_API_KEY", "")
if len(key) < 40:
    # fall back to the WorkShield .env key
    for line in open(r"C:\Users\dwayn\OneDrive\Desktop\WorkShield\.env", encoding="utf-8", errors="replace"):
        if line.strip().startswith("OPENAI_API_KEY") and "=" in line:
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
client = OpenAI(api_key=key)

OUT = r"C:\Users\dwayn\OneDrive\Desktop\HyperspaceAtlas\assets\img"
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("void_bg.png", "1536x1024",
     "A very dark, near-black deep-space backdrop for a website background. Subtle deep indigo, violet and teal nebula clouds drifting through blackness, a faint scattering of tiny distant stars, and barely-visible thin geometric lattice lines and delicate sacred-geometry filigree woven into the dark. Extremely low contrast, muted, atmospheric, MOSTLY BLACK so bright interface elements read clearly on top. No text, no characters, no central subject, seamless ambient cosmic texture, cinematic, elegant, refined."),
    ("chrysanthemum.png", "1024x1024",
     "A luminous, intricate fractal mandala in the shape of a glowing chrysanthemum flower, radiating many concentric kaleidoscopic petals in deep gold, warm amber, magenta and violet, opening like a doorway into infinite tunneling depth, on a pure black background. Hyper-detailed symmetrical sacred geometry, psychedelic yet elegant and refined, soft inner glow, gentle bloom, centered, no text, no face. Premium poster quality."),
]

for fname, size, prompt in JOBS:
    print(f"generating {fname} ({size}) ...", flush=True)
    r = client.images.generate(model="gpt-image-2", prompt=prompt, size=size, quality="high")
    b64 = r.data[0].b64_json
    with open(os.path.join(OUT, fname), "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  saved {fname}", flush=True)
print("done")
