import os
import google.generativeai as genai
from airflow_llm_plugin.llm.base import LLMClient

class GeminiClient(LLMClient):
    """Client for Google Gemini models."""

    def __init__(self, model_name=None):
        """Initialize the Gemini client.
        
        Args:
            model_name (str, optional): The model to use
        """
        super().__init__()
    
        
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(model_name=self.config.model_name)
    def get_completion(self, prompt, system_prompt=None, max_tokens=None):
        """Get a completion from Gemini.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str, optional): System instructions for the LLM
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        generation_config = {}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        chat = self.model.start_chat(
            history=[] if not system_prompt else [
                {"role": "user", "parts": ["You are a helpful assistant with these instructions: " + system_prompt]},
                {"role": "model", "parts": ["I understand and will follow these instructions."]}
            ]
        )
        
        response = chat.send_message(
            prompt, 
            generation_config=generation_config if generation_config else None
        )
        
        return response.text
    
    def get_chat_completion(self, messages, max_tokens=None):
        """Get a chat completion from Gemini.
        
        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        generation_config = {}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Convert the messages to Gemini's format
        chat_history = []
        for msg in messages:
            if msg['role'] == 'system':
                # For Gemini, we'll make a system message a user message with special formatting
                chat_history.append({
                    "role": "user", 
                    "parts": ["You are a helpful assistant with these instructions: " + msg['content']]
                })
                chat_history.append({
                    "role": "model", 
                    "parts": ["I understand and will follow these instructions."]
                })
            elif msg['role'] == 'user':
                chat_history.append({"role": "user", "parts": [msg['content']]})
            elif msg['role'] == 'assistant':
                chat_history.append({"role": "model", "parts": [msg['content']]})
        
        # If we have history, we'll create a chat with it
        if chat_history:
            chat = self.model.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
            response = chat.send_message(
                chat_history[-1]["parts"][0],
                generation_config=generation_config if generation_config else None
            )
        else:
            # No history, just send a single message
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config if generation_config else None
            )
        
        return response.text
    
    def get_available_models(self):
        """Get a list of available Gemini models.
        
        Returns:
            list: List of available model names
        """
        models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
            "gemini-1.0-ultra"
        ]
        
        return models
    
    @classmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.
        
        Returns:
            str: Provider name
        """
        return "gemini"
