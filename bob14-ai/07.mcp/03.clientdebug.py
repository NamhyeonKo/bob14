import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 프록시를 통해 디버그 서버와 연결
    server_params = StdioServerParameters(
        command="python3", 
        args=["07.mcp/simple_proxy.py", "07.mcp/hello_serverdebug.py"]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 사용 가능한 도구 목록 가져오기
                tools = await session.list_tools()

                # hello 도구 테스트
                result = await session.call_tool("hello", {"name": "Alice"})

                # add_numbers 도구 테스트  
                result = await session.call_tool("add_numbers", {"a": 10, "b": 20})

                # get_server_info 도구 테스트
                result = await session.call_tool("get_server_info", {})

    except Exception as e:
        # 오류만 stderr로 출력
        import sys
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    # 잠시 대기 후 종료 (로그 파일 쓰기 완료 대기)
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())