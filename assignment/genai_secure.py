import re
import time

# --- 1. 사용자 디바이스 (User Device) ---
class UserDevice:
    """사용자 기기를 시뮬레이션합니다."""
    def __init__(self, proxy_module):
        self.proxy_module = proxy_module
        print("💻 사용자 디바이스가 준비되었습니다.")

    def get_user_input(self):
        """사용자로부터 원본 데이터를 입력받습니다."""
        # 예시: 민감 정보(주민등록번호, 이메일)가 포함된 텍스트
        raw_data = "안녕하세요, 제 이름은 고남현이고, 주민등록번호는 950101-1234567 입니다. 문의는 namhyun@go.com 으로 주세요."
        print(f"\n[Step 1. 사용자 입력]\n   - 원본 데이터: \"{raw_data}\"")
        return raw_data

    def start_process(self):
        """전체 프로세스를 시작하고 최종 결과를 받습니다."""
        raw_data = self.get_user_input()
        # 프록시 모듈을 통해 데이터 처리 및 전송
        final_result = self.proxy_module.process_and_send(raw_data)
        self.display_result(final_result)

    def display_result(self, result):
        """AI 서버로부터 받은 최종 결과를 화면에 표시합니다."""
        print(f"\n[Step 7. 사용자 결과 확인]\n   - 최종 결과: \"{result}\"")


# --- 2. 디바이스 내 프록시 모듈 (Proxy Module on Device) ---
class ProxyModule:
    """디바이스 내에서 데이터를 난독화하고 프록시 서버로 전송합니다."""
    def __init__(self, proxy_server):
        self.proxy_server = proxy_server
        print("🔒 디바이스 내 프록시 모듈이 준비되었습니다.")

    def _obfuscate_data(self, raw_data):
        """
        데이터를 중간 산출물로 변환하고 민감 정보를 난독화합니다.
        (PoC에서는 텍스트 변환 및 정규식을 이용한 마스킹으로 시뮬레이션)
        """
        # 민감 정보 제거 (주민번호, 이메일)
        obfuscated_data = re.sub(r'\d{6}-\d{7}', '[JUMIN_REDACTED]', raw_data)
        obfuscated_data = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]', obfuscated_data)
        
        # 중간 산출물로 변환 (간단한 텍스트 뒤집기로 시뮬레이션)
        intermediate_output = obfuscated_data[::-1] # "....으로 주세요" -> "요세주 로으...."
        
        print(f"\n[Step 2. 데이터 난독화]\n   - 민감정보 제거: \"{obfuscated_data}\"")
        print(f"   - 중간 산출물 변환: \"{intermediate_output}\"")
        return intermediate_output

    def process_and_send(self, raw_data):
        """데이터를 난독화하여 프록시 서버로 전송하고 최종 결과를 반환받습니다."""
        intermediate_output = self._obfuscate_data(raw_data)
        
        print("\n[Step 3. 중간 산출물 전송 (디바이스 -> 프록시 서버)]")
        time.sleep(1) # 통신 시간 시뮬레이션
        
        # 프록시 서버로 중간 산출물 전송 및 최종 결과 수신
        final_result = self.proxy_server.handle_request(intermediate_output)
        return final_result

# --- 3. 프록시 서버 (Proxy Server) ---
class ProxyServer:
    """중간 산출물을 AI 서버에 전달하고 결과를 재변환하여 디바이스로 보냅니다."""
    def __init__(self, ai_server):
        self.ai_server = ai_server
        print("🌐 프록시 서버가 준비되었습니다.")

    def handle_request(self, intermediate_output):
        """디바이스로부터 요청을 받아 AI 서버로 전달하고 결과를 처리합니다."""
        print("   - 프록시 서버가 중간 산출물을 수신했습니다.")
        
        print("\n[Step 4. 추론 요청 (프록시 서버 -> AI 서버)]")
        time.sleep(1) # 통신 시간 시뮬레이션
        
        # AI 서버에 추론 요청
        ai_result = self.ai_server.run_inference(intermediate_output)
        
        # AI 결과를 사용자가 볼 수 있는 형태로 재변환하여 전송
        final_result = self._reconstruct_result(ai_result)
        
        print("\n[Step 6. 결과 재변환 및 전송 (프록시 서버 -> 디바이스)]")
        print(f"   - AI 결과 재변환: \"{final_result}\"")
        time.sleep(1) # 통신 시간 시뮬레이션
        
        return final_result
        
    def _reconstruct_result(self, ai_result):
        """AI의 결과를 사용자가 이해할 수 있는 형태로 재변환합니다."""
        # AI 결과가 중간 산출물과 유사한 형태(뒤집힌 텍스트)라고 가정하고 다시 원복
        reconstructed_text = ai_result[::-1]
        return reconstructed_text

# --- 4. AI 서버 (AI Server) ---
class AIServer:
    """클라우드에서 동작하는 AI 모델 서버를 시뮬레이션합니다."""
    def __init__(self):
        print("🤖 AI 서버가 준비되었습니다.")

    def run_inference(self, data):
        """입력된 중간 산출물을 기반으로 추론하고 결과를 생성합니다."""
        print("   - AI 서버가 중간 산출물을 기반으로 추론을 시작합니다.")
        time.sleep(2) # AI 추론 시간 시뮬레이션
        
        # PoC: 입력된 데이터에 AI의 답변을 덧붙이는 간단한 로직
        # 실제로는 이 데이터(벡터, 임베딩)를 기반으로 복잡한 연산 수행
        ai_response = f".다니입 답응 의IA {data}" # 뒤집힌 형태로 답변 생성
        
        print(f"\n[Step 5. AI 추론 및 결과 생성]\n   - AI 생성 결과(중간 형태): \"{ai_response}\"")
        return ai_response


# --- PoC 실행 ---
if __name__ == "__main__":
    # 1. 각 컴포넌트 초기화 (의존성 주입)
    ai_server = AIServer()
    proxy_server = ProxyServer(ai_server=ai_server)
    proxy_module = ProxyModule(proxy_server=proxy_server)
    user_device = UserDevice(proxy_module=proxy_module)
    
    print("\n" + "="*40)
    print("      생성형 AI 보안 PoC 워크플로우 시작")
    print("="*40)
    
    # 2. 사용자 디바이스에서 프로세스 시작
    user_device.start_process()