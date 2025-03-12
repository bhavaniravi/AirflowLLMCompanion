from airflow_llm_plugin.llm.base import LLMClient
from airflow_llm_plugin.llm.openai_client import OpenAIClient
from airflow_llm_plugin.llm.anthropic_client import AnthropicClient
from airflow_llm_plugin.llm.gemini_client import GeminiClient


def get_llm_client(config):
    """Factory function to get the appropriate LLM client."""
    provider = config.provider.value
    if provider == 'openai':
        return OpenAIClient(config)
    elif provider == 'anthropic':
        return AnthropicClient(config)
    elif provider == 'gemini':
        return GeminiClient(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
