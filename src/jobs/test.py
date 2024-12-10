from transformers import pipeline

def sentiment_analysis(comment: str) -> str:
    if comment:
        print(comment)
        
        # Load pre-trained sentiment analysis pipeline
        classifier = pipeline("sentiment-analysis")
        
        # Classify sentiment
        result = classifier(comment)
        label = result[0]['label']
        
        # Map labels to POSITIVE, NEGATIVE, or NEUTRAL
        if "positive" in label.lower():
            sentiment = "POSITIVE"
        elif "negative" in label.lower():
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        return sentiment
    return "Empty"

# Example usage
print(sentiment_analysis("Best thai food in the area.  Everything was authentic and delicious.  Will definitely be back again and again."))
