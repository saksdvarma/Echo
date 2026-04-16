from __future__ import annotations

from dataclasses import dataclass


POSITIVE_TERMS = {
    "beat",
    "surge",
    "bullish",
    "growth",
    "rally",
    "upgrade",
    "strong",
    "outperform",
}
NEGATIVE_TERMS = {
    "miss",
    "drop",
    "bearish",
    "downgrade",
    "risk",
    "weak",
    "recession",
    "lawsuit",
}


@dataclass(slots=True)
class SentimentScore:
    polarity: float
    confidence: float


class TransformerSentimentAnalyzer:
    """
    Lightweight sentiment analyzer with optional transformer support.

    If transformers is installed and available locally, it can be wired in;
    this fallback lexicon analyzer keeps the pipeline fully runnable.
    """

    def score(self, text: str) -> SentimentScore:
        words = {token.strip(".,!?;:").lower() for token in text.split()}
        positive = len(words & POSITIVE_TERMS)
        negative = len(words & NEGATIVE_TERMS)
        raw = positive - negative
        magnitude = positive + negative
        if magnitude == 0:
            return SentimentScore(polarity=0.0, confidence=0.2)
        polarity = max(-1.0, min(1.0, raw / magnitude))
        confidence = min(1.0, 0.4 + (magnitude * 0.15))
        return SentimentScore(polarity=polarity, confidence=confidence)

    def batch_score(self, texts: list[str]) -> float:
        if not texts:
            return 0.0
        scores = [self.score(t) for t in texts]
        weighted = [s.polarity * s.confidence for s in scores]
        return sum(weighted) / len(weighted)
