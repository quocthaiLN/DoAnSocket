import socket
import threading
import os
import csv
import time
#duong dan toi thu muc sever va client
PathSever = "DataSever"  
PathUsers = "users.csv"
PathHistory = "DataSever/OperationHistory.txt"
ListForbiddenFile = ["users.csv", "OperationHistory"]
#HOST, PORT, NumberOfClient
HOST = socket.gethostname()
PORT = 12000
NumberOfClient = 5


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

#ham lay thoi gian thuc
def getTime():
    localTime = time.strftime("%a %d-%m-%Y %H:%M:%S", time.localtime(time.time()))
    return localTime

def operationHistory(msg):
    ofs = open(PathHistory, "a")
    ofs.write(msg)
    ofs.close()


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
        try:
            data = client.recv(1024)
        except Exception as e:
            print(f"Co loi khi upload file {fileName}/ Connect Error:[{addr}].")
            return False
        try:
            data = client.recv(1024)
        except Exception as e:
            print(f"Co loi khi upload file {fileName}/ Connect Error:[{addr}].")
            return False
        if not data:
            break
        ofs.write(data)
        sw += len(data)
        
    ofs.close()
    print(f"Sever: Yeu cau upload file cua client {addr} hoan thanh. File dang duoc luu tru tai {fileWrite} tren sever")
    client.sendall(f"File dang duoc luu tru tai {fileWrite} tren sever".encode('utf-8'))
    temp = client.recv(1024).decode('utf-8')
    return True

def isForbiddenFile(fileName):
    for file in ListForbiddenFile:
        if file == fileName:
            return False
    return True

def downloadFile(client, fileName, addr):
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    Path = PathSever + tmp
    if isForbiddenFile(Path):
        msg = "File is in list forbidden file. Can't download this file"
        print(msg)
        client.sendall("ff".encode('utf-8'))
        return
    if (check1(fileName) and Path != fileName) or not checkExist(Path):
        msg = "Not exist"
        print("File is not exist")
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
        try:
            resp = client.recv(1024).decode('utf-8')
        except Exception as e:
            print(f"Co loi khi download file {fileName}/ Connect Error:[{addr}].")
            return False
    ifs.close()
    print(f"Yeu cau download file cua client {addr} hoan thanh.")
    return True

def uploadFilesInFolderSequentially(client, pathFolder, addr):
    size = client.recv(1024).decode('utf-8')
    size = int(size)
    if size == 0:
        print(f"Folder '{pathFolder}'was sent by client {addr} is empty. Can't upload folder")
        client.sendall(f"Folder '{pathFolder}'was sent by client {addr} is empty. Can't upload folder".encode('utf-8'))
        return
    client.sendall("da nhan".encode('utf-8'))
    i = 0
    cnt = 0
    while i < size:
        i += 1
        files = client.recv(1024).decode('utf-8')
        client.sendall("da nhan".encode('utf-8'))
        if uploadFile(client, pathFolder + "/" + files, addr):
            resp = "Success"
            client.sendall(resp.encode('utf-8'))
        else:
            cnt += 1
            resp = "Failed"
            client.sendall(resp.encode('utf-8'))
    tmp = client.recv(1024).decode('utf-8')
    if cnt > 0:
        operationHistory("\n" + str(getTime()) + f"Client {addr} da upload folder voi duong dan {pathFolder}. Co {cnt} file khong duoc upload")
        client.sendall(f"Sever: Upload khong thanh cong {cnt} file")
    else:
        operationHistory("\n" + str(getTime()) + f"Client {addr} da upload folder voi duong dan {pathFolder} thanh cong")
        client.sendall(f"Sever: Upload thanh cong toan bo folder")

# Hàm xác thực account của một client: Tìm thông tin client trong file users
def authenticate_client(username, password):

    with open('DataSever/users.csv', mode = 'r') as file:
        reader = csv.reader(file)
        # fields = next(reader)
        for row in reader:
            # Giống với vector ví dụ: vector<string> a = {"username", "password"}
            if(len(row) == 2 and row[0] == username and row[1] == password):
                return True
        
    return False

def server_receive(client, addr, message):
        client.settimeout(600)
        try:
            message = client.recv(1024).decode('utf-8')
            print(f"Client[{addr}]: {message}")
            return message
        except socket.timeout:
            print(f"Client [{addr}]: TimeOut.")
        except Exception as e:
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

            if len(list_Connection) > NumberOfClient:
                server_send(client, addr, "Server da day.")
                list_Connection.remove((client, addr))
                client.close()
                return
            else:
                server_send(client, addr,"Enter your username and password to login: ")

            # Nhận thông tin account từ client
            login_information = ""
            login_information = server_receive(client, addr,login_information) 
                

            if login_information is None:
                server_send(client, addr, "timeout")
                list_Connection.remove((client, addr))
                client.close()
                return


            username, password = login_information.split(',')
            if(authenticate_client(username, password)):
                operationHistory("\n" + str(getTime()) + f"Client {addr} da dang nhap voi ten tai khoan la {username}")
                client.sendall("Successful".encode('utf-8'))
                print(f"Server: Login successfully towards account {username}")
                break
            else:
                client.sendall("Unsuccessfull".encode('utf-8'))
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""

        while True:
            try:
                data = client.recv(1024)
            except socket.timeout:
                print(f"Da ngat ket noi voi Client {client, addr} do TimeOut.")
                list_Connection.remove((client, addr))
                break
            data = data.decode('utf-8')
            if data == "exit":
                operationHistory("\n" + str(getTime()) + f"Client {addr} da ngat ket noi voi sever")
                print(f"Client[{addr}]: Da ngat ket noi khoi Server.")
                list_Connection.remove((client, addr))
                break
            if data == "uploadFile":
                #gui yeu cau
                request = "Nhap vao duong dan hoac ten file: "
                client.sendall(request.encode('utf-8'))
                #nhan ten file hoac duong dan
                msg = client.recv(1024).decode('utf-8')
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + f"Client {addr} da yeu cau upload file voi duong dan {msg}")
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(client, msg, addr):
                    operationHistory("\n" + str(getTime()) + f"Client {addr} da upload file voi duong dan {msg} thanh cong")
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
            if data == "downloadFile":
                #gui yeu cau: Lấy thông tin từ gui
                request = "Nhap vao duong dan hoac ten file: "
                client.sendall(request.encode('utf-8'))
                #nhan ten file hoac duong dan
                msg = client.recv(1024).decode('utf-8')
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + f"Client {addr} da yeu cau download file voi duong dan {msg}")
                print(f"Client {addr}: Download file voi duong dan {msg}")
                if downloadFile(client, msg, addr):
                    operationHistory("\n" + str(getTime()) + f"Client {addr} da download file voi duong dan {msg} thanh cong")
                    resp = "Success"
                    client.sendall(resp.encode('utf-8'))
                else:
                    resp = "Failed"
                    client.sendall(resp.encode('utf-8'))
            if data == "uploadFilesInFolderSequentially":
                #gui yeu cau
                request = "Nhap vao duong dan den folder: "
                client.sendall(request.encode('utf-8'))
                #nhan ten folder
                msg = client.recv(1024).decode('utf-8')
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + f"Client {addr} da yeu cau upload folder voi duong dan {msg}")
                print(f"Client {addr}: Upload folder voi duong dan {msg}")
                uploadFilesInFolderSequentially(client, msg, addr)
                
    except Exception as e:
        print(f"Connect Error {e} from Client : {client, addr}")
    client.close()
    

#tao socket

def main():
    sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever.bind((HOST, PORT))
    sever.listen(NumberOfClient)
    print("Sever dang lang nghe...")
    operationHistory("\n------------------------------------------------------------------------------------------------------------------------------------")
    operationHistory("\n" + str(getTime()) + ":" + "Sever mo ket noi")
    #tao da luong
    list_Connection = []
    while True:
        if len(list_Connection) <= NumberOfClient:
            client, addr = sever.accept()
            operationHistory("\n" + str(getTime()) + ":" + f"Client {addr} da ket noi toi sever")
            list_Connection.append((client, addr))
            thread = threading.Thread(target = handle_Client, args = (client, addr, list_Connection))
            thread.daemon = False
            thread.start()

    operationHistory("\n" + str(getTime()) + ":" + "Sever da ngat ket noi")
    operationHistory("--------------------------------------------")
    sever.close()    
if __name__ == "__main__":
    main()


