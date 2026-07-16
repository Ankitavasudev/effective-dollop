"""
ML Model for Sentiment Analysis
Advanced emotion detection with transformers
"""

import re
import pickle
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
import os


class SentimentModel:
    """
    Multi-class sentiment analysis model.
    
    Supports 6 emotions: happy, sad, angry, fear, surprise, neutral
    """
    
    EMOTIONS = ['happy', 'sad', 'angry', 'fear', 'surprise', 'neutral']
    
    # Emoji mapping for emotions
    EMOTION_EMOJIS = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'fear': '😨',
        'surprise': '😲',
        'neutral': '😐'
    }
    
    # Keyword dictionaries for fallback analysis
    KEYWORDS = {
        'happy': [
            'love', 'happy', 'great', 'amazing', 'wonderful', 'excellent', 'fantastic',
            'joy', 'beautiful', 'awesome', 'perfect', 'best', 'thank', 'grateful',
            'blessed', 'excited', 'delighted', 'thrilled', 'ecstatic', 'blissful'
        ],
        'sad': [
            'sad', 'sorry', 'unfortunate', 'depressed', 'miserable', 'heartbroken',
            'disappointed', 'regret', 'miss', 'lonely', 'crying', 'tears',
            'grief', 'sorrow', 'melancholy', 'gloomy', 'hopeless', 'devastated'
        ],
        'angry': [
            'angry', 'terrible', 'horrible', 'hate', 'furious', 'rage', 'annoyed',
            'frustrated', 'irritated', 'mad', 'livid', 'outraged', 'disgusted',
            'infuriated', 'enraged', 'hostile', 'bitter', 'resentful'
        ],
        'fear': [
            'scared', 'afraid', 'worried', 'anxious', 'terrified', 'panic',
            'nervous', 'frightened', 'alarmed', 'concerned', 'dread', 'horror',
            'phobia', 'uneasy', 'apprehensive', 'tense', 'stressed'
        ],
        'surprise': [
            'wow', 'amazing', 'incredible', 'unbelievable', 'shocked', 'unexpected',
            'astonished', 'stunned', 'bewildered', 'startled', 'speechless',
            'remarkable', 'extraordinary', 'unprecedented', 'mind-blowing'
        ],
        'neutral': [
            'okay', 'fine', 'regular', 'normal', 'average', 'standard', 'typical',
            'ordinary', 'mundane', 'routine', 'everyday', 'common', 'usual'
        ]
    }
    
    def __init__(self):
        """Initialize the sentiment model."""
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available."""
        model_path = os.path.join('models', 'sentiment_model.pkl')
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data.get('model')
                    self.vectorizer = data.get('vectorizer')
                    self.is_loaded = True
            else:
                print("No pre-trained model found. Using keyword-based analysis.")
                self.is_loaded = True  # Use fallback
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_loaded = True  # Use fallback
    
    def preprocess(self, text: str) -> str:
        """
        Clean and preprocess input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text
        """
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _keyword_analysis(self, text: str) -> Dict:
        """
        Perform keyword-based sentiment analysis.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Analysis results
        """
        text_lower = text.lower()
        
        # Count keyword matches for each emotion
        scores = {}
        for emotion, keywords in self.KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = count
        
        # Calculate probabilities
        total = sum(scores.values()) or 1
        probabilities = {emotion: count / total for emotion, count in scores.items()}
        
        # If no keywords found, default to neutral
        if all(v == 0 for v in scores.values()):
            probabilities['neutral'] = 1.0
        
        # Get emotion with highest score
        emotion = max(probabilities, key=probabilities.get)
        confidence = probabilities[emotion]
        
        return {
            'emotion': emotion,
            'confidence': round(confidence, 3),
            'scores': probabilities
        }
    
    def _ml_analysis(self, text: str) -> Dict:
        """
        Perform ML-based sentiment analysis.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Analysis results
        """
        if self.model is None or self.vectorizer is None:
            return self._keyword_analysis(text)
        
        try:
            # Vectorize text
            features = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Get emotion and confidence
            emotion = self.EMOTIONS[prediction]
            confidence = float(max(probabilities))
            
            # Get all scores
            scores = {
                emotion: float(prob) 
                for emotion, prob in zip(self.EMOTIONS, probabilities)
            }
            
            return {
                'emotion': emotion,
                'confidence': round(confidence, 3),
                'scores': scores
            }
            
        except Exception as e:
            print(f"ML analysis failed: {e}")
            return self._keyword_analysis(text)
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion, confidence, and scores
        """
        # Preprocess
        processed = self.preprocess(text)
        
        # Use ML model if available, otherwise use keywords
        if self.model is not None:
            result = self._ml_analysis(processed)
        else:
            result = self._keyword_analysis(processed)
        
        # Add emoji
        result['emoji'] = self.EMOTION_EMOJIS.get(result['emotion'], '❓')
        
        return result
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of analysis results
        """
        return [self.analyze(text) for text in texts]
    
    def get_distribution(self, texts: List[str]) -> Dict:
        """
        Get emotion distribution for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            Distribution statistics
        """
        results = self.analyze_batch(texts)
        emotions = [r['emotion'] for r in results]
        
        counts = Counter(emotions)
        total = len(emotions) or 1
        
        distribution = {
            emotion: {
                'count': counts.get(emotion, 0),
                'percentage': round(counts.get(emotion, 0) / total * 100, 2)
            }
            for emotion in self.EMOTIONS
        }
        
        return distribution


# Singleton instance
_model_instance = None


def get_model() -> SentimentModel:
    """Get or create model singleton."""
    global _model_instance
    if _model_instance is None:
        _model_instance = SentimentModel()
    return _model_instance
