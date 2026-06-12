"""Redaktor-uczeń (Layer 3) — korpus par machine ↔ docx-pass do analizy wzorców.

Skanuje outputs/videos_pl/*/, dla każdego sluga z parą (04_final_machine.md,
fallback 04_final.md  ×  script_corrected.md) paruje zdania logiką
draft_ceiling_report (regex zdań + difflib, próg 0.85) i emituje
.tmp/redaktor_korpus.md: [MOD] (z diffem słów) / [DEL] / [ADD] w kolejności
dokumentu, z sekcją maszyny i tagiem generacji łańcucha. Zero tokenów, zero API.

Usage:
    PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "<slug>"

<slug> = świeżo skorygowany film: walidowany (musi mieć parę); jeśli
docx/script_corrected.docx jest nowszy niż md/script_corrected.md (albo md
brak), najpierw robiona jest ekstrakcja. Korpus ZAWSZE obejmuje wszystkie
slugi z parą.
"""

import argparse
import datetime as dt
import difflib
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.dev.draft_ceiling_report import SIMILAR, sentence_diff_stats, split_sentences
from tools.utils import read_script_docx_text

VIDEOS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "videos_pl"
TMP_DIR = Path(__file__).resolve().parents[2] / ".tmp"


def pair_sentences(ms: list[str], hs: list[str]) -> dict:
    """Greedy best-match jak sentence_diff_stats, ale zwraca pary (indeksy).

    Kontrakt: liczby kubełków identyczne z sentence_diff_stats dla tych samych
    list zdań (test test_pair_sentences_zgodne_z_ceiling_report).
    """
    used: set[int] = set()
    identical: list[tuple[int, int]] = []
    modified: list[tuple[int, int, float]] = []
    for i, m in enumerate(ms):
        best_ratio, best_j = 0.0, -1
        for j, h in enumerate(hs):
            if j in used:
                continue
            r = difflib.SequenceMatcher(None, m, h).ratio()
            if r > best_ratio:
                best_ratio, best_j = r, j
        if best_ratio == 1.0:
            identical.append((i, best_j))
            used.add(best_j)
        elif best_ratio >= SIMILAR:
            modified.append((i, best_j, best_ratio))
            used.add(best_j)
    matched_m = {i for i, _ in identical} | {i for i, _, _ in modified}
    return {
        "identical": identical,
        "modified": modified,
        "deleted": [i for i in range(len(ms)) if i not in matched_m],
        "added": [j for j in range(len(hs)) if j not in used],
    }


def machine_sentences_with_sections(text: str) -> list[tuple[str, str]]:
    """Zdania maszyny z nagłówkiem sekcji `## `, z której pochodzą.

    Tekst przed pierwszą sekcją dostaje etykietę "(otwarcie)". Linie nagłówków
    wycina _narration wewnątrz split_sentences, więc konkatenacja zdań ==
    split_sentences(text) — patrz test zgodności.
    """
    out: list[tuple[str, str]] = []
    header = "(otwarcie)"
    buf: list[str] = []

    def flush() -> None:
        for s in split_sentences("\n".join(buf)):
            out.append((s, header))

    for line in text.splitlines():
        if line.strip().startswith("## "):
            flush()
            header = line.strip()[3:].strip()
            buf = []
        else:
            buf.append(line)
    flush()
    return out


def word_diff(machine: str, human: str) -> str:
    """Diff słowo-po-słowie: [-usunięte-] {+dodane+}."""
    mw, hw = machine.split(), human.split()
    sm = difflib.SequenceMatcher(None, mw, hw)
    parts: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            parts.extend(mw[i1:i2])
        if op in ("delete", "replace"):
            parts.append("[-" + " ".join(mw[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            parts.append("{+" + " ".join(hw[j1:j2]) + "+}")
    return " ".join(parts)


def strip_title(text: str) -> str:
    """Usuwa pierwszą niepustą linię, jeśli wygląda na tytuł (bez interpunkcji
    na końcu). script_corrected.md zaczyna się tytułem bez kropki — bez tego
    doklejałby się do pierwszego zdania i fałszował parę na otwarciu."""
    lines = text.splitlines()
    for k, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or s[-1] in '.!?…"”':
            return text
        return "\n".join(lines[k + 1:])
    return text


def detect_generation(md_dir: Path) -> str:
    """Tag generacji łańcucha /draft, po obecnych plikach snapshotu."""
    if (md_dir / "04_final_machine.md").exists():
        return "gen5"
    if (md_dir / "04_final_presqueeze.md").exists():
        return "sciskacz"
    return "lean"


def corpus_for_pair(pair: dict) -> tuple[str, dict]:
    """Fragment korpusu (md) + statystyki ceiling dla jednej pary slug."""
    machine_text = pair["machine"].read_text(encoding="utf-8")
    human_text = strip_title(pair["human"].read_text(encoding="utf-8"))

    ms_sec = machine_sentences_with_sections(machine_text)
    ms = [s for s, _ in ms_sec]
    hs = split_sentences(human_text)
    res = pair_sentences(ms, hs)
    stats = sentence_diff_stats(machine_text, human_text)

    j2section = {j: ms_sec[i][1] for i, j in res["identical"]}
    j2section.update({j: ms_sec[i][1] for i, j, _r in res["modified"]})
    mod_by_i = {i: j for i, j, _r in res["modified"]}
    deleted = set(res["deleted"])
    added = set(res["added"])

    lines = [
        f"## SLUG: {pair['slug']} [generacja: {pair['generation']}]",
        f"Zdania maszyny: {stats['machine_total']} | identyczne {stats['identical']} | "
        f"MOD {stats['modified']} | DEL {stats['deleted']} | ADD {stats['added']} | "
        f"słowa {stats['machine_words']} -> {stats['human_words']}",
        "",
    ]
    for i, (sent, section) in enumerate(ms_sec):
        if i in mod_by_i:
            j = mod_by_i[i]
            lines += [f"[MOD] (sekcja: {section})", f"  M: {sent}",
                      f"  H: {hs[j]}", f"  D: {word_diff(sent, hs[j])}", ""]
        elif i in deleted:
            lines += [f"[DEL] (sekcja: {section})", f"  M: {sent}", ""]

    last_section = "(otwarcie)"
    for j, h in enumerate(hs):
        if j in j2section:
            last_section = j2section[j]
        elif j in added:
            lines += [f"[ADD] (po sekcji: {last_section})", f"  H: {h}", ""]
    return "\n".join(lines), stats


def find_pairs() -> list[dict]:
    """Wszystkie slugi z parą machine↔human, posortowane po nazwie."""
    pairs = []
    if not VIDEOS_DIR.exists():
        return pairs
    for slug_dir in sorted(p for p in VIDEOS_DIR.iterdir() if p.is_dir()):
        md = slug_dir / "md"
        human = md / "script_corrected.md"
        machine = next(
            (md / n for n in ("04_final_machine.md", "04_final.md")
             if (md / n).exists()), None)
        if machine is not None and human.exists():
            pairs.append({"slug": slug_dir.name, "machine": machine,
                          "human": human, "generation": detect_generation(md)})
    return pairs


def ensure_extracted(slug: str) -> None:
    """docx/script_corrected.docx → md/script_corrected.md, gdy md brak/starszy."""
    base = VIDEOS_DIR / slug
    docx = base / "docx" / "script_corrected.docx"
    md = base / "md" / "script_corrected.md"
    if not docx.exists():
        return
    if md.exists() and md.stat().st_mtime >= docx.stat().st_mtime:
        return
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(read_script_docx_text(docx), encoding="utf-8")
    print(f"  Ekstrakcja: {docx} -> {md}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redaktor-uczeń — korpus par machine↔docx-pass (cały katalog)")
    parser.add_argument("slug", help="świeżo skorygowany slug (walidacja pary)")
    args = parser.parse_args()

    ensure_extracted(args.slug)
    pairs = find_pairs()
    if not any(p["slug"] == args.slug for p in pairs):
        print(f"Error: slug '{args.slug}' nie ma pary machine↔script_corrected — "
              "najpierw docx pass (docx/script_corrected.docx).")
        sys.exit(1)

    header = [
        "# Korpus redakcyjny machine ↔ docx-pass",
        f"Wygenerowano: {dt.date.today().isoformat()} | Slugi z parą: {len(pairs)}",
        "Format: [MOD] zdanie zmienione przez usera (M maszyna / H user / D diff słów)"
        " | [DEL] usunięte w całości | [ADD] dopisane przez usera."
        " Zdania identyczne pominięto.",
        "",
    ]
    frags, trend = [], []
    totals = {"modified": 0, "deleted": 0, "added": 0}
    for pair in pairs:
        frag, stats = corpus_for_pair(pair)
        frags.append(frag)
        for k in totals:
            totals[k] += stats[k]
        trend.append((pair["slug"], pair["generation"], stats["pct_touched"]))

    trend_lines = ["## TREND (ceiling)"] + [
        f"- {s} [{g}]: {pct:.0f}% zdań maszyny dotkniętych" for s, g, pct in trend]

    TMP_DIR.mkdir(exist_ok=True)
    dest = TMP_DIR / "redaktor_korpus.md"
    dest.write_text("\n".join(header + frags + trend_lines) + "\n", encoding="utf-8")

    print(f"Korpus: {dest}")
    print(f"Pary: MOD {totals['modified']} / DEL {totals['deleted']} / "
          f"ADD {totals['added']} ({len(pairs)} slugów)")
    for s, g, pct in trend:
        print(f"  {s} [{g}]: {pct:.0f}% dotkniętych")


if __name__ == "__main__":
    main()
