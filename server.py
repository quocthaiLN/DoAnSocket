import socket
import threading
import os
import csv
import time
from tkinter import *
from tkinter import scrolledtext
#duong dan toi thu muc server va client
PATH_SERVER = "DataServer"
PATH_ADMIN = "DataServer/admin.csv"
PATH_USER = "DataServer/users.csv"
PATH_HISTORY = "DataServer/OperationHistory.txt"
LIST_FORBIDEN_FILE = ["DataServer/users.csv", "DataServer/OperationHistory.txt"]
PATH_ERROR_DOWNLOAD = "DataServer/ErrorDownload.txt"
PATH_ERROR_UPLOAD = "DataServer/ErrorUpload.txt"

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
    ofs = open(PATH_HISTORY, "a", encoding = FORMAT)
    ofs.write(msg)
    ofs.close()


#ham upload file tu client len server
def uploadFile(client, file_name, addr):
    tmp = name(file_name)
    if not check(tmp):
        tmp = "/" + tmp
    name_with_not_exten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PATH_SERVER + tmp
    #kiem tra xem trong thu muc server co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(fileWrite):
            tmp = name_with_not_exten + "(" + str(i) + ")" + exten
            fileWrite = PATH_SERVER + tmp
            i += 1
    sizeRecv = client.recv(1024).decode(FORMAT)
    size = int(sizeRecv)
    
    sizeResp = "Nhan thanh cong"
    client.sendall(sizeResp.encode(FORMAT))
    #ofs = open(fileWrite, "wb")
    with open(fileWrite, "wb") as ofs:
        sw = 0
        while size > sw:
            try:
                data = client.recv(1024)
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
        temp = client.recv(1024).decode("utf-8")
    #ofs.close()

    print(f"Sever: Yeu cau upload file cua client {addr} hoan thanh. File dang duoc luu tru tai {fileWrite} tren sever")
    client.sendall(f"File dang duoc luu tru tai {fileWrite} tren sever".encode(FORMAT))
    temp = client.recv(1024).decode(FORMAT)
    return True

def isForbiddenFile(file_name):
    for file in LIST_FORBIDEN_FILE:
        if file == file_name:
            return True
    return False

def writeErrorDownload(username, file_path):
    data = username + ' ' + file_path + '\n'
    ofs = open(PATH_ERROR_DOWNLOAD, "a", encoding = "utf-8")
    ofs.write(data)
    ofs.close()

def writeErrorUpload(username, file_path):
    data = username + ' ' + file_path
    ofs = open(PATH_ERROR_UPLOAD, "a", encoding = "utf-8")
    ofs.write(data)
    ofs.close()

def downloadFile(client, Path, addr, username):

    size = os.path.getsize(Path)
    client.sendall(str(size).encode(FORMAT))
    sizeResp = client.recv(1024).decode(FORMAT)
    ifs = open(Path, "rb")
    while 1:
        data = ifs.read(1024)
        if not data:
            break
        try:
            client.sendall(data)
            resp = client.recv(1024).decode("utf-8")
        #! Bắt lỗi gián đoạn kết nối
        except socket.error:
            print(f"Client {addr}: bị gián đoạn kết nối khi DOWNLOAD_FILE.")
            writeErrorDownload(username, Path)
            return False
        #! Bắt lỗi dừng chương trình bên Client
        except ConnectionResetError:
            print(f"Client {addr}: đột ngột dừng chương trình khi DOWNLOAD_FILE.")
            writeErrorDownload(username, Path)
            return False
    ifs.close()
    print(f"Yeu cau download file cua client {addr} hoan thanh.")
    return True
#*Nhận vào tên Username kiểm tra xem Username này có bị lỗi ở lần đăng nhập trước không và trả kết quả
def getErrorDownload(username):
    with open(PATH_ERROR_DOWNLOAD, 'r') as file:
        line = file.readline()
        while line:
            line = line.strip()  # Loại bỏ ký tự xuống dòng '\n'
            if username in line:
                return line            
            line = file.readline()
    #*Nếu không thấy thì trả về NoError 
    return "NoError"

#*Nhận vào tên Username kiểm tra xem Username này có bị lỗi ở lần đăng nhập trước không và trả kết quả
def getErrorUpload(username):
    with open(PATH_ERROR_UPLOAD, 'r') as file:
        line = file.readline()
        while line:
            line = line.strip()  # Loại bỏ ký tự xuống dòng '\n'
            if username in line:
                return line            
            line = file.readline()
    #*Nếu không thấy thì trả về NoError 
    return "NoError"

def uploadFilesInFolderSequentially(client, path_folder, addr):
    size = client.recv(1024).decode(FORMAT)
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
        files = client.recv(1024).decode(FORMAT)
        client.sendall("da nhan".encode(FORMAT))
        if uploadFile(client, path_folder + "/" + files, addr):
            resp = "Success"
            client.sendall(resp.encode(FORMAT))
        else:
            cnt += 1
            resp = "Failed"
            client.sendall(resp.encode(FORMAT))
    tmp = client.recv(1024).decode(FORMAT)
    if cnt > 0:
        operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da upload folder voi duong dan {path_folder}. Co {cnt} file khong duoc upload")
        client.sendall(f"server: Upload khong thanh cong {cnt} file".encode("utf-8"))
        print(f"server: Upload folder {path_folder} khong thanh cong {cnt} file")
    else:
        operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da upload folder voi duong dan {path_folder} thanh cong")
        client.sendall(f"server: Upload thanh cong toan bo folder".encode("utf-8"))
        print(f"server: Upload thanh cong toan bo folder")
# Hàm xác thực account của một client: Tìm thông tin client trong file users
def authenticateClient(username, password):

    with open(PATH_USER, mode = "r") as file:
        reader = csv.reader(file)
        # fields = next(reader)
        for row in reader:
            # Giống với vector ví dụ: vector<string> a = {"username", "password"}
            if(len(row) == 2 and row[0] == username and row[1] == password):
                return True
        
    return False
#*Nhận đầu vào là 1 dòng, xóa dòng đó ra khỏi File
def removeLineInFile(delete_line):
    try:
        # Đọc và lọc các dòng khác với delete_line
        with open(PATH_ERROR_DOWNLOAD, 'r') as file:
            filtered_lines = [line for line in file if line.strip() != delete_line.strip()]

        # Ghi các dòng đã lọc vào file
        with open(PATH_ERROR_DOWNLOAD, 'w') as file:
            file.writelines(filtered_lines)
    except FileNotFoundError:
        print(f"Lỗi: File '{PATH_ERROR_DOWNLOAD}' không tồn tại.")
    except PermissionError:
        print(f"Lỗi: Không có quyền ghi vào file '{PATH_ERROR_DOWNLOAD}'.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# def serverReceive(client, addr, list_connection):
#     client.settimeout(600)
#     try:
#         message = client.recv(1024).decode(FORMAT)
#         if not message:
#             print(f"Client {addr} đã đóng kết nối.")
#             list_connection.remove((client, addr))
#             client.close()
#         else:    
#             return message
#     except socket.timeout:
#         print(f"Client {addr}: TimeOut.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi server do qua timeout")
#         list_connection.remove((client, addr))
#         client.close()
#     except ConnectionResetError:
#         print(f"Client {addr}: đột ngột ngắt kết nối.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dot ngot ngat ket noi toi server")
#         list_connection.remove((client, addr))
#         client.close()
#     except Exception as e:
#         print(f"Có lỗi {e} khi nhận dữ liệu từ:{addr}.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi server chua ro ly do")
#         list_connection.remove((client, addr))
#         client.close()
#     return None
        

# def serverSend(client, addr, list_connection ,message):
#     try:

#         print(f"Da gui thong bao den Client: {addr}.")
#         client.sendall(message.encode(FORMAT))
#     except socket.error:
#         print(f"Client {addr} đã ngắt kết nối.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi server")
#         list_connection.remove((client, addr))
#         client.close()
#     except ConnectionResetError:
#         print(f"Client {addr} đột ngột ngắt kết nối.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dot ngot ngat ket noi toi server")
#         list_connection.remove((client, addr))
#         client.close()
#     except Exception as e:
#         print(f"Có lỗi {e} khi gửi dữ liệu đến Client: {addr}.")
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da ngat ket noi toi server chua ro ly do")
#         list_connection.remove((client, addr))
#         client.close()

def handleDownloadFile(client, addr, list_connection, username):
    #*Nhận tên file hoặc Cancel
    msg = client.recv(1024).decode(FORMAT)
    if msg == "CANCEL":
        return "BACK"
    #*Kiểm tra lỗi về cú pháp, truy cập File không cho phép, kiểm tra File có tồn tại không và gửi trả lời cho Client
    #*Kiểm tra lỗi về cú pháp 
    tmp = name(msg)
    if not check(tmp):
        tmp = "/" + tmp
    Path = PATH_SERVER + tmp
    #*Check File không cho phép truy cập
    if isForbiddenFile(Path):
        msg = "File is in list forbidden file. Can't download this file"
        print(msg)
        client.sendall("ff".encode("utf-8"))
        return "BACK"
    #*Kiểm tra tên file hợp lệ và file có tồn tại hay không
    if (check1(msg) and Path != msg) or not checkExist(Path):
        msg = "Not exist"
        print("File is not exist")
        client.sendall(msg.encode("utf-8"))
        return "BACK"
    #*Thực hiện gửi File cho Client
    else:
        #*Gửi thông báo về trạng thái File đã tồn tại và bắt đâu tải
        message = "Exist"
        client.sendall(message.encode(FORMAT))
        respMsg = client.recv(1024).decode(FORMAT)
        #*Ghi nhật kí về lần tải
        operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau download file voi duong dan {msg}")
        print(f"Client {addr}: Download file voi duong dan {msg}")
        #*Kiểm tra hàm downloadFile có lỗi đường truyền khi đang gửi hay không
        #*Nếu không có lỗi thì ghi nhật gửi File thành công và gửi tin nhắ "Success" đến Client 
        if downloadFile(client, Path, addr, username):
            operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da download file voi duong dan {msg} thanh cong")
            resp = "Success"
            client.sendall(resp.encode("utf-8"))
        #*Nếu có lỗi trong quá trình truyền thì sẽ được hàm Handle xử lí
    return "BACK"

#ham nhan du lieu tu client va gui phan hoi
def handleClient(client, addr, list_connection) :
    STATUS = "" #? Dùng để cập nhật trạng thái làm việc với Client
    #*Đặt timeout là 60, khi quá lâu mà Client không giao tiếp thì ngắt kết nối
    client.settimeout(60)
    print(f"Ket noi thanh cong voi Client: {addr} .")
    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:
            client.sendall("Da ket noi thanh cong den server".encode("utf-8"))
            tmp = client.recv(1024).decode(FORMAT)
            # Nhận thông tin account từ client
            STATUS = "LOGIN"
            client.sendall("Enter your username and password to login".encode("utf-8"))
            login_information = ""
            login_information = client.recv(1024).decode(FORMAT)

            username, password = login_information.split(",")
            if(authenticateClient(username, password)):

                operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} da dang nhap voi ten tai khoan la {username}")
                print(f"Server: Login successfully towards account {username}")
                client.sendall("Successful".encode("utf-8"))
                break
            else:
                client.sendall("Unsuccessful".encode("utf-8"))
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""

        while True:
            STATUS = "CHOOSEN"
            data = client.recv(1024).decode(FORMAT)
            if data == "exit":
                STATUS = "EXIT"
                print(f"Client {addr}: Đã đăng xuất khỏi Server.")
                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da ngat ket noi voi server")
                list_connection.remove((client, addr))
                break
            if data == "uploadFile":
                STATUS = "UPLOAD_FILE"
                #gui yeu cau
                request = "Nhap vao duong dan hoac ten file: "
                client.sendall(request.encode("utf-8"))
                msg = client.recv(1024).decode(FORMAT)
                if msg is None:
                    return 
                client.sendall("da nhan".encode("utf-8"))
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau upload file voi duong dan {msg}")
                print(f"Client {addr}: Upload file voi duong dan {msg}")
                if uploadFile(client, msg, addr):
                    operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da upload file voi duong dan {msg} thanh cong")
                    resp = "Success"
                    client.sendall(resp.encode("utf-8"))
                else:
                    resp = "Failed"

            if data == "downloadFile":
                #*Cập nhật trạng thái làm việc 
                STATUS = "DOWNLOAD_FILE"
                #gui yeu cau: Lấy thông tin từ gui
                errorName = getErrorDownload(username)
                client.sendall(errorName.encode("utf-8"))
                if errorName != "NoError":
                    continue_download = client.recv(1024).decode(FORMAT)
                    if continue_download == "Y":
                        is_done = handleDownloadFile(client, addr, list_connection, username)
                        if is_done == "BACK":
                            #XÓA file lỗi ra khỏi file errordownload.txt
                            removeLineInFile(errorName)
                            continue
                        elif is_done == "ERROR":
                            break
                    elif continue_download == "N":
                        removeLineInFile(errorName)
                        is_done = handleDownloadFile(client, addr, list_connection, username)
                        if is_done == "BACK":
                            continue
                        elif is_done == "ERROR":
                            break
                else:
                    is_done = handleDownloadFile(client, addr, list_connection, username)
                    if is_done == "BACK":
                        continue
                    elif is_done == "ERROR":
                        break

            if data == "uploadFilesInFolderSequentially":
                STATUS = "UPLOAD_FILES_IN_FOLDER_SEQUENTIALLLY"
                #gui yeu cau
                request = "Nhap vao duong dan den folder: "
                client.sendall(request.encode("utf-8"))
                #nhan ten folder
                msg = client.recv(1024).decode(FORMAT)
                client.sendall("da nhan".encode("utf-8"))
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau upload folder voi duong dan {msg}")
                print(f"Client {addr}: Upload folder voi duong dan {msg}")
                uploadFilesInFolderSequentially(client, msg, addr)
    except TimeoutError:
        print(f"Client {addr}: Timeout khi {STATUS}.")
        list_connection.remove((client, addr))
    except socket.error:
        print(f"Client {addr}: bị gián đoạn kết nối khi {STATUS}.")
        list_connection.remove((client, addr))
    except ConnectionResetError:
        print(f"Client {addr}: đột ngột bị đóng khi {STATUS}.")
        list_connection.remove((client, addr))
    except Exception as e:
        print(f"Client {addr}: bị lỗi {e} khi {STATUS}")
        list_connection.remove((client, addr))
    client.close()

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






#tao socket

# def main():

#     # -------------- GUI ------------
#     win = Tk()
#     win.title("Server")

#     log_text = scrolledtext.ScrolledText(win, width = 80, height = 20)
#     log_text.pack(pady = 20)

#     start_server_btn = Button(win, text = "Start Server", state = NORMAL)
#     stop_server_btn = Button(win, text = "Stop Server", state = DISABLED)

#     # ----------------------------

#     flag = False
#     server = None
#     server_thread = None

#     def serverThreadFunction():
#         # python không có khai báo kiểu, nên không biết nó là biến toàn cục hay địa phương
#         # nonlocal -> biến được khai báo trước khi vô hàm
#         nonlocal server
#         try:
#             if server is None:
#                 server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 server.bind((HOST, PORT))
#                 server.listen(NUMBER_OF_CLIENT + 1)

#             # ----- GUI -------
#             log_text.insert(END, "Server dang lang nghe....\n")
#             log_text.see(END)
#             # ---------------
#             operationHistory("\n------------------------------------------------------------------------------------------------------------------------------------")
#             operationHistory("\n" + str(getTime()) + ":" + "server mo ket noi")

#             list_connection = []
#             while flag:
#                 try:
#                     if len(list_connection) < NUMBER_OF_CLIENT:
#                         client, addr = server.accept()
#                         # --------- GUI -------
#                         log_text.insert(END, f"Account [{len(list_connection) + 1}/{NUMBER_OF_CLIENT}]\n")
#                         log_text.see(END)
#                         # ------------------
#                         # == print(f"Account [{len(list_connection) + 1}/{NUMBER_OF_CLIENT}]")
#                         operationHistory("\n" + str(getTime()) + ":" + f"Client {addr} da ket noi toi server")
#                         list_connection.append((client, addr))
#                         thread = threading.Thread(target = handleClient, args = (client, addr, list_connection))
#                         thread.daemon = True
#                         thread.start()
#                 except socket.timeout:
#                     continue
#                 except OSError as e:
#                     if not flag:
#                         break
#                     log_text.insert(END, f"Error: {e}\n")
#         except Exception as e:
#             log_text.insert(END, f"Server error: {e}\n")
#         finally:
#             if server:
#                 server.close()
#                 server = None
#             log_text.insert(END, "Server stopped.\n")
#             log_text.see(END)

#     def startServer():
#         nonlocal server_thread
#         nonlocal flag
#         flag = True
#         server_thread = threading.Thread(target = serverThreadFunction)
#         server_thread.daemon = True
#         server_thread.start()

#         # ----------- GUI --------
#         nonlocal start_server_btn, stop_server_btn
#         start_server_btn.config(state = DISABLED)
#         stop_server_btn.config(state = NORMAL)
#         #--------------

#     def stopServer():
#         nonlocal flag, server
#         flag = False

#         if server:
#             try:
#                 server.close()
#                 server = None
#             except Exception as e:
#                 log_text.insert(END, f"Error closing server: {e}\n")
        
#         # ---------- GUI -------
#         log_text.insert(END, "Stopping Server...\n")
#         log_text.see(END)
#         nonlocal start_server_btn, stop_server_btn
#         stop_server_btn.config(state = DISABLED)
#         start_server_btn.config(state = NORMAL)
#         # --------------------
    
#     start_server_btn.config(command = startServer)
#     stop_server_btn.config(command = stopServer)

#     start_server_btn.pack(pady = 5)
#     stop_server_btn.pack(pady = 5)

#     def onClose():
#         if flag:
#             stopServer()
#         win.destroy()
    
#     win.protocol("WM_DELETE_WINDOW", onClose)
#     win.mainloop()

           
# if __name__ == "__main__":
#     main()