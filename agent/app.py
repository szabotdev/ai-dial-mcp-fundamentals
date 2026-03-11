import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    #TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    # 2. Get Available MCP Resources and print them
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
    # 4. Create DialClient
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
    # 6. Add to messages Prompts from MCP server as User messages
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
    mcp_client = MCPClient(mcp_server_url="http://localhost:8005/mcp")
    async with mcp_client as mcp_client:
        print("\n=== Available Resources ===")
        resources: List[Resource] = await mcp_client.get_resources()
        for resource in resources:
            print(resource)
        
        print("\n=== Available Tools ===")
        tools: List[Tool] = await mcp_client.get_tools()
        for tool in tools:
            print(tool)

        dial_client = DialClient(
            endpoint="https://ai-proxy.lab.epam.com",
            api_key=os.getenv("DIAL_API_KEY"),
            tools=tools,
            mcp_client=mcp_client,
        )

        messages: List[Message] = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT),
        ]

        print("\n=== Available Prompts ===")
        prompts: List[Prompt] = await mcp_client.get_prompts()
        for prompt in prompts:
            print(prompt)
            content = await mcp_client.get_prompt(prompt.name)
            print(content)
            messages.append(
                Message(
                    role=Role.USER,
                    content=f"## Prompt provided by MCP server:\n{prompt.description}\n{content}"
                )
            )

        print("MCP-based Agent is ready! Type your query or 'exit' to exit.")
        while True:
            user_input = input("> ").strip()
            if user_input.lower() == "exit":
                break
            messages.append(Message(role=Role.USER, content=user_input))
            response = await dial_client.get_completion(messages)
            messages.append(response)    


if __name__ == "__main__":
    asyncio.run(main())
