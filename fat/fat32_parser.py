# namhyungo's FAT32 parser
import sys
import uuid

def parse_fat32(f):
    f.seek(0)
    vbr = f.read(512)  # 첫번째 섹터에서 얻는 정보들
    
    bps = int.from_bytes(vbr[11:11+2], 'little') # byte per sector # 0x200 = 512
    spc = int.from_bytes(vbr[13:13+1], 'little') # sector per cluster # 0x2 = 2
    cluster_size = bps * spc # 클러스터 사이즈 = bps * spc # 1024

    reserved_sector_count = int.from_bytes(vbr[14:14+2], 'little') # 0x1b3e = 
    number_of_fats = int.from_bytes(vbr[16:16+1], 'little')
    number_of_heads = int.from_bytes(vbr[26:26+2], 'little')   # 0xff =
    total_secter32 = int.from_bytes(vbr[32:32+4], 'little')    # 0x028000 = 
    fat32_size = int.from_bytes(vbr[36:36+4], 'little')    # 0x0261 = 
    root_dir_cluster = int.from_bytes(vbr[44:44+4], 'little')  # 0x02 = 

    print(f"BPS: {bps}, SPC: {spc}, Cluster Size: {cluster_size}")
    print(f"Reserved Sectors: {reserved_sector_count}, FATs: {number_of_fats}, FAT Size: {fat32_size}")
    print(f"Root Directory starts at cluster: {root_dir_cluster}")

    # LBA 계산
    fat1_start_lba = reserved_sector_count
    data_area_start_lba = fat1_start_lba + (number_of_fats * fat32_size)

    print(f"FAT#1 starts at LBA: {fat1_start_lba}")
    print(f"Data Area starts at LBA: {data_area_start_lba}")

    return 

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
            f.seek(510)
            boot_sector_signiture = f.read(2)   # 0x55AA
            f.seek(82)
            file_system_type = f.read(8) #  헤더에서 타입 찾기 FAT32인지 확인 하고 비교 # 0x4641543332202020
            if boot_sector_signiture == b"\x55\xAA" and file_system_type == b"FAT32   ":
                parse_fat32(f)

    # 파일 탐색 오류
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    # 기타 에러 발생
    except Exception as e:
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()