from airflow_llm_plugin.models import db, LLMModelConfig
from airflow_llm_plugin.llm import get_llm_client
from airflow_llm_plugin.llm.openai_client import OpenAIClient
from airflow_llm_plugin.llm.anthropic_client import AnthropicClient
from airflow_llm_plugin.llm.gemini_client import GeminiClient

def get_available_providers():
    """Get all available LLM providers."""
    providers = [
        {
            "id": OpenAIClient.get_provider_name(),
            "name": "OpenAI",
            "models": OpenAIClient().get_available_models()
        },
        {
            "id": AnthropicClient.get_provider_name(),
            "name": "Anthropic Claude",
            "models": AnthropicClient().get_available_models()
        },
        {
            "id": GeminiClient.get_provider_name(),
            "name": "Google Gemini",
            "models": GeminiClient().get_available_models()
        }
    ]
    
    return providers

def get_model_configs():
    """Get all saved model configurations."""
    configs = db.session.query(LLMModelConfig).all()
    
    result = {
        "providers": get_available_providers(),
        "configs": [],
        "default": None
    }
    
    for config in configs:
        config_data = {
            "id": config.id,
            "provider": config.provider,
            "model_name": config.model_name,
            "default": config.default
        }
        
        result["configs"].append(config_data)
        
        if config.default:
            result["default"] = config_data
    
    # Create default config if none exists
    if not result["default"]:
        default_config = LLMModelConfig.get_default_config()
        result["default"] = {
            "id": default_config.id,
            "provider": default_config.provider,
            "model_name": default_config.model_name,
            "default": default_config.default
        }
        result["configs"].append(result["default"])
    
    return result

def save_model_config(provider, model_name):
    """Save a model configuration and set it as default."""
    # Validate that the provider and model are valid
    providers = get_available_providers()
    valid_provider = False
    valid_model = False
    
    for p in providers:
        if p["id"] == provider:
            valid_provider = True
            if model_name in p["models"]:
                valid_model = True
                break
    
    if not valid_provider:
        raise ValueError(f"Invalid provider: {provider}")
    
    if not valid_model:
        raise ValueError(f"Invalid model name for provider {provider}: {model_name}")
    
    # Set the new default configuration
    config = LLMModelConfig.set_default_config(provider, model_name)
    
    return config

def get_default_llm_client():
    """Get an LLM client using the default configuration."""
    config = LLMModelConfig.get_default_config()
    return get_llm_client(config.provider, config.model_name)
