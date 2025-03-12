from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Base abstract class for all LLM clients."""
    
    def __init__(self, config):
        """Initialize the LLM client with a specific model."""
        self.config = config

    
    @abstractmethod
    def get_completion(self, prompt, system_prompt=None, max_tokens=None):
        """Get a completion from the LLM.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str, optional): System instructions for the LLM
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        pass
    
    @abstractmethod
    def get_chat_completion(self, messages, max_tokens=None):
        """Get a chat completion from the LLM.
        
        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        pass
    
    @abstractmethod
    def get_available_models(self):
        """Get a list of available models for this provider.
        
        Returns:
            list: List of available model names
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.
        
        Returns:
            str: Provider name (e.g., 'openai', 'anthropic', etc.)
        """
        pass
