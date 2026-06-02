# Agent 0 — Materials Extraction Prompt

<!-- Loaded by agent0_materials.py via _load_prompt(). Lines starting with # or <!-- are stripped. -->
<!-- Placeholders {topic} and {book_text} are filled at runtime via .format(). -->

You are preparing source material for a YouTube psychology video about: "{topic}".

Below is the full text of a book the creator has selected as a trusted reference.

Extract and organize the following into a structured markdown document:
- Key psychological frameworks or models described in the book
- Counterintuitive or surprising findings
- Concrete examples, case studies, or stories that illustrate the main ideas
- Quotable passages (with approximate location if possible)
- Any arguments or mechanisms most relevant to the topic

Be specific and thorough. This will be used directly by a scriptwriter — prioritize insight density over brevity.

BOOK TEXT:
{book_text}
