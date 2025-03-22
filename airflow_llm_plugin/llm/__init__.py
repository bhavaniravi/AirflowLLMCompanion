from airflow_llm_plugin.llm.base import LLMClient
from airflow_llm_plugin.llm.openai_client import OpenAIClient
from airflow_llm_plugin.llm.anthropic_client import AnthropicClient
from airflow_llm_plugin.llm.gemini_client import GeminiClient
from airflow_llm_plugin.llm.prompts import SYSTEM_PROMPT



def get_llm_client(config, tools):
    """Factory function to get the appropriate LLM client."""
    provider = config.provider.value
    if provider == 'openai':
        return OpenAIClient(config, tools, system_prompt=SYSTEM_PROMPT)
    elif provider == 'anthropic':
        return AnthropicClient(config, tools, system_prompt=SYSTEM_PROMPT)
    elif provider == 'gemini':
        return GeminiClient(config, tools, system_prompt=SYSTEM_PROMPT)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
