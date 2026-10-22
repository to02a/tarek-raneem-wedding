from pathlib import Path
import base64
import io
import re
from PIL import Image

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")
pattern = re.compile(r"data:image/png;base64,([A-Za-z0-9+/=]+)")
matches = pattern.findall(html)

if not matches:
    print("No embedded PNG data URIs found; nothing to optimize.")
    raise SystemExit(0)

cache = {}
counter = 0

def replacement(match):
    global counter
    b64 = match.group(1)
    raw = base64.b64decode(b64)
    key = raw[:64] + len(raw).to_bytes(8, "big")
    if key in cache:
        return cache[key]

    counter += 1
    name = f"floral-{counter}.webp"
    im = Image.open(io.BytesIO(raw)).convert("RGBA")

    max_width = 760
    if im.width > max_width:
        new_height = round(im.height * max_width / im.width)
        im = im.resize((max_width, new_height), Image.Resampling.LANCZOS)

    im.save(name, "WEBP", quality=82, method=3)
    cache[key] = name
    print(f"Wrote {name}: {Path(name).stat().st_size} bytes")
    return name

optimized = pattern.sub(replacement, html)
html_path.write_text(optimized, encoding="utf-8")
print(f"index.html: {html_path.stat().st_size} bytes")
print(f"Unique floral assets: {len(cache)}")
