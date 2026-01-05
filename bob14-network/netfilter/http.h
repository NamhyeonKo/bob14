#pragma once
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

typedef struct my_http_hdr {
    char* method;
    char* uri;
    char* version;
    char* host;
} HTTP_HDR;

char* parse_http_host(const char* http_payload, int payload_len);
int is_http_request(const char* payload, int len);
void print_http_header(const char* payload, int len);