from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("MultiToolServer")

@mcp.tool()
def hello(name: str) -> str:
    """
    사용자에게 개인화된 인사말을 생성하는 도구

    매개변수:
    - name (str): 인사말에 사용할 이름
    반환값 :
    - (str): "Hello, {name}" 형태의 인사말
    """
    return f"Hello, {name}"

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    두 숫자를 더하는 도구

    매개변수:
    - a (int): 더할 첫 번째 숫자
    - b (int): 더할 두 번째 숫자
    반환값 :
    - (int): 두 숫자의 합
    """
    return a + b

@mcp.tool()
def now() -> str:
    """
    현재 시간을 반환하는 도구

    매개변수 : 없음
    반환값 :
    - (str): 현재 시간 (형식: YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
    # 우리가 만든것은? 표준 입출력으로 mcp 프로토콜을 통해서 json-rpc로 통신하는 mcp 서버 개발 완료
