import socket
import threading
import os
import csv
import time
#duong dan toi thu muc sever va client
PathSever = "DataServer"  
PathUsers = "users.csv"

#HOST, PORT, NumberOfClient
HOST = socket.gethostname()
PORT = 12000
NumberOfClient = 1
FORMAT = 'utf-8'

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
    sizeRecv = client.recv(1024).decode(FORMAT)
    size = int(sizeRecv)
    sizeResp = "Nhan thanh cong"
    client.sendall(sizeResp.encode(FORMAT))
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
        client.sendall("Loi ket noi".encode(FORMAT))
        temp = client.recv(1024).decode(FORMAT)
        return False
    print(f"Sever: Yeu cau upload file cua client {addr} hoan thanh. File dang duoc luu tru tai {fileWrite} tren sever")
    client.sendall(f"File dang duoc luu tru tai {fileWrite} tren sever".encode(FORMAT))
    temp = client.recv(1024).decode(FORMAT)
    return True

def downloadFile(client, fileName, addr):
    tmp = name(fileName)
    if not check(tmp):
        tmp = '/' + tmp
    Path = PathSever + tmp
    if (check1(fileName) and Path != fileName) or not checkExist(Path):
        msg = "Not exist"
        client.sendall(msg.encode(FORMAT))
        return
    else:
        msg = "Exist"
        client.sendall(msg.encode(FORMAT))
        respMsg = client.recv(1024).decode(FORMAT)
    size = os.path.getsize(Path)
    client.sendall(str(size).encode(FORMAT))
    sizeResp = client.recv(1024).decode(FORMAT)
    ifs = open(Path, "rb")
    while 1:
        data = ifs.read(1024)
        if not data:
            break
        client.sendall(data)
    ifs.close()
    resp = client.recv(1024).decode(FORMAT)
    if int(resp) != size:
        print("Loi ngung ket noi tu sever toi client")
        return False
    print(f"Yeu cau download file cua client {addr} hoan thanh.")
    return True

def uploadFilesInFolderSequentially(client, pathFolder, addr):
    size = client.recv(1024).decode(FORMAT)
    size = int(size)
    if size == 0:
        print(f"Folder '{pathFolder}'was sent by client {addr} is empty. Can't upload folder")
        client.sendall(f"Folder '{pathFolder}'was sent by client {addr} is empty. Can't upload folder".encode(FORMAT))
        return
    client.sendall("da nhan".encode(FORMAT))
    i = 0
    cnt = 0
    while i < size:
        i += 1
        files = client.recv(1024).decode(FORMAT)
        client.sendall("da nhan".encode(FORMAT))
        if uploadFile(client, pathFolder + "/" + files, addr):
            resp = "Success"
            client.sendall(resp.encode(FORMAT))
        else:
            cnt += 1
            resp = "Failed"
            client.sendall(resp.encode(FORMAT))
    tmp = client.recv(1024).decode(FORMAT)
    if cnt > 0:
        client.sendall(f"Sever: Upload khong thanh cong {cnt} file")
    else:
        client.sendall(f"Sever: Upload thanh cong toan bo folder")

def activityHistory():
    print("")

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

def server_receive(client, addr, list_Connection):
    client.settimeout(600)
    try:
        message = client.recv(1024).decode(FORMAT)
        if not message:
            print(f"Client {addr} đã đóng kết nối.")
            list_Connection.remove((client, addr))
            client.close()
        else:    
            #print(f"Client{addr}: {message}")
            return message
    except socket.timeout:
        print(f"Client {addr}: TimeOut.")
        list_Connection.remove((client, addr))
        client.close()
    except ConnectionResetError:
        print(f"Client {addr}: đột ngột ngắt kết nối.")
        list_Connection.remove((client, addr))
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi nhận dữ liệu từ:{addr}.")
        list_Connection.remove((client, addr))
        client.close()
    return None
    
        

def server_send(client, addr, list_Connection ,message):
    try:
        print(f"Da gui thong bao den Client: {addr}.")
        client.sendall(message.encode(FORMAT))
    except socket.error:
        print(f"Client {addr} đã ngắt kết nối.")
        list_Connection.remove((client, addr))
        client.close()
    except ConnectionResetError:
        print(f"Client {addr} đột ngột ngắt kết nối.")
        list_Connection.remove((client, addr))
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi gửi dữ liệu đến Client: {addr}.")
        list_Connection.remove((client, addr))
        client.close()





# def init_Connection(client, addr, list_Connection):

#     if len(list_Connection) > NumberOfClient:
#         #server_send(client, addr, list_Connection, "Server da day.")
#         return False
#     else:
#         server_send(client, addr,list_Connection,"Enter your username and password to login")
#         return True


#ham nhan du lieu tu client va gui phan hoi
def handle_Client(client, addr, list_Connection) :
    print(f"Ket noi thanh cong voi Client: {addr} .")

    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:
            
            # i = 0
            # while True:

            #     if init_Connection == False:
            #         continue
            #     else:
            #         break
            #init_Connection(client, addr, list_Connection)

            # Nhận thông tin account từ client
            server_send(client, addr,list_Connection,"Enter your username and password to login")
            login_information = ""
            login_information = server_receive(client, addr, list_Connection)
            if login_information is None:
                 return
            #print(f"Nhận Username, Password từ Client: {addr}")

            username, password = login_information.split(',')
            if(authenticate_client(username, password)):
                print(f"Server: Login successfully towards account {username}")
                server_send(client, addr, list_Connection, "Successful")
                break
            else:
                #client.sendall("Unsuccessfull".encode(FORMAT))
                server_send(client, addr, list_Connection, "Unsuccessful")
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""

        while True:
            # try:
            #     data = client.recv(1024)
            # except socket.timeout:
            #     print(f"Da ngat ket noi voi Client {client, addr} do TimeOut.")
            #     list_Connection.remove((client, addr))
            #     break
            data = server_receive(client, addr, list_Connection)
            if data is None:
                return
            #data = data.decode(FORMAT)
            if data == "exit":
                print(f"Client {addr}: Đã đăng xuất khỏi Server.")
                list_Connection.remove((client, addr))
                break
            if data == "uploadFile":
                #gui yeu cau
                request = "Nhap vao duong dan hoac ten file: "
                server_send(client, addr, list_Connection, request)
                #nhan ten file hoac duong dan
                #msg = client.recv(1024).decode(FORMAT)
                msg = server_receive(client, addr, list_Connection)
                if msg is None:
                    return 
                if msg == "CANCEL":
                    continue
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(client, msg, addr):
                    resp = "Success"
                    server_send(client, addr, list_Connection, resp)
                else:
                    resp = "Failed"
                    server_send(client, addr, list_Connection, resp)
            if data == "downloadFile":
                #gui yeu cau: Lấy thông tin từ gui
                request = "Nhập tên file hoặc dường đẫn: "
                server_send(client, addr, list_Connection, request)
                #nhan ten file hoac duong dan
                msg = server_receive(client, addr, list_Connection)
                if msg == "CANCEL":
                    continue
                print(f"Client {addr}: Download file voi duong dan {msg}")
                if downloadFile(client, msg, addr):
                    resp = "Success"
                    server_send(client, addr, list_Connection, resp)
                else:
                    resp = "Failed"
                    server_send(client, addr, list_Connection, resp)
            if data == "uploadFilesInFolderSequentially":
                #gui yeu cau
                request = "Nhap vao duong dan den folder: "
                server_send(client, addr, list_Connection, request)
                #nhan ten folder
                msg = server_receive(client, addr, list_Connection)
                if msg == "CANCEL":
                    continue
                print(f"Client {addr}: Upload folder voi duong dan {msg}")
                uploadFilesInFolderSequentially(client, msg, addr)
    except Exception as e:
        print(f"(Hàm ngoài) Connect Error {e} from Client : {client, addr}")
    client.close()
    

#tao socket

def main():
    sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever.bind((HOST, PORT))
    sever.listen(NumberOfClient + 1)
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


