from airflow_llm_plugin.llm.base import LLMClient
from airflow_llm_plugin.llm.openai_client import OpenAIClient
from airflow_llm_plugin.llm.anthropic_client import AnthropicClient
from airflow_llm_plugin.llm.gemini_client import GeminiClient

def get_llm_client(provider, model_name):
    """Factory function to get the appropriate LLM client."""
    if provider == 'openai':
        return OpenAIClient(model_name)
    elif provider == 'anthropic':
        return AnthropicClient(model_name)
    elif provider == 'gemini':
        return GeminiClient(model_name)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
