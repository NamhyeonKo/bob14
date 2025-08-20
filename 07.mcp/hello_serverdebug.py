# -*- coding: utf-8 -*-
import sys
import json
from mcp.server.fastmcp import FastMCP

def debug_log(msg):
    """Debug log to stderr"""
    print(f"[DEBUG] {msg}", file=sys.stderr, flush=True)

mcp = FastMCP("HelloWorldDebug")

@mcp.tool()
def hello(name: str) -> str:
    """Return greeting message"""
    debug_log(f"hello function called, name={name}")
    result = f"Hello, {name}! (from debug server)"
    debug_log(f"hello function result: {result}")
    return result

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    debug_log(f"add_numbers function called, a={a}, b={b}")
    result = a + b
    debug_log(f"add_numbers function result: {result}")
    return result

@mcp.tool()
def get_server_info() -> dict:
    """Return server information"""
    debug_log("get_server_info function called")
    result = {
        "server_name": "HelloWorldDebug",
        "version": "1.0.0",
        "tools": ["hello", "add_numbers", "get_server_info"]
    }
    debug_log(f"get_server_info function result: {result}")
    return result

if __name__ == "__main__":
    debug_log("HelloWorldDebug server starting")
    mcp.run()