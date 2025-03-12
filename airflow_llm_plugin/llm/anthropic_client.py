import os
import sys
from anthropic import Anthropic
from airflow_llm_plugin.llm.base import LLMClient

class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models."""
    
    def __init__(self, model_name=None):
        """Initialize the Anthropic client.
        
        Args:
            model_name (str, optional): The model to use
        """
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        # do not change this unless explicitly requested by the user
        model_name = model_name or "claude-3-5-sonnet-20241022"
        super().__init__(model_name)
        
        # Initialize the Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        
        self.client = Anthropic(api_key=api_key)
    
    def get_completion(self, prompt, system_prompt=None, max_tokens=None):
        """Get a completion from Anthropic.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str, optional): System instructions for the LLM
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        response = self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        return response.content[0].text
    
    def get_chat_completion(self, messages, max_tokens=None):
        """Get a chat completion from Anthropic.
        
        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        # Extract system message if it exists
        system_message = None
        chat_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                chat_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        response = self.client.messages.create(
            model=self.model_name,
            system=system_message,
            messages=chat_messages,
            max_tokens=max_tokens
        )
        
        return response.content[0].text
    
    def get_available_models(self):
        """Get a list of available Anthropic models.
        
        Returns:
            list: List of available model names
        """
        models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
        
        return models
    
    @classmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.
        
        Returns:
            str: Provider name
        """
        return "anthropic"
