import json
import sys
import subprocess
import threading

def log_message(msg):
    with open("07.mcp/debug.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.flush()

def main():
    server_file = sys.argv[1]

    with open("07.mcp/debug.log", "w", encoding="utf-8") as f:
        f.write("=== MCP 디버그 로그 ===\n")

    log_message(f"[proxy] 서버 시작 : {server_file}")
    server = subprocess.Popen(
        [sys.executable, server_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def log_server_stderr():
        while True:
            try:
                line = server.stderr.readline()
                if not line:
                    break
                log_message(f"[server stderr] {line.strip()}")
            except:
                break

    stderr_thread = threading.Thread(target=log_server_stderr, daemon=True)
    stderr_thread.start()

    def read_from_server():
        while True:
            try:
                line = server.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        log_message(f"[server->client] {json.dumps(msg, indent=2)}")
                    except:
                        log_message(f"[server->client] {line}")

                    print(line,flush=True)
            except Exception as e:
                log_message(f"[error] {str(e)}")
                break

    server_thread = threading.Thread(target=read_from_server, daemon=True)
    server_thread.start()

    try:
        # 클라이언트 입력 처리
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if line:
                # 클라이언트 -> 서버 로그
                try:
                    msg = json.loads(line)
                    log_message(f"[client->server] {json.dumps(msg, indent=2)}")
                except:
                    log_message(f"[client->server] {line}")
                
                # 서버로 전달
                server.stdin.write(line + "\n")
                server.stdin.flush()
    except Exception as e:
        log_message(f"[error] {str(e)}")
    finally:
        server.terminate()
        log_message("[proxy] 서버 종료")

if __name__ == "__main__":
    main()