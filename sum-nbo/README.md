## 과제 설명

https://gitlab.com/gilgil/sns/-/wikis/byte-order/report-sum-nbo

## 과제 영상

https://youtu.be/P0nZgspO0KU

## 공부 내용

### File I/O

- fopen은 FILE 포인터 변수 fp 선언해서 binary file read 형식으로 읽기
    
    ```cpp
    FILE *fopen(
       const char *filename,
       const char *mode
    );
    ```
    
- file open 실패하면 에러 내용 출력하고 프로그램 종료
- fread 함수 원형 (한번에 읽을 사이즈, 읽을 개수)
    
    ```cpp
    size_t fread(
    	void *ptr,
    	size_t size,
    	size_t count,
    	FILE *stream
    );
    ```
    
- fclose 함수 원형
    
    ```cpp
    int fclose(
       FILE *stream
    );
    ```

 출처 : https://learn.microsoft.com/ko-kr/cpp/c-runtime-library/reference/fread?view=msvc-170 등   

### main 함수 인자 받는 법

- argc는 인자의 갯수를 의미
- argv로 실행 파일 뒤에 인자를 넣을 수 있다.
- argv의 첫 번째 값은 실행 경로이므로 뒤에 넣은 인자를 확인하려면 argv[1]부터 확인한다.

출처 : https://hmjo.tistory.com/90

### htonl 함수

host byte order to network byte order

## 소스 코드 설명

### 라이브러리 불러오기

- `stddef.h` for size_t
- `stdint.h` for uint32_t
- `stdio.h` for printf
- `netinet/in.h` for htonl
- `stdlib.h` for allocation

```cpp
#include <stddef.h> // for size_t
#include <stdint.h> // for uint32_t
#include <stdio.h> // for printf
#include <netinet/in.h> // for htonl
#include <stdlib.h> // for allocation
```

### `file_content_read`

- 인자로 file path인 address를 받습니다.
- fopen을 이용해 fp 파일 포인터 변수에 rb권한으로 파일을 엽니다.
- 파일에서 읽은 내용을 저장할 buffer를 생성하고, fread 함수를 이용해 읽습니다.
    - 이때 한번에 읽을 사이즈는 4바이트, 읽는 수는 1번이므로 인자에 그대로 넣습니다.
- 파일 내용을 buffer에 저장했으니 fclose로 닫습니다.
- 받은 값을 htnol함수를 이용해 빅엔디안 형식으로 변환합니다. (host byte order → network byte order)

```cpp
// file open, read, and close function
uint32_t file_content_read(char* address){
    FILE* fp = fopen(address, "rb");
    if (fp == NULL){ /* file open with read binary mode */
        printf("file open error");
        return -1;
    }  

    uint32_t *buffer;
    fread(buffer, sizeof(uint32_t), 1, fp);   // buffer to read data
    fclose(fp);

    /* we need to change host byte order to network byte order */
    /* because integers store as little endian in binary files */
    return htonl(*buffer);
}
```

### `main function`

- main 함수 인자로 파일 경로들을 받아야 하므로 argc, argv[]를 받습니다.
- 합을 저장하기 위한 변수 sum를 선언합니다.
- argv에 저장되는 값의 첫번째는 해당 파일의 실행 경로 이므로 두번째 인자부터 받아서 배열에 저장합니다.
    - 이때 인자를 새로 만든 file_content_read라는 함수에 넣어 htonl을 실행한 값으로 받아옵니다.
- 해당 값들을 각각의 형태로 출력해주고 더해줍니다.
- 마지막 값의 출력이 끝나면 sum을 출력해줍니다.

```cpp
// main function
int main(int argc, char* argv[]){
    uint32_t *nums = (uint32_t*) malloc(sizeof(uint32_t) * argc);   // nums array dynamic allocation;
    uint32_t sum = 0;

    for (int i = 1; i < argc ; i++) nums[i-1] = file_content_read(argv[i]); // file_contents store in array
    for (int i = 0; i < argc - 1 ; i++) {
        printf("%d(0x%08x)", nums[i], nums[i]); // print num as digit and hex

        sum += nums[i]; // sum all nums

        if (i != argc - 2) printf(" + ");   // make output format
        else printf("= %d(0x%08x)", sum, sum);  // print sum as digit and hex
    }

    return 0;
}
```
