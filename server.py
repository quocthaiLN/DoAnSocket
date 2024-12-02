import socket
import threading
import os
import csv
import time
#duong dan toi thu muc sever va client
PathSever = "DataSever"  
PathUsers = "users.csv"

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

def check1(s):
    for i in s:
        if i == '/':
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
        
def checkExist(path):
    if os.path.isfile(path):
        return True
    return False
        
#ham upload file tu client len sever
def uploadFile(client, fileName, addr):
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    nameWithNotExten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PathSever + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(PathSever + tmp):
            tmp = nameWithNotExten + "(" + str(i) + ")" + exten
            fileWrite = PathSever + tmp
            i += 1
    sizeRecv = client.recv(1024).decode('utf-8')
    size = int(sizeRecv)
    sizeResp = "Nhan thanh cong"
    client.sendall(sizeResp.encode('utf-8'))
    ofs = open(fileWrite, "wb")
    sw = 0
    while size > sw:
        data = client.recv(1024)
        if not data:
            break
        ofs.write(data)
        sw += len(data)
    ofs.close()
    if os.path.getsize(fileWrite) != size:
        print("Loi ngung ket noi tu sever toi client")
        client.sendall("Loi ket noi".encode('utf-8'))
        temp = client.recv(1024).decode('utf-8')
        return False
    print(f"Sever: Yeu cau upload file cua client {addr} hoan thanh. File dang duoc luu tru tai {fileWrite} tren sever")
    client.sendall(f"File dang duoc luu tru tai {fileWrite} tren sever".encode('utf-8'))
    temp = client.recv(1024).decode('utf-8')
    return True

def downloadFile(client, fileName, addr):
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    Path = PathSever + tmp
    if (check1(fileName) and Path != fileName) or not checkExist(Path):
        msg = "Not exist"
        client.sendall(msg.encode('utf-8'))
        return
    else:
        msg = "Exist"
        client.sendall(msg.encode('utf-8'))
        respMsg = client.recv(1024).decode('utf-8')
    size = os.path.getsize(Path)
    client.sendall(str(size).encode('utf-8'))
    sizeResp = client.recv(1024).decode('utf-8')
    ifs = open(Path, "rb")
    while 1:
        data = ifs.read(1024)
        if not data:
            break
        client.sendall(data)
    ifs.close()
    resp = client.recv(1024).decode('utf-8')
    if int(resp) != size:
        print("Loi ngung ket noi tu sever toi client")
        return False
    print(f"Yeu cau download file cua client {addr} hoan thanh.")
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

#ham nhan du lieu tu client va gui phan hoi
def recvData(client, addr) :
    print(f"Client {addr} ket noi thanh cong!!!")

    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:
            client.sendall("Server: Enter your username and password to login: ".encode('utf-8'))

            # Nhận thông tin account từ client
            login_information = client.recv(1024).decode('utf-8')
            username, password = login_information.split(',')

            if(authenticate_client(username, password)):
                client.sendall("Successful".encode('utf-8'))
                print(f"Server: Login successfully towards account {username}")
                break
            else:
                client.sendall("Unsuccessfull".encode('utf-8'))
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""
        while data != "exit":
            data = client.recv(1024)
            data = data.decode('utf-8')
            if data == "exit":
                break
            if data == "uploadFile":
                #gui yeu cau
                request = "Nhap vao duong dan hoac ten file: "
                client.sendall(request.encode('utf-8'))
                #nhan ten file hoac duong dan
                msg = client.recv(1024).decode('utf-8')
                if msg == "CANCEL":
                    continue
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(client, msg, addr):
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
            if data == "downloadFile":
                 #gui yeu cau: Lấy thông tin từ gui
                # request = "Nhap vao duong dan hoac ten file: "
                # client.sendall(request.encode('utf-8'))
                #nhan ten file hoac duong dan
                msg = client.recv(1024).decode('utf-8')
                if msg == "CANCEL":
                    continue
                print(f"Client {addr}: Download file voi duong dan {msg}")
                if downloadFile(client, msg, addr):
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
    except:
        print("Connect Error")
    client.close()

#tao socket
sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sever.bind((socket.gethostname(), 2810))
NumsOfClient = int(input("Nhap vao so luong client:"))
sever.listen(NumsOfClient)
print("Sever dang lang nghe.....")
#tao da luong
count = 0
while count < NumsOfClient:
    client, addr = sever.accept()
    thread = threading.Thread(target = recvData, args = (client, addr))
    thread.daemon = False
    thread.start()
    count += 1

sever.close()    
