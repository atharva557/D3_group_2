# import time  # For adding delays (pacing the output)
# import torch  # The core deep learning library
# import pandas as pd  # For handling the CSV label file
# import numpy as np  # For numerical operations
# from transformers import BertTokenizer, BertForSequenceClassification  # HuggingFace BERT tools
# from get_titles import get_reddit_titles  # Custom module to scrape/fetch Reddit data
#
#
# class RedditEmotionAnalyzer:
#     def __init__(self, model_path="./best_reddit_model_2"):
#         """
#         Initialize the model ONCE to save memory and time.
#         """
#         print(model_path)
#         self.model_path = model_path
#         # Check if a GPU is available, otherwise use the CPU
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         print(f"🚀 Loaded on Device: {self.device}")
#
#         print("⏳ Loading model... (This may take a moment)")
#         try:
#             # Load the pre-trained BERT classification model from the local directory
#             self.model = BertForSequenceClassification.from_pretrained(self.model_path)
#             # Load the vocabulary/tokenizer used during training
#             self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
#             # Send the model weights to the GPU or CPU
#             self.model.to(self.device)
#             # Set the model to evaluation mode (disables dropout, etc.)
#             self.model.eval()
#
#             # Load the list of emotion names from the local CSV file
#             self.labels = pd.read_csv(f"{self.model_path}/labels.csv").iloc[:, 0].tolist()
#             print("✅ Model Ready!")
#         except Exception as e:
#             # Catch errors like missing files or incompatible PyTorch versions
#             print(f"❌ Error loading model: {e}")
#             self.model = None
#
#         # --- SENTIMENT MAPPING ---
#         # Grouping specific emotions into broader sentiment buckets
#         self.sentiment_map = {
#             'positive': [
#                 'admiration', 'amusement', 'approval', 'caring', 'desire',
#                 'excitement', 'gratitude', 'joy', 'love', 'optimism',
#                 'pride', 'relief'
#             ],
#             'negative': [
#                 'anger', 'annoyance', 'disappointment', 'disapproval',
#                 'disgust', 'embarrassment', 'fear', 'grief', 'nervousness',
#                 'remorse', 'sadness'
#             ],
#             'ambiguous': [
#                 'confusion', 'curiosity', 'realization', 'surprise'
#             ],
#             'neutral': [
#                 'neutral'
#             ]
#         }
#
#     def get_sentiment(self, emotion):
#         """Helper to find if an emotion is Positive, Negative, Ambiguous, or Neutral"""
#         # Iterate through the dictionary to find which list contains the specific emotion
#         for category, emotions in self.sentiment_map.items():
#             if emotion in emotions:
#                 return category
#         return "neutral"  # Fallback if no match is found
#
#     def predict(self, text):
#         # Prevent execution if the model failed to load in __init__
#         if not self.model:
#             return {"error": "Model not loaded"}
#         # 1. Preprocess: Convert text to tokens, truncate to 128 words, and move to GPU/CPU
#         inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)
#
#         # 2. Predict: Pass inputs through BERT without calculating gradients (faster)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#
#         # 3. Process Probabilities: Apply Sigmoid to get scores between 0 and 1
#         probs = torch.sigmoid(outputs.logits).squeeze().cpu().numpy()
#
#         valid_emotions = {}
#         # Loop through every possible emotion label and its calculated score
#         for i, score in enumerate(probs):
#             label = self.labels[i]
#
#             # Dynamic Thresholds: Adjust sensitivity based on the emotion type
#             limit = 0.30
#
#             # 1. Very Strict: Neutral and High-Confidence Positives
#             # These often "spam" the results if the threshold is too low.
#             if label in ["neutral", "admiration", "approval", "gratitude"]:
#                 limit = 0.70
#
#                 # 2. Sensitive: Rare/Strong emotions
#             # We lower the bar here so we don't miss "Grief" or "Fear" (the Red Bars)
#             elif label in ["fear", "surprise", "anger", "disgust", "grief", "relief", "pride"]:
#                 limit = 0.15
#             # If the model's confidence is higher than the limit, keep it
#             if score > limit:
#                 valid_emotions[label] = float(score)
#
#         # Handle Empty Result: If no emotions passed their thresholds, return neutral
#         if not valid_emotions:
#             return {
#                 "content": text,
#                 "primary_emotion": "neutral",
#                 "confidence": 0.0,
#                 "sentiment": "neutral",
#                 "raw_json": {}
#             }
#
#         # Sort the detected emotions so the highest confidence is first
#         sorted_emotions = sorted(valid_emotions.items(), key=lambda x: x[1], reverse=True)
#         best_emotion, best_score = sorted_emotions[0]
#
#         # Logic: If 'neutral' is #1 but something else was also detected, pick the 'something else'
#         if best_emotion == "neutral" and len(sorted_emotions) > 1:
#             best_emotion, best_score = sorted_emotions[1]
#
#         # Map the final chosen emotion to its sentiment category
#         sentiment = self.get_sentiment(best_emotion)
#
#         # --- RETURN DICTIONARY (Structured for Database insertion) ---
#         return {
#             "content": text,
#             "primary_emotion": best_emotion,
#             "confidence": float(best_score),
#             "sentiment": sentiment,
#             "raw_json": dict(sorted_emotions)
#         }
#
#     def get_dominant_emotion_from_batch(self, results):
#         """
#         Takes the list of results from analyze_batch and
#         returns the single most common emotion (e.g., 'joy').
#         """
#         if not results:
#             return "neutral"
#
#         # Extract just the primary emotions list
#         emotions = [r['primary_emotion'] for r in results]
#
#         # Count frequencies
#         from collections import Counter
#         counts = Counter(emotions)
#
#         # Get the most common one (e.g., 'joy')
#         dominant = counts.most_common(1)[0][0]
#
#         return dominant
#     def analyze_batch(self, text_list):
#         results = []
#         print(f"\n🧠 Analyzing {len(text_list)} titles...\n")
#
#         # Process each title in the provided list
#         for text in text_list:
#             result = self.predict(text)
#             results.append(result)
#
#             # Display the result in the console
#             #print(f"📝 Content: {result['content']}")
#
#             # Choose an emoji based on the sentiment for visual clarity
#             emoji = "⚪"
#             if result['sentiment'] == 'positive':
#                 emoji = "🟢"
#             elif result['sentiment'] == 'negative':
#                 emoji = "🔴"
#             elif result['sentiment'] == 'ambiguous':
#                 emoji = "🤔"
#
#             # print(f"   {emoji} Sentiment: {result['sentiment'].upper()}")
#             # print(f"   ➤ Primary:   {result['primary_emotion']} ({result['confidence']:.1%})")
#
#             # If multiple emotions were detected, list the secondary ones
#             if len(result['raw_json']) > 1:
#                 others = [k for k in result['raw_json'].keys() if k != result['primary_emotion']]
#                 # print(f"   (Also detected: {', '.join(others)})")
#             # print("-" * 50)
#
#         return results
#
#
#
#
# if __name__ == "__main__":
#     # Create an instance of the class
#     analyzer = RedditEmotionAnalyzer()
#
#     try:
#         # Attempt to fetch live data from Reddit
#         reddit_data = get_reddit_titles()
#         if not reddit_data:
#             print("⚠️ No titles found. Using test data.")
#             # Fallback data if the scraper returns nothing
#             reddit_data = ["This update is trash", "I love this community", "Is this a bug?", "Just a normal day"]
#
#         # Run the analysis
#         analyzer.analyze_batch(reddit_data)
#
#     except Exception as e:
#         # Handle errors related to network or the custom get_titles module
#         print(f"Error getting titles: {e}")


"""
Reddit Pulse - Emotion Analysis Module
=======================================
This module contains the core AI logic for detecting emotions and sentiment
in Reddit posts and comments using a fine-tuned BERT model.

The analyzer supports 28 distinct emotions and maps them to 4 sentiment categories:
    - Positive: joy, love, admiration, gratitude, etc.
    - Negative: anger, sadness, fear, disgust, etc.
    - Ambiguous: confusion, curiosity, surprise, realization
    - Neutral: neutral

Author: Reddit Pulse Team
Model: Fine-tuned BERT (bert-base-uncased)
License: MIT
"""

import torch
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from get_titles import get_reddit_titles


class RedditEmotionAnalyzer:
    """
    Fine-tuned BERT model for multi-label emotion classification.

    This class handles loading the model, tokenizing input, running inference,
    and mapping emotions to sentiment categories.
    """

    def __init__(self, model_path="./best_reddit_model_2"):
        """
        Initialize the emotion analyzer with a pre-trained model.

        Args:
            model_path (str): Path to the directory containing:
                - pytorch_model.bin (model weights)
                - config.json (model configuration)
                - vocab.txt (tokenizer vocabulary)
                - labels.csv (emotion label names)

        Raises:
            Exception: If model files are missing or incompatible
        """
        self.model_path = model_path

        # Determine device (GPU if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Loaded on Device: {self.device}")

        print("⏳ Loading model... (This may take a moment)")
        try:
            # Load pre-trained BERT classification model
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)

            # Load tokenizer (converts text to numerical tokens)
            self.tokenizer = BertTokenizer.from_pretrained(self.model_path)

            # Move model to GPU/CPU
            self.model.to(self.device)

            # Set to evaluation mode (disables dropout layers)
            self.model.eval()

            # Load emotion labels from CSV file
            self.labels = pd.read_csv(f"{self.model_path}/labels.csv").iloc[:, 0].tolist()
            print("✅ Model Ready!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None

        # Define emotion-to-sentiment mapping
        self.sentiment_map = {
            'positive': [
                'admiration', 'amusement', 'approval', 'caring', 'desire',
                'excitement', 'gratitude', 'joy', 'love', 'optimism',
                'pride', 'relief'
            ],
            'negative': [
                'anger', 'annoyance', 'disappointment', 'disapproval',
                'disgust', 'embarrassment', 'fear', 'grief', 'nervousness',
                'remorse', 'sadness'
            ],
            'ambiguous': [
                'confusion', 'curiosity', 'realization', 'surprise'
            ],
            'neutral': [
                'neutral'
            ]
        }

    def get_sentiment(self, emotion):
        """
        Map an emotion to its broader sentiment category.

        Args:
            emotion (str): Specific emotion label (e.g., 'joy', 'anger')

        Returns:
            str: Sentiment category ('positive', 'negative', 'ambiguous', or 'neutral')
        """
        for category, emotions in self.sentiment_map.items():
            if emotion in emotions:
                return category
        return "neutral"  # Fallback for unknown emotions

    def predict(self, text):
        """
        Analyze a single text for emotional content.

        This method:
        1. Tokenizes the input text
        2. Passes it through the BERT model
        3. Applies sigmoid to get emotion probabilities
        4. Filters emotions using dynamic thresholds
        5. Returns the dominant emotion and sentiment

        Args:
            text (str): Input text to analyze (post title, comment, or statement)

        Returns:
            dict: Analysis result containing:
                - content (str): Original input text
                - primary_emotion (str): Dominant emotion detected
                - confidence (float): Confidence score (0-1)
                - sentiment (str): Overall sentiment category
                - raw_json (dict): All detected emotions with scores

        Dynamic Thresholding:
            - Neutral: 0.85 (requires high confidence to classify as truly neutral)
            - Strong emotions (fear, anger, etc.): 0.10 (more sensitive detection)
            - Other emotions: 0.05 (standard threshold)
        """
        if not self.model:
            return {"error": "Model not loaded"}

        # Step 1: Tokenize input text
        # - Converts text to token IDs
        # - Truncates to 128 tokens (BERT's max effective length)
        # - Adds padding if needed
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        # Step 2: Run inference (no gradient calculation for speed)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Step 3: Convert logits to probabilities using sigmoid
        # Sigmoid maps any number to a 0-1 range, suitable for multi-label classification
        probs = torch.sigmoid(outputs.logits).squeeze().cpu().numpy()

        # Step 4: Filter emotions based on dynamic thresholds
        valid_emotions = {}
        for i, score in enumerate(probs):
            label = self.labels[i]

            # Apply emotion-specific thresholds
            if label == "neutral":
                threshold = 0.85  # Be strict with neutral (avoid false neutrals)
            elif label in ["fear", "surprise", "anger", "disgust"]:
                threshold = 0.10  # Be sensitive to strong/rare emotions
            else:
                threshold = 0.05  # Standard threshold for other emotions

            # Keep emotion if it exceeds its threshold
            if score > threshold:
                valid_emotions[label] = float(score)

        # Step 5: Handle edge cases
        if not valid_emotions:
            # No emotions passed threshold - default to neutral
            return {
                "content": text,
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "sentiment": "neutral",
                "raw_json": {}
            }

        # Step 6: Determine primary emotion
        # Sort by confidence (highest first)
        sorted_emotions = sorted(valid_emotions.items(), key=lambda x: x[1], reverse=True)
        best_emotion, best_score = sorted_emotions[0]

        # Special logic: If neutral wins but other emotions exist, pick the next emotion
        # This prevents weak neutral signals from overriding more specific emotions
        if best_emotion == "neutral" and len(sorted_emotions) > 3:
            best_emotion, best_score = sorted_emotions[1]

        # Step 7: Map to sentiment category
        sentiment = self.get_sentiment(best_emotion)

        # Return structured result
        return {
            "content": text,
            "primary_emotion": best_emotion,
            "confidence": float(best_score),
            "sentiment": sentiment,
            "raw_json": dict(sorted_emotions)
        }

    def get_dominant_emotion_from_batch(self, results):
        """
        Calculate the most common emotion across multiple analysis results.

        This is used to determine the overall "vibe" of a subreddit or topic
        by finding which emotion appears most frequently across all posts.

        Args:
            results (list[dict]): List of prediction results from analyze_batch()

        Returns:
            str: The most frequently occurring primary_emotion

        Example:
            results = [
                {'primary_emotion': 'joy', ...},
                {'primary_emotion': 'joy', ...},
                {'primary_emotion': 'anger', ...}
            ]
            Returns: 'joy'
        """
        if not results:
            return "neutral"

        # Extract just the primary emotions
        emotions = [r['primary_emotion'] for r in results]

        # Count frequency of each emotion
        emotion_counts = {}
        for emotion in emotions:
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
            else:
                emotion_counts[emotion] = 1

        # 3. Find the key with the highest value
        dominant = max(emotion_counts, key=emotion_counts.get)

        return dominant

    def analyze_batch(self, text_list):
        """
        Analyze multiple texts in batch (optimized for processing Reddit data).

        Args:
            text_list (list[str]): List of texts to analyze

        Returns:
            list[dict]: List of analysis results, one per input text
                Each result has the same structure as predict()
        """
        results = []
        print(f"\n🧠 Analyzing {len(text_list)} titles...\n")

        for text in text_list:
            result = self.predict(text)
            results.append(result)

        return results


# ============================================================================
# COMMAND LINE TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test the analyzer with live Reddit data or fallback test data.

    Usage:
        python RedditEmotionAnalyzer.py
    """
    # Initialize analyzer
    analyzer = RedditEmotionAnalyzer()

    try:
        # Attempt to fetch live Reddit data
        reddit_data = get_reddit_titles()

        if not reddit_data:
            print("⚠️ No titles found. Using test data.")
            # Fallback test data
            reddit_data = [
                "This update is trash",
                "I love this community",
                "Is this a bug?",
                "Just a normal day"
            ]

        # Run analysis and display results
        results = analyzer.analyze_batch(reddit_data)

        # Print formatted results
        for r in results:
            emoji = "🟢" if r['sentiment'] == 'positive' else \
                "🔴" if r['sentiment'] == 'negative' else \
                    "🤔" if r['sentiment'] == 'ambiguous' else "⚪"

            print(f"{emoji} {r['primary_emotion'].upper()} ({r['confidence']:.1%})")
            print(f"   Text: {r['content'][:80]}...")
            print("-" * 50)

    except Exception as e:
        print(f"Error getting titles: {e}")
