from airflow_llm_plugin.llm import get_llm_client
from airflow_llm_plugin.llm.openai_client import OpenAIClient
from airflow_llm_plugin.llm.anthropic_client import AnthropicClient
from airflow_llm_plugin.llm.gemini_client import GeminiClient
from airflow.configuration import conf
from pydantic import BaseModel
from pydantic.types import Enum
from airflow_llm_plugin.mcp_tools.mcp_client import load_tools
import logging
import os


logger = logging.getLogger(__name__)

class LLMProviderEnum(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

class LLMModelEnum(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GEMINI_PRO_EXPERIMENTAL="gemini-2.0-pro-exp-02-05"
    GPT_4 = "gpt-4o"
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"

class LLMModelConfig(BaseModel):
    provider: LLMProviderEnum
    model_name: LLMModelEnum
    api_key: str
    base_url: str | None = None

def get_model_configs():
    """Get all saved model configurations."""
    plugin_enabled = conf.get('airflow_llm_plugin', 'enabled', False)
    if not plugin_enabled:
        logger.info("plugin not enabled")
        raise Exception("plugin not enabled")
    provider = conf.get('airflow_llm_plugin', 'llm_provider')
    model = conf.get('airflow_llm_plugin', 'llm_model')
    api_key = os.environ.get('AIRFLOW__AIRFLOW_LLM_PLUGIN__LLM_API_KEY') or conf.get('airflow_llm_plugin', 'llm_api_key')
    base_url = os.environ.get('AIRFLOW__AIRFLOW_LLM_PLUGIN__LLM_BASE_URL') or conf.get('airflow_llm_plugin', 'llm_base_url', fallback=None)
    config = LLMModelConfig(provider=provider, model_name=model, api_key=api_key, base_url=base_url)
    return config


def get_default_llm_client():
    """Get an LLM client using the default configuration."""
    config = get_model_configs()
    tools = load_tools()
    # tools = tools[:5]
    return get_llm_client(config, tools)