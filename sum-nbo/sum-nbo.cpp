#include <stddef.h> // for size_t
#include <stdint.h> // for uint32_t
#include <stdio.h> // for printf
#include <netinet/in.h> // for htonl
#include <stdlib.h> // for allocation

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
