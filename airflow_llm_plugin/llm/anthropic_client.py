import os
import sys
from anthropic import Anthropic, NOT_GIVEN
from airflow_llm_plugin.llm.base import LLMClient
from airflow_llm_plugin.mcp_tools.mcp_client import call_tool
import asyncio

class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models."""
    
    def __init__(self, config, tools):
        super().__init__(config)
        self.tools = tools
        self.client = Anthropic(api_key=self.config.api_key)
        self.final_text = []


    def process_response(self, response, messages):
        # print ("\n\n==========messages=========\n\n", messages, "\n\n", response)

        assistant_message_content = []
        for content in response.content:
            print ("processing......",content.type, content.type=='text')
            if content.type == 'text':
                self.final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = asyncio.run(call_tool(tool_name, tool_args))
                # print ("\n\n\n ============ \n\n tool call result is here", result)
                # final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })
                self.get_chat_completion(messages)

        print ("======================final text========", self.final_text)
        return "\n".join(self.final_text)

    def get_completion(self, prompt, system_prompt=None, max_tokens=20):
        """Get a completion from Anthropic.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str, optional): System instructions for the LLM
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        response = self.client.beta.messages.create(
            model=self.config.model_name,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=self.tools,
            max_tokens=max_tokens,
            # betas=["token-efficient-tools-2025-02-19"] # 'claude-3-5-sonnet-20241022' does not support token-efficient tool use.
        )
        return self.process_response(response, [])
    
    def get_chat_completion(self, messages, max_tokens=500):
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
        
        print ("getting chat completions", chat_messages)
        response = self.client.beta.messages.create(
            model=self.config.model_name,
            system=system_message,
            messages=chat_messages,
            max_tokens=max_tokens,
            tools=self.tools,
            # betas=["token-efficient-tools-2025-02-19"],
        )

        return self.process_response(response, messages)
        
    
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
