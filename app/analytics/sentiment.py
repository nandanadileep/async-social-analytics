from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiments(texts):
    """
    texts: list[str]
    returns: dict with sentiment counts
    """
    result = {"positive": 0, "neutral": 0, "negative": 0}

    for text in texts:
        score = analyzer.polarity_scores(text)["compound"]
        if score >= 0.05:
            result["positive"] += 1
        elif score <= -0.05:
            result["negative"] += 1
        else:
            result["neutral"] += 1

    return result
