# namhyungo's mbr parser
import sys

partitions = []
SIZE = 16
SECTOR_SIZE = 512

def parse_ebr(f, base_ebr, offset):
    for i in range(2):
        current_ebr_byte_pos = (base_ebr + offset) * SECTOR_SIZE
        f.seek(current_ebr_byte_pos + 446 + i * SIZE)
        entry = f.read(SIZE)

        file_type = entry[4]

        if file_type == 0x07:
            partitions.append({
                    "start_sector": base_ebr + offset + int.from_bytes(entry[8:12], 'little'),
                    "total_sectors": int.from_bytes(entry[12:], 'little'),
                })
        elif file_type == 0x05:
            off = int.from_bytes(entry[8:12], 'little')
            parse_ebr(f, base_ebr, off)
        else:
            continue

def parse_mbr(f):
    f.seek(446)
    partition_table = f.read(4 * SIZE)

    for i in range(4):
        entry = partition_table[i * SIZE : (i + 1) * SIZE]

        file_type = entry[4]
        if file_type == 0x07:
            partitions.append({
                    "start_sector": int.from_bytes(entry[8:12], 'little'),
                    "total_sectors": int.from_bytes(entry[12:], 'little'),
                })
        elif file_type == 0x05:
            base_ebr = int.from_bytes(entry[8:12], 'little')
            parse_ebr(f, base_ebr, 0)
        else:
            continue

def main():
    # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
    if len(sys.argv) < 2:
        print(f"사용법: python {sys.argv[0]} <disk_image.dd>")
        sys.exit(1)

    # 파일 경로 저장 후 사용 & # 파일 열고 바이너리로 읽기
    dd_filepath = sys.argv[1]
    try:
        with open(dd_filepath, 'rb') as f:       
            f.seek(510) # boot code(446byte)와 파티션 테이블 엔트리(64byte) 건너 뛰기 & mbr 헤더에서 시그니처 찾기
            boot_sig = f.read(2)
            
            if boot_sig != b'\x55\xAA': # mbr boot signiture가 존재할때 함수 호출
                print("boot_sig err")
                sys.exit(1)
            parse_mbr(f)
            
            f.close()

            if not partitions: # 파티션 없으면 종료
                print("파티션이 없습니다.")
            else:
                for p in partitions:  # 파티션 값들 출력
                    print(p['start_sector'], p['total_sectors'])

    except FileNotFoundError: # 파일 탐색 오류
        print("파일을 찾을 수 없습니다.")
    except Exception as e: # 기타 에러 발생
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()