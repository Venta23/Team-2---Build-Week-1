import socket

def scanPort():
    target_ip = input("Please, insert the target IP to scan: ")
    target_range_port = input("Please, insert the port range to scan [0-65535]: ")

    low_port = int(target_range_port.split('-')[0])
    high_port = int(target_range_port.split('-')[1])

    total_ports = high_port - low_port + 1


    open_ports = []

    for i, port in enumerate(range(low_port, high_port + 1), start=1):
        print(f"\rScanning port {port} ({i}/{total_ports})...", end="")
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(0.5)
        status = s.connect_ex((target_ip,port))

        if(status == 0):
            try:
                service = socket.getservbyport(port, "tcp")
            except OSError:
                service = "Unknown"

            open_ports.append((port, service))
            
        s.close()
        
    print("\n--- Scan Results ---")

    if open_ports:
        for port, service in open_ports:
            print(f"[✔] OPEN  -> {target_ip}:{port} ({service})")
        print("\n====================")
        print("   SCAN COMPLETED   ")
        print("====================")
    else:
        print("\n====================")
        print("   SCAN COMPLETED   ")
        print("====================")

scanPort()