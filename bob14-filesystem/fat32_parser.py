# namhyungo's FAT32 parser
import sys

def parse_fat32_vbr(f):
    f.seek(0)
    vbr = f.read(512)  # 첫번째 섹터에서 얻는 정보들
    
    vbr_info = {
        'bps' : int.from_bytes(vbr[11:11+2], 'little'), # byte per sector # 0x200 = 512
        'spc' : int.from_bytes(vbr[13:13+1], 'little'), # sector per cluster # 0x2 = 2
        'reserved_sector_count' : int.from_bytes(vbr[14:14+2], 'little'), # 0x1b3e = 
        'number_of_fats' : int.from_bytes(vbr[16:16+1], 'little'),
        'number_of_heads' : int.from_bytes(vbr[26:26+2], 'little'),   # 0xff =
        'total_sector32' : int.from_bytes(vbr[32:32+4], 'little'),    # 0x028000 = 
        'fat32_size' : int.from_bytes(vbr[36:36+4], 'little'),    # 0x0261 = 
        'root_dir_cluster' : int.from_bytes(vbr[44:44+4], 'little')  # 0x02 = 
    }

    # fat1 시작 주소와 data_area 시작 주소계산 계산
    vbr_info['cluster_size'] = vbr_info['bps'] * vbr_info['spc']
    vbr_info['fat1_start_lba'] = vbr_info['reserved_sector_count']
    vbr_info['data_area_start_lba'] = vbr_info['fat1_start_lba'] + (vbr_info['number_of_fats'] * vbr_info['fat32_size'])

    data_area_total_sectors = vbr_info['total_sector32'] - vbr_info['data_area_start_lba']
    total_clusters = data_area_total_sectors // vbr_info['spc'] # 정수 나눗셈
    vbr_info['total_clusters'] = total_clusters

    return vbr_info

def get_cluster_chain(f, start_cluster, vbr_info):
    chain = []
    current_cluster = start_cluster
    fat_start_offset = vbr_info['fat1_start_lba'] * vbr_info['bps']

    while current_cluster < 0x0FFFFFF8:
        chain.append(current_cluster)

        fat_offset = fat_start_offset + (current_cluster * 4)
        f.seek(fat_offset)
        next_cluster_bytes = f.read(4)
        current_cluster = int.from_bytes(next_cluster_bytes, 'little')

    return chain

def parse_dir(f, start_cluster, vbr_info):
    dir_cluster_chain = get_cluster_chain(f, start_cluster, vbr_info)

    dir_data = b''
    data_area_start_offset = vbr_info['data_area_start_lba'] * vbr_info['bps']
    for cluster_num in dir_cluster_chain:
        cluster_offset = data_area_start_offset + (cluster_num - 2) * vbr_info['cluster_size']
        f.seek(cluster_offset)
        dir_data += f.read(vbr_info['cluster_size'])

    for i in range(0, len(dir_data), 32):
        entry = dir_data[i:i+32]

        if entry[0] == 0x00: break
        if entry[0] == 0xE5: continue

        attributes = entry[11]
        if attributes == 0x0F: continue

        filename = entry[0:8].strip().decode('cp437')
        if filename == '.' or filename == '..': continue

        extension = entry[8:11].strip().decode('cp437')

        start_cluster_hi = int.from_bytes(entry[20:22], 'little')
        start_cluster_lo = int.from_bytes(entry[26:28], 'little')
        entry_start_cluster = (start_cluster_hi << 16) + start_cluster_lo
        
        file_size = int.from_bytes(entry[28:32], 'little')

        is_directory = (attributes & 0x10) != 0
        if is_directory:
            print(f"[DIR]  {filename} (Cluster: {entry_start_cluster})")
            parse_dir(f, entry_start_cluster, vbr_info)
        else:
            full_filename = f"{filename}.{extension}" if extension else filename
            print(f"[FILE] {full_filename} (Size: {file_size} bytes, Cluster: {entry_start_cluster})")
            get_cluster_chain(f, entry_start_cluster, vbr_info)


def main():
    if len(sys.argv) < 3: # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
        print(f"사용법: python {sys.argv[0]} <disk_image.dd> <start_cluster>")
        print("예시: python fat32_parser.py fat32.dd 2")
        sys.exit(1)
    
    dd_filepath = sys.argv[1] # 파일 경로 저장
    try:
        start_cluster = int(sys.argv[2]) # 시작 클러스터 번호
    except ValueError:
        print("시작 클러스터는 숫자여야 합니다.")
        sys.exit(1)
    
    try:
        with open(dd_filepath, 'rb') as f:
            f.seek(510)
            boot_sector_sig = f.read(2)   # 0x55AA
            f.seek(82)
            fs_type = f.read(8) #  헤더에서 타입 찾기 FAT32인지 확인 하고 비교 # 0x4641543332202020
            
            if boot_sector_sig != b"\x55\xAA" or fs_type != b"FAT32   ":
                print("FAT32 disk image가 이상해요")
                sys.exit(1)
            
            vbr_info = parse_fat32_vbr(f)
            cluster_chain = get_cluster_chain(f, start_cluster, vbr_info)
            
            print(f"{','.join(map(str, cluster_chain))}")

            f.close()

    except FileNotFoundError:   # 파일 탐색 오류
        print("파일을 찾을 수 없습니다.")
    except Exception as e:  # 기타 에러 발생
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()