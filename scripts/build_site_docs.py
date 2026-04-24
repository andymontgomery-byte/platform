#!/usr/bin/env python3
"""Render Markdown docs into GitHub Pages HTML pages."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "site" / "docs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pages = []
    for source in sorted(DOCS.rglob("*.md")):
        slug = slug_for(source)
        title = title_for(source)
        body = markdown_to_html(source.read_text(), source)
        html_page = render_page(title, body, source)
        target = OUT / f"{slug}.html"
        target.write_text(html_page)
        pages.append((title, target.name, source.relative_to(ROOT).as_posix()))
    (OUT / "index.html").write_text(render_index(pages))
    print(f"generated {OUT.relative_to(ROOT)}")


def slug_for(path: Path) -> str:
    relative = path.relative_to(DOCS).with_suffix("")
    return "-".join(relative.parts).replace("_", "-")


def title_for(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def render_page(title: str, body: str, source: Path) -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <title>{escape(title)}</title>\n"
        "  <link rel=\"stylesheet\" href=\"../styles.css\">\n"
        "</head>\n"
        "<body class=\"doc-page\">\n"
        "  <main class=\"doc-shell\">\n"
        "    <p class=\"eyebrow\">Rendered portal documentation</p>\n"
        f"    <p><a class=\"text-link\" href=\"index.html\">Docs index</a></p>\n"
        f"    {body}\n"
        f"    <p class=\"source-note\">Source file: <code>{escape(source.relative_to(ROOT).as_posix())}</code></p>\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def render_index(pages: list[tuple[str, str, str]]) -> str:
    cards = "\n".join(
        "<article class=\"doc-card\">"
        f"<h2><a href=\"{escape(file_name)}\">{escape(title)}</a></h2>"
        f"<p><code>{escape(source)}</code></p>"
        "</article>"
        for title, file_name, source in pages
    )
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <title>Platform Documentation</title>\n"
        "  <link rel=\"stylesheet\" href=\"../styles.css\">\n"
        "</head>\n"
        "<body class=\"doc-page\">\n"
        "  <main class=\"doc-shell\">\n"
        "    <p class=\"eyebrow\">Rendered portal documentation</p>\n"
        "    <h1>Platform Documentation</h1>\n"
        "    <p class=\"doc-lede\">HTML-rendered versions of the planning, dictionary, decisions, and accounting documents.</p>\n"
        f"    <div class=\"doc-grid\">{cards}</div>\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def markdown_to_html(markdown: str, source: Path) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    ordered_items: list[str] = []
    in_code = False
    code_lines: list[str] = []
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline(' '.join(paragraph), source)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, ordered_items
        if list_items:
            output.append("<ul>" + "".join(f"<li>{inline(item, source)}</li>" for item in list_items) + "</ul>")
            list_items = []
        if ordered_items:
            output.append("<ol>" + "".join(f"<li>{inline(item, source)}</li>" for item in ordered_items) + "</ol>")
            ordered_items = []

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                output.append("<pre><code>" + escape("\n".join(code_lines)) + "</code></pre>")
                in_code = False
                code_lines = []
            else:
                flush_paragraph()
                flush_list()
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            i += 1
            continue
        if is_table_start(lines, i):
            flush_paragraph()
            flush_list()
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            output.append(table_to_html(table_lines, source))
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)), 4)
            output.append(f"<h{level}>{inline(heading.group(2), source)}</h{level}>")
            i += 1
            continue
        bullet = re.match(r"^-\s+(.*)$", line)
        if bullet:
            flush_paragraph()
            ordered_items = []
            list_items.append(bullet.group(1))
            i += 1
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", line)
        if ordered:
            flush_paragraph()
            list_items = []
            ordered_items.append(ordered.group(1))
            i += 1
            continue
        paragraph.append(line.strip())
        i += 1
    flush_paragraph()
    flush_list()
    return "\n".join(output)


def is_table_start(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and lines[index].startswith("|")
        and re.match(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", lines[index + 1])
    )


def table_to_html(lines: list[str], source: Path | None = None) -> str:
    header = split_table_row(lines[0])
    body = [split_table_row(line) for line in lines[2:]]
    head_html = "".join(f"<th>{inline(cell, source)}</th>" for cell in header)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{inline(cell, source)}</td>" for cell in row) + "</tr>"
        for row in body
    )
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{rows_html}</tbody></table>"


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def inline(value: str, source: Path | None = None) -> str:
    escaped = escape(value)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(rewrite_href(match.group(2), source))}">{match.group(1)}</a>',
        escaped,
    )
    return escaped


def rewrite_href(href: str, source: Path | None) -> str:
    if not source or href.startswith(("http://", "https://", "#")):
        return href
    if href.endswith(".md"):
        target = (source.parent / href).resolve()
        try:
            target.relative_to(DOCS.resolve())
        except ValueError:
            return href
        return f"{slug_for(target)}.html"
    return href


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


if __name__ == "__main__":
    main()
