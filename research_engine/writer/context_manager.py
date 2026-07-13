"""
research_engine/writer/context_manager.py
Tier 2 — Multi-chapter compressed context for MSc/PhD

For long projects (MSc/PhD), feeding raw chapter text into each new
chapter prompt blows the context window and costs too much.

This module produces a structured, compressed summary of all previous
chapters — capturing objectives, key arguments, methods, and findings
in ~400 words regardless of how long the original chapters are.

Public API
----------
    compress_chapter(chapter_content, api_key)     → str (compressed summary)
    build_context_summary(session, up_to, api_key) → str (all prior chapters compressed)
    inject_into_prompt(prompt, context_summary)    → str (enhanced prompt)
"""
from __future__ import annotations

import os
import re
from typing import Optional


def compress_chapter(
    chapter_content: str,
    chapter_number:  int,
    chapter_title:   str,
    api_key:         str | None = None,
    model:           str        = "gpt-4o-mini",
) -> str:
    """
    Produce a ~300-word structured summary of one chapter.

    Used to maintain cross-chapter continuity without consuming the
    full context window.

    Returns the compressed summary as a string.
    Falls back to a naive truncation if the API is unavailable.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return _naive_compress(chapter_content, chapter_number, chapter_title)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": (
                    f"Summarise Chapter {chapter_number} ({chapter_title}) of a research project "
                    f"in exactly 250–300 words. Structure your summary as:\n\n"
                    f"CHAPTER {chapter_number} SUMMARY ({chapter_title.upper()})\n"
                    f"• Main argument/purpose: ...\n"
                    f"• Key concepts defined: ...\n"
                    f"• Core findings/positions: ...\n"
                    f"• Specific commitments for later chapters "
                    f"  (variables named, tools stated, hypotheses made): ...\n"
                    f"• Tone and register: ...\n\n"
                    f"CHAPTER TEXT:\n{chapter_content[:6000]}"
                )
            }],
            temperature=0.2,
            max_tokens=512,
        )
        return response.choices[0].message.content or _naive_compress(
            chapter_content, chapter_number, chapter_title)
    except Exception:
        return _naive_compress(chapter_content, chapter_number, chapter_title)


def _naive_compress(content: str, n: int, title: str) -> str:
    """Simple extraction fallback: first 300 words of the chapter."""
    words = content.split()[:300]
    return (
        f"CHAPTER {n} SUMMARY ({title.upper()})\n"
        f"[Compressed from {len(content.split())} words]\n\n"
        + " ".join(words) + "…"
    )


def build_context_summary(
    session,
    up_to:    int,
    api_key:  str | None = None,
    model:    str        = "gpt-4o-mini",
) -> str:
    """
    Build a compressed context block for all chapters before `up_to`.

    Used when writing Chapter N to give the LLM awareness of
    Chapters 1 through N-1 without filling the context window.

    Parameters
    ----------
    session  : ProjectSession
    up_to    : chapter number being written (summaries of ch < up_to)
    api_key  : OpenAI API key
    model    : model for compression (mini is fine — cheaper)

    Returns
    -------
    str — compressed context block to inject into the writing prompt
    """
    from research_engine.writer.project_session import CHAPTER_TITLES

    summaries = []
    for n in range(1, up_to):
        ch = session.get_chapter(n)
        if ch is None:
            continue
        title = CHAPTER_TITLES.get(n, f"Chapter {n}")
        # Check cache first
        cache_key = f"_ctx_summary_ch{n}"
        cached = session.notes  # notes list used as lightweight cache
        hit = next((x for x in cached if x.startswith(f"{cache_key}:")), None)
        if hit:
            summary = hit[len(cache_key)+1:]
        else:
            summary = compress_chapter(ch.content, n, title, api_key=api_key, model=model)
            session.notes.append(f"{cache_key}:{summary}")
        summaries.append(summary)

    if not summaries:
        return ""

    return (
        "\n\n=== PREVIOUS CHAPTERS CONTEXT (compressed for continuity) ===\n\n"
        + "\n\n---\n\n".join(summaries)
        + "\n\n=== END CONTEXT ==="
    )


def inject_into_prompt(base_prompt: str, context_summary: str) -> str:
    """
    Inject the context summary into a chapter writing prompt.

    Inserts it just before the 'Write the complete chapter now:' line
    so it sits close to the generation instruction.
    """
    if not context_summary:
        return base_prompt
    marker = "Write the complete chapter now:"
    if marker in base_prompt:
        return base_prompt.replace(
            marker,
            f"{context_summary}\n\n{marker}"
        )
    return base_prompt + "\n\n" + context_summary
