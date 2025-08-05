#! namhyun's NTFS
import sys

class NTFS:
    def parse_vbr(f):
        f.seek(0)
        vbr = f.read(512)  # VBR (Volume Boot Record) 분석
        
        vbr_info = {
            'bps' : int.from_bytes(vbr[11:13], 'little'), # bytes per sector
            'spc' : int.from_bytes(vbr[13:14], 'little'), # sectors per cluster
            'media_descriptor' : int.from_bytes(vbr[21:22], 'little'),
            'sectors_per_track' : int.from_bytes(vbr[24:26], 'little'),
            'number_of_heads' : int.from_bytes(vbr[26:28], 'little'),
            'hidden_sectors' : int.from_bytes(vbr[28:32], 'little'),
            'total_sectors' : int.from_bytes(vbr[40:48], 'little'),  # NTFS는 8바이트
            'mft_cluster' : int.from_bytes(vbr[48:56], 'little'),    # MFT 시작 클러스터
            'mft_mirror_cluster' : int.from_bytes(vbr[56:64], 'little'), # MFT Mirror 시작 클러스터
            'file_record_size' : int.from_bytes(vbr[64:65], 'little'),  # MFT 레코드 크기 (클러스터 단위 또는 바이트)
            'index_buffer_size' : int.from_bytes(vbr[68:69], 'little')  # 인덱스 버퍼 크기
        }

        # 클러스터 크기 계산
        vbr_info['cluster_size'] = vbr_info['bps'] * vbr_info['spc']
        
        # MFT 레코드 크기 계산 (음수면 2^|값|, 양수면 클러스터 단위)
        file_record_size = vbr_info['file_record_size']
        if file_record_size & 0x80:  # MSB가 1이면 음수 (signed byte)
            # 음수인 경우: 2^|값| 바이트
            vbr_info['mft_record_size'] = 1 << (256 - file_record_size)
        else:
            vbr_info['mft_record_size'] = vbr_info['file_record_size'] * vbr_info['cluster_size']
            
        # 총 클러스터 개수 계산
        vbr_info['total_clusters'] = vbr_info['total_sectors'] // vbr_info['spc']

        return vbr_info
    
    def parse_data_runs(data_runs_data):
        """데이터 런을 파싱하여 클러스터 정보 추출"""
        runs = []
        offset = 0
        current_cluster = 0
        
        while offset < len(data_runs_data):
            if data_runs_data[offset] == 0:
                break
                
            header = data_runs_data[offset]
            length_bytes = header & 0x0F
            offset_bytes = (header & 0xF0) >> 4

            if length_bytes == 0 or offset_bytes == 0:
                break
                
            offset += 1
            
            # 길이 읽기
            length = 0
            for i in range(length_bytes):
                if offset + i >= len(data_runs_data):
                    break
                length |= data_runs_data[offset + i] << (i * 8)
            offset += length_bytes
            
            # 오프셋 읽기 (부호 있는 정수)
            if offset_bytes > 0:
                cluster_offset = 0
                for i in range(offset_bytes):
                    if offset + i >= len(data_runs_data):
                        break
                    cluster_offset |= data_runs_data[offset + i] << (i * 8)
                
                # 부호 확장 처리 (MSB가 1이면 음수)
                if data_runs_data[offset + offset_bytes - 1] & 0x80:
                    # 음수 처리: 2의 보수
                    cluster_offset = cluster_offset - (1 << (offset_bytes * 8))
                
                current_cluster += cluster_offset
                offset += offset_bytes
            else:
                # sparse file의 경우 (오프셋이 0바이트)
                # 현재 클러스터는 변경되지 않음 (홀 처리)
                pass
            
            runs.append((current_cluster, length))
            
        return runs
    
    def parse_mft_record(f, cluster_number, vbr_info):
        """MFT 레코드 파싱"""
        # MFT 레코드의 실제 위치 계산
        mft_offset = cluster_number * vbr_info['cluster_size']
        f.seek(mft_offset)
        
        record = f.read(vbr_info['mft_record_size'])
        
        # MFT 레코드 시그니처 확인
        if record[:4] != b'FILE':
            print(f"Invalid MFT record signature: {record[:4]}")
            return None
        
        # 첫 번째 속성의 오프셋
        attr_offset = int.from_bytes(record[20:22], 'little')
        
        attributes = []
        while attr_offset < len(record) and attr_offset < vbr_info['mft_record_size']:
            # 속성 타입 확인
            if attr_offset + 4 > len(record):
                break
                
            attr_type = int.from_bytes(record[attr_offset:attr_offset+4], 'little')
            if attr_type == 0xFFFFFFFF:  # 종료 마커
                break
            
            # 속성 길이 확인
            if attr_offset + 8 > len(record):
                break
                
            attr_length = int.from_bytes(record[attr_offset+4:attr_offset+8], 'little')
            if attr_length == 0 or attr_offset + attr_length > len(record):
                break
                
            non_resident = record[attr_offset+8] & 0x01
            
            if attr_type == 0x80:  # $DATA 속성
                if non_resident:
                    # 데이터 런 오프셋 확인
                    if attr_offset + 34 <= len(record):
                        data_runs_offset = int.from_bytes(record[attr_offset+32:attr_offset+34], 'little')
                        data_runs_start = attr_offset + data_runs_offset
                        data_runs_end = attr_offset + attr_length
                        
                        if data_runs_start < len(record) and data_runs_end <= len(record):
                            data_runs_data = record[data_runs_start:data_runs_end]
                            runs = NTFS.parse_data_runs(data_runs_data)
                            attributes.append(('DATA', runs))
            
            attr_offset += attr_length
            
        return attributes

def main():
    if len(sys.argv) < 2: # sys.argv 인자 제대로 들어왔는지 확인, 오류 발생 시 사용법 출력
        print(f"사용법: python {sys.argv[0]} <disk_image.dd>")
        sys.exit(1)
    
    dd_filepath = sys.argv[1] # 파일 경로 저장 후 해당 파일 읽기
    try:
        with open(dd_filepath, 'rb') as f:
            # NTFS 시그니처 확인
            f.seek(3)
            oem_id = f.read(8)
            f.seek(510)
            boot_sector_sig = f.read(2)
            
            if boot_sector_sig != b"\x55\xAA" or b"NTFS" not in oem_id:
                print("NTFS가 아닌데영")
                sys.exit(1)
            
            # VBR 정보 파싱
            vbr_info = NTFS.parse_vbr(f)
            
            # MFT 0번 레코드 분석
            mft_cluster = vbr_info['mft_cluster']
            attributes = NTFS.parse_mft_record(f, mft_cluster, vbr_info)
            
            if attributes:
                print(f"{vbr_info['total_clusters']}")
                for attr_type, runs in attributes:
                    if attr_type == 'DATA':
                        for start_cluster, length in runs:
                            print(f"{start_cluster} {length}")
            else:
                print("MFT 0번 레코드를 분석할 수 없습니다.")

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생 : {e}")
        
if __name__ == "__main__":
    main()