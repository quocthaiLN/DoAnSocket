import socket
import threading
import os
import csv
import time
#duong dan toi thu muc sever va client
PATH_SERVER = "DataServer"  
PATH_USER = "users.csv"
PATH_HISTORY = "DataServer/OperationHistory.txt"
LIST_FORBIDEN_FILE = ["DataServer/users.csv", "DataServer/OperationHistory.txt"]
#HOST, PORT, NumberOfClient
HOST = socket.gethostname()
PORT = 12000
NUMBER_OF_CLIENT = 10
FORMAT = "utf-8"
#lay tu ki tu "/" cuoi cung tro ve sau trong duong dan hoac ten file
def name(file_name):
    res = ""
    cnt = 0
    for chara in file_name:
        if chara == "/":
            cnt += 1
    i = 0
    for charac in file_name:
        if charac == "/" and i < cnt:
            i += 1
        if i == cnt:
            res += charac
    return res

#kiem tra xem co ki tu "/" trong ham o tren chua
def check(s):
    if s[0] == "/":
        return True
    return False

def check1(s):
    for i in s:
        if i == "/":
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
    ofs = open(PATH_HISTORY, "a")
    ofs.write(msg)
    ofs.close()


#ham upload file tu client len sever
def uploadFile(client, file_name, addr):
    tmp = name(file_name)
    if not check(tmp):
        tmp = "/" + tmp
    name_with_not_exten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PATH_SERVER + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(fileWrite):
            tmp = name_with_not_exten + "(" + str(i) + ")" + exten
            fileWrite = PATH_SERVER + tmp
            i += 1
    sizeRecv = client.recv(10240).decode(FORMAT)
    size = int(sizeRecv)
    
    sizeResp = "Nhan thanh cong"
    client.sendall(sizeResp.encode(FORMAT))
    #ofs = open(fileWrite, "wb")
    with open(fileWrite, "wb") as ofs:
        sw = 0
        while size > sw:
            try:
                data = client.recv(10240)
            except Exception as e:
                print(f"Co loi khi upload file {file_name}/ Connect Error:[{addr}].")
                return False
            if not data:
                break
            ofs.write(data)
            sw += len(data)
            try:
                client.sendall("da nhan".encode("utf-8"))
            except Exception as e:
                print(f"Co loi khi upload file {file_name}/ Connect Error:[{addr}].")
                return False
        temp = client.recv(10240).decode("utf-8")
    #ofs.close()
    print(f"Sever: Yeu cau upload file cua client {addr} hoan thanh. File dang duoc luu tru tai {fileWrite} tren sever")
    client.sendall(f"File dang duoc luu tru tai {fileWrite} tren sever".encode(FORMAT))
    temp = client.recv(10240).decode(FORMAT)
    return True

def isForbiddenFile(file_name):
    for file in LIST_FORBIDEN_FILE:
        if file == file_name:
            return True
    return False

def downloadFile(client, file_name, addr):
    tmp = name(file_name)
    if not check(tmp):
        tmp = "/" + tmp
    Path = PATH_SERVER + tmp
    if isForbiddenFile(Path):
        msg = "File is in list forbidden file. Can't download this file"
        print(msg)
        client.sendall("ff".encode("utf-8"))
        return
    if (check1(file_name) and Path != file_name) or not checkExist(Path):
        msg = "Not exist"
        print("File is not exist")
        client.sendall(msg.encode("utf-8"))

        return
    else:
        msg = "Exist"
        client.sendall(msg.encode(FORMAT))
        respMsg = client.recv(10240).decode(FORMAT)
    size = os.path.getsize(Path)
    client.sendall(str(size).encode(FORMAT))
    sizeResp = client.recv(10240).decode(FORMAT)
    ifs = open(Path, "rb")
    while 1:
        data = ifs.read(10240)
        if not data:
            break
        try:
            client.sendall(data)
        except:
            print(f"Co loi khi download file {file_name}/ Connect Error:[{addr}].")
            return False   
        try:
            resp = client.recv(10240).decode("utf-8")
        except:
            print(f"Co loi khi download file {file_name}/ Connect Error:[{addr}].")
            return False
    ifs.close()
    print(f"Yeu cau download file cua client {addr} hoan thanh.")
    return True

def uploadFilesInFolderSequentially(client, path_folder, addr):
    size = client.recv(10240).decode(FORMAT)
    size = int(size)
    if size == 0:
        print(f"Folder {path_folder} was sent by client {addr} is empty. Can't upload folder")
        client.sendall(f"Folder {path_folder} was sent by client {addr} is empty. Can't upload folder".encode(FORMAT))
        return
    client.sendall("da nhan".encode(FORMAT))
    i = 0
    cnt = 0
    while i < size:
        i += 1
        files = client.recv(10240).decode(FORMAT)
        client.sendall("da nhan".encode(FORMAT))
        if uploadFile(client, path_folder + "/" + files, addr):
            resp = "Success"
            client.sendall(resp.encode(FORMAT))
        else:
            cnt += 1
            resp = "Failed"
            client.sendall(resp.encode(FORMAT))
    tmp = client.recv(10240).decode(FORMAT)
    if cnt > 0:
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da upload folder voi duong dan {path_folder}. Co {cnt} file khong duoc upload")
        client.sendall(f"Sever: Upload khong thanh cong {cnt} file".encode("utf-8"))
        print(f"Sever: Upload folder {path_folder} khong thanh cong {cnt} file")
    else:
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da upload folder voi duong dan {path_folder} thanh cong")
        client.sendall(f"Sever: Upload thanh cong toan bo folder".encode("utf-8"))
        print(f"Sever: Upload thanh cong toan bo folder")
# Hàm xác thực account của một client: Tìm thông tin client trong file users
def authenticateClient(username, password):

    with open("DataServer/users.csv", mode = "r") as file:
        reader = csv.reader(file)
        # fields = next(reader)
        for row in reader:
            # Giống với vector ví dụ: vector<string> a = {"username", "password"}
            if(len(row) == 2 and row[0] == username and row[1] == password):
                return True
        
    return False

def serverReceive(client, addr, list_connection):
    client.settimeout(600)
    try:
        message = client.recv(10240).decode(FORMAT)
        if not message:
            print(f"Client {addr} đã đóng kết nối.")
            list_connection.remove((client, addr))
            client.close()
        else:    
            return message
    except socket.timeout:
        print(f"Client {addr}: TimeOut.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi sever do qua timeout")
        list_connection.remove((client, addr))
        client.close()
    except ConnectionResetError:
        print(f"Client {addr}: đột ngột ngắt kết nối.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dot ngot ngat ket noi toi sever")
        list_connection.remove((client, addr))
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi nhận dữ liệu từ:{addr}.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi sever chua ro ly do")
        list_connection.remove((client, addr))
        client.close()
    return None
        

def serverSend(client, addr, list_connection ,message):
    try:

        print(f"Da gui thong bao den Client: {addr}.")
        client.sendall(message.encode(FORMAT))
    except socket.error:
        print(f"Client {addr} đã ngắt kết nối.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi sever")
        list_connection.remove((client, addr))
        client.close()
    except ConnectionResetError:
        print(f"Client {addr} đột ngột ngắt kết nối.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dot ngot ngat ket noi toi sever")
        list_connection.remove((client, addr))
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi gửi dữ liệu đến Client: {addr}.")
        #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi sever chua ro ly do")
        list_connection.remove((client, addr))
        client.close()


#ham nhan du lieu tu client va gui phan hoi
def handleClient(client, addr, list_connection) :
    print(f"Ket noi thanh cong voi Client: {addr} .")

    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:
            serverSend(client, addr, list_connection, "Da ket noi thanh cong den sever")
            tmp = serverReceive(client, addr, list_connection)
            # Nhận thông tin account từ client
            serverSend(client, addr,list_connection,"Enter your username and password to login")
            login_information = ""
            login_information = serverReceive(client, addr, list_connection)
            # if login_information is None:
            #     serverSend()
            #     continue
            #print(f"Nhận Username, Password từ Client: {addr}")

            username, password = login_information.split(",")
            if(authenticateClient(username, password)):

                #operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dang nhap voi ten tai khoan la {username}")
                #client.sendall("Successful".encode("utf-8"))
                print(f"Server: Login successfully towards account {username}")
                serverSend(client, addr, list_connection, "Successful")
                break
            else:
                #client.sendall("Unsuccessfull".encode(FORMAT))
                serverSend(client, addr, list_connection, "Unsuccessful")
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""

        while True:
            # try:
            #     data = client.recv(10240)
            # except socket.timeout:
            #     print(f"Da ngat ket noi voi Client {client, addr} do TimeOut.")
            #     list_connection.remove((client, addr))
            #     break
            data = serverReceive(client, addr, list_connection)
            if data is None:
                return
            #data = data.decode(FORMAT)
            if data == "exit":

                print(f"Client {addr}: Đã đăng xuất khỏi Server.")

                #operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da ngat ket noi voi sever")

                list_connection.remove((client, addr))
                break
            if data == "uploadFile":
                #gui yeu cau
                request = "Nhap vao duong dan hoac ten file: "
                serverSend(client, addr, list_connection, request)
                #nhan ten file hoac duong dan
                #msg = client.recv(10240).decode(FORMAT)
                msg = serverReceive(client, addr, list_connection)
                if msg is None:
                    return 
                serverSend(client, addr, list_connection, "da nhan")
                if msg == "CANCEL":
                    continue
                # operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau upload file voi duong dan {msg}")
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(client, msg, addr):
                    #operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da upload file voi duong dan {msg} thanh cong")
                    resp = "Success"
                    serverSend(client, addr, list_connection, resp)
                else:
                    resp = "Failed"
                    serverSend(client, addr, list_connection, resp)
            if data == "downloadFile":
                #gui yeu cau: Lấy thông tin từ gui
                request = "Nhập tên file hoặc dường đẫn: "
                serverSend(client, addr, list_connection, request)
                #nhan ten file hoac duong dan
                msg = serverReceive(client, addr, list_connection)
                if msg == "CANCEL":
                    continue
                #operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau download file voi duong dan {msg}")
                print(f"Client {addr}: Download file voi duong dan {msg}")
                if downloadFile(client, msg, addr):
                    #operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da download file voi duong dan {msg} thanh cong")
                    resp = "Success"
                    serverSend(client, addr, list_connection, resp)
                else:
                    resp = "Failed"
                    serverSend(client, addr, list_connection, resp)
            if data == "uploadFilesInFolderSequentially":
                #gui yeu caus
                request = "Nhap vao duong dan den folder: "
                serverSend(client, addr, list_connection, request)
                #nhan ten folder
                msg = serverReceive(client, addr, list_connection)
                serverSend(client, addr, list_connection, "da nhan")
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau upload folder voi duong dan {msg}")
                print(f"Client {addr}: Upload folder voi duong dan {msg}")
                uploadFilesInFolderSequentially(client, msg, addr)
    except Exception as e:
        print(f"(Hàm ngoài) Connect Error {e} from Client : {client, addr}")
    client.close()
    

#tao socket

def main():
    sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever.bind((HOST, PORT))
    sever.listen(NUMBER_OF_CLIENT + 1)
    print("Sever dang lang nghe...")
    operationHistory("\n------------------------------------------------------------------------------------------------------------------------------------")
    operationHistory("\n" + str(getTime()) + ":" + "Sever mo ket noi")
    #tao da luong
    list_connection = []
    while True:
        if len(list_connection) < NUMBER_OF_CLIENT:
            client, addr = sever.accept()
            print(f"Account [{len(list_connection) + 1}/{NUMBER_OF_CLIENT}]")
            operationHistory("\n" + str(getTime()) + ":" + f"Client {addr} da ket noi toi sever")
            list_connection.append((client, addr))
            thread = threading.Thread(target = handleClient, args = (client, addr, list_connection))
            thread.daemon = True
            thread.start()
           
if __name__ == "__main__":
    main()
        # operationHistory("\n" + str(getTime()) + ":" + "Sever da ngat ket noi")
        # operationHistory("--------------------------------------------")


