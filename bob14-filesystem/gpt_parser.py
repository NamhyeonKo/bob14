# namhyungo's gpt parser
import sys
import uuid

def parse_gpt(f):
    f.seek(512) # gpt 헤더 (512byte) 읽기
    header = f.read(92)

    partition_array_lba = int.from_bytes(header[72:80], 'little')
    num_entries = int.from_bytes(header[80:84], 'little')
    entry_size = int.from_bytes(header[84:88], 'little')
    
    f.seek(partition_array_lba * 512) # 파티션 엔트리 배열로 이동

    partitions = []
    for i in range(num_entries):
        entry = f.read(entry_size)
        if not entry: break

        partition_type_guid = uuid.UUID(bytes_le = entry[0:16])
        if partition_type_guid.int == 0: continue

        partition_info = {
            "guid": entry[16:32],
            "start_sector": int.from_bytes(entry[32:40], 'little'),
            "total_sectors": int.from_bytes(entry[40:48], 'little') - int.from_bytes(entry[32:40], 'little') + 1
        }
        partition_info["size_gb"] = (partition_info['total_sectors'] * 512) / (1024**3)

        partitions.append(partition_info)

    return partitions

def main():
    if len(sys.argv) < 2: # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
        print(f"사용법: python {sys.argv[0]} <disk_image.dd>")
        sys.exit(1)
    
    dd_filepath = sys.argv[1] # 파일 경로 저장 후 열기
    try:
        with open(dd_filepath, 'rb') as f:
            f.seek(512)
            gpt_signiture = f.read(8) # gpt 헤더에서 시그니처 찾기 & gpt 시그니처가 gpt를 지칭할 때만 함수 호출
            if gpt_signiture != b'EFI PART':
                print("Not GPT")
                sys.exit(1)
            partitions = parse_gpt(f)
            
            f.close()

            if not partitions: # 파티션 없으면 종료
                print("파티션이 없습니다.")
            else:
                for p in partitions: print(p['guid'].hex().upper(), p['start_sector'], p['total_sectors']) # 파티션 값들 출력

    except FileNotFoundError: # 파일 탐색 오류
        print("파일을 찾을 수 없습니다.")
    except Exception as e:  # 기타 에러 발생
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()