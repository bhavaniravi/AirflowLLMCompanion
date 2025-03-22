import os
import sys
from anthropic import Anthropic, NOT_GIVEN
from airflow_llm_plugin.llm.base import LLMClient
from airflow_llm_plugin.mcp_tools.mcp_client import call_tool
import asyncio


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, config, tools, system_prompt=None):
        super().__init__(config)
        self.tools = tools
        self.client = Anthropic(api_key=self.config.api_key, base_url=config.base_url)
        self.final_text = []
        self.system_prompt = system_prompt
        self.loop_count = 0

    def process_response(self, response, messages):
        self.loop_count += 1
        if self.loop_count == 3:
            print("loop count=", self.loop_count)
            return "end of text"
        assistant_message_content = []
        for content in response.content:
            print(
                "processing......",
                getattr(content, "name", None),
                content.type,
                content.type == "text",
            )
            if content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = asyncio.run(call_tool(tool_name, tool_args))

                assistant_message_content.append(content)
                messages.append(
                    {"role": "assistant", "content": assistant_message_content}
                )
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result.content,
                            }
                        ],
                    }
                )
                self.get_chat_completion(messages)

        return "\n".join(self.final_text)

    def get_chat_completion(self, messages, max_tokens=500, final_text=""):
        """Get a chat completion from Anthropic.

        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response

        Returns:
            str: The LLM's completion text
        """
        self.loop_count += 1
        print(f"loop count={self.loop_count}")
        final_text = final_text.split("\n")

        response = self.client.messages.create(
            model=self.config.model_name,
            system=self.system_prompt,
            messages=messages,
            max_tokens=max_tokens,
            tools=self.tools,
        )

        if self.loop_count == 10:
            return "\n".join(final_text)
        


        loop_messages = []
        for content in response.content:
            if content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                result = asyncio.run(call_tool(tool_name, tool_args))
                loop_messages.append(
                    {
                        "type": "tool_use",
                        "id": content.id,
                        "name": tool_name,
                        "input": tool_args,
                    }
                )
                result = asyncio.run(call_tool(tool_name, tool_args))
                loop_messages.append("figure out which of these keys are required for next tool call and give it in a json format")
                # add all system messages until this point
                messages.append({"role": "assistant", "content": loop_messages})
                loop_messages = []

                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result.content,
                            }
                        ],
                    }
                )
                self.loop_count += 1
                print ("Recalling with", messages)
                self.get_chat_completion(messages, final_text="\n".join(final_text))
            elif content.type == "text":
                print("processing text", content.text)
                loop_messages.append({"type": "text", "text": content.text})
                final_text.append(content.text)
            else:
                print ("unhandled content type")
                print (content)
            

        return "\n".join(final_text)

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
            "claude-2.0",
        ]

        return models

    @classmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.

        Returns:
            str: Provider name
        """
        return "anthropic"
