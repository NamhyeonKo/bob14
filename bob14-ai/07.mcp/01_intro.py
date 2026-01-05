import mcp
from importlib.metadata import version

print(f"mcp version: {version('mcp')}")
print(f"mcp package location: {mcp.__file__}")

import inspect
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession

print(inspect.getdoc(FastMCP))
print(inspect.getdoc(ClientSession))