"""Offline dictionary lookup for DeepTutor Immersive Reading.

This example does not call an LLM or external API. It extracts the selected
word, derives a short gloss from surrounding context, and returns a card.
"""

from __future__ import annotations

import re

from deeptutor.reading.extensions import (
    ReadingAction,
    ReadingExtensionManifest,
    ReadingExtensionResult,
)


def _find_sentence(text: str, word: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        if word.casefold() in sentence.casefold():
            return sentence.strip()
    return ""


def _short_gloss(sentence: str, word: str) -> str:
    if not sentence:
        return "No surrounding sentence found."
    start = max(0, sentence.casefold().find(word.casefold()) - 40)
    end = min(len(sentence), sentence.casefold().find(word.casefold()) + len(word) + 60)
    return sentence[start:end].strip()


class DictionaryExtension:
    manifest = ReadingExtensionManifest(
        id="dictionary",
        version="1.0.0",
        name="Dictionary lookup",
        protocol_version="1",
        requires_llm=False,
        actions=[
            ReadingAction(
                id="lookup",
                label="Look up word",
                requires=["selection"],
            ),
        ],
        result_types=["card"],
    )

    def run_action(self, action: str, context) -> ReadingExtensionResult:
        if action != "lookup":
            raise ValueError(f"Unsupported action: {action}")

        selection = context.selection.strip()
        if not selection:
            raise ValueError("Dictionary lookup requires a selection.")

        words = selection.split()
        if len(words) > 5:
            raise ValueError("Dictionary lookup accepts up to 5 words.")

        entries = []
        for word in words[:5]:
            clean = word.strip(".,!?;:'\"()[]{}")
            if not clean:
                continue
            sentence = _find_sentence(context.visible_text, clean)
            entries.append(
                {
                    "term": clean,
                    "context": _short_gloss(sentence, clean),
                }
            )

        if not entries:
            entries.append({"term": selection, "context": "No usable word found."})

        return ReadingExtensionResult(
            type="card",
            title="Dictionary" if context.locale != "zh" else "词典",
            message="Context-based lookup" if context.locale != "zh" else "基于上下文的释义",
            payload={"entries": entries},
        )
