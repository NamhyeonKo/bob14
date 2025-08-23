import sys
import struct

class EXT:
    def __init__(self, image_path):
        """ 함수에 필요한 인자들 한번에 self로 저장 후 사용 함수 """
        self.image_path = image_path
        self.file = open(image_path, 'rb')
        self.superblock = None
        self.block_size = None
        self.group_desc = None
    
    def read_superblock(self):
        """ 슈퍼 블록 읽기 함수 """
        self.file.seek(1024)
        sb_data = self.file.read(1024)
        
        magic = struct.unpack('<H', sb_data[56:58])[0] # Magic Signature 오프셋 : 0x38, 사이즈 : 2
        if magic != 0xEF53:
            raise ValueError(f"Invalid ext filesystem, magic: 0x{magic:04x}")
            
        self.superblock = {
            'inodes_count': struct.unpack('<L', sb_data[0:4])[0],
            'blocks_count': struct.unpack('<L', sb_data[4:8])[0],
            'log_block_size': struct.unpack('<L', sb_data[24:28])[0],
            'inodes_per_group': struct.unpack('<L', sb_data[40:44])[0],
            'blocks_per_group': struct.unpack('<L', sb_data[32:36])[0],
            'inode_size': struct.unpack('<H', sb_data[88:90])[0] if len(sb_data) > 90 else 128
        }
        
        self.block_size = 1024 << self.superblock['log_block_size'] # 0 = 1kb, 1 = 2kb, 2 = 4kb
        
    def read_group_descriptor(self):
        """ Group Descriptor Table 읽기 함수 """
        gdt_offset = 2048 if self.block_size == 1024 else self.block_size
        self.file.seek(gdt_offset)
        gd_data = self.file.read(32)
        
        self.group_desc = {
            'inode_table': struct.unpack('<L', gd_data[8:12])[0] # inode table의 시작 블록 주소
        }
        
    def read_inode(self, inode_num):
        """ inode 읽기 함수 """
        group_num = (inode_num - 1) // self.superblock['inodes_per_group']
        inode_size = 128 if 'inode_size' not in self.superblock else self.superblock['inode_size']
        inode_offset = ((inode_num - 1) % self.superblock['inodes_per_group']) * inode_size
        
        if group_num == 0:
            inode_table_block = self.group_desc['inode_table']
        else:
            gdt_offset = 2048 if self.block_size == 1024 else self.block_size
            self.file.seek(gdt_offset + group_num * 32)
            gd_data = self.file.read(32)
            inode_table_block = struct.unpack('<L', gd_data[8:12])[0]
        
        inode_table_offset = inode_table_block * self.block_size
        offset = inode_table_offset + inode_offset
        
        self.file.seek(offset)
        inode_data = self.file.read(inode_size)
        
        mode = struct.unpack('<H', inode_data[0:2])[0] # file mode 오프셋 : 0x0, 사이즈 : 2
        size = struct.unpack('<L', inode_data[4:8])[0] # file size 오프셋 : 0x4, 사이즈 : 4
        blocks = []
        
        for i in range(12):
            block = struct.unpack('<L', inode_data[40 + i*4:44 + i*4])[0] # block pointer 오프셋 : 0x28, 사이즈 : 4
            if block != 0:
                blocks.append(block)
                
        return {
            'mode': mode,
            'size': size,
            'blocks': blocks,
            'is_dir': (mode & 0x4000) != 0
        }
        
    def read_directory_entries(self, inode_num):
        """ 디렉토리 엔트리 읽기 함수 """
        inode = self.read_inode(inode_num)
        entries = []
        
        if not inode['is_dir']:
            return entries
            
        for block_num in inode['blocks']:
            if block_num == 0:
                continue
                
            self.file.seek(block_num * self.block_size)
            block_data = self.file.read(self.block_size)
            
            offset = 0
            while offset < len(block_data) and offset < inode['size']:
                if offset + 8 > len(block_data):
                    break

                entry_inode = struct.unpack('<L', block_data[offset:offset+4])[0] # entry_inode 오프셋 : 0x0, 사이즈 : 4
                if entry_inode == 0:
                    break

                rec_len = struct.unpack('<H', block_data[offset+4:offset+6])[0] # rec_len 오프셋 : 0x4, 사이즈 : 2
                name_len = block_data[offset+6] # name_len 오프셋 : 0x6, 사이즈 : 1

                if rec_len == 0 or rec_len < 8 or offset + rec_len > len(block_data):
                    break
                    
                if name_len > 0 and name_len <= rec_len - 8:
                    name = block_data[offset+8:offset+8+name_len].decode('utf-8', errors='ignore')
                    entries.append((name, entry_inode)) # (이름, inode 번호) 튜플 추가

                offset += rec_len # 다음 엔트리로 이동

        return entries
        
    def list_root_directory(self):
        """
        루트 디렉토리 목록 출력 함수
        루트 디렉토리는 대부분 inode 2, "."가 inode 2를 가리키는지 확인 후 출력
        """
        for i in range(1, 20):
            inode = self.read_inode(i)
            if inode['mode'] != 0 and inode['is_dir']:
                entries = self.read_directory_entries(i)
                for name, inode_num in entries:
                    if name == "." and inode_num == 2:
                        # 루트 디렉토리 확인
                        for name, inode_num in entries:
                            print(f"{name} {inode_num}")
                        return
            
    def close(self):
        """ 파일 닫기 """
        self.file.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python ext.py <image_file>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    try:
        fs = EXT(image_path)
        fs.read_superblock()
        fs.read_group_descriptor()
        fs.list_root_directory()
        fs.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()