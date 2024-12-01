import socket
import threading
import os
import csv
import time
#duong dan toi thu muc sever va client
PathSever = "DataSever"  
PathClient = "DataClient"
PathUsers = "users.csv"

#HOST, PORT, NumberOfClient
HOST = socket.gethostname()
PORT = 12000
NumberOfClient = 1


#lay tu ki tu '/' cuoi cung tro ve sau trong duong dan hoac ten file
def name(fileName):
    res = ""
    cnt = 0
    for chara in fileName:
        if chara == '/':
            cnt += 1
    i = 0
    for charac in fileName:
        if charac == '/' and i < cnt:
            i += 1
        if i == cnt:
            res += charac
    return res

#kiem tra xem co ki tu '/' trong ham o tren chua
def check(s):
    if s[0] == '/':
        return True
    return False

#lay phan ten file va khong lay them phan mo rong
def getNameWithNotExten(name):
    res = name[0 : name.index(".")]
    return res

#lay phan mo rong cua file
def getExten(name):
    res = name[name.index(".") : len(name)]
    return res
        
#ham upload file tu client len sever
def uploadFile(fileName):
    #kiem tra xem file co ton tai khong
    if not os.path.isfile(fileName):
        print("Tai file khong thanh cong")
        return False
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    nameWithNotExten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PathSever + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(PathSever + tmp):
            tmp = nameWithNotExten + str(i) + exten
            fileWrite = PathSever + tmp
            i += 1
    #doc va ghi file
    ofs = open(fileWrite, "wb")
    ifs = open(fileName, "rb")
    while True:
        data = ifs.read(1024)
        if not data:
            break
        ofs.write(data)
    ifs.close()
    ofs.close()
    print("Tai file thanh cong")
    return True

#ham download sever tai xuong file cho client
def downloadFile(fileName):
    #check rong hay khong
    if not os.path.isfile(fileName):
        print("Sever: Tai file khong thanh cong")
        return False
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    nameWithNotExten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PathClient + tmp
    i = 1
    #check file trong thu muc da ton tai chua
    while os.path.isfile(PathClient + tmp):
        tmp = nameWithNotExten + str(i) + exten
        fileWrite = PathClient + tmp
        i += 1
    ofs = open(fileWrite, "w")
    ifs = open(fileName, "r")
    while True:
        data = ifs.read(1024)
        if not data:
            break
        ofs.write(data)
    ifs.close()
    ofs.close()
    print("Sever: Tai file xuong thanh cong")
    return True

# Hàm xác thực account của một client: Tìm thông tin client trong file users
def authenticate_client(username, password):

    with open('users.csv', mode = 'r') as file:
        reader = csv.reader(file)
        # fields = next(reader)
        for row in reader:
            # Giống với vector ví dụ: vector<string> a = {"username", "password"}
            if(len(row) == 2 and row[0] == username and row[1] == password):
                return True
        
    return False

def server_receive(client, addr, message):
        try:
            message = client.recv(1024).decode('utf-8')
            print(f"Client[{addr}]: {message}")
            return message
        except:
            print(f"Co loi khi nhan du lieu tu Client:[{addr}].")


def server_send(client, addr, message):
    try:
        print(f"Da gui thong bao den Client[{addr}].")
        client.send(message.encode('utf-8'))
    except:
        print(f"Co loi khi gui thong bao den Client[{addr}]")


#ham nhan du lieu tu client va gui phan hoi
def handle_Client(client, addr, list_Connection) :
    print(f"Ket noi thanh cong voi Client:[{addr}].")

    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:
            server_send(client, addr,"Enter your username and password to login: ")

            # Nhận thông tin account từ client
            login_information = ""
            login_information = server_receive(client, addr,login_information)
            username, password = login_information.split(',')

            if(authenticate_client(username, password)):
                client.sendall("Successful".encode('utf-8'))
                print(f"Server: Login successfully towards account {username}")
                break
            else:
                client.sendall("Unsuccessfull".encode('utf-8'))
                print(f"Server: Login unsuccessfully towards account {username}")
        
        # Xử lý download, upload file
        data = ""
        while True:
            data = client.recv(1024);
            data = data.decode('utf-8')
            if data == "exit":
                print(f"Client[{addr}]: Da ngat ket noi khoi Server.")
                list_Connection.remove((client, addr))
                break
            if data == "uploadFile":
                msg = client.recv(1024).decode('utf-8')
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(msg):
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
            if data == "downloadFile":
                msg = client.recv(1024).decode('utf-8')
                print(f"Client {addr}: Download file voi duong dan {msg}")
                if downloadFile(msg):
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
    except:
        print("Connect Error")
    client.close()
    

#tao socket

def main():
    sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever.bind((HOST, PORT))
    sever.listen(NumberOfClient)
    print("Sever dang lang nghe...")
#tao da luong
    list_Connection = []
    while True:
        if len(list_Connection) < NumberOfClient:
            client, addr = sever.accept()
            list_Connection.append((client, addr))
            thread = threading.Thread(target = handle_Client, args = (client, addr, list_Connection))
            thread.daemon = False
            thread.start()

            
    sever.close()    
if __name__ == "__main__":
    main()

