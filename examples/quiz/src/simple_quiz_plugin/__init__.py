"""Offline cloze quiz for DeepTutor Immersive Reading.

This example builds a simple fill-in-the-blank question from the most
frequent long word in the visible text. It does not call an LLM.
"""

from __future__ import annotations

import re
from collections import Counter

from deeptutor.reading.extensions import (
    ReadingAction,
    ReadingExtensionManifest,
    ReadingExtensionResult,
)


class SimpleQuizExtension:
    manifest = ReadingExtensionManifest(
        id="simple_quiz",
        version="1.0.0",
        name="Simple quiz",
        protocol_version="1",
        requires_llm=False,
        actions=[
            ReadingAction(
                id="start",
                label="Quick quiz",
                requires=["visible_text"],
            ),
        ],
        result_types=["quiz"],
    )

    def run_action(self, action: str, context) -> ReadingExtensionResult:
        if action != "start":
            raise ValueError(f"Unsupported action: {action}")

        text = context.visible_text.strip()
        if len(text) < 100:
            raise ValueError("Quick quiz needs at least 100 characters of text.")

        words = re.findall(r"\b[a-zA-Z]{6,}\b", text.casefold())
        if not words:
            raise ValueError("Quick quiz could not find a suitable word.")

        counts = Counter(words)
        target = counts.most_common(1)[0][0]

        sentence_match = None
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if target in sentence.casefold() and 20 <= len(sentence) <= 300:
                sentence_match = sentence
                break

        if not sentence_match:
            raise ValueError("Quick quiz could not build a question from this text.")

        distractors = [w for w, _ in counts.most_common(5) if w != target][:3]
        while len(distractors) < 3:
            distractors.append(f"option{len(distractors) + 1}")

        choices = [target] + distractors
        correct_index = 0

        import random

        random.shuffle(choices)
        correct_index = choices.index(target)

        blanked = re.sub(
            re.escape(target),
            "______",
            sentence_match,
            flags=re.IGNORECASE,
            count=1,
        )

        return ReadingExtensionResult(
            type="quiz",
            title="Quick quiz" if context.locale != "zh" else "快速测验",
            message="Fill in the blank" if context.locale != "zh" else "填空",
            payload={
                "questions": [
                    {
                        "id": "q_1",
                        "prompt": blanked,
                        "choices": choices,
                        "correct_choice_index": correct_index,
                    }
                ]
            },
        )
