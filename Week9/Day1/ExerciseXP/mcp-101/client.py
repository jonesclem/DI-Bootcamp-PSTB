# client.py

import asyncio

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Configure how to start the MCP server process.
# This assumes we can run your server with: `mcp run server.py`
# (If not, we can change this to command="python", args=["server.py"])
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None,  # or a dict of env vars if needed
)


async def run():
    # Start the server as a subprocess and get its stdio streams
    async with stdio_client(server_params) as (read, write):
        # Wrap those streams in a high-level MCP ClientSession
        async with ClientSession(read, write) as session:
            # Perform the MCP handshake (capabilities, etc.)
            await session.initialize()

            # ------------------------
            # 1) List resources
            # ------------------------
            resources_result = await session.list_resources()
            print("=== Resources ===")
            for res in resources_result.resources:
                # Each `res` is a types.Resource
                print(f"- {res.uri}")
            print()

            # ------------------------
            # 2) List tools
            # ------------------------
            tools_result = await session.list_tools()
            print("=== Tools ===")
            for tool in tools_result.tools:
                # Each `tool` is a types.Tool
                print(f"- {tool.name}")
            print()

            # ------------------------
            # 3) Read greeting://hello
            # ------------------------
            # This hits the resource defined as greeting://{name}
            # with name="hello" → "Hello, hello!"
            greeting_result = await session.read_resource("greeting://hello")

            print("=== Read resource: greeting://hello ===")
            if greeting_result.contents:
                first = greeting_result.contents[0]
                # The server returns text content, so we check for that
                if isinstance(first, types.TextContent):
                    print("Resource text:", first.text)
                else:
                    print("Resource content (non-text):", first)
            else:
                print("No contents returned for greeting://hello")
            print()

            # ------------------------
            # 4) Call tool add(a=1, b=7)
            # ------------------------
            call_result = await session.call_tool("add", arguments={"a": 1, "b": 7})

            print("=== Call tool: add(1, 7) ===")
            # FastMCP typically returns the typed result in `structuredContent`
            if getattr(call_result, "structuredContent", None) is not None:
                print("Structured result:", call_result.structuredContent)
            elif call_result.content:
                first = call_result.content[0]
                if isinstance(first, types.TextContent):
                    print("Text result:", first.text)
                else:
                    print("Result (non-text):", first)
            else:
                print("No result content from add tool")
            print()


if __name__ == "__main__":
    asyncio.run(run())