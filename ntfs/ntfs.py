#! namhyun's NFTS
import sys

class NTFS:
    def parse_vbr(f):
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

        print(f" -> BPS: {vbr_info['bps']}, SPC: {vbr_info['spc']}, Cluster Size: {vbr_info['cluster_size']}")
        print(f" -> FAT#1 Start LBA: {vbr_info['fat1_start_lba']}")
        print(f" -> Data Area Start LBA: {vbr_info['data_area_start_lba']}")
        print(f" -> Total Clusters in Data Area: {total_clusters}")

        return vbr_info

def main():
    if len(sys.argv) < 2: # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
        print(f"사용법: python {sys.argv[0]} <disk_image.dd>")
        sys.exit(1)
    
    dd_filepath = sys.argv[1] # 파일 경로 저장 후 해당 파일 읽기
    try:
        with open(dd_filepath, 'rb') as f:
            f.seek(510)
            boot_sector_sig = f.read(2)   # 0x55AA
            f.seek(82)
            jump_boot_code = f.read(3) #  헤더에서 타입 찾기 FAT32인지 확인 하고 비교 # 0x4641543332202020
            
            if boot_sector_sig != b"\x55\xAA" or jump_boot_code != b"\xEB\x52\x90":
                print("NTFS가 아닌데영")
                sys.exit(1)
            vbr_info = NTFS.parse_vbr(f)
            # parse_dir(f, vbr_info['root_dir_cluster'], vbr_info)

            f.close()

    except FileNotFoundError:   # 파일 탐색 오류
        print("파일을 찾을 수 없습니다.")
    except Exception as e:  # 기타 에러 발생
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()