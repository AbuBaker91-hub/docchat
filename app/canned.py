"""Canned answers for the keyless offline demo and the offline eval run
(LLM_PROVIDER_ORDER=mock). Imported lazily; never used with real providers.

Quotes are copied verbatim from the sample PDFs so citation verification
passes against the real ingested chunks.

CannedAnswerProvider is a stateless mock provider: it extracts the question
from the rendered prompt and answers the 20 gold questions (plus the demo
return-window question) with their cited canned answer, everything else with
an honest found=false. Stateless matters for the public serverless demo,
where concurrent visitors would otherwise race through an ordered reply list.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOT_FOUND = {"answer": "", "citations": [], "confidence": 0.2, "found": False}


def _cit(doc: str, page: int, quote: str) -> dict:
    return {"doc": doc, "page": page, "quote": quote}


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def _gold_questions() -> list[str]:
    lines = (ROOT / "samples" / "gold.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line)["question"] for line in lines if line.strip()]


class CannedAnswerProvider:
    """Duck-typed LLMProvider (complete(prompt, json_schema) -> str) that picks
    the canned answer by the question inside the rendered answer prompt."""

    name = "mock"

    def __init__(self):
        self._by_question = {
            _norm(q): resp
            for q, resp in zip(_gold_questions(), eval_responses(), strict=True)
        }
        self._by_question[_norm("What is the return window?")] = ask_responses()[0]

    def complete(self, prompt: str, json_schema: dict) -> str:
        m = re.search(r"Question:\s*(.+?)\s*Chunks \(JSON\):", prompt, re.DOTALL)
        question = _norm(m.group(1)) if m else ""
        return json.dumps(self._by_question.get(question, NOT_FOUND))


POLICY = "store_policy_manual.pdf"
KETTLE = "aurora_kettle_manual.pdf"
CONTRACT = "service_contract_template.pdf"


def ask_responses() -> list:
    """Responses for POST /ask in mock mode: the first question gets the
    canned return-window answer, every later one an honest not-found
    (MockProvider repeats the last list item)."""
    return [
        {
            "answer": "The standard return window is 30 days from the date of delivery.",
            "citations": [
                _cit(POLICY, 1, "The standard return window is 30 days from the date of delivery.")
            ],
            "confidence": 0.95,
            "found": True,
        },
        {"answer": "", "citations": [], "confidence": 0.2, "found": False},
    ]


def eval_responses() -> list:
    """One canned answer per line of samples/gold.jsonl, in order."""
    return [
        {
            "answer": "The standard return window is 30 days from the date of delivery.",
            "citations": [
                _cit(POLICY, 1, "The standard return window is 30 days from the date of delivery.")
            ],
            "confidence": 0.95,
            "found": True,
        },
        {
            "answer": "Standard shipping takes 5 to 7 business days.",
            "citations": [
                _cit(
                    POLICY,
                    2,
                    "Standard shipping takes 5 to 7 business days and is free on orders above 50 dollars.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Visa, Mastercard, American Express, PayPal and Northwind gift cards.",
            "citations": [
                _cit(
                    POLICY,
                    2,
                    "We accept Visa, Mastercard, American Express, PayPal and Northwind gift cards.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Contact customer service within 7 days of delivery with a photo of the damage.",
            "citations": [
                _cit(
                    POLICY,
                    1,
                    "If an item arrives damaged or defective, contact customer service within 7 days of delivery with a photo of the damage.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Yes, Northwind price matches major online retailers within 14 days of purchase.",
            "citations": [
                _cit(POLICY, 3, "Northwind offers price matching against major online retailers.")
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "No, gift cards never expire.",
            "citations": [
                _cit(
                    POLICY,
                    3,
                    "Gift cards are available in amounts from 10 to 500 dollars and never expire.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "You earn 1 point for every dollar spent.",
            "citations": [
                _cit(
                    POLICY,
                    4,
                    "Members of the Northwind Rewards loyalty program earn 1 point for every dollar spent.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "The kettle has a capacity of 1.7 liters.",
            "citations": [
                _cit(
                    KETTLE,
                    4,
                    "The Aurora AK-200 has a capacity of 1.7 liters and a 2200 watt concealed heating element.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Fill the kettle with half water and half white vinegar, boil once, let it stand for 30 minutes, then rinse. Repeat every 4 to 6 weeks in hard water areas.",
            "citations": [
                _cit(
                    KETTLE,
                    3,
                    "Fill the kettle with a mixture of half water and half white vinegar, boil once, then let it stand for 30 minutes before rinsing thoroughly three times.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Check that the power base is plugged in and the kettle is fully seated on the base.",
            "citations": [
                _cit(
                    KETTLE,
                    3,
                    "If the kettle does not turn on, check that the power base is plugged in and that the kettle sits fully seated on the base.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "No, never immerse the kettle, base or cord in water.",
            "citations": [_cit(KETTLE, 1, "Do not immerse the kettle, base or cord in water.")],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Press the TEMP button to select one of five presets.",
            "citations": [
                _cit(KETTLE, 2, "Press the TEMP button to select the water temperature.")
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Green tea is best at 80 degrees Celsius.",
            "citations": [
                _cit(
                    KETTLE,
                    2,
                    "Green tea is best at 80 degrees, coffee at 90 degrees, and black tea at a full boil of 100 degrees.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "The kettle has a 2 year limited warranty from the date of purchase.",
            "citations": [
                _cit(
                    KETTLE,
                    4,
                    "The Aurora AK-200 is covered by a 2 year limited warranty from the date of purchase.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Net 30: each undisputed invoice is due within 30 days of receipt.",
            "citations": [
                _cit(
                    CONTRACT,
                    2,
                    "The Client shall pay each undisputed invoice within 30 days of receipt, known as net 30 payment terms.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Late payments accrue a late fee of 1.5 percent per month.",
            "citations": [
                _cit(
                    CONTRACT,
                    2,
                    "Late payments accrue a late fee of 1.5 percent per month on the outstanding balance.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "30 days written notice is required to terminate for convenience.",
            "citations": [
                _cit(
                    CONTRACT,
                    3,
                    "Either party may terminate this Agreement for convenience with 30 days written notice to the other party.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Confidential Information may not be disclosed for 3 years after termination.",
            "citations": [
                _cit(
                    CONTRACT,
                    3,
                    "may not be disclosed to third parties for a period of 3 years after termination.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "Total liability is capped at the fees paid in the preceding 12 months.",
            "citations": [
                _cit(
                    CONTRACT,
                    4,
                    "The total liability of either party under this Agreement is capped at the fees paid by the Client in the 12 months preceding the claim.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
        {
            "answer": "The Agreement is governed by the laws of the State of Delaware.",
            "citations": [
                _cit(
                    CONTRACT,
                    4,
                    "This Agreement is governed by the laws of the State of Delaware, without regard to its conflict of law rules.",
                )
            ],
            "confidence": 0.9,
            "found": True,
        },
    ]
