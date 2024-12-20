import socket
import os
import time
import getpass
import time

PATH_CLIENT = "DataClient"
FORMAT = "utf-8"
#HOST, PORT
HOST = socket.gethostname()
PORT = 12000

#!Các hàm liên quan đến xử lí tên file
# Lay tu ki tu "/" cuoi cung tro ve sau trong duong dan hoac ten file
def name(file_name):
    res = ""
    # Dem so ki tu "/" de tim den ki tu "/" cuoi cung
    cnt = 0
    for chara in file_name:
        if chara == "/":
            cnt += 1
    i = 0
    # Lay ten cua file bat dau tu ki tu "/" cuoi hoac lay nguyen ten file
    for charac in file_name:
        if charac == "/" and i < cnt:
            i += 1
        if i == cnt:
            res += charac
    return res

# Kiem tra xem co ki tu "/" trong ham o tren chua
def checkSlashInFileName(s):
    if s[0] == "/":
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

# Ham xoa man hinh
def cleanScreen():
    os.system("cls")

# Kiem tra xem file co ton tai khong
def checkExist(path):
    if os.path.isfile(path):
        return True
    return False

# Kiem tra xem folder co ton tai khong
def checkFolderExist(path):
    if os.path.isdir(path):
        return True
    return False

#!Các hàm về UPLOAD

def getErrorUpload(before_error_upload):
    start_of_path_idx = before_error_upload.find(" ") + 1
    path = before_error_upload[start_of_path_idx:len(before_error_upload)]
    # start_of_filename_idx = path.find("/") + 1
    # error_file= path[start_of_filename_idx:]
    return path

# Ham upload file
def uploadFile(client, msg):
    # Lay kich thuoc cua file roi gui toi cho sever va nhan thong bao cua sever neu gui thanh cong
    size_send = os.path.getsize(msg)
    client.sendall(str(size_send).encode(FORMAT))
    size_resp = client.recv(1024).decode(FORMAT)
    # Mo va lam viec voi file
    with open(msg, "rb") as ifs:
        while 1:
            # Doc du lieu tu file va thoat ra khoi vong lap neu khong doc duoc du lieu nua
            data = ifs.read(1024)
            if not data:
                break
            # Co gang du lieu va nhan thong bao tu sever  
            try:
                client.sendall(data)
            except Exception as e:
                print(f"There was an error when uploading file {msg} / Connect Error with sever.")
                return False
            try:
                resp = client.recv(1024).decode(FORMAT)
            except Exception as e:
                print(f"There was an error when uploading file {msg} / Connect Error with sever.")
                return False
    # Gui thong bao "xong" toi cho sever de sever gui lai trang thai 
    client.sendall("xong".encode(FORMAT))
    resp_sta = client.recv(1024).decode(FORMAT)
    # Gui thong bao da nhan trang thai va nhan thong bao "success" hay "failed" tu sever gui toi
    client.sendall("da nhan".encode(FORMAT))
    resp = client.recv(1024).decode(FORMAT)
    if resp == "Success":
        print(f"Sever: The file {msg} has been successfully uploaded to the server. {resp_sta}") 
        return True
    else:
        print(f"Sever: The file {msg} has been unsuccessfully uploaded to the server. {resp_sta}")
        return False

#!Các hàm DOWNLOAD

#*Nhận vào dòng báo lỗi của Server và trả về tên File bị lỗi 
def getErrorDownload(before_error_download):
    start_of_path_idx = before_error_download.find(" ") + 1
    path = before_error_download[start_of_path_idx:]
    start_of_filename_idx = path.find("/") + 1
    error_file= path[start_of_filename_idx:]
    return error_file


# Ham download file
def downloadFile(client, msg):

    #tao duong dan den noi luu tru file
    tmp = name(msg)
    if not checkSlashInFileName(tmp):
        tmp = "/" + tmp
    name_with_not_exten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    file_write = PATH_CLIENT + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(PATH_CLIENT + tmp):
            tmp = name_with_not_exten + "(" + str(i) + ")" + exten
            file_write = PATH_CLIENT + tmp
            i += 1

    # Nhan kich thuoc file va gui lai thong bao toi sever
    size_recv = client.recv(1024).decode(FORMAT)
    size = int(size_recv)
    # Gui ten file
    client.sendall(file_write.encode(FORMAT))

    
    
    # Tuong tu nhu upload file o sever
    ofs = open(file_write, "wb")
    sw = 0
    while size > sw:
        data = client.recv(1024)
        ofs.write(data)
        sw += len(data)
        client.sendall(str(sw).encode(FORMAT))
    ofs.close()

    # Nhan thong bao tu sever
    resp = client.recv(1024).decode(FORMAT)
    if resp == "Success":
        print(f"Sever: The file has been successfully downloaded and is currently stored at {file_write}. ")
    else:
        print(f"Sever: There was an error when download file {msg}/ Connect Error with sever!")

#!Các hàm UPLOAD_FOLDER
def uploadFilesInFolderSequentially(client, msg):
    # Lay danh sach cac ten file trong folder
    fileName = os.listdir(msg)
    # Gui so luong file cho sever
    client.sendall(str(len(fileName)).encode(FORMAT))
    size_resp = client.recv(1024).decode(FORMAT)
    # Nhan trang thai khong thanh cong neu so luong file la 0
    if size_resp != "Received":
        print(f"Sever: {size_resp}")
        return
    # Gui ten file va upload file
    for file in fileName:
        client.sendall(file.encode(FORMAT))
        fileRep = client.recv(1024).decode(FORMAT)
        uploadFile(client, msg + "/" + file)
    # Gui thong bao da gui xong
    client.sendall("Success".encode(FORMAT))
    # Nhan trang thai tu sever gui ve
    res = client.recv(1024).decode(FORMAT)
    print(res)


#!Hàm đăng nhập 
def login(client):

    status = client.recv(1024).decode(FORMAT)
    os.system("cls")
    # In ra man hinh da ket noi thanh cong voi sever
    print(status)
    res = "success"
    client.sendall(res.encode(FORMAT))
    reply = client.recv(1024).decode(FORMAT)
    print(reply)
    username = input("\nUsername: ")
    password = input("Password: ")

    # Gui thong tin ten dang nhap va mat khau toi sever
    login_information = f"{username},{password}"
    client.sendall(login_information.encode(FORMAT))
    # Nhận phản hồi từ server
    resp = client.recv(1024).decode(FORMAT)
    if resp == "Successful":
        print("Login Successful")
        return True
    else:
        print("Login unsuccessfully")
        return False

#!Menu
def menu():
    print("0. Exit")
    print("1. Upload File")
    print("2. Download File")
    print("3. Upload Files In Folder Sequentially")

# --------------------------- main ----------------
#!Hàm main
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #*Kết nối đến Server
        client.connect((HOST, PORT))
        print(f"Connecting to the server, please wait.")
        while not login(client): 
            continue
        connect = True
        while connect:
            menu()
            choice = input("Sever: Enter your choice: ")
            # Kiem tra xem client nhap co hop le khong
            if choice > '9' or choice < '0' or len(choice) > 1:
                print("Sever: Your input is invalid. Please try again!!!")
                continue
            else:
                choice = int(choice)
            match choice:
                #*Nếu Client chọn thoát khỏi chương trình
                case 0:
                    msg = "exit"
                     #*Hỏi Client có chắc chắn muốn ngắt kết nối không
                    again_check = input("Sever: Are you sure you want to disconnect?(Y/N): ")
                    if again_check == "Y":
                        client.sendall(msg.encode(FORMAT))
                        print("Sever: You have disconnected from the server!")
                        connect = False
                    else:
                        continue
                case 1:
                    msg = "uploadFile"
                    # Gui thong bao se upload file den sever
                    client.sendall(msg.encode(FORMAT))
                    before_error_upload = client.recv(1024).decode(FORMAT)
                    if before_error_upload != "NoError":
                        # Lay ten file tai loi
                        error_file = getErrorUpload(before_error_upload)
                        print(f"You previously attempted to upload the file {error_file}, but it was interrupted during your last session. Would you like to resume the download? (Y/N)")
                        continue_upload  = input()
                        # Gui yeu cau tiep tuc va tiep tuc tai
                        if continue_upload == "Y":
                            client.sendall(continue_upload.encode(FORMAT))
                            time.sleep(0.1)
                            client.sendall(error_file.encode(FORMAT))
                            # Bien nhan file ton tai
                            is_exist = client.recv(1024).decode(FORMAT)
                            uploadFile(client, error_file)
                        # Gui yeu cau khong tiep tuc va tiep tuc tai file khac
                        else:
                            client.sendall(continue_upload.encode(FORMAT))
                            time.sleep(0.1)
                            # Dat co de neu client nhap CANCEL thi se khong thuc hien upload
                            flag = True
                            # Nhan yeu cau nhap duong dan tu sever
                            resp = client.recv(1024).decode(FORMAT)
                            # Nhap yeu cau gui toi sever
                            while 1:
                                print("Type 'CANCEL' to return to the menu!!!")
                                msg = input(f"(Sever request) - {resp}")
                                if msg == "CANCEL":
                                    client.sendall(msg.encode(FORMAT))
                                    rec = client.recv(1024).decode(FORMAT)
                                    flag = False
                                    break
                                if not checkExist(msg):
                                    print("The file does not exist. Please enter again!!!")
                                    continue
                                client.sendall(msg.encode(FORMAT))
                                rec = client.recv(1024).decode(FORMAT)
                                break

                            if flag == True:
                                uploadFile(client, msg)
                    else:
                            # Dat co de neu client nhap CANCEL thi se khong thuc hien upload
                            flag = True
                            # Nhan yeu cau nhap duong dan tu sever
                            resp = client.recv(1024).decode(FORMAT)
                            # Nhap yeu cau gui toi sever
                            while 1:
                                print("Type 'CANCEL' to return to the menu!!!")
                                msg = input(f"(Sever request) - {resp}")
                                if msg == "CANCEL":
                                    client.sendall(msg.encode(FORMAT))
                                    rec = client.recv(1024).decode(FORMAT)
                                    flag = False
                                    break
                                if not checkExist(msg):
                                    print("The file does not exist. Please enter again!!!")
                                    continue
                                client.sendall(msg.encode(FORMAT))
                                rec = client.recv(1024).decode(FORMAT)
                                break

                            # Neu nhap duong dan dung thi thuc hien upload
                            if flag == True:
                                uploadFile(client, msg)

                case 2:
                    # Gui yeu cau download toi cho sever
                    msg = "downloadFile"
                    client.sendall(msg.encode(FORMAT))
                    # Kiem tra xem client truoc day co tung co file tai loi khong
                    before_error_download = client.recv(1024).decode(FORMAT)
                    #*Kiểm tra có lỗi hay không
                    #*Nếu có File tải lỗi trước đó
                    if before_error_download != "NoError":
                        #*Lấy tên của File bị lỗi và hiển thị ra màn hình để hỏi Client có muốn tải lại File khoong
                        error_file = getErrorDownload(before_error_download)
                        print(f"You previously attempted to download the file {error_file}, but it was interrupted during your last session. Would you like to resume the download? (Y/N)")
                        continue_download  = input()
                        #*Nếu Client muốn tải lại File
                        if continue_download == "Y":
                            #*Gửi hồi đáp rằng muốn tải File lỗi trước đó đến Server
                            client.sendall(continue_download.encode(FORMAT))
                            time.sleep(0.1)
                            #*Gửi tên File lỗi đến Server, để thực hiện tải file
                            client.sendall(error_file.encode(FORMAT))
                            # Bien nhan file ton tai
                            is_exist = client.recv(1024).decode(FORMAT)
                            client.sendall("Receive".encode(FORMAT))
                            downloadFile(client, error_file)
                        #*Nếu Client không muốn tải lại File
                        else:
                            #*Gửi hồi đáp rằng không muốn tải File lỗi trước đó đến Server
                            client.sendall(continue_download.encode(FORMAT))
                            time.sleep(0.1)
                            #*Thực hiện tải File
                            flag = True
                            while 1:
                                #*Nhập tên File cần tải, hoặc thoát công việc tải File
                                print("Type 'CANCEL' to return to the menu!!!")
                                msg = input(f"Sever: Enter the name of the file you want to download: ")
                                if msg == "CANCEL":
                                    client.sendall(msg.encode(FORMAT))
                                    flag = False
                                    break
                                client.sendall(msg.encode(FORMAT))
                                # Nhan trang thai xem file co ton tai tren sever hay co bi cam tai khong
                                check_status = client.recv(1024).decode(FORMAT)
                                if check_status == "forbidden file":
                                    print("Sever: File is in list forbidden file. Can't download this file")
                                    continue
                                if check_status == "Not exist":
                                    print("Sever: File is not exist!!!")
                                    continue
                                else:
                                    resp = "Received"
                                    client.sendall(resp.encode(FORMAT))
                                
                                break
                            if flag == True:
                                #*Tiến hành tải File
                                downloadFile(client, msg)
                    # Neu khong co file tai loi truoc do thi tai file
                    else:
                        #*Thực hiện tải File
                        flag = True
                        while 1:
                            #*Nhập tên File cần tải, hoặc thoát công việc tải File
                            print("Type 'CANCEL' to return to the menu!!!")
                            msg = input(f"(Sever request): Enter the name of the file you want to download: ")
                            if msg == "CANCEL":
                                client.sendall(msg.encode(FORMAT))
                                flag = False
                                break
                            client.sendall(msg.encode(FORMAT))
                            # Nhan trang thai xem file co ton tai tren sever hay co bi cam tai khong
                            check_status = client.recv(1024).decode(FORMAT)
                            if check_status == "forbidden file":
                                print("Sever: File is in list forbidden file. Can't download this file")
                                continue
                            if check_status == "Not exist":
                                print("Sever: File is not exist!!!")
                                continue
                            else:
                                resp = "Received"
                                client.sendall(resp.encode(FORMAT))
                            break
                        if flag == True:
                            #*Tiến hành tải File
                            downloadFile(client, msg)

                case 3:
                    # Gui thong bao den cho sever
                    msg = "uploadFilesInFolderSequentially"
                    client.sendall(msg.encode(FORMAT))
                    flag = True
                    #Nhan yeu cau nhap duong dan folder tu sever
                    resp = client.recv(1024).decode(FORMAT)
                    while 1:
                        print("Type 'CANCEL' to return to the menu!!!")
                        msg = input(f"(Sever request) - {resp}")
                        if msg == "CANCEL":
                            client.sendall(msg.encode(FORMAT))
                            rec = client.recv(1024).decode(FORMAT)
                            flag = False
                            break
                        if not checkFolderExist(msg):
                            print("The folder does not exist. Please enter again!")
                            continue
                        client.sendall(msg.encode(FORMAT))
                        rec = client.recv(1024).decode(FORMAT)
                        break
                    if flag == True:
                        uploadFilesInFolderSequentially(client, msg)
                case default:
                    print("The input request is invalid. Please try again.")
    #!Bắt lỗi, chương trình bên SERVER bị đóng
    except ConnectionResetError:
        print("The server was abruptly shut down.")
    #!Bắt lỗi, kết nối wifi của bản thân bị gián đoạn
    except socket.error:
        print(f"The connection to the server was interrupted, causing the send/receive timeout to be too long. Please log in again.")
    #!Bắt các lỗi khác...
    except Exception as e:
        print(F"Cannot connect to the server, Error: {e}")
    #!Dừng chương trình để Client đọc thông báo
    input()
    #!Đóng kết nối với Server
    client.close()
if __name__ == "__main__":
    main()
#C:/Users/Admin/Documents/vs code/vs code python/anh.bin
