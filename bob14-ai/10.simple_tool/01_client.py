import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python", args=["10.simple_tool/server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print('-'*20)
            print("MCP 서버 정보")
            print('-'*20)

            print(f"연결 상태: {'연결됨' if session else '연결 안됨'}")
            print(f"\n사용 가능한 도구:")
            tools_response = await session.list_tools()
            if tools_response and hasattr(tools_response, 'tools') and tools_response.tools:
                for i, tool in enumerate(tools_response.tools, 1):
                    print(f"{i}. {tool.name}: {tool.description}")
                    if hasattr(tool, 'parameters'):
                        print(f"   파라미터: {tool.parameters}")

                    print()
            else:
                print("도구가 없습니다.")
            print("\n도구 실행 데모")
            res1 = await session.call_tool("hello", {"name": "bob"})
            print(f"- hello 툴 실행 호출 결과: {res1.content[0].text}")
            
            res2 = await session.call_tool("add", {"a": 5, "b": 10})
            print(f"- add 툴 실행 호출 결과: {res2.content[0].text}")

            res3 = await session.call_tool("now")
            print(f"- now 툴 실행 호출 결과: {res3.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())