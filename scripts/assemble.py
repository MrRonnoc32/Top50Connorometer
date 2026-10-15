"""Inject the generated data and land outlines into src/page.html. Writes dist/index.html."""
import os, sys
root = sys.argv[1]
s = open(os.path.join(root, "src/page.html")).read()
s = s.replace("__DATA__", open("story_data.json").read().replace("</", "<\\/")).replace("__LAND__", open(os.path.join(root, "vendor/land-110m.geo.json")).read())
cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>'
assert cdn in s
s = s.replace(cdn, "<script>" + open(os.path.join(root, "vendor/d3-7.8.5.min.js")).read() + "</script>")
i = s.index("</style>") + len("</style>")
s = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
     + s[:i] + "\n<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n" + s[i:] + "\n</body>\n</html>\n")
os.makedirs(os.path.join(root, "dist"), exist_ok=True)
open(os.path.join(root, "dist/index.html"), "w").write(s)
print("dist/index.html", len(s), "bytes")
