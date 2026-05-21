# YouTube Psychology Script Style Guide

Reference guide for Agent 3 (script writer) and Agent 4 (script editor). Defines tone, structure, and writing rules for YouTube psychology video scripts.

## 1. Channel Identity

- **Channel name:** TBD (psychology/mental health channel similar to UnordinaryMind)
- **Audience:** General public — curious people with no prior psychology background
- **Video length:** 10–15 min (target ~1,700 words narration); one image per sentence or two (~40–60 images per video)
- **Science standard:** Peer-reviewed sources only (no pop-science, no pseudoscience)

## 2. Tone Rules

- **Direct address:** Always "you" and "your" — speak directly to the viewer
- **Validate before explain:** Land the feeling first. The viewer must recognize themselves before any mechanism is introduced. Empathy is not a hook — it's the whole register.
- **Voice:** Warm and one-on-one — like a therapist sitting across from the viewer. You don't perform expertise; you offer recognition. The viewer trusts the speaker, not the citation.
- **Research is invisible:** The writer reads research; the script never references it. No "researchers found", no "studies show", no "scientists discovered", no "neuroscience has found", no "one study", no "the science is clear". Findings appear as observations about being human, not as scientific reports. Real bibliographic citations live in the YouTube description (Agent 8), never in the spoken narration.
- **Technical terms:** Lead with everyday language. Describe the phenomenon, never the term. Name a scientific concept only if (a) the name itself is genuinely memorable, and (b) it appears once, late, after the idea has already landed in plain words. Default to no name. Do NOT use the jargon-then-translation pattern ("ego depletion — the depletion of…") — it reads like a lecture.
- **Sentence structure:** Short punchy sentences. Fragments for emphasis
- **Confidence:** No hedging ("might", "perhaps", "could be") — be direct. Replace hedging with claims spoken in the speaker's own voice. *"Your brain does X"*, not *"Research shows your brain does X"*.
- **Grammar:** No passive voice
- **Openings:** No throat-clearing openings ("In this video we will discuss...")
- **Rhythm:** Alternate between long, complex explanatory sentences and short, brutal ones (2–4 words). Fragments are intentional, not errors. The contrast creates impact.

### Numbers

Round, framed numbers only. *"Roughly half"*, *"most people"*, *"in many cases"*, *"more often than not"*.

Never use:

- Decimals (`0.62`, `37.4%`)
- Effect sizes (`d = 0.6`, `r = 0.4`, `Cohen's d`)
- p-values, confidence intervals, statistical significance
- Study counts (*"a meta-analysis of 94 experiments"*, *"across 47 studies"*)
- Participant counts (*"8,000 people"*, *"over twelve thousand subjects"*)
- Methodology terms (*pre-registered, double-blind, longitudinal, meta-analysis, replication crisis*)
- Greek letters or statistical notation of any kind

If a number doesn't land emotionally as plain English, cut it.

**Script structure** is defined in `workflows/narrative_architectures.md` — that document replaces any section structure listed here.

## 3. Metaphor Guidelines

- Every scientific concept should have a metaphor or analogy
- Metaphors should be modern and relatable (cameras, computers, RAM, high-res screens, etc.)
- Metaphors from the example: brain as camera (720p vs 8K), dandelion vs orchid, RAM being full
- One strong metaphor per scientific concept — don't mix metaphors

## 4. IMAGE Marker Guidelines

- **Format:** `[IMAGE: emotion=EMOTION, perspective=PERSPECTIVE, space=SPACE, scene=description]`
  See `workflows/style_guide_images.md` for the full visual bible, emotion lookup table, and valid field values.
- **Frequency:** 1 image every 1–2 sentences — place one at every new idea, statistic, metaphor, or scene shift. Aim for 60–80 markers per video.
- **Placement:** Every sentence or two — do not save markers for section transitions only.
- **Scene field:** Free-form body and environment description only. Do NOT include palette, style, or lighting words — those come from the emotion lookup.
- **Example:** `[IMAGE: emotion=FEAR, perspective=overhead, space=real, scene=A body curled on a bathroom floor, arms wrapped around knees, cool blue light seeping under the door]`

## 5. Example Transcript

Reference for **sentence rhythm and metaphor style only** (verbatim).

**This script is from the old voice — do NOT calibrate voice off it.** It contains research-framing phrases that are now banned (*"Research shows that your brain processes information differently"*, *"Neuroscience has identified three specific upgrades"*, *"the research shows something amazing called vantage sensitivity"*). Under the current voice, those lines would be rewritten as direct claims with no research framing — e.g. *"Your brain processes information differently than most people's"* and *"There are three upgrades in your wiring that explain why life feels so intense."*

Use this transcript only for: sentence length contrast, fragment usage, the camera/RAM/dandelion-vs-orchid metaphor style, and how empathy is layered through. Ignore: every "Research shows / Neuroscientists call this / Psychologists call this / the research shows" construction.

---

I know exactly what you have been told your whole life. You have been told that you are too sensitive. You have been told to toughen up.

You have been told probably a thousand times not to take things so personally. You have likely spent years apologizing for your tears. But I am here today to tell you that the diagnosis you've been given is wrong.

There is nothing wrong with you. You are not weak. And you are certainly not a mistake.

You are what psychologists call a highly sensitive person. But I prefer a different term. You are a super sensor.

While others are recording the world in standard definition, your brain is recording in 8k resolution. And today we're going to look at the neuroscience that proves your sensitivity is not a defect. It is a high performance radar system that the world desperately needs.

To understand yourself, we have to look at your hardware. Because this isn't just a personality quirk, it is biology. Research shows that your brain processes information differently than the other 80% of the population.

Think of the human brain like a camera. Most people's brains are recording the world in standard definition, maybe 720p. It's a good picture.

It's efficient. It gets the job done without taking up too much memory. But your brain? Your brain is recording in 8k resolution.

Neuroscience has identified three specific upgrades in your hardware that explain why life feels so intense. First, your brain lacks a filter. Neuroscientists call this low latent inhibition.

Most brains are designed to ignore 90% of what they see to save energy. They treat the background noise as irrelevant. But your brain treats everything as relevant.

You process the texture of the chair, the hum of the refrigerator, and the mood of the person sitting next to you all at once. This is why you get overwhelmed. But it is also why you notice the beauty, the patterns, and the solutions that everyone else misses.

Second, your mirror neurons are hyperactive. These are the neurons that allow us to empathize. But for you, you don't just understand that someone is sad.

You physically feel their sadness in your own body. You are not imagining it. Your brain is literally simulating their emotional state.

You are an emotional sponge in a world full of spills. And third, this leads to the most misunderstood feature of your hardware. Depth of processing.

Psychologists call this the pause to check strategy. In a conversation or when making a decision, you might feel like you are slower than others. You might beat yourself up for hesitating or overthinking.

But here is the science. You are not slow. You are thorough.

While others are engaging in shallow processing, just reacting to what is right in front of them, your brain is engaging in deep semantic encoding. You are unconsciously connecting the current moment to your past. Memories.

Predicting future outcomes and analyzing the meaning behind the words. You aren't hesitating because you are confused. You are hesitating because your brain is running a complex simulation to ensure the best possible outcome.

That is not a bug. That is high-level computation. Now, you might be asking, if this makes life so hard, why did evolution keep this trait? This is the most important part.

If being sensitive was a weakness, natural selection would have eliminated it thousands of years ago. But it didn't. It kept it.

Why? Because the tribe needs you. In ancient times, the warriors, the non-sensitive majority, were essential for hunting and fighting. They were bold and risk-taking.

But a tribe of only warriors would die. They would rush into danger without a plan. The tribe needed royal advisors.

That is you. You were the one who noticed the weather changing before the storm hit. You were the one who sensed that the neighboring tribe was lying.

Your weakness is actually a sophisticated early warning system. Society today is loud, fast, and aggressive. It is built for the warriors.

That is why you feel out of place. But do not mistake being out of place for being without value. I know that carrying this radar comes with a cost.

Because you process everything so deeply, you reach your limit faster. When you suddenly shut down or need to hide in a dark room, that is not you being dramatic. That is your RAM being full.

Your system has overheated. But science has a beautiful metaphor for this. Most people are like dandelions.

They are resilient. They can grow anywhere. In a crack in the sidewalk or a beautiful garden.

They are fine, regardless of the environment. But you? You are an orchid. If you try to grow in a harsh, noisy, or toxic environment, you will wither.

You will struggle more than the dandelions. And for years, you've probably blamed yourself for not being a dandelion. But the research shows something amazing called vantage sensitivity.

When an orchid is placed in the right environment, with the right light, the right soil, and the right care, it doesn't just survive. It blooms with a complexity and beauty that the dandelion can never achieve. You don't need to toughen up to survive the sidewalk.

You need to move yourself to the greenhouse. When you curate your life to support your sensitivity, you don't just catch up to others. You surpass them.

So, here is my prescription for you. Stop trying to install a tougher filter. You cannot change your biology.

And you shouldn't want to. The world has enough numbness. We don't need you to be thicker skinned.

We need you to be exactly who you are. But you must protect your gift, build your boundaries, honor your need for silence. And the next time someone tells you that you are too sensitive, take a breath, smile internally, and remember the truth.

You do not have a defect. You are just seeing the world in 8K resolution. And in a world that is increasingly disconnected, your ability to feel is not a burden.

It is the very thing that makes you human.

---

## 6. What to Avoid

- Do NOT start with "In this video..."
- Do NOT use passive voice
- Do NOT introduce a scientific term and then translate it. Lead with plain language and skip the term entirely unless it's genuinely memorable.
- Do NOT use hedging language ("it might be", "some studies suggest", "could be", "perhaps"). Replace hedging with **direct claims spoken in the speaker's own voice** — not by citing research. *"Your brain does X"* beats *"Research shows your brain does X"*.
- Do NOT write long paragraphs — keep to 1–3 sentences max per paragraph
- Do NOT use more than one metaphor per concept
- Do NOT use any research-framing language at all — no *"researchers found"*, no *"studies show"*, no *"scientists discovered"*, no *"neuroscience has found"*, no *"one study"*, no *"a meta-analysis"*, no *"the data shows"*, no *"according to research"*, no *"the science is clear"*. The research informs the writer; it never appears in the script. Present findings as observations about being human.
- Do NOT cite researcher names, author teams, or study years inline — never write *"a study by Sonnentag et al."* or *"research by Smith (2020)"*. All real bibliographic citations live in the YouTube description (Agent 8), not in the spoken narration.
- Do NOT use statistical notation, decimals, effect sizes, study counts, participant counts, p-values, or methodology terms (*pre-registered, double-blind, longitudinal, meta-analysis*). See the **Numbers** section above.
