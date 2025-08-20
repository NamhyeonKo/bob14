import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python3", 
        args=["07.mcp/hello_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("hello", {"name": "bob"})
        
            print(f"Result from server: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())