'''
Common AI processing module for the Personal AI Employee system.
Implements gemini-3.1-flash-lite-preview integration with fallback mechanisms.
'''

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Optional, Dict, Any
from google import genai

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        """
        Initialize the AI processor with gemini-3.1-flash-lite-preview model and fallback mechanisms.
        """
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY required")

        self.client = genai.Client(api_key=api_key)

        # Configure the primary model (gemini-3.1-flash-lite-preview as specified in requirements)
        self.primary_model = "gemini-3.1-flash-lite-preview"

        # Define fallback models in case primary fails
        self.fallback_models = [
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ]

        logging.info(f"AI Processor initialized with primary model: {self.primary_model}")

    def generate_content(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Generate content using the primary model, with fallback mechanisms.

        Args:
            prompt: The main prompt for content generation
            context: Additional context to include in the generation

        Returns:
            Generated content as string, or None if all models fail
        """
        models_to_try = [self.primary_model] + self.fallback_models

        for model_name in models_to_try:
            try:
                logging.info(f"Attempting to generate content using model: {model_name}")

                # Combine context and prompt if context is provided
                full_prompt = prompt
                if context:
                    full_prompt = f"{context}\n\n{prompt}"

                response = self.client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview",
                    contents=full_prompt
                )

                if response.text:
                    logging.info(f"Successfully generated content using model: {model_name}")
                    return response.text.strip()
                else:
                    logging.warning(f"No content returned from model: {model_name}")

            except Exception as e:
                logging.error(f"Failed to generate content with model {model_name}: {str(e)}")
                continue  # Try next model in fallback sequence

        logging.error("All models failed to generate content")
        return None

    def validate_completion(self, task_content: str, result: str) -> bool:
        """
        Validate if the AI-generated result adequately completes the task.

        Args:
            task_content: Original task content
            result: AI-generated result

        Returns:
            True if task appears to be completed satisfactorily, False otherwise
        """
        # Basic validation - in a real implementation this would be more sophisticated
        if not result or len(result.strip()) == 0:
            return False

        # Check if result contains meaningful content
        if len(result.strip().split()) < 3:
            return False

        # Placeholder for more sophisticated validation
        # Could include semantic similarity checks, task-specific validation, etc.
        return True

# Global instance for easy access
ai_processor = AIProcessor()

def get_ai_processor():
    """Return the global AI processor instance"""
    return ai_processor