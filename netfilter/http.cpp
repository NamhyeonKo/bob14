#include "http.h"

char* parse_http_host(const char* http_payload, int payload_len) {
    if (!http_payload || payload_len <= 0) return NULL;
    
    const char* host_start = strstr(http_payload, "Host: ");
    if (!host_start) return NULL;
    
    host_start += 6; // "Host: " 길이
    const char* host_end = strstr(host_start, "\r\n");
    if (!host_end) {
        host_end = strstr(host_start, "\n");
        if (!host_end) return NULL;
    }
    
    int host_len = host_end - host_start;
    char* host = (char*)malloc(host_len + 1);
    if (!host) return NULL;
    
    strncpy(host, host_start, host_len);
    host[host_len] = '\0';
    
    return host;
}

int is_http_request(const char* payload, int len) {
    if (!payload || len < 4) return 0;
    
    if (strncmp(payload, "GET ", 4) == 0 ||
        strncmp(payload, "POST ", 5) == 0 ||
        strncmp(payload, "HEAD ", 5) == 0 ||
        strncmp(payload, "PUT ", 4) == 0 ||
        strncmp(payload, "DELETE ", 7) == 0) {
        return 1;
    }
    
    return 0;
}

void print_http_header(const char* payload, int len) {
    if (!payload || len <= 0) return;
    
    printf("[HTTP Header]\n");
    
    const char* end_of_headers = strstr(payload, "\r\n\r\n");
    if (!end_of_headers) {
        end_of_headers = strstr(payload, "\n\n");
        if (!end_of_headers) {
            printf("Invalid HTTP header format\n");
            return;
        }
    }
    
    int header_len = end_of_headers - payload;
    
    char* host = parse_http_host(payload, len);
    if (host) {
        printf("Host: %s\n", host);
        free(host);
    }
    
    const char* method_end = strstr(payload, " ");
    if (method_end) {
        int method_len = method_end - payload;
        printf("Method: %.*s\n", method_len, payload);
    }
}