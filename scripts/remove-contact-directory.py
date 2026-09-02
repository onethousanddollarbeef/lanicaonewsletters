#!/usr/bin/env python3
"""Remove contact/email info and professional services directory from newsletter pages."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTH_FILES = sorted(ROOT.glob("*-2026.html"))


def strip_header_json_keys(text: str) -> str:
    def clean_obj(obj):
        if isinstance(obj, dict):
            obj.pop("contact", None)
            obj.pop("directoryTitle", None)
            obj.pop("directoryItems", None)
            for value in obj.values():
                clean_obj(value)
        elif isinstance(obj, list):
            for item in obj:
                clean_obj(item)
        return obj

    def repl(match):
        payload = json.loads(match.group(1))
        clean_obj(payload)
        return f'{match.group(0)[: match.start(1) - match.start()]}{json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}'

    return re.sub(
        r'(<script[^>]*id="[^"]*-header-data"[^>]*>\s*)(\{.*?\})(\s*</script>)',
        lambda m: m.group(1) + json.dumps(clean_obj(json.loads(m.group(2))), ensure_ascii=False, separators=(",", ":")) + m.group(3),
        text,
        flags=re.S,
    )


def patch_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original

    text = re.sub(r'\n\s*<p class="article-contact"[^>]*>.*?</p>\s*', "\n", text, flags=re.S)
    text = re.sub(
        r'\n\s*<h2[^>]*data-[^=]+-ui="directoryTitle"[^>]*>.*?</h2>\s*<div class="article-list-block directory-list">.*?</div>\s*',
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r'\n\s*<h2>Professional Services Directory</h2>\s*<div class="article-list-block directory-list">.*?</div>\s*',
        "\n",
        text,
        flags=re.S,
    )

    text = strip_header_json_keys(text)

    text = re.sub(r"\n\s*const directoryEl = document\.getElementById\([^)]+\);\n", "\n", text)
    text = re.sub(
        r"\n\s*directoryEl\.innerHTML = ui\[selectedLang\]\.directoryItems[\s\S]*?\.join\(\"\"\);\n",
        "\n",
        text,
    )
    text = re.sub(
        r"chunks\.push\(`<h2 data-[^`]+-ui=\"directoryTitle\">.*?</div>`\);\n",
        "",
        text,
        flags=re.S,
    )
    text = re.sub(
        r'if \(key === "directoryItems"\) return;\n\s*',
        "",
        text,
    )
    text = re.sub(
        r'if \(key === "directoryItems" \|\| key === "page"\) return;\n',
        'if (key === "page") return;\n',
        text,
    )
    text = re.sub(
        r'if \(key === "directoryItems" \|\| key === "page" \|\| key === "pageTitle" \|\| key === "metaDescription"\) return;\n',
        'if (key === "page" || key === "pageTitle" || key === "metaDescription" || key === "contact" || key === "directoryTitle") return;\n',
        text,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def patch_assets() -> bool:
    path = ROOT / "assets" / "script-BUOrxcsY.js"
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    text = original
    text = re.sub(r'\n\s*<p class="article-contact">.*?</p>\n', "\n", text, flags=re.S)
    text = re.sub(
        r'\n\s*<h2>Professional Services Directory</h2>\s*<div class="article-list-block directory-list">.*?</div>\n',
        "\n",
        text,
        flags=re.S,
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = []
    for path in MONTH_FILES:
        if patch_file(path):
            changed.append(path.name)
    if patch_assets():
        changed.append("assets/script-BUOrxcsY.js")
    print("Updated:", ", ".join(changed) if changed else "no files changed")


if __name__ == "__main__":
    main()
