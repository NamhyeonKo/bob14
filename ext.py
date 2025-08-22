import sys
import struct


class ExtFS:
    def __init__(self, image_path):
        self.image_path = image_path
        self.file = open(image_path, 'rb')
        self.superblock = None
        self.block_size = None
        self.group_desc = None
        
    def read_superblock(self):
        self.file.seek(1024)
        sb_data = self.file.read(1024)
        
        magic = struct.unpack('<H', sb_data[56:58])[0]
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
        
        self.block_size = 1024 << self.superblock['log_block_size']
        
    def read_group_descriptor(self):
        gdt_offset = 2048 if self.block_size == 1024 else self.block_size
        self.file.seek(gdt_offset)
        gd_data = self.file.read(32)
        
        self.group_desc = {
            'inode_table': struct.unpack('<L', gd_data[8:12])[0]
        }
        
    def read_inode(self, inode_num):
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
        
        mode = struct.unpack('<H', inode_data[0:2])[0]
        size = struct.unpack('<L', inode_data[4:8])[0]
        blocks = []
        
        for i in range(12):
            block = struct.unpack('<L', inode_data[40 + i*4:44 + i*4])[0]
            if block != 0:
                blocks.append(block)
                
        return {
            'mode': mode,
            'size': size,
            'blocks': blocks,
            'is_dir': (mode & 0x4000) != 0
        }
        
    def read_directory_entries(self, inode_num):
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
                    
                entry_inode = struct.unpack('<L', block_data[offset:offset+4])[0]
                if entry_inode == 0:
                    break
                    
                rec_len = struct.unpack('<H', block_data[offset+4:offset+6])[0]
                name_len = block_data[offset+6]
                
                if rec_len == 0 or rec_len < 8 or offset + rec_len > len(block_data):
                    break
                    
                if name_len > 0 and name_len <= rec_len - 8:
                    name = block_data[offset+8:offset+8+name_len].decode('utf-8', errors='ignore')
                    entries.append((name, entry_inode))
                
                offset += rec_len
                
        return entries
        
    def list_root_directory(self):
        # Root directory is usually inode 2, but let's check where "." points to inode 2
        for i in range(1, 20):
            inode = self.read_inode(i)
            if inode['mode'] != 0 and inode['is_dir']:
                entries = self.read_directory_entries(i)
                for name, inode_num in entries:
                    if name == "." and inode_num == 2:
                        # This is the root directory
                        for name, inode_num in entries:
                            print(f"{name} {inode_num}")
                        return
            
    def close(self):
        self.file.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python ext.py <image_file>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    try:
        fs = ExtFS(image_path)
        fs.read_superblock()
        fs.read_group_descriptor()
        fs.list_root_directory()
        fs.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()