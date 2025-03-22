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
    args=["/Users/bhavaniravi/projects/personal/airflow-mcp-server/src/airflow_mcp_server/__main__.py", "--unsafe"],
    env={
        "AIRFLOW_BASE_URL":"http://localhost:8080",
        "AIRFLOW_HOST":"http://localhost:8080",
        "AIRFLOW_USERNAME":"admin",
        "AIRFLOW_PASSWORD":"H8rVQ5Kd2N5pYCTB",
        "AUTH_TOKEN": "YWRtaW46SDhyVlE1S2QyTjVwWUNUQg==",
        "PYTHONPATH": "src/"
    }
)

async def _load_tools_raw():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print ("initializing session")
            await session.initialize()
            tools = await session.list_tools()
            # print (tools)
            return tools
        
def load_tools():
    print ("loading raw tools")
    tools = asyncio.run(_load_tools_raw())
    json_tools = [tool.model_dump(mode="python") for tool in tools.tools]
    for tool in json_tools:
        tool["input_schema"] = tool.pop("inputSchema")
    print ("\n\n\n",json_tools)
    return json_tools


async def call_tool(tool_name: str, sampling_callback=None, **arguments: dict[str, Any]):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=sampling_callback) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result

if __name__ == '__main__':
    print (load_tools())