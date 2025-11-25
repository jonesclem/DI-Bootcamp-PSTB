# server.py

"""
Minimal MCP server using FastMCP.

This server exposes:
- one tool:    add(a, b) -> a + b
- one resource: greeting://{name} -> "Hello, {name}!"

It communicates with clients over STDIO (standard input/output),
which is how a local MCP client will talk to it.
"""

# Import the FastMCP helper class from the MCP Python SDK.
# FastMCP takes care of almost all the MCP boilerplate for you.
from mcp.server.fastmcp import FastMCP

# Create an MCP server instance.
# The string "Demo" is the server's name and is what clients will see.
mcp = FastMCP("Demo")


# -------------------------
# Tool definition: add(a,b)
# -------------------------

# The @mcp.tool() decorator registers this function as an MCP *tool*.
# Tools are actions the client (or LLM) can call, like RPC methods.
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two integers and return the sum.

    Parameters
    ----------
    a : int
        First integer to add.
    b : int
        Second integer to add.

    Returns
    -------
    int
        The sum of a and b.
    """
    # Actual implementation: just return the sum.
    # FastMCP will handle serializing/deserializing arguments and results.
    return a + b


# -----------------------------
# Resource definition: greeting
# -----------------------------

# The @mcp.resource decorator registers a *resource*.
# The string "greeting://{name}" is a URI template:
# - The "{name}" part is a path parameter.
# - When a client requests e.g. "greeting://Alice",
#   FastMCP will call this function with name="Alice".
@mcp.resource("greeting://{name}")
def greet(name: str) -> str:
    """
    Return a greeting for the given name.

    Parameters
    ----------
    name : str
        The name to greet, taken from the URI template.

    Returns
    -------
    str
        A greeting message like "Hello, Alice!".
    """
    # Build and return the greeting string using an f-string.
    return f"Hello, {name}!"


# -----------------
# Server entrypoint
# -----------------

# This block runs only when you execute this file directly, e.g.:
#   python server.py
#
# It will *not* run if the module is imported from somewhere else,
# which is a common Python pattern.
if __name__ == "__main__":
    # Start the MCP server event loop using STDIO as the transport.
    #
    # transport="stdio" means:
    # - Read requests from standard input (stdin)
    # - Write responses to standard output (stdout)
    #
    # An MCP client that launches this script will connect over STDIO
    # and can then discover the `add` tool and `greeting://{name}` resource.
    mcp.run(transport="stdio")