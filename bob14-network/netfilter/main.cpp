#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <linux/netfilter.h>
#include <libnetfilter_queue/libnetfilter_queue.h>
#include <arpa/inet.h>
#include <errno.h>

#include "ethhdr.h"
#include "ipv4.h"
#include "tcp.h"
#include "http.h"

static char* blocked_host = NULL;

static int cb(
    struct nfq_q_handle *qh,
     struct nfgenmsg *nfmsg,
    struct nfq_data *nfa,
     void *data
) {
    uint32_t id = 0;
    struct nfqnl_msg_packet_hdr *ph;
    unsigned char *packet_data;
    int ret;
    
    ph = nfq_get_msg_packet_hdr(nfa);
    if (ph) {
        id = ntohl(ph->packet_id);
    }
    
    ret = nfq_get_payload(nfa, &packet_data);
    if (ret < 0) {
        printf("Error getting payload\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    printf("Packet received, length: %d bytes\n", ret);
    
    // IP 헤더 파싱 (IPV4_HDR 구조체 사용)
    if (ret < sizeof(IPV4_HDR)) {
        printf("Packet too small for IP header\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    IPV4_HDR* ip_hdr = (IPV4_HDR*)packet_data;
    
    // IP 버전 확인 (IPv4)
    if ((ip_hdr->ip_v_n_hl >> 4) != 4) {
        printf("Not IPv4 packet\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    // TCP 프로토콜 확인
    if (ip_hdr->ip_p != IPPROTO_TCP) {
        printf("Not TCP packet\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    // IP 헤더 길이 계산
    int ip_header_len = (ip_hdr->ip_v_n_hl & 0x0F) * 4;
    
    // TCP 헤더 위치 계산 (Tcp_HDR 구조체 사용)
    if (ret < ip_header_len + sizeof(Tcp_HDR)) {
        printf("Packet too small for TCP header\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    Tcp_HDR* tcp_hdr = (Tcp_HDR*)(packet_data + ip_header_len);
    
    // TCP 헤더 길이 계산
    int tcp_header_len = (tcp_hdr->th_off >> 4) * 4;
    
    // HTTP 페이로드 위치 계산
    int http_offset = ip_header_len + tcp_header_len;
    if (ret <= http_offset) {
        printf("No HTTP payload\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    char* http_payload = (char*)(packet_data + http_offset);
    int http_payload_len = ret - http_offset;
    
    // HTTP 요청인지 확인
    if (!is_http_request(http_payload, http_payload_len)) {
        printf("Not HTTP request\n");
        return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
    }
    
    printf("HTTP Request detected!\n");
    print_http_header(http_payload, http_payload_len);
    
    // Host 헤더 추출
    char* host = parse_http_host(http_payload, http_payload_len);
    if (host) {
        printf("Extracted Host: %s\n", host);
        
        // 차단할 호스트와 비교
        if (blocked_host && strcmp(host, blocked_host) == 0) {
            printf("BLOCKED: Host %s matches blocked host %s\n", host, blocked_host);
            free(host);
            return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);
        }
        
        free(host);
    }
    
    printf("ACCEPTED: Packet allowed\n");
    return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
}

int main(int argc, char **argv) {
    struct nfq_handle *h;
    struct nfq_q_handle *qh;
    int fd;
    int rv;
    char buf[4096] __attribute__ ((aligned));
    
    if (argc != 2) {
        printf("Usage: %s <host_to_block>\n", argv[0]);
        printf("Example: %s test.gilgil.net\n", argv[0]);
        exit(1);
    }
    
    blocked_host = argv[1];
    printf("Blocking host: %s\n", blocked_host);
    
    printf("Opening library handle\n");
    h = nfq_open();
    if (!h) {
        fprintf(stderr, "Error during nfq_open()\n");
        exit(1);
    }
    
    printf("Unbinding existing nf_queue handler for AF_INET (if any)\n");
    if (nfq_unbind_pf(h, AF_INET) < 0) {
        fprintf(stderr, "Error during nfq_unbind_pf()\n");
        exit(1);
    }
    
    printf("Binding nfnetlink_queue as nf_queue handler for AF_INET\n");
    if (nfq_bind_pf(h, AF_INET) < 0) {
        fprintf(stderr, "Error during nfq_bind_pf()\n");
        exit(1);
    }
    
    printf("Binding this socket to queue '0'\n");
    qh = nfq_create_queue(h, 0, &cb, NULL);
    if (!qh) {
        fprintf(stderr, "Error during nfq_create_queue()\n");
        exit(1);
    }
    
    printf("Setting copy_packet mode\n");
    if (nfq_set_mode(qh, NFQNL_COPY_PACKET, 0xffff) < 0) {
        fprintf(stderr, "Can't set packet_copy mode\n");
        exit(1);
    }
    
    fd = nfq_fd(h);
    
    printf("Netfilter queue initialized. Waiting for packets...\n");
    printf("Use 'sudo iptables -I INPUT -j NFQUEUE --queue-num 0' to redirect packets\n");
    printf("Use 'sudo iptables -I OUTPUT -j NFQUEUE --queue-num 0' to redirect packets\n");
    printf("Press Ctrl+C to stop\n");
    
    for (;;) {
        if ((rv = recv(fd, buf, sizeof(buf), 0)) >= 0) {
            printf("Packet received from netfilter queue\n");
            nfq_handle_packet(h, buf, rv);
            continue;
        }
        
        if (rv < 0 && errno == ENOBUFS) {
            printf("Losing packets!\n");
            continue;
        }
        
        printf("recv failed\n");
        break;
    }
    
    printf("Unbinding from queue 0\n");
    nfq_destroy_queue(qh);
    
    printf("Closing library handle\n");
    nfq_close(h);
    
    exit(0);
}