"""Make docs/ work with no internet (for presenting on an iPad from the Home Screen).

Usage: python3 scripts/offline.py [repo root]

What it does (safe to run more than once):
1. Swaps the Google Fonts link in docs/index.html for the same fonts embedded in the page
   (vendor/fonts, from Fontsource, SIL Open Font License). D3, the data and the background
   image are already embedded by assemble.py, so after this the page has no outside requests.
2. Adds the Home Screen tags (manifest, icon, full-screen mode) and registers a service worker.
3. Writes docs/sw.js, docs/manifest.webmanifest and the icons. The service worker's cache name
   carries a hash of the page, so each new build replaces the old copy on the iPad.
"""
import base64, hashlib, os, re, shutil, sys

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
docs, vend = os.path.join(root, "docs"), os.path.join(root, "vendor")
page = os.path.join(docs, "index.html")
s = open(page, encoding="utf-8").read()

# 1. Fonts: replace the three Google Fonts lines with embedded @font-face rules.
FONTS = [("Figtree", 400, "figtree-latin-400-normal"), ("Figtree", 600, "figtree-latin-600-normal"),
         ("Figtree", 700, "figtree-latin-700-normal"), ("IBM Plex Mono", 500, "ibm-plex-mono-latin-500-normal"),
         ("IBM Plex Mono", 600, "ibm-plex-mono-latin-600-normal"), ("Zilla Slab", 300, "zilla-slab-latin-300-normal"),
         ("Zilla Slab", 400, "zilla-slab-latin-400-normal")]
s = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n?', "", s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">\n?', "", s)
if 'id="embedded-fonts"' not in s:
    rules = "".join(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
        "src:url(data:font/woff2;base64,%s) format('woff2')}\n"
        % (fam, w, base64.b64encode(open(os.path.join(vend, "fonts", f + ".woff2"), "rb").read()).decode())
        for fam, w, f in FONTS)
    s = s.replace("<title>", '<style id="embedded-fonts">\n' + rules + "</style>\n<title>", 1)
assert "fonts.googleapis.com" not in s and "<script src=" not in s, "page still loads something from the internet"

# 2. Home Screen tags and service worker registration.
HEAD = ('<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="apple-touch-icon" href="icon-180.png">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-title" content="Top 50">\n'
        '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
        '<meta name="theme-color" content="#F3F6F6">\n')
if 'rel="manifest"' not in s:
    s = s.replace("<title>", HEAD + "<title>", 1)
REG = ('<script>if("serviceWorker" in navigator){window.addEventListener("load",function(){'
       'navigator.serviceWorker.register("sw.js").catch(function(){});});}</script>\n')
if "serviceWorker.register" not in s:
    i = s.rindex("</body>")
    s = s[:i] + REG + s[i:]
open(page, "w", encoding="utf-8").write(s)

# 3. Service worker, manifest, icons.
for n in (180, 192, 512):
    shutil.copy(os.path.join(vend, "pwa", "icon-%d.png" % n), os.path.join(docs, "icon-%d.png" % n))
open(os.path.join(docs, "manifest.webmanifest"), "w").write("""{
  "name": "Path to the Top 50",
  "short_name": "Top 50",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#F3F6F6",
  "theme_color": "#F3F6F6",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
""")
version = hashlib.sha256(s.encode()).hexdigest()[:12]
sw = open(os.path.join(root, "scripts", "sw.template.js")).read().replace("__VERSION__", version)
open(os.path.join(docs, "sw.js"), "w").write(sw)
print("docs/ is offline-ready. Page %d bytes, cache version %s" % (len(s.encode()), version))
