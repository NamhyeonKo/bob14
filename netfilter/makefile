LDLIBS=-lnetfilter_queue

all: netfilter-test

main.o: ethhdr.h ipv4.h tcp.h http.h main.cpp

ethhdr.o: ethhdr.h ethhdr.cpp

ipv4.o: ipv4.h ipv4.cpp

tcp.o: tcp.h tcp.cpp

http.o: http.h http.cpp

netfilter-test: main.o ethhdr.o ipv4.o tcp.o http.o
	$(LINK.cc) $^ $(LOADLIBES) $(LDLIBS) -o $@

clean:
	rm -f netfilter-test *.o
