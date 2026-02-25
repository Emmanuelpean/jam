import re, pathlib

for path in pathlib.Path("./").glob("Indeed_*.html"):
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<noscript[\s\S]*?</noscript>", "", html, flags=re.DOTALL)
    path.write_text(html, encoding="utf-8")
    print(f"Cleaned {path.name}")