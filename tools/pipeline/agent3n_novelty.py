"""
Agent 3-Novelty: Catch and rewrite phrase/structural reuse from prior scripts.

Sits between Agent 3a (Draft) and Agent 3b (Critic). Compares the new draft
(md/03a_draft.md) against every prior shipped narration in the corpus
(outputs/*/md/06_script_narration.md, excluding the current slug) and:

  Pass A — deterministic 4-token n-gram match (Python, no API cost)
  Pass B — Claude semantic / structural check (paraphrased reuse, reused
           metaphor templates, reused opening/closing formulas)
  Pass C — if anything flagged, Claude rewrites ONLY the flagged spans and
           the agent re-runs Pass A. Iterates up to MAX_ATTEMPTS times.

Overwrites md/03a_draft.md with the deduped draft. Preserves the original
once as md/03a_draft.bak.md.

Chain: 3a -> 3n -> 3b -> 3c -> 4a -> 4b -> record

Usage:
    python tools/agent3n_novelty.py "the-grief-for-the-versions-of-you-that-didn-t-happen"
"""

import json
import re
import sys
import os
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, query_claude, log_cost

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRAFT_FILENAME = "md/03a_draft.md"
BACKUP_FILENAME = "md/03a_draft.bak.md"
REPORT_FILENAME = "md/03_novelty_report.md"
CORPUS_GLOB = "*/md/06_script_narration.md"

CLAUDE_MODEL = "claude-sonnet-4-6"
NGRAM_SIZE = 4
MAX_ATTEMPTS = 3
MAX_LITERAL_SPANS_IN_PROMPT = 25
MAX_SEMANTIC_SPANS_IN_PROMPT = 15

# Stop words: 4-grams composed only of these are skipped (too common, low signal).
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "am",
    "of", "in", "on", "at", "to", "for", "with", "by", "from", "into", "onto",
    "and", "or", "but", "so", "yet", "as", "if", "than", "then", "though",
    "this", "that", "these", "those", "it", "its", "itself",
    "he", "him", "his", "she", "her", "hers", "you", "your", "yours",
    "i", "me", "my", "mine", "we", "our", "ours", "us", "they", "them", "their",
    "do", "does", "did", "doing", "done",
    "have", "has", "had", "having",
    "will", "would", "can", "could", "should", "may", "might", "must", "shall",
    "not", "no", "nor", "yes", "all", "some", "any", "more", "most", "much",
    "many", "very", "just", "only", "even", "still", "ever", "never",
    "what", "when", "where", "why", "how", "who", "which", "whom", "whose",
    "there", "here", "now", "today",
}

# Lines we skip as metadata when extracting narration-only text.
_META_LINE_PATTERNS = [
    re.compile(r"^\s*#"),
    re.compile(r"^\s*Generated:", re.I),
    re.compile(r"^\s*Model:", re.I),
    re.compile(r"^\s*Pass:", re.I),
    re.compile(r"^\s*Estimated duration:", re.I),
    re.compile(r"^\s*Source:", re.I),
    re.compile(r"^\s*ARCHITECTURE:", re.I),
    re.compile(r"^\s*-{3,}\s*$"),
    re.compile(r"^\s*\[Visual Pause\]\s*$", re.I),
]

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+")

# ---------------------------------------------------------------------------
# Tokenization & narration extraction
# ---------------------------------------------------------------------------


def _is_meta_line(line: str) -> bool:
    return any(p.search(line) for p in _META_LINE_PATTERNS)


def _strip_inline_markers(text: str) -> str:
    text = re.sub(r"\[EDITOR NOTE:[^\]]*\]", "", text)
    text = re.sub(r"\[IMAGE:[^\]]*\]", "", text)
    text = re.sub(r"\[Visual Pause\]", "", text, flags=re.I)
    return text


def extract_narration(script: str) -> str:
    """Return narration body with metadata lines removed."""
    out_lines = []
    for line in script.splitlines():
        if _is_meta_line(line):
            continue
        out_lines.append(line)
    return _strip_inline_markers("\n".join(out_lines))


def find_intra_script_duplicates(narration: str) -> list[dict]:
    """Return sentences appearing verbatim (normalized) 2+ times in the same narration.

    Each result: { "text": str, "line": int, "first_occurrence_line": int }
    Only the second+ occurrence is reported; the first is considered authoritative.
    Sentences shorter than 5 words are skipped (too short to be meaningful duplicates).
    """
    occurrences: dict[str, list[dict]] = {}
    for m in _SENTENCE_RE.finditer(narration):
        text = m.group(0).strip()
        if len(text.split()) < 5:
            continue
        normalized = re.sub(r"[^\w\s]", "", text.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if not normalized:
            continue
        entry = {"text": text, "line": _line_of(narration, m.start())}
        occurrences.setdefault(normalized, []).append(entry)

    duplicates = []
    for occ_list in occurrences.values():
        if len(occ_list) >= 2:
            for occ in occ_list[1:]:
                duplicates.append({
                    "text": occ["text"],
                    "line": occ["line"],
                    "first_occurrence_line": occ_list[0]["line"],
                })
    return duplicates


def _intra_duplicates_to_semantic_findings(dupes: list[dict]) -> list[dict]:
    """Convert intra-script duplicates into the semantic_findings dict format for Pass C."""
    findings = []
    for d in dupes:
        findings.append({
            "span_in_new_script": d["text"],
            "type": "intra-script-duplicate",
            "similar_to_in_corpus": d["text"],
            "source_slug": f"[same script — first at line {d['first_occurrence_line']}]",
            "why": (
                f"Exact duplicate: appears at line {d['first_occurrence_line']} and again at "
                f"line {d['line']}. Remove or substantially vary this second occurrence."
            ),
        })
    return findings


def tokenize(text: str) -> list[tuple[str, int]]:
    """Tokenize to (lowercase_token, char_offset) pairs."""
    tokens = []
    for m in _TOKEN_RE.finditer(text):
        tokens.append((m.group(0).lower(), m.start()))
    return tokens


def all_stopwords(tokens: list[str]) -> bool:
    return all(t in STOPWORDS for t in tokens)


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    return Path(__file__).parent.parent.parent


def load_corpus(current_slug: str) -> list[tuple[str, str]]:
    """Return list of (slug, narration_text) for every prior shipped script
    except the current slug. Empty list if no prior scripts exist."""
    root = _project_root() / "outputs" / "videos_pl"
    corpus = []
    for path in sorted(root.glob(CORPUS_GLOB)):
        slug = path.parent.parent.name
        if slug == current_slug:
            continue
        text = path.read_text(encoding="utf-8")
        corpus.append((slug, extract_narration(text)))
    return corpus


# ---------------------------------------------------------------------------
# Pass A — 4-gram literal match
# ---------------------------------------------------------------------------


def _line_of(text: str, char_offset: int) -> int:
    return text.count("\n", 0, char_offset) + 1


def build_corpus_ngrams(corpus: list[tuple[str, str]]) -> dict[tuple, tuple[str, int]]:
    """Map every significant 4-gram in the corpus to (source_slug, source_line)
    of its first occurrence."""
    out: dict[tuple, tuple[str, int]] = {}
    for slug, text in corpus:
        toks = tokenize(text)
        for i in range(len(toks) - NGRAM_SIZE + 1):
            window = [toks[i + j][0] for j in range(NGRAM_SIZE)]
            if all_stopwords(window):
                continue
            key = tuple(window)
            if key not in out:
                out[key] = (slug, _line_of(text, toks[i][1]))
    return out


def find_literal_matches(
    draft_narration: str,
    corpus_ngrams: dict[tuple, tuple[str, int]],
) -> list[dict]:
    """Return greedy-merged duplicate spans in draft. Each span:
        { "text": str, "draft_line": int, "source_slug": str, "source_line": int }
    """
    toks = tokenize(draft_narration)
    matches: list[dict] = []  # (start_tok_idx, end_tok_idx_exclusive, source)
    i = 0
    while i <= len(toks) - NGRAM_SIZE:
        window = tuple(toks[i + j][0] for j in range(NGRAM_SIZE))
        if all_stopwords(window) or window not in corpus_ngrams:
            i += 1
            continue
        source = corpus_ngrams[window]
        # Greedy-extend: while next position also matches the corpus, extend.
        end = i + NGRAM_SIZE
        while end - NGRAM_SIZE + 1 < len(toks) - NGRAM_SIZE + 1:
            next_window = tuple(toks[end - NGRAM_SIZE + 1 + j][0] for j in range(NGRAM_SIZE))
            if all_stopwords(next_window) or next_window not in corpus_ngrams:
                break
            end += 1
        # Slice the original text from start char to end char
        start_char = toks[i][1]
        # End char = end of last token in the span
        last_tok_idx = end - 1
        last_tok_text, last_tok_start = toks[last_tok_idx]
        end_char = last_tok_start + len(last_tok_text)
        span_text = draft_narration[start_char:end_char]
        matches.append({
            "text": span_text.strip(),
            "draft_line": _line_of(draft_narration, start_char),
            "source_slug": source[0],
            "source_line": source[1],
            "token_count": end - i,
        })
        i = end  # skip past matched span
    return matches


# ---------------------------------------------------------------------------
# Pass B — Claude semantic check
# ---------------------------------------------------------------------------

SEMANTIC_PROMPT_TEMPLATE = """\
Jesteś audytorem nowości dla polskiego kanału psychologicznego YouTube SENSUM. Twoje zadanie to flagowanie reuse treści między NOWYM szkicem skryptu a KORPUSEM wcześniej shippniętych skryptów. Osobny pass n-gramowy już złapał dosłowne powtórzenia (są wymienione poniżej); Twoje zadanie to złapać to co umknęło.

**Skrypty i korpus są po polsku. Twoja analiza również po polsku (JSON values po polsku).**

Flaguj TYLKO te formy reuse:
  - paraphrase: zdanie lub fraza której słownictwo się różni ale której
    funkcja i konkretne obrazowanie duplikuje zdanie z korpusu
    (np. "Dzisiaj robimy sekcję zwłok tej żałoby" vs
    "Dzisiaj przeprowadzamy autopsję tego uczucia")
  - metaphor: ten sam wzorzec metafory wyjaśniającej się powtarza
    (np. "twój mózg traktuje X jak Y" gdzie Y jest reused vehicle)
  - structure: wielo-zdaniowe otwarcie lub zamknięcie podąża za tym samym
    wzorcem beatów co opener/closer z korpusu (szczegół sensoryczny -> wyzwalacz
    czasowy -> nazwanie uczucia; lub pozwolenie -> akcja -> forward image)

NIE flaguj:
  - generycznego języka psychologicznego (np. "mózg", "ciało", "układ nerwowy")
  - fragmentów krótszych niż 6 słów
  - czegokolwiek co po prostu używa tego samego konceptu psychologicznego
    (koncepty mają się powtarzać — tylko SŁOWNICTWO/FRAMING jest problemem)

Dla każdego findingu, zwróć obiekt JSON z:
  "span_in_new_script": dokładny span jak pojawia się w nowym szkicu
  "type": jeden z "paraphrase" | "metaphor" | "structure"
  "similar_to_in_corpus": krótki cytat z korpusu który echo
  "source_slug": slug korpusu z którego pochodzi
  "why": jedno krótkie zdanie po polsku

Zwróć tablicę JSON (potencjalnie pustą). Zwróć WYŁĄCZNIE JSON, bez preambuły.

# Literal duplicates already caught (do NOT re-list these)
{literal_summary}

# NEW DRAFT
{new_draft}

# CORPUS (each prior shipped narration, with slug header)
{corpus_dump}
"""


def _format_literal_for_prompt(matches: list[dict]) -> str:
    if not matches:
        return "(none)"
    lines = []
    for m in matches[:MAX_LITERAL_SPANS_IN_PROMPT]:
        lines.append(f'- "{m["text"]}" (from {m["source_slug"]})')
    if len(matches) > MAX_LITERAL_SPANS_IN_PROMPT:
        lines.append(f"- ... ({len(matches) - MAX_LITERAL_SPANS_IN_PROMPT} more omitted)")
    return "\n".join(lines)


def _format_corpus_for_prompt(corpus: list[tuple[str, str]]) -> str:
    parts = []
    for slug, text in corpus:
        parts.append(f"## {slug}\n\n{text.strip()}")
    return "\n\n---\n\n".join(parts)


def run_semantic_check(
    new_draft_narration: str,
    corpus: list[tuple[str, str]],
    literal_matches: list[dict],
    slug: str,
) -> tuple[list[dict], dict]:
    """Call Claude for paraphrase/metaphor/structure reuse. Returns (findings, usage)."""
    prompt = SEMANTIC_PROMPT_TEMPLATE.format(
        literal_summary=_format_literal_for_prompt(literal_matches),
        new_draft=new_draft_narration,
        corpus_dump=_format_corpus_for_prompt(corpus),
    )
    response, usage = query_claude(prompt, CLAUDE_MODEL, 4096, "novelty semantic check")
    findings = _parse_json_array(response)
    return findings, usage


def _parse_json_array(text: str) -> list[dict]:
    """Tolerant JSON-array extraction from a Claude response."""
    # Strip code fences if present
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
    if fenced:
        candidate = fenced.group(1)
    else:
        # Find the first [...] block
        bracket = re.search(r"\[\s*(?:\{.*?\}\s*,?\s*)*\]", text, re.S)
        candidate = bracket.group(0) if bracket else "[]"
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass
    return []


# ---------------------------------------------------------------------------
# Pass C — Claude rewrite
# ---------------------------------------------------------------------------

REWRITE_PROMPT_TEMPLATE = """\
Rewizjujesz polski skrypt psychologiczny YouTube SENSUM żeby usunąć reuse treści ze wcześniejszych skryptów kanału. Szkic poniżej zawiera spany flagowane jako duplikaty wcześniejszych skryptów. Przepisz TYLKO flagowane spany. Nie ruszaj nieflagowanych pasaży. Zachowaj voice skryptu, architekturę, podziały akapitów, markery [Visual Pause] i całkowitą długość.

**Skrypt jest po polsku. Output również po polsku.**

Ograniczenia przy przepisywaniu flagowanego span:
  - Zamień dokładne słownictwo na nowe które pełni tę samą funkcję narracyjną.
    NIE tasuj słów ani nie podmieniaj synonimów.
  - Jeśli flagowany span to metafora, zmień na zupełnie inny konkretny vehicle
    (nie używaj tego samego wzorca metafory z nowymi słowami).
  - Jeśli flagowany span to wzorzec strukturalny otwarcia/zamknięcia, zmień
    KOLEJNOŚĆ beatów lub zamień jeden beat całkowicie.
  - Zachowaj te same twierdzenia faktyczne (to kanał naukowy).
  - Bez cytatów inline, bez nazwisk badaczy, bez zbanowanego language
    research-framingowego ("badania pokazują", "naukowcy odkryli"), bez
    polskich cringe self-help fraz ("po prostu BĄDŹ", "zaufaj procesowi"),
    bez polskich academic-textbookowych fraz ("warto zauważyć", "kluczowe jest").

# Literal duplicate spans (4+ token n-gram matches against corpus)
{literal_block}

# Semantic / structural duplicate spans (Claude-flagged)
{semantic_block}

# Full draft to revise
{draft}

Zwróć PEŁEN zrewidowany szkic i NIC WIĘCEJ. Nie dodawaj preambuły. Nie owijaj w code fences. Zachowaj nagłówek metadata (linie zaczynające się od # Script Draft:, Generated:, Model:, Pass:, Estimated duration: i separator ---) bajt-po-bajcie jeśli obecny w inputcie.
"""


def _format_literal_block(matches: list[dict]) -> str:
    if not matches:
        return "(none)"
    lines = []
    for m in matches:
        lines.append(
            f'- SPAN: "{m["text"]}"\n  COLLIDES WITH: {m["source_slug"]} (line {m["source_line"]})'
        )
    return "\n".join(lines)


def _format_semantic_block(findings: list[dict]) -> str:
    if not findings:
        return "(none)"
    lines = []
    for f in findings[:MAX_SEMANTIC_SPANS_IN_PROMPT]:
        span = f.get("span_in_new_script", "").strip()
        kind = f.get("type", "?")
        similar = f.get("similar_to_in_corpus", "").strip()
        source = f.get("source_slug", "?")
        why = f.get("why", "").strip()
        lines.append(
            f'- TYPE: {kind}\n  SPAN: "{span}"\n  ECHOES: "{similar}" (from {source})\n  REASON: {why}'
        )
    return "\n".join(lines)


def run_rewrite(
    draft_full: str,
    literal_matches: list[dict],
    semantic_findings: list[dict],
) -> tuple[str, dict]:
    prompt = REWRITE_PROMPT_TEMPLATE.format(
        literal_block=_format_literal_block(literal_matches),
        semantic_block=_format_semantic_block(semantic_findings),
        draft=draft_full,
    )
    return query_claude(prompt, CLAUDE_MODEL, 8192, "novelty rewrite")


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------


def _ensure_backup(slug: str, original_content: str) -> bool:
    try:
        read_output(slug, BACKUP_FILENAME)
        return False
    except FileNotFoundError:
        write_output(slug, BACKUP_FILENAME, original_content)
        return True


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def _format_iteration_log(
    attempt: int,
    literal_matches: list[dict],
    semantic_findings: list[dict],
    rewrite_applied: bool,
) -> str:
    parts = [f"## Attempt {attempt}"]
    parts.append(f"- Literal duplicate spans: **{len(literal_matches)}**")
    parts.append(f"- Semantic / structural findings: **{len(semantic_findings)}**")
    parts.append(f"- Rewrite applied: **{'yes' if rewrite_applied else 'no'}**")
    parts.append("")

    if literal_matches:
        parts.append("### Literal duplicates")
        parts.append("")
        for m in literal_matches:
            parts.append(
                f'- _"{m["text"]}"_ — collides with `{m["source_slug"]}` (line {m["source_line"]}), '
                f'draft line {m["draft_line"]}, {m["token_count"]} tokens'
            )
        parts.append("")

    if semantic_findings:
        parts.append("### Semantic / structural findings")
        parts.append("")
        for f in semantic_findings:
            span = f.get("span_in_new_script", "").strip()
            kind = f.get("type", "?")
            similar = f.get("similar_to_in_corpus", "").strip()
            source = f.get("source_slug", "?")
            why = f.get("why", "").strip()
            parts.append(
                f'- **{kind}** — _"{span}"_  echoes _"{similar}"_ in `{source}` — {why}'
            )
        parts.append("")

    parts.append("---\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python tools/agent3n_novelty.py "<slug>"')
        print('Example: python tools/agent3n_novelty.py "emotional-dysregulation-in-adhd"')
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print("\n=== Agent 3-Novelty: Phrase & Structure De-duplication ===")
    print(f"Slug : {slug}\n")

    # [1/6] Load draft
    print(f"[1/6] Reading {DRAFT_FILENAME}...")
    try:
        draft_full = read_output(slug, DRAFT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3a first:")
        print(f'  python tools/agent3a_draft.py "{slug}"')
        sys.exit(1)
    print(f"  Draft length: {len(draft_full):,} characters")

    backup_created = _ensure_backup(slug, draft_full)
    if backup_created:
        print(f"  Backup created: {BACKUP_FILENAME}")
    else:
        print(f"  Backup already exists: {BACKUP_FILENAME} (preserved)")

    # [2/6] Pass 0 — Intra-Script Sentence Dedup
    print(f"\n[2/6] Pass 0 — Intra-Script Sentence Dedup...")
    pass0_narration = extract_narration(draft_full)
    intra_dupes = find_intra_script_duplicates(pass0_narration)
    pass0_found = len(intra_dupes)
    pass0_resolved = 0

    if not intra_dupes:
        print("  No intra-script duplicate sentences found.")
    else:
        print(f"  Found {pass0_found} duplicate sentence(s):")
        for d in intra_dupes:
            print(f'    - "{d["text"][:80]}" (lines {d["first_occurrence_line"]} and {d["line"]})')
        print("  Running Pass C rewrite to resolve...")
        intra_findings = _intra_duplicates_to_semantic_findings(intra_dupes)
        try:
            revised, _usage0 = run_rewrite(draft_full, [], intra_findings)
            if revised.strip() and len(revised) >= 0.6 * len(draft_full):
                draft_full = revised
                write_output(slug, DRAFT_FILENAME, draft_full)
                pass0_resolved = pass0_found
                print(f"  Rewrite applied. Updated {DRAFT_FILENAME} ({len(draft_full):,} chars).")
            else:
                print(f"  Warning: rewrite output too short ({len(revised):,} chars). Not applied.")
        except Exception as exc:
            print(f"  Warning: Pass 0 rewrite failed ({exc}). Continuing.")

    # [3/6] Load corpus
    print(f"\n[3/6] Loading corpus (excluding current slug)...")
    corpus = load_corpus(slug)
    if not corpus:
        print("  No prior scripts found. Nothing to compare against.")
        report = (
            f"# Novelty Report\n"
            f"Generated: {date.today().isoformat()}\n"
            f"Slug: {slug}\n\n"
            f"## Pass 0 — Intra-Script Duplicates\n\n"
            f"Found: {pass0_found} | Resolved: {pass0_resolved}\n\n"
            f"## Verdict: SKIPPED\n\n"
            f"No prior shipped narrations found in `outputs/*/md/06_script_narration.md`.\n"
            f"This is the first video in the channel, or all other outputs are still in progress.\n"
        )
        write_output(slug, REPORT_FILENAME, report)
        print(f"  Report saved: {REPORT_FILENAME}")
        print("\nDone. Proceeding to Agent 3b will read the unmodified draft.")
        return
    print(f"  Corpus loaded: {len(corpus)} prior narration(s)")
    for s, t in corpus:
        print(f"    - {s} ({len(t):,} chars)")

    # [4/6] Build n-gram index
    corpus_ngrams = build_corpus_ngrams(corpus)
    print(f"\n[4/6] Built corpus n-gram index: {len(corpus_ngrams):,} significant 4-grams")

    iteration_logs: list[str] = []
    rewrites_applied = 0
    total_usage = {"input_tokens": 0, "output_tokens": 0}
    final_literal: list[dict] = []
    final_semantic: list[dict] = []

    current_draft = draft_full

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n[5/6] Attempt {attempt}/{MAX_ATTEMPTS}")

        # Pass A
        draft_narration = extract_narration(current_draft)
        literal_matches = find_literal_matches(draft_narration, corpus_ngrams)
        print(f"  Pass A (literal 4-grams): {len(literal_matches)} duplicate span(s)")
        for m in literal_matches[:5]:
            print(f"    - \"{m['text']}\" <- {m['source_slug']}")
        if len(literal_matches) > 5:
            print(f"    ... ({len(literal_matches) - 5} more)")

        # Pass B
        print(f"  Pass B (semantic / structural): calling Claude...")
        try:
            semantic_findings, b_usage = run_semantic_check(
                draft_narration, corpus, literal_matches, slug
            )
        except Exception as exc:
            print(f"  Warning: semantic check failed ({exc}). Continuing with literal only.")
            semantic_findings = []
            b_usage = {"input_tokens": 0, "output_tokens": 0}
        total_usage["input_tokens"] += b_usage.get("input_tokens", 0)
        total_usage["output_tokens"] += b_usage.get("output_tokens", 0)
        print(f"  Pass B: {len(semantic_findings)} additional finding(s)")
        for f in semantic_findings[:5]:
            kind = f.get("type", "?")
            span = f.get("span_in_new_script", "").strip()
            print(f"    - [{kind}] \"{span[:80]}\"")
        if len(semantic_findings) > 5:
            print(f"    ... ({len(semantic_findings) - 5} more)")

        final_literal = literal_matches
        final_semantic = semantic_findings

        if not literal_matches and not semantic_findings:
            print("  Both passes clean. Stopping.")
            iteration_logs.append(_format_iteration_log(attempt, [], [], False))
            break

        if attempt == MAX_ATTEMPTS:
            iteration_logs.append(_format_iteration_log(attempt, literal_matches, semantic_findings, False))
            print(f"  Reached MAX_ATTEMPTS={MAX_ATTEMPTS} with residual findings. Stopping.")
            break

        # Pass C — rewrite
        print(f"  Pass C (rewrite): calling Claude...")
        try:
            revised, c_usage = run_rewrite(current_draft, literal_matches, semantic_findings)
        except Exception as exc:
            print(f"  Error: rewrite failed ({exc}). Stopping with current draft.")
            iteration_logs.append(_format_iteration_log(attempt, literal_matches, semantic_findings, False))
            break
        total_usage["input_tokens"] += c_usage.get("input_tokens", 0)
        total_usage["output_tokens"] += c_usage.get("output_tokens", 0)

        if not revised.strip() or len(revised) < 0.6 * len(current_draft):
            print(f"  Warning: rewrite returned suspiciously short output "
                  f"({len(revised):,} vs {len(current_draft):,} chars). Not applying.")
            iteration_logs.append(_format_iteration_log(attempt, literal_matches, semantic_findings, False))
            break

        current_draft = revised
        write_output(slug, DRAFT_FILENAME, current_draft)
        rewrites_applied += 1
        print(f"  Rewrite applied. Updated {DRAFT_FILENAME} ({len(current_draft):,} chars).")
        iteration_logs.append(_format_iteration_log(attempt, literal_matches, semantic_findings, True))

    # Step 4 — Verdict
    if not final_literal and not final_semantic:
        verdict = "PASS" if rewrites_applied == 0 else "PASS_AFTER_REWRITE"
    else:
        verdict = "RESIDUAL_AFTER_3_ATTEMPTS"

    print(f"\n[6/6] Verdict: {verdict}")
    print(f"  Rewrites applied: {rewrites_applied}")
    print(f"  Residual literal duplicates: {len(final_literal)}")
    print(f"  Residual semantic findings: {len(final_semantic)}")

    # Step 5 — Write report
    today = date.today().isoformat()
    report = (
        f"# Novelty Report\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Slug: {slug}\n"
        f"Corpus: {len(corpus)} prior narration(s)\n"
        f"Draft: {DRAFT_FILENAME}\n"
        f"Backup: {BACKUP_FILENAME}\n\n"
        f"## Pass 0 — Intra-Script Duplicates\n\n"
        f"Found: {pass0_found} | Resolved: {pass0_resolved}\n\n"
        f"---\n\n"
        f"## Summary\n\n"
        f"- Verdict: **{verdict}**\n"
        f"- Rewrites applied: **{rewrites_applied}**\n"
        f"- Residual literal duplicate spans: **{len(final_literal)}**\n"
        f"- Residual semantic / structural findings: **{len(final_semantic)}**\n\n"
        f"---\n\n"
        + "\n".join(iteration_logs)
    )
    write_output(slug, REPORT_FILENAME, report)
    print(f"  Report saved: {REPORT_FILENAME}")

    log_cost(slug, "3-novelty", {
        "model": CLAUDE_MODEL,
        "input_tokens": total_usage["input_tokens"],
        "output_tokens": total_usage["output_tokens"],
        "rewrites_applied": rewrites_applied,
        "verdict": verdict,
    })

    if verdict.startswith("PASS"):
        print("\nNext: proceed to Agent 3b.")
    else:
        print("\nWarning: residual duplicates remain after 3 rewrite attempts.")
        print("         Inspect md/03_novelty_report.md and consider manual edit before Agent 3b.")


if __name__ == "__main__":
    main()
