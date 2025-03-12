# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


server_params = StdioServerParameters(
    command="/Users/bhavaniravi/projects/airflow-local/venv/bin/python",
    args=["/Users/bhavaniravi/projects/personal/mcp-server-apache-airflow/src/server.py"],
    env={
        "AIRFLOW_HOST":"http://localhost:8080",
        "AIRFLOW_USERNAME":"admin",
        "AIRFLOW_PASSWORD":"H8rVQ5Kd2N5pYCTB"
    }
)

async def _load_tools_raw():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools
        
def load_tools():
    tools = asyncio.run(_load_tools_raw())

    json_tools = [tool.model_dump(mode="python") for tool in tools.tools]
    for tool in json_tools:
        tool["input_schema"] = tool.pop("inputSchema")
    return json_tools


async def call_tool(tool_name: str, sampling_callback=None, **arguments: dict[str, Any]):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=sampling_callback) as session:
            # Initialize the connection
            await session.initialize()

            # Call a tool
            result = await session.call_tool(tool_name, arguments=arguments)
            return result