from __future__ import annotations

from collections import OrderedDict

DEMO_QUESTIONS: "OrderedDict[str, str]" = OrderedDict(
    [
        (
            "CRM / FTD anomaly",
            "Why did European FTD conversion deteriorate after July 15?",
        ),
        (
            "Net-deposit anomaly",
            "Why did European net deposits fall in the week starting August 3?",
        ),
        (
            "Customer Intelligence",
            "How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?",
        ),
        (
            "Marketing lead quality",
            "Why did Americas lead volume rise while FTD conversion fell after June 15?",
        ),
        (
            "False-correlation guardrail",
            "Why did Asia FTD conversion fall after July 20, and is the nearby office relocation the cause?",
        ),
    ]
)

DEFAULT_QUESTION = next(iter(DEMO_QUESTIONS.values()))

__all__ = ["DEMO_QUESTIONS", "DEFAULT_QUESTION"]
