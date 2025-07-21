# namhyungo's gpt parser
import struct
import sys
import uuid

def parse_gpt(f):
    # gpt 헤더 (512byte) 읽기
    f.seek(512)
    header = f.read(92)

    partition_array_lba = struct.unpack('<Q', header[72:80])[0]
    num_entries = struct.unpack('<I', header[80:84])[0]
    entry_size = struct.unpack('<I', header[84:88])[0]
    
    # 파티션 엔트리 배열로 이동
    f.seek(partition_array_lba * 512)

    partitions = []
    for i in range(num_entries):
        entry = f.read(entry_size)
        if not entry:
            break

        partition_type_guid = uuid.UUID(bytes_le = entry[0:16])
        if partition_type_guid.int == 0:
            continue

        unique_guid = entry[16:32]
        start_sector = struct.unpack('<Q', entry[32:40])[0]
        end_sector = struct.unpack('<Q', entry[40:48])[0]
        total_sectors = end_sector - start_sector + 1

        partitions.append({
            "guid": unique_guid,
            "start_sector": start_sector,
            "total_sectors": total_sectors,
            "size_gb": (total_sectors * 512) / (1024**3)
        })

    return partitions

def main():
    # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
    if len(sys.argv) < 2:
        print(f"사용법: python {sys.argv[0]} <disk_image.dd>")
        sys.exit(1)

    # 파일 경로 저장 후 사용
    dd_filepath = sys.argv[1]

    # 파일 열고 바이너리로 읽기
    try:
        with open(dd_filepath, 'rb') as f:
            # 보호 mbr (512byte) 건너 뛰기
            f.seek(512)
            # gpt 헤더에서 시그니처 찾기
            gpt_signiture = f.read(8)

            # gpt 시그니처가 gpt를 지칭할 때만 함수 호출
            if gpt_signiture == b'EFI PART':
                partitions = parse_gpt(f)
            
            f.close()

            # 파티션 없으면 종료
            if not partitions:
                print("파티션이 없습니다.")
                return
            
            # 파티션 값들 출력
            for p in partitions:
                print(
                    p['guid'].hex().upper(),
                    p['start_sector'],
                    p['total_sectors']
                )

    # 파일 탐색 오류
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    # 기타 에러 발생
    except Exception as e:
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()