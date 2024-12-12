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
LIST_FORBIDEN_FILE = ["DataServer/users.csv", "DataServer/OperationHistory.txt", "DataServer/ErrorDownload.txt", "DataServer/ErrorUpload.txt"]
PATH_ERROR_DOWNLOAD = "DataServer/ErrorDownload.txt"
PATH_ERROR_UPLOAD = "DataServer/ErrorUpload.txt"

#HOST, PORT, NumberOfClient, FORMAT
HOST = socket.gethostname()
PORT = 12000
NUMBER_OF_CLIENT = 10
FORMAT = "utf-8"

#!Các hàm liên quan đến xử lí tên file
# Lay tu ki tu "/" cuoi cung tro ve sau trong duong dan hoac ten file
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

# Kiem tra xem co ki tu "/" trong ham "name" o tren chua
def checkSlashInFileName(s):
    if s[0] == "/":
        return True
    return False

# Kiem tra xem ten duong dan co "/" khong
def checkSlashInPath(s):
    for i in s:
        if i == "/":
            return True
    return False

# Lay phan ten file va khong lay them phan mo rong
def getNameWithNotExten(name):
    res = name[0 : name.index(".")]
    return res

# Lay phan mo rong cua file
def getExten(name):
    res = name[name.index(".") : len(name)]
    return res
        
# Kiem tra xem file ton tai khong
def checkExist(path):
    if os.path.isfile(path):
        return True
    return False

#!Các hàm liên quan đến viết nhật kí LOG
# Ham lay thoi gian thuc
def getTime():
    local_time = time.strftime("%a %d-%m-%Y %H:%M:%S", time.localtime(time.time()))
    return local_time

# Ghi vao nhat ky 
def operationHistory(msg):
    ofs = open(PATH_HISTORY, "a", encoding = FORMAT)
    ofs.write(msg)
    ofs.close()

#!Các hàm UPLOAD
# Viet vao file nhung tai khoan bi loi upload file do ngat ket noi dot ngot
def writeErrorUpload(username, file_path):
    data = username + ' ' + file_path
    ofs = open(PATH_ERROR_UPLOAD, "a", encoding = "utf-8")
    ofs.write(data)
    ofs.close()

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

def removeLineInFileUpload(delete_line):
    try:
        # Đọc và lọc các dòng khác với delete_line
        with open(PATH_ERROR_UPLOAD, 'r') as file:
            filtered_lines = [line for line in file if line.strip() != delete_line.strip()]

        # Ghi các dòng đã lọc vào file
        with open(PATH_ERROR_UPLOAD, 'w') as file:
            file.writelines(filtered_lines)
    except FileNotFoundError:
        print(f"ERROR: File '{PATH_ERROR_UPLOAD}' is not exist.")
    except PermissionError:
        print(f"ERROR: You do not have permission to write to the file. '{PATH_ERROR_UPLOAD}'.")
    except Exception as e:
        print(f"An error has occurred: {e}")

# Ham upload file tu client len server
def uploadFile(client, file_name, addr, username):
    # Lay ten file can upload
    tmp = name(file_name)
    # Kiem tra xem trong do da co "/" neu khong co thi them vao
    if not checkSlashInFileName(tmp):
        tmp = "/" + tmp
    # Lay ten file khong chua phan mo rong va lay phan mo rong de sau nay dat ten moi cho file neu file da ton tai
    name_with_not_exten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    # Ten thu muc can duoc viet vao
    file_write = PATH_SERVER + tmp
    #kiem tra xem trong thu muc server co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(file_write):
            tmp = name_with_not_exten + "(" + str(i) + ")" + exten
            file_write = PATH_SERVER + tmp
            i += 1

    # Nhan kich thuoc file tu client va gui lai thong bao den cho client
    size_recv = client.recv(1024).decode(FORMAT)
    size = int(size_recv)
    sizeResp = "Recv success"
    client.sendall(sizeResp.encode(FORMAT))

    # Mo file va lam viec 
    with open(file_write, "wb") as ofs:
        # sw la kich thuoc bien xem da nhan bao nhieu du lieu tu client da bang voi kich thuoc file chua
        sw = 0
        while size > sw:
            # Nhan du lieu tu client ghi vao file va gui lai thong bao den cho client
            try:
                data = client.recv(1024)
            except Exception as e:
                #print(f"Sever: There were an error when uploading file {file_name}/ Connect Error:[{addr}].")
                writeErrorUpload(username, file_name)
                return False
            if not data:
                break
            ofs.write(data)
            sw += len(data)
            try:
                client.sendall("Received".encode("utf-8"))
            except Exception as e:
                #print(f"Sever: There were an error when uploading file {file_name}/ Connect Error:[{addr}].")
                writeErrorUpload(username, file_write)
                return False
        # Nhan thong bao da gui xong tu client
        temp = client.recv(1024).decode("utf-8")
    
    # Gui trang thai den cho client va nhan thong bao tu client
    print(f"Sever: The file upload request from the client at {addr} has been completed. The file is now stored at {file_write} on the server.")
    client.sendall(f"The file is now stored at {file_write} on the server.".encode(FORMAT))
    temp = client.recv(1024).decode(FORMAT)
    return True

def handleUploadFile(client, addr, list_connection, username):

    msg = client.recv(1024).decode(FORMAT)
    if msg is None:
        return "BACK"
    client.sendall("Received".encode(FORMAT))
    if msg == "CANCEL":
        return "BACK"
    operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has requested to upload the file with the path {msg}.")
    print(f"Client {addr}: Upload file with the path {msg}")
    if uploadFile(client, msg, addr, username):
        operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has successfully uploaded the file with the path {msg}.")
        resp = "Success"
        client.sendall(resp.encode(FORMAT))
    else:
        resp = "Failed"
        client.sendall(resp.encode(FORMAT))
        list_connection.remove((client, addr))
        return "ERROR"
    return "BACK"

#!Các hàm liên quan đến DOWNLOAD

# Kiem tra xem file co trong danh sach khong duoc tai khong
def isForbiddenFile(file_name):
    for file in LIST_FORBIDEN_FILE:
        if file == file_name:
            return True
    return False

# Viet vao file nhung tai khoan bi loi tai file do ngat ket noi dot ngot
def writeErrorDownload(username, file_path):
    data = username + ' ' + file_path + '\n'
    ofs = open(PATH_ERROR_DOWNLOAD, "a", encoding = "utf-8")
    ofs.write(data)
    ofs.close()

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

#*Nhận đầu vào là 1 dòng, xóa dòng đó ra khỏi File
def removeLineInFileDownLoad(delete_line):
    try:
        # Đọc và lọc các dòng khác với delete_line
        with open(PATH_ERROR_DOWNLOAD, 'r') as file:
            filtered_lines = [line for line in file if line.strip() != delete_line.strip()]

        # Ghi các dòng đã lọc vào file
        with open(PATH_ERROR_DOWNLOAD, 'w') as file:
            file.writelines(filtered_lines)
    except FileNotFoundError:
        print(f"ERROR: File '{PATH_ERROR_DOWNLOAD}' is not exist.")
    except PermissionError:
        print(f"ERROR: You do not have permission to write to the file. '{PATH_ERROR_DOWNLOAD}'.")
    except Exception as e:
        print(f"An error has occurred: {e}")
        
# Ham download file
def downloadFile(client, Path, addr, username):
    # Gui kich thuoc file client yeu cau tai xuong va nhan lai thong bao
    size = os.path.getsize(Path)
    client.sendall(str(size).encode(FORMAT))
    # Nhan ten file
    file_name_resp = client.recv(1024).decode(FORMAT)

    # Mo va lam viec voi file
    ifs = open(Path, "rb")
    while 1:
        data = ifs.read(1024)
        if not data:
            break
        # gui du lieu. Neu khong gui duoc thi viet lai file khong gui duoc
        try:
            client.sendall(data)
            resp = client.recv(1024).decode("utf-8")
        #! Bắt lỗi gián đoạn kết nối
        except socket.error:
            #print(f"Client {addr}: Connection interrupted when DOWNLOAD_FILE.")
            writeErrorDownload(username, Path)
            return False
        #! Bắt lỗi dừng chương trình bên Client
        except ConnectionResetError:
            #print(f"Client {addr}: Abruptly disconnected while downloading the file with the path {Path}.")
            writeErrorDownload(username, Path)
            return False
    ifs.close()
    print(f"The file download request from client {addr} has been completed.")
    return True

def handleDownloadFile(client, addr, list_connection, username):
    #Nhận tên file hoặc Cancel
    while 1:
        msg = client.recv(1024).decode(FORMAT)
        if msg == "CANCEL":
            return "BACK"
        
        # Kiem tra xem file co ton tai hoac hop le khi nhap duong dan khong
        tmp = name(msg)
        if not checkSlashInFileName(tmp):
            tmp = "/" + tmp
        Path = PATH_SERVER + tmp
        # Kiem tra file bi cam tai khong
        if isForbiddenFile(Path):
            msg = "File is in list forbidden file. Can't download this file"
            print(msg)
            client.sendall("forbidden file".encode("utf-8"))
            continue
        # Nhap duong dan khong hop le hoac file khong ton tai
        if (checkSlashInPath(msg) and Path != msg) or not checkExist(Path):
            msg = "Not exist"
            print("File is not exist")
            client.sendall(msg.encode("utf-8"))
            continue
        message = "Exist"
        client.sendall(message.encode(FORMAT))
        break
    #Neu có thi thuc hien tai
    
    respMsg = client.recv(1024).decode(FORMAT)
    operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has requested to download the file with the path {msg}.")
    print(f"Client {addr}: Download file with the path {msg}")
    if downloadFile(client, Path, addr, username):
        operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has successfully downloaded the file with the path {msg}.")
        resp = "Success"
        client.sendall(resp.encode(FORMAT))
    else:
        list_connection.remove((client, addr))
        return "ERROR"
    return "BACK"

#! Các hàm liên quan đến UPLOAD_FOLDER
def uploadFilesInFolderSequentially(client, path_folder, addr, username):
    # Nhan so luong file tu client
    number_of_file = client.recv(1024).decode(FORMAT)
    number_of_file = int(number_of_file)
    # Neu khong co file nao thi gui thong bao den client và dung upload
    if number_of_file == 0:
        print(f"Folder {path_folder} was sent by client {addr} is empty. Can't upload folder")
        client.sendall(f"Sever: Folder {path_folder} was sent by client {addr} is empty. Can't upload folder".encode(FORMAT))
        return
    client.sendall("Received".encode(FORMAT))
    
    # Bat dau upload file tuan tu cho toi khi du so luong file
    i = 0
    # Dem xem co bao nhieu file khong tai thanh cong
    cnt = 0
    while i < number_of_file:
        i += 1
        files = client.recv(1024).decode(FORMAT)
        client.sendall("Received".encode(FORMAT))
        if uploadFile(client, path_folder + "/" + files, addr, username):
            resp = "Success"
            client.sendall(resp.encode(FORMAT))
        else:
            cnt += 1
            resp = "Failed"
            client.sendall(resp.encode(FORMAT))
    tmp = client.recv(1024).decode(FORMAT)

    # Gui trang thai den cho client va ghi vao nhat ky
    if cnt > 0:
        operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} has uploaded a folder with the path {path_folder}. {cnt} files failed to upload.")
        client.sendall(f"Server: The upload was unsuccessful for {cnt} files.".encode("utf-8"))
        print(f"Server: Upload folder {path_folder} was unsuccessful for {cnt} file")
    else:
        operationHistory("\n" + str(getTime()) + ": " + f"Client {addr} has successfully uploaded the folder with the path {path_folder}.")
        client.sendall(f"Server: The entire folder has been successfully uploaded.".encode("utf-8"))
        print(f"Server: The entire folder has been successfully uploaded.")

#!Xác thực tài khoản
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



# def handleDownloadFile(client, addr, list_connection, username):
#     #*Nhận tên file hoặc Cancel
#     msg = client.recv(1024).decode(FORMAT)
#     if msg == "CANCEL":
#         return "BACK"
#     #*Kiểm tra lỗi về cú pháp, truy cập File không cho phép, kiểm tra File có tồn tại không và gửi trả lời cho Client
#     #*Kiểm tra lỗi về cú pháp 
#     tmp = name(msg)
#     if not checkSlashInFileName(tmp):
#         tmp = "/" + tmp
#     Path = PATH_SERVER + tmp
#     #*Check File không cho phép truy cập
#     if isForbiddenFile(Path):
#         msg = "File is in list forbidden file. Can't download this file"
#         print(msg)
#         client.sendall("ff".encode("utf-8"))
#         return "BACK"
#     #*Kiểm tra tên file hợp lệ và file có tồn tại hay không
#     if (checkSlashInPath(msg) and Path != msg) or not checkExist(Path):
#         msg = "Not exist"
#         print("File is not exist")
#         client.sendall(msg.encode("utf-8"))
#         return "BACK"
#     #*Thực hiện gửi File cho Client
#     else:
#         #*Gửi thông báo về trạng thái File đã tồn tại và bắt đâu tải
#         message = "Exist"
#         client.sendall(message.encode(FORMAT))
#         respMsg = client.recv(1024).decode(FORMAT)
#         #*Ghi nhật kí về lần tải
#         operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da yeu cau download file voi duong dan {msg}")
#         print(f"Client {addr}: Download file voi duong dan {msg}")
#         #*Kiểm tra hàm downloadFile có lỗi đường truyền khi đang gửi hay không
#         #*Nếu không có lỗi thì ghi nhật gửi File thành công và gửi tin nhắ "Success" đến Client 
#         if downloadFile(client, Path, addr, username):
#             operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr} da download file voi duong dan {msg} thanh cong")
#             resp = "Success"
#             client.sendall(resp.encode("utf-8"))
#         #*Nếu có lỗi trong quá trình truyền thì sẽ được hàm Handle xử lí
#     return "BACK"

#! Hàm xử lí các yêu cầu của Client
def handleClient(client, addr, list_connection) :
    STATUS = "" #? Dùng để cập nhật trạng thái làm việc với Client
    client.settimeout(6000)
    print(f"Successfully connected to the client: {addr}.")

    # Xử lý các yêu cầu khác từ client
    try:
        # Gửi yêu cầu login đến client
        while True:

            client.sendall("Successfully connected to the server.".encode("utf-8"))
            tmp = client.recv(1024).decode(FORMAT)

            # Nhận thông tin account từ client
            STATUS = "LOGIN"
            client.sendall("Enter your username and password to login".encode("utf-8"))
            login_information = ""
            login_information = client.recv(1024).decode(FORMAT)

            username, password = login_information.split(",")
            if(authenticateClient(username, password)):

                operationHistory("\n" + str(getTime()) + ": " + f"Client {addr}: Has logged in with the username {username}.")

                print(f"Server: Login successfully towards account {username}")
                client.sendall("Successful".encode("utf-8"))
                break
            else:
                client.sendall("Unsuccessful".encode("utf-8"))
                print(f"Server: Login unsuccessfully towards account {username}")
        #gui nhan file
        data = ""

        # Xử lý các yêu cầu từ client
        while True:
            STATUS = "CHOOSEN"
            data = client.recv(1024).decode(FORMAT)
            if data == "exit":
                STATUS = "EXIT"
                print(f"Client {addr}: Has logged out of the server.")

                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has disconnected from the server.")

                list_connection.remove((client, addr))
                break

            if data == "uploadFile":
                STATUS = "UPLOAD_FILE"
                #gui yeu cau
                #gui yeu cau: Lấy thông tin từ gui
                error_name = getErrorUpload(username)
                client.sendall(error_name.encode("utf-8"))
                #nhan ten file hoac duong dan
                if error_name != "NoError":
                    continue_upload = client.recv(1024).decode(FORMAT)
                    if continue_upload == "Y":
                        #os.remove(error_name)
                        is_done = handleUploadFile(client, addr, list_connection, username)
                        if is_done == "BACK":
                            #XÓA file lỗi ra khỏi file errordownload.txt
                            removeLineInFileUpload(error_name)
                            continue
                        elif is_done == "ERROR":
                            break
                    elif continue_upload == "N":
                        removeLineInFileUpload(error_name)
                        request = "Enter the file path or filename: "
                        client.sendall(request.encode(FORMAT))
                        is_done = handleUploadFile(client, addr, list_connection, username)
                        if is_done == "BACK":
                            continue
                        elif is_done == "ERROR":
                            break
                else:
                    request = "Enter the file path or filename: "
                    client.sendall(request.encode(FORMAT))
                    is_done = handleUploadFile(client, addr, list_connection, username)
                    if is_done == "BACK":
                        continue
                    elif is_done == "ERROR":
                        break

                
                

            if data == "downloadFile":
                #*Cập nhật trạng thái làm việc 
                STATUS = "DOWNLOAD_FILE"
                #gui yeu cau: Lấy thông tin từ gui
                error_name = getErrorDownload(username)
                client.sendall(error_name.encode("utf-8"))
                if error_name != "NoError":
                    continue_download = client.recv(1024).decode(FORMAT)
                    if continue_download == "Y":
                        is_done = handleDownloadFile(client, addr, list_connection, username)
                        if is_done == "BACK":
                            #XÓA file lỗi ra khỏi file errordownload.txt
                            removeLineInFileDownLoad(error_name)
                            continue
                        elif is_done == "ERROR":
                            break
                    elif continue_download == "N":
                        removeLineInFileDownLoad(error_name)
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
                request = "Enter the path to the folder: "
                client.sendall(request.encode("utf-8"))
                #nhan ten folder
                msg = client.recv(1024).decode(FORMAT)
                client.sendall("Received".encode("utf-8"))
                if msg == "CANCEL":
                    continue
                operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has requested to upload the folder with the path {msg}.")
                print(f"Client {addr}: Upload folder with the path {msg}")
                uploadFilesInFolderSequentially(client, msg, addr, username)
    except TimeoutError:
        print(f"Client {addr}: Timeout when {STATUS}.")
        list_connection.remove((client, addr))
    except socket.error:
        print(f"Client {addr}:  Connection interrupted when {STATUS}.")
        list_connection.remove((client, addr))
    except ConnectionResetError:
        print(f"Client {addr}: Abruptly shut down when {STATUS}.")
        list_connection.remove((client, addr))
    except Exception as e:
        print(f"Client {addr}: error {e} when {STATUS}")
        list_connection.remove((client, addr))
    client.close()

def main():
    sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever.bind((HOST, PORT))
    sever.listen(NUMBER_OF_CLIENT + 1)
    print("The server is listening...")
    operationHistory("\n------------------------------------------------------------------------------------------------------------------------------------")
    operationHistory("\n" + str(getTime()) + ":" + "The server has opened the connection.")
    #tao da luong
    list_connection = []
    while True:
        if len(list_connection) < NUMBER_OF_CLIENT:
            client, addr = sever.accept()
            print(f"Account [{len(list_connection) + 1}/{NUMBER_OF_CLIENT}]")
            operationHistory("\n" + str(getTime()) + ":" + f"Client {addr} has connected to the server.")
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
