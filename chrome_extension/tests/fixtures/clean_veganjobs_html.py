import pathlib
import re

for path in pathlib.Path("./").glob("veganjobs_*.html"):
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r'\s*style="[^"]*"', "", html)
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(
        r"<link[^>]*(?:maps\.googleapis|maps\.google|fonts\.googleapis|fonts\.gstatic|code\.jquery)[^>]*/?>", "", html
    )
    path.write_text(html, encoding="utf-8")
    print(f"Cleaned {path.name}")
