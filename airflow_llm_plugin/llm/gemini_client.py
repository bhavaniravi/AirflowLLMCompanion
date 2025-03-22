import os
import google.generativeai as genai
from airflow_llm_plugin.llm.base import LLMClient
from google.generativeai import types as genai_types
from typing import Dict, Any

class GeminiClient(LLMClient):
    """Client for Google Gemini models."""

    def __init__(self, config, tools, system_prompt=None):
        """Initialize the Gemini client.
        
        Args:
            model_name (str, optional): The model to use
        """
        super().__init__(config)
        self.tools = genai_types.FunctionLibrary([self.to_gemini_tool(tool) for tool in tools])
        self.system_prompt = system_prompt
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(model_name=self.config.model_name, tools=self.tools, system_instruction=self.system_prompt)

    

    def to_gemini_tool(self, mcp_tool: Dict[str, Any]) -> genai_types.Tool:
        """
        Converts an MCP tool schema (from JSON) to a Gemini tool.

        Args:
            mcp_tool: The MCP tool in dictionary format containing name, description, and input schema.

        Returns:
            A Gemini tool with the appropriate function declaration.
        """
        function_declaration = self.to_gemini_function_declarations(mcp_tool)
        tool = genai_types.Tool(function_declarations=[function_declaration])
        print (tool)
        return tool

    def to_gemini_function_declarations(self, mcp_tool: Dict[str, Any]) -> genai_types.FunctionDeclaration:
        """
        Converts the MCP tool's input schema into a Gemini function declaration.

        Args:
            mcp_tool: The MCP tool dictionary.

        Returns:
            A Gemini function declaration.
        """
        required_params: list[str] = mcp_tool["input_schema"].get("required", [])
        properties = {}

        # Loop through the properties of the MCP tool and convert them
        for key, value in mcp_tool["input_schema"].get("properties", {}).items():
            schema_dict = {
                "type": value.get("type", "STRING").upper(),  # Use uppercase for the type
                "description": value.get("title", ""),  # Assuming title as description
            }
            # Map to SchemaDict
            properties[key] = schema_dict

        # Create the function declaration for Gemini
        parameters = None if not properties else {
            "type": "OBJECT",
            "properties": properties,
            "required": required_params,
        }
        function_declaration = genai_types.FunctionDeclaration(
            name=mcp_tool["name"],
            description=mcp_tool["description"],
            parameters=parameters
        )
        return function_declaration
        
    
    def get_chat_completion(self, messages, max_tokens=None):
        """Get a chat completion from Gemini.
        
        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int, optional): Maximum tokens for the response
            
        Returns:
            str: The LLM's completion text
        """
        generation_config = {}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Convert the messages to Gemini's format
        chat_history = []
        for msg in messages:
            if msg['role'] == 'system':
                chat_history.append({"role": "system", "parts": [msg['content']]})
            elif msg['role'] == 'user':
                chat_history.append({"role": "user", "parts": [msg['content']]})
            elif msg['role'] == 'assistant':
                chat_history.append({"role": "model", "parts": [msg['content']]})
        
        print ("\n\n\n", chat_history)
        if chat_history:
            chat = self.model.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
            response = chat.send_message(
                chat_history[-1]["parts"][0],
                generation_config=generation_config if generation_config else None
            )
        else:
            # No history, just send a single message
            response = self.model.generate_content(
                self.system_prompt, 
                generation_config=generation_config if generation_config else None
            )
        
        return response.text
    
    def get_available_models(self):
        """Get a list of available Gemini models.
        
        Returns:
            list: List of available model names
        """
        models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
            "gemini-1.0-ultra"
        ]
        
        return models
    
    @classmethod
    def get_provider_name(cls):
        """Get the name of the LLM provider.
        
        Returns:
            str: Provider name
        """
        return "gemini"
