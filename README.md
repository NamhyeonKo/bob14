# File System Analysis Tools

디지털 포렌식 분석을 위한 파일시스템 파서 모음입니다.

## 파이썬 프로그램 목록

### 1. gpt_parser.py

GPT (GUID Partition Table) 파티션 테이블을 분석하는 프로그램입니다.

**사용법:**

```bash
python gpt_parser.py <disk_image.dd>
```

**기능:**

- GPT 시그니처 확인 (EFI PART)
- 파티션 GUID, 시작 섹터, 총 섹터 수 출력
- 파티션 크기 (GB) 계산

**출력 형식:**

```
<GUID> <시작_섹터> <총_섹터_수>
```

### 2. mbr_parser.py

MBR (Master Boot Record) 파티션 테이블을 분석하는 프로그램입니다.

**사용법:**

```bash
python mbr_parser.py <disk_image.dd>
```

**기능:**

- MBR 부트 시그니처 확인 (0x55AA)
- 기본 파티션 (타입 0x07) 분석
- 확장 파티션 (타입 0x05) 및 EBR 재귀 분석
- 시작 섹터와 총 섹터 수 출력

**출력 형식:**

```
<시작_섹터> <총_섹터_수>
```

### 3. fat32_parser.py
FAT32 파일시스템의 클러스터 체인을 분석하는 프로그램입니다.

**사용법:**

```bash
python fat32_parser.py <disk_image.dd> <시작_클러스터>
```

**기능:**

- FAT32 시그니처 확인
- VBR (Volume Boot Record) 분석
- 지정된 시작 클러스터부터 클러스터 체인 추적
- FAT 테이블을 이용한 연결된 클러스터 번호 출력

**출력 형식:**

```
<클러스터1>,<클러스터2>,<클러스터3>,...
```

### 4. ntfs.py

NTFS 파일시스템의 MFT (Master File Table) 0번 레코드를 분석하는 프로그램입니다.

**사용법:**

```bash
python ntfs.py <disk_image.dd>
```

**기능:**

- NTFS 시그니처 확인
- VBR 분석 및 MFT 정보 추출
- MFT 0번 레코드의 DATA 속성 분석
- 데이터 런(Data Runs) 파싱
- MFT가 사용하는 총 클러스터 수와 각 런의 정보 출력

**출력 형식:**

```
<총_클러스터_수>
<시작_클러스터> <길이>
<시작_클러스터> <길이>
...
```

### 5. ext.py

Ext3/Ext4 파일시스템의 루트 디렉토리 파일 목록을 출력하는 프로그램입니다.

**사용법:**

```bash
python ext.py <증거이미지>
```

**기능:**

- Ext3/Ext4 파일시스템 시그니처 확인 (0xEF53)
- 슈퍼블록과 그룹 디스크립터 분석
- 루트 디렉토리(inode 2) 엔트리 파싱
- 파일명과 inode 번호 출력

**출력 형식:**

```
<파일명> <inode번호>
```

**조건:**

- 파일명은 대소문자 그대로 출력
- inode 번호는 10진수로 출력
- 파일명과 inode 번호는 스페이스 하나로만 구분
- Ext4의 extents는 leaf 노드만 존재하는 경우로 한정
