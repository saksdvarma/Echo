from echo.models.sentiment import TransformerSentimentAnalyzer


def test_positive_phrase_scores_positive() -> None:
    analyzer = TransformerSentimentAnalyzer()
    score = analyzer.score("Company beat earnings and strong growth outlook.")
    assert score.polarity > 0


def test_negative_phrase_scores_negative() -> None:
    analyzer = TransformerSentimentAnalyzer()
    score = analyzer.score("Bearish recession risk after weak guidance.")
    assert score.polarity < 0
