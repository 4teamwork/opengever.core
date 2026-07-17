#!/usr/bin/env python3
"""Render the Hintergrundtasks project report.

Deterministic renderer for the reporting harness: reads the merged
``report-data.json`` and the mustache-lite template and writes the
self-contained ``report.html``. This is the MECHANICAL half of the pipeline
(SKILL.md Step 6) — the judgment-heavy steps (operator layer, signal gathering,
per-area assessment, merge) stay in the LLM/skill and produce report-data.json.

Template mini-language (see report.html.tmpl header, alongside this script):
  {{path.to.field}}                     scalar substitution (dotted path)
  <!-- REPEAT arr --> … <!-- /REPEAT arr -->   repeat once per array item
  <!-- IF cond --> … <!-- /IF -->       keep block if cond is truthy
  <!-- IF NOT cond --> … <!-- /IF -->   keep block if cond is falsy
  <!-- COMPUTE: … -->                   SVG geometry computed here in Python

Stdlib only (no external deps), Python 3. Fails loudly (raises) if any template
marker or {{token}} survives rendering, so a template change can't silently
produce a broken report.

Usage:
    python3 render_report.py [REPORTING_DIR]   # default: docs/reporting
"""
import io
import json
import os
import re
import sys
from datetime import date

# ── paths ───────────────────────────────────────────────────────────────────
REPORTING_DIR = sys.argv[1] if len(sys.argv) > 1 else "docs/reporting"
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(REPORTING_DIR, "report-data.json")
TMPL_PATH = os.path.join(SKILL_DIR, "report.html.tmpl")
OUT_PATH = os.path.join(REPORTING_DIR, "report.html")

TOKEN = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")

# array path -> loop-variable prefix used inside its REPEAT block
LOOP_SINGULAR = {
    "areas": "area", "stories": "story", "risks": "risk",
    "offene_entscheidungen": "entscheidung",
    "budget.by_week": "week", "budget.by_person": "person",
    "ci.failing": "fail", "ci.trend": "trend", "trajektorie.history": "point",
    "prognose.items": "item",
}


# ── value access & formatting ───────────────────────────────────────────────
def get(path, ctx):
    cur = ctx
    for part in path.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
        if cur is None:
            return None
    return cur


def fmtnum(v):
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return "%.1f" % v if abs(v * 10 - round(v * 10)) < 1e-9 else "%.2f" % v
    return str(v)


def scalar(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return fmtnum(v)
    return str(v)


def truthy(cond, ctx):
    v = get(cond, ctx)
    return len(v) > 0 if isinstance(v, (list, dict)) else bool(v)


# ── substitution ────────────────────────────────────────────────────────────
def subst(text, ctx, loopvar=None, loopitem=None):
    def repl(m):
        path = m.group(1)
        if loopvar and path.split(".")[0] == loopvar:
            rest = path[len(loopvar) + 1:] if "." in path else None
            val = loopitem if rest is None else get(rest, loopitem)
            return scalar(val)
        return scalar(get(path, ctx))
    return TOKEN.sub(repl, text)


def subst_scalar_loop(text, ctx, loopvar, value):
    def repl(m):
        return scalar(value) if m.group(1) == loopvar else scalar(get(m.group(1), ctx))
    return TOKEN.sub(repl, text)


def process_repeats(text, ctx):
    pat = re.compile(
        r"[ \t]*<!-- REPEAT ([a-zA-Z0-9_.]+) -->(.*?)<!-- /REPEAT \1 -->[ \t]*\n?", re.S)
    while True:
        m = pat.search(text)
        if not m:
            return text
        arrpath, body = m.group(1), m.group(2)
        items = get(arrpath, ctx) or []
        lv = LOOP_SINGULAR.get(arrpath, arrpath.split(".")[-1])
        out = []
        for it in items:
            if isinstance(it, dict):
                out.append(subst(body, ctx, lv, it))
            else:  # scalar list (e.g. offene_entscheidungen)
                out.append(subst_scalar_loop(body, ctx, lv, it))
        text = text[:m.start()] + "".join(out) + text[m.end():]


def process_ifs(text, ctx):
    pat_not = re.compile(r"[ \t]*<!-- IF NOT ([a-zA-Z0-9_.]+) -->(.*?)<!-- /IF -->[ \t]*\n?", re.S)
    pat = re.compile(r"[ \t]*<!-- IF ([a-zA-Z0-9_.]+) -->(.*?)<!-- /IF -->[ \t]*\n?", re.S)
    while True:
        m = pat_not.search(text)
        if m:
            keep = "" if truthy(m.group(1), ctx) else m.group(2)
            text = text[:m.start()] + keep + text[m.end():]
            continue
        m = pat.search(text)
        if m:
            keep = m.group(2) if truthy(m.group(1), ctx) else ""
            text = text[:m.start()] + keep + text[m.end():]
            continue
        return text


def replace_between(text, start_marker, end_marker, replacement):
    i = text.find(start_marker)
    if i == -1:
        raise AssertionError("start marker not found: %s" % start_marker)
    j = text.find(end_marker, i)
    if j == -1:
        raise AssertionError("end marker not found after start: %s" % end_marker)
    return text[:i] + replacement + text[j + len(end_marker):]


# ── SVG geometry (the COMPUTE blocks) ───────────────────────────────────────
def parse_de(s):
    d, m, y = s.split(".")
    return date(int(y), int(m), int(d))


def budget_bars_svg(data):
    weeks = data["budget"]["by_week"]
    n = len(weeks)
    slot = 1000.0 / n
    barw = slot / 2.0
    maxat = max((w["ist_at"] for w in weeks), default=1.0) or 1.0
    max_h = 140.0
    bars = []
    for i, w in enumerate(weeks):
        h = w["ist_at"] / maxat * max_h
        x = i * slot + (slot - barw) / 2.0
        bars.append(
            '<rect class="bar-el" data-tip="%s|%s AT" x="%.1f" y="%.1f" '
            'width="%.1f" height="%.1f"></rect>'
            % (w["week"], fmtnum(w["ist_at"]), x, 159.0 - h, barw, h))
    return ('<svg width="100%" height="160" viewBox="0 0 1000 160" preserveAspectRatio="none">\n'
            '        <line class="axis zero" x1="0" y1="159" x2="1000" y2="159"/>\n        '
            + "\n        ".join(bars) + "\n      </svg>")


def ci_spark_svg(data):
    trend = data["ci"]["trend"]

    def y_of(p):
        return max(10.0, min(80.0, 80.0 - (p / 100.0) * 60.0))

    if len(trend) >= 2:
        step = 1000.0 / (len(trend) - 1)
        pts = [(i * step, y_of(t["pass_rate_pct"])) for i, t in enumerate(trend)]
        path = '<path class="proj-line" d="M%s"></path>' % " L".join("%.1f,%.1f" % p for p in pts)
        cx, cy = pts[-1]
        marker = ('\n        <circle class="hist-pt" r="4" cx="%.1f" cy="%.1f" '
                  'data-tip="%s · %s %%"></circle>'
                  % (cx, cy, trend[-1]["date_de"], fmtnum(trend[-1]["pass_rate_pct"])))
    else:
        t = trend[0]
        path = ('<circle class="hist-pt" r="4" cx="500" cy="%.1f" data-tip="%s · %s %%"></circle>'
                % (y_of(t["pass_rate_pct"]), t["date_de"], fmtnum(t["pass_rate_pct"])))
        marker = ""
    return ('<svg width="100%" height="90" viewBox="0 0 1000 90" preserveAspectRatio="none">\n'
            '        <line class="axis zero" x1="0" y1="89" x2="1000" y2="89"/>\n        '
            + path + marker + "\n      </svg>")


def trajectory_svg(data):
    traj = data["trajektorie"]
    hist = traj["history"]
    start = parse_de(traj["ideal"]["start_date_de"])
    target = parse_de(traj["target_date_de"])
    stretch = parse_de(traj["stretch_date_de"]) if traj.get("stretch_date_de") else None
    end = max(d for d in (target, stretch) if d is not None)
    span = (end - start).days or 1

    def tx(dd):
        return (dd - start).days / float(span) * 1000.0

    def ty(pct):
        return 200.0 - pct / 100.0 * 180.0

    ideal_x2 = tx(target)
    ideal_line = ('<line class="ideal-line" x1="0.0" y1="200.0" x2="%.1f" y2="20.0" '
                  'data-tip="Ideal|%s bis %s"></line>'
                  % (ideal_x2, traj["ideal"]["start_date_de"], traj["ideal"]["target_date_de"]))
    ideal_label = '<text class="ideal-label" x="%.1f" y="16" text-anchor="end">Ideal</text>' % min(ideal_x2, 994)

    pts = [(tx(parse_de(h["date_de"])), ty(h["overall_progress_pct"])) for h in hist]
    proj_line = '<path class="proj-line" d="M%s"></path>' % " L".join("%.1f,%.1f" % p for p in pts)
    circles = "\n      ".join(
        '<circle class="hist-pt" r="4" cx="%.1f" cy="%.1f" data-tip="%s · %s %%"></circle>'
        % (cx, cy, h["date_de"], fmtnum(h["overall_progress_pct"]))
        for h, (cx, cy) in zip(hist, pts))

    today_x = tx(parse_de(data["meta"]["report_date_de"]))
    tgt_x = tx(target)
    markers = (
        '<line class="marker-line" x1="%.1f" y1="20" x2="%.1f" y2="200" data-tip="Heute|%s"></line>\n'
        '      <text class="marker-label" x="%.1f" y="214" text-anchor="middle">HEUTE</text>\n\n'
        '      <line class="marker-line" x1="%.1f" y1="20" x2="%.1f" y2="200" data-tip="Zieltermin|%s"></line>\n'
        '      <text class="marker-label" x="%.1f" y="214" text-anchor="end">ZIELTERMIN %s</text>'
        % (today_x, today_x, data["meta"]["report_date_de"], today_x,
           tgt_x, tgt_x, traj["target_date_de"], min(tgt_x, 994), traj["target_date_de"]))
    if stretch is not None:
        st_x = tx(stretch)
        markers += (
            '\n\n      <line class="marker-line stretch" x1="%.1f" y1="20" x2="%.1f" y2="200" '
            'data-tip="Streckungsende|%s"></line>\n'
            '      <text class="marker-label" x="%.1f" y="228" text-anchor="end" '
            'style="fill:var(--tl-gelbrot)">STRECKUNGSENDE %s</text>'
            % (st_x, st_x, traj["stretch_date_de"], min(st_x, 998), traj["stretch_date_de"]))

    return ('''<svg width="100%" height="230" viewBox="0 0 1000 230" preserveAspectRatio="none">
      <line class="axis" x1="0" y1="20"  x2="1000" y2="20"/>
      <text x="994" y="16" text-anchor="end">100 %</text>
      <line class="axis" x1="0" y1="65"  x2="1000" y2="65"/>
      <text x="994" y="61" text-anchor="end">75 %</text>
      <line class="axis" x1="0" y1="110" x2="1000" y2="110"/>
      <text x="994" y="106" text-anchor="end">50 %</text>
      <line class="axis" x1="0" y1="155" x2="1000" y2="155"/>
      <text x="994" y="151" text-anchor="end">25 %</text>
      <line class="axis zero" x1="0" y1="200" x2="1000" y2="200"/>
      <text x="994" y="196" text-anchor="end">0 %</text>

      ''' + ideal_line + "\n      " + ideal_label + "\n\n      " + proj_line + "\n      "
            + circles + "\n\n      " + markers + "\n    </svg>")


# ── minimal markdown (bullets + **bold**) -> HTML, for prose fields ──────────
def md_inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def md_to_html(text):
    lines = text.strip("\n").split("\n")
    out, in_list = [], False
    for raw in lines:
        line = raw.strip()
        is_bullet = line.startswith("- ") or line.startswith("* ")
        if is_bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>%s</li>" % md_inline(line[2:].strip()))
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if line:
                out.append("<p>%s</p>" % md_inline(line))
    if in_list:
        out.append("</ul>")
    return "".join(out)


# ── main ────────────────────────────────────────────────────────────────────
def render():
    data = json.load(io.open(DATA_PATH, encoding="utf-8"))
    tmpl = io.open(TMPL_PATH, encoding="utf-8").read()

    # summary_de is operator-written plain Markdown (bullets + **bold**) — the
    # renderer, not status.md, owns turning it into HTML.
    if data.get("summary_de"):
        data["summary_de"] = md_to_html(data["summary_de"])

    # Strip the leading convention comment block.
    tmpl = re.sub(r"<!--\s*\n\s*═+.*?══════\n-->", "", tmpl, count=1, flags=re.S)

    # Strip COMPUTE/label helper comments BEFORE the SVG swaps: some COMPUTE
    # comments contain the literal "<svg width=… height=…>" string on one line,
    # which would otherwise make replace_between match inside the comment.
    tmpl = re.sub(r"[ \t]*<!-- COMPUTE:.*?-->[ \t]*\n?", "", tmpl, flags=re.S)
    tmpl = re.sub(r"[ \t]*<!-- label:.*?-->[ \t]*\n?", "", tmpl, flags=re.S)

    # Swap the empty SVG scaffolds for computed geometry.
    tmpl = replace_between(tmpl, '<svg width="100%" height="160" viewBox="0 0 1000 160"',
                           '</svg>', budget_bars_svg(data))
    tmpl = replace_between(tmpl, '<svg width="100%" height="90" viewBox="0 0 1000 90"',
                           '</svg>', ci_spark_svg(data))
    tmpl = replace_between(tmpl, '<svg width="100%" height="230" viewBox="0 0 1000 230"',
                           '</svg>', trajectory_svg(data))

    # Loops, conditionals, then scalar tokens.
    tmpl = process_repeats(tmpl, data)
    tmpl = process_ifs(tmpl, data)
    tmpl = subst(tmpl, data)

    # Fail loudly if anything was left unrendered.
    leftover = re.findall(r"<!-- (?:REPEAT|/REPEAT|IF|/IF|COMPUTE)[^>]*-->", tmpl)
    tokens = TOKEN.findall(tmpl)
    if leftover or tokens:
        raise SystemExit("Unrendered content remains: markers=%r tokens=%r"
                         % (leftover[:5], tokens[:5]))

    io.open(OUT_PATH, "w", encoding="utf-8").write(tmpl)
    print("Rendered %s (%d chars)" % (OUT_PATH, len(tmpl)))


if __name__ == "__main__":
    render()
