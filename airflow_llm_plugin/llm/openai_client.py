import os
import json
from openai import OpenAI
from openai import AsyncOpenAI
from airflow_llm_plugin.llm.base import LLMClient

from mcp_agent.config import MCPSettings, MCPServerSettings
from airflow_llm_plugin.mcp_tools import mcp_client
# from airflow_llm_plugin.api import model_config
import asyncio

from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)

class AgentContext:
    def __init__(self):
        self.mcp_config = MCPSettings(
            servers={
                "airflow_api_mcp": MCPServerSettings(
                    command=mcp_client.server_params.command,
                    args=mcp_client.server_params.args,
                    env=mcp_client.server_params.env
                ),
            }
        )



class OpenAIClient(LLMClient):
    """Client for OpenAI models."""
    
    def __init__(self, config, tools, system_prompt: str=None):
        """Initialize the OpenAI client.
        
        Args:
            model_name (str, optional): The model to use (defaults to gpt-4o)
        """
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        self.tools = tools
        self.system_prompt = system_prompt
        set_default_openai_client(client=self.client, use_for_tracing=False)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(disabled=True)
        self.agent = Agent(
            name="Airflow LLM interface",
            instructions="You only respond in haikus.",
            model=config.model_name,
            mcp_servers=["airflow_api_mcp"]
        )
        self.context = AgentContext()

    
    def get_chat_completion(self, messages, max_tokens=None):
        print (messages)
        run_result = asyncio.run(Runner.run(self.agent, input=messages, context=self.context))
        return run_result.final_output
    
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
