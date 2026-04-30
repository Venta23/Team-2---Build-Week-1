from scapy.all import sniff, IP, TCP, UDP

def get_flags(tcp):
    flags = tcp.flags

    if flags == 0x02:
        return "SYN"
    elif flags == 0x12:
        return "SYN-ACK"
    elif flags == 0x10:
        return "ACK"
    elif flags == 0x18:
        return "PSH-ACK"
    elif flags == 0x11:
        return "FIN-ACK"
    else:
        return str(flags)

def process_packet(packet):
    if IP in packet:

        ip = packet[IP]

        # TCP
        if TCP in packet:
            tcp = packet[TCP]
            flag = get_flags(tcp)

            print(f"[TCP {flag}] {ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport}")

        # UDP
        elif UDP in packet:
            udp = packet[UDP]

            print(f"[UDP] {ip.src}:{udp.sport} -> {ip.dst}:{udp.dport}")

if __name__ == "__main__":
    print("Sniffing TCP + UDP... (CTRL+C per fermare)")
    sniff(filter="tcp or udp", store=False, prn=process_packet)
