import os
import json
from openai import OpenAI
from airflow_llm_plugin.llm.base import LLMClient

class OpenAIClient(LLMClient):
    """Client for OpenAI models."""
    
    def __init__(self, model_name=None):
        """Initialize the OpenAI client.
        
        Args:
            model_name (str, optional): The model to use (defaults to gpt-4o)
        """
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        model_name = model_name or "gpt-4o"
        super().__init__(model_name)
        
        # Initialize the OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    def get_completion(self, prompt, system_prompt=None, max_tokens=None):
        """Get a completion from OpenAI.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str, optional): System instructions for the LLM
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def get_chat_completion(self, messages, max_tokens=None):
        """Get a chat completion from OpenAI.
        
        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def get_available_models(self):
        """Get a list of available OpenAI models.
        
        Returns:
            list: List of available model names
        """
        # Focus on chat completion models
        models = [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        return models
    
    @classmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.
        
        Returns:
            str: Provider name
        """
        return "openai"
