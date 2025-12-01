# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This script is a manual test of MCP integration:
# - Loads MCP servers from config.py (external + custom)
# - Uses MCPMultiClient to:
#   * list a directory with the external "files" server
#   * read a file with the external "files" server
#   * clean the text with the custom "local_insights" server (my_mcp_server.py)
#   * generate JSON insights with the custom tool
# This demonstrates composition of ≥ 2 external servers + the custom server
# WITHOUT using the LLM (pure integration test).


from __future__ import annotations

import asyncio
from config import load_mcp_server_configs
from mcp_multi_client import MCPMultiClient


async def main() -> None:
    configs = load_mcp_server_configs()

    print("=== CONFIGURED SERVERS ===")
    for cfg in configs:
        print(f"- {cfg.name}: {cfg.command} {' '.join(cfg.args)}")

    print("\n=== CONNECTING TO MCP SERVERS ===")
    async with MCPMultiClient(configs, debug=True) as client:
        print("\n=== DISCOVERED MCP TOOLS ===")
        for name, td in client.tools.items():
            print(f"- {name} (server={td.server_name})")

        required = {
            "files__listDirectory",
            "files__readFile",
            "local_insights__clean_text",
            "local_insights__generate_insights",
        }

        if not required.issubset(client.tools.keys()):
            print("\nERROR: Missing some required tools for the demo.")
            return

        print("\n=== MULTI-SERVER COMPOSITION DEMO ===")

        print("\n1) Listing folder with filesystem MCP:")
        listing = await client.call_tool(
            "files__listDirectory",
            {"path": "/home/yacine/mcp_root"},
        )
        print(listing)

        print("\n2) Reading test.txt with filesystem MCP:")
        file_content = await client.call_tool(
            "files__readFile",
            {"path": "/home/yacine/mcp_root/test.txt"},
        )
        print(file_content)

        print("\n3) Cleaning text with custom MCP server:")
        cleaned = await client.call_tool(
            "local_insights__clean_text",
            {"text": file_content, "lowercase": True},
        )
        print(cleaned)

        print("\n4) Generating insights with custom MCP server:")
        insights = await client.call_tool(
            "local_insights__generate_insights",
            {"text": cleaned},
        )
        print(insights)

        print("\n=== TEST COMPLETED ===")


if __name__ == "__main__":
    asyncio.run(main())
