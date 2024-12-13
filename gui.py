from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import threading
import socket
import os
import time

FONT = "Inter"
BTN_COLOR = "#A1EEBD"
MAIN_COLOR = "#6c63ff"
WIDTH_BTN = 18 # width of featured buttons
PATH_CLIENT = "DataClient"
HOST = socket.gethostname()
PORT = 12000
PathClient = "DataClient"
PathSever = "DataServer"  
PathUsers = "users.csv"

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

#*Nhận vào dòng báo lỗi của Server và trả về tên File bị lỗi 
def getErrorDownload(before_error_download):
    start_of_path_idx = before_error_download.find(" ") + 1
    path = before_error_download[start_of_path_idx:]
    start_of_filename_idx = path.find("/") + 1
    error_file= path[start_of_filename_idx:]
    return error_file

def getErrorUpload(before_error_upload):
    start_of_path_idx = before_error_upload.find(" ") + 1
    path = before_error_upload[start_of_path_idx:]
    start_of_filename_idx = path.find("/") + 1
    error_file= path[start_of_filename_idx:]
    return error_file


class DownloadFilePage(Frame):
    
    def browseFiles(self, entry_var: StringVar):
        # Lấy đường dẫn tuyệt đối tương đối với thư mục hiện tại
        current_dir = os.path.dirname(__file__) # Path to current file
        folder_path = os.path.join(current_dir, PathSever)
        # Đường dẫn tuyệt đối -> thích ứng trên mọi hệ điều hành
        absolute_path = os.path.abspath(folder_path)
        filename = filedialog.askopenfilename(initialdir = absolute_path,
                                            title = "Select a File",
                                            filetypes = (("Text files",
                                                            "*.txt*"),
                                                        ("all files",
                                                            "*.*")))
        if filename:
            filename_only = os.path.basename(filename)
            path_for_download = PathSever + "/" + filename_only
            entry_var.set(path_for_download)
    
    def clickButton(self, filename:str, app_pointer):
        if filename != "":
            app_pointer.downloadFileThread(self, client)
    
    def clickBack(self, app_pointer, name_page: Frame):
        app_pointer.geometry("860x600")
        app_pointer.showPage(name_page)
            
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)
        
        self["bg"] = "white"
        # Main label
        mainLabel = Label(self, text="Download Page", font=(FONT, 22, "bold"), bg = "white", fg = MAIN_COLOR)
        mainLabel.place(x = 100, y = 70) # 50
        # Note label
        lb_note = Label(self, text = "Path", font = (FONT, 12, "bold"), bg = "white")
        lb_note.place(x = 20, y = 150)

        # Notice label
        self.lb_notice = Label(self, text = "", font = (FONT, 10), fg = "red", bg = "white")
        self.lb_notice.place(x = 10, y = 185)

        # Entry path file
        self.text_entry = StringVar()

        self.entry_path = Entry(self, width = 45, font = (FONT, 10), fg = "blue", textvariable = self.text_entry, bg = "#f5f5f5")
        self.entry_path.focus()
        self.entry_path.place(x = 75, y = 150, height = 24)

        # Button 
        btn_select_file = Button(self, text = "Select file", width = WIDTH_BTN, font = (FONT, 13, "bold"), bg = MAIN_COLOR, fg = "white",
                                 bd = 0.01, command = lambda: self.clickButton(self.entry_path.get(), app_pointer))
        btn_select_file.place(x = 125, y = 290)

        btn_back = Button(self, text = "Back", font = (FONT, 13, "bold"), bg = MAIN_COLOR, fg = "white", width = WIDTH_BTN,
                          bd = 0.01, command = lambda: self.clickBack(app_pointer, MainMenu))
        btn_back.place(x = 125, y = 330) #40

        # File Explorer StringVar() -> to get filename
        btn_explore = Button(self, text = "...", font = (FONT, 6, "bold"), fg = "blue",
                             command = lambda: self.browseFiles(self.text_entry))
        btn_explore.place(x = 400, y = 155)

        # Image
        self.img = PhotoImage(file = "./img/undraw_Filing_system_re_56h6.png")
        lb_img = Label(self, image = self.img, width = 163, height = 102, bg = "white")
        lb_img.place(x = 287, y = 448) # -30
        
class UploadFilePage(Frame):

    def browseFolder(self, entry_var: StringVar):
        foldername = filedialog.askdirectory(initialdir="/", title="Select a Directory")
        if foldername:
            entry_var.set(foldername) 

    def browseFiles(self, entry_var: StringVar):
        filename = filedialog.askopenfilename(initialdir = "/",
                                            title = "Select a File",
                                            filetypes = (("Text files",
                                                            "*.txt*"),
                                                        ("all files",
                                                            "*.*")))
        if filename:
            entry_var.set(filename)  

    def browse(self, current_choice_in_combobox: str, entry_var:StringVar):
        if(current_choice_in_combobox == "Upload File"):
            self.browseFiles(entry_var)
        else:
            self.browseFolder(entry_var)

    def clickButton(self, current_choice_in_combobox: str, filename: str, app_pointer):
        if(current_choice_in_combobox == "Upload File"):
            if filename != "":
                app_pointer.uploadFileSupportGUI(self, client)
        elif current_choice_in_combobox == "Upload Folder":
            if(filename != ""):
                app_pointer.uploadFolderSupportGUI(self, client)

    def clickBack(self, app_pointer, name_page: Frame):
        app_pointer.geometry("860x600")
        app_pointer.showPage(name_page)

    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)
        
        self["bg"] = "white"
        # Main label
        mainLabel = Label(self, text="Upload Page", font=(FONT, 22, "bold"), bg = "white", fg = MAIN_COLOR)
        mainLabel.place(x = 110, y = 70) # 50
        # Note label
        lb_note = Label(self, text = "Path", font = (FONT, 12, "bold"), bg = "white")
        lb_note.place(x = 20, y = 150)

        # Notice label
        self.lb_notice = Label(self, text = "", font = (FONT, 10), fg = "red")
        self.lb_notice.place(x = 10, y = 185)

        # Entry path file
        self.text_entry = StringVar()

        self.entry_path = Entry(self, width = 45, font = (FONT, 10), fg = "blue", textvariable = self.text_entry, bg = "#f5f5f5")
        self.entry_path.focus()
        self.entry_path.place(x = 75, y = 150, height = 24)

        # combo box
        self.combo_box = ttk.Combobox(self, values = ["Upload File", "Upload Folder"])
        self.combo_box.set("Upload File")
        self.combo_box.place(x = 290, y = 220)


        # Button 
        btn_select_file = Button(self, text = "Select file", width = WIDTH_BTN, font = (FONT, 13, "bold"), bg = MAIN_COLOR, fg = "white",
                                 bd = 0.01, command = lambda: self.clickButton(self.combo_box.get(), self.entry_path.get(), app_pointer))
        btn_select_file.place(x = 125, y = 290)

        btn_back = Button(self, text = "Back", font = (FONT, 13, "bold"), bg = MAIN_COLOR, fg = "white", width = WIDTH_BTN,
                          bd = 0.01, command = lambda: self.clickBack(app_pointer, MainMenu))
        btn_back.place(x = 125, y = 330) #40

        # File Explorer StringVar() -> to get filename
        btn_explore = Button(self, text = "...", font = (FONT, 6, "bold"), fg = "blue",
                             command = lambda: self.browse(self.combo_box.get(), self.text_entry))
        btn_explore.place(x = 400, y = 155)

        # Image
        self.img = PhotoImage(file = "./img/undraw_Filing_system_re_56h6.png")
        lb_img = Label(self, image = self.img, width = 163, height = 102, bg = "white")
        lb_img.place(x = 287, y = 448) # -30


class MainMenu(Frame): # 860x600
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)

        self["bg"] = "white"
        # ----------------- Widget --------------------------
        lb_main = Label(self, text = "Main Menu", font = (FONT, 22, "bold"), bg = "white", fg = MAIN_COLOR)
        lb_main.place(x = 340, y = 30)

        # Img 1
        self.img_download = PhotoImage(file = "./img/undraw_Download_re_li50.png")
        lb_img_download = Label(self, image = self.img_download, width = 339, height = 300, bg = "white")
        lb_img_download.place(x = 40, y = 90) # -30

        # Img 2
        self.img_upload = PhotoImage(file = "./img/upload.png")
        lb_img_upload = Label(self, image = self.img_upload, width = 409, height = 300, bg = "white")
        lb_img_upload.place(x = 490 - 30, y = 80) # -80

        # Button download
        btn_download = Button(self, text = "Download", font = (FONT, 14, "bold"), bg = MAIN_COLOR, width = 10, fg = "white", bd = 0.01,
                            command = lambda: self.resizeGeometry(app_pointer, DownloadFilePage))
        btn_download.place(x = 170 - 30, y = 450)

        # Button upload
        btn_upload = Button(self, text = "Upload", font = (FONT, 14, "bold"), bg = MAIN_COLOR, width = 10, fg = "white", bd = 0.01,
                            command = lambda: self.resizeGeometry(app_pointer, UploadFilePage))
        btn_upload.place(x = 610 - 30, y = 450)
    
    def resizeGeometry(self, app_pointer, name_page):
        app_pointer.geometry("450x550")
        app_pointer.showPage(name_page)
    
    

 
class LoginPage(Frame): # 1000x600
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)

        self["bg"] = "white"
        
        # Main picture
        self.img = PhotoImage(file = "./img/undraw_Internet_on_the_go_re_vben.png")
        lb_img = Label(self, image = self.img, width = 496, height = 600, bg = MAIN_COLOR)
        lb_img.place(x = 498, y = 0)

        # Sub picture
        self.sub_img = PhotoImage(file = "./img/undraw_Fingerprint_re_uf3f.png")
        lb_sub_img = Label(self, image = self.sub_img, width = 171, height = 120, bg = "white")
        lb_sub_img.place(x = 0, y = 480)

        # Extra label
        lb_title = Label(self, text = "Computer Networking", font = (FONT, 25, "bold"), fg = "white", bg = MAIN_COLOR)
        lb_title.place(x = 585, y = 30)

        # Label - header
        lb_head = Label(self, text = "LOGIN", font = (FONT, 25, "bold"), bg = "white", fg = MAIN_COLOR,
                        width = 10, height = 5)
        lb_head.place(x = 130, y = 20) # 10
        # Label username
        lb_username = Label(self, text = "Username", font = (FONT, 12), bg = "white", fg = MAIN_COLOR,
                            width = 10, height = 3)
        lb_username.place(x = 83, y = 167)

        # Label password
        lb_password = Label(self, text = "Password", font = (FONT, 12), bg = "white", fg = MAIN_COLOR,
                            width = 10, height = 3)
        lb_password.place(x = 83, y = 268)

        # Label notice
        self.lb_notice = Label(self, text = "", font = (FONT, 12), fg = "red", bg = "white")
        self.lb_notice.place(x = 90, y = 350)
        # Entry username

        self.entry_username = Entry(self, width = 28, font = (FONT, 14), bd = 0.25, bg = "#e1e1e1")
        self.entry_username.place(x = 98, y = 220)
        self.entry_username.focus()
        
        # Entry password
        self.entry_password = Entry(self, width = 28, font = (FONT, 14), bd = 0.25, bg = "#e1e1e1")
        self.entry_password.place(x = 98, y = 321)

        # Button

        btn_login = Button(self, text = "Sign in", font = (FONT, 14, "bold"), bg = MAIN_COLOR, width = 10, fg = "white",
                           command = lambda: app_pointer.login(self, client), bd = 0.01)
        btn_login.place(x = 177, y = 406)



class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.closing = False # Flag to check when program was closed

        self.title("Application")
        self.geometry("1000x600")
        self.resizable(width = False, height = False)
        self.attributes("-topmost", False)
        
        # Favicon
        icon = PhotoImage(file = "./img/icons8-internet-96.png")
        self.iconphoto(False, icon)

        # Đoạn code dùng nếu muốn thay đổi các frame
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Tạo một dictionary để lưu các class page
        # Dùng vòng for để grid các frame này, thay vì làm tuần tự
        self.frames = {}
        for F in (LoginPage, MainMenu, DownloadFilePage, UploadFilePage):
            frame = F(container, self)
            frame.grid(row = 0, column = 0, sticky = "nsew")
            self.frames[F] = frame
        
        self.frames[LoginPage].tkraise()
    
    def onCloseGlobal(self):
        self.closing = True
        if hasattr(self, "socket"):
            try:
                self.client.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error closing socket: {e}")
        self.destroy()

    def showPage(self, class_name):
        self.frames[class_name].tkraise()


    def login(self, curFrame: Frame, sck: socket):
        status = sck.recv(1024).decode("utf-8")
        os.system("cls")
        # In ra man hinh da ket noi thanh cong voi sever
        print(status)
        res = "success"
        sck.sendall(res.encode("utf-8"))
        reply = sck.recv(1024).decode("utf-8")
        print(reply)
        try:
            username = curFrame.entry_username.get()
            password = curFrame.entry_password.get()

            if username == "" or password == "":
                curFrame.lb_notice["text"] = "Fields cannot be empty"
                return

            login_information = f"{username},{password}"
            sck.sendall(login_information.encode("utf-8"))

            # Nhận phản hồi từ server
            resp = sck.recv(1024).decode("utf-8")
            if resp == "Successful":
                self.geometry("860x600")
                self.showPage(MainMenu)
            else:
                # operationHistory("\n" + str(getTime()) + ": " + f"Client {username} {addr}: Has unsuccessfully uploaded the file with the path {msg}.")
                curFrame.lb_notice["text"] = "Invalid username/password"
        except:
            print("Server is not responding")
    # ------------------------------------------------
    def downloadFileThread(self, curFrame: Frame, sck: socket):
        # Tạo một luồng mới để chạy hàm download mà không làm đơ UI
        download_thread = threading.Thread(target=self.downloadSupportGUI, args=(curFrame, sck))
        download_thread.start()

    def downloadFile(self, sck: socket, msg):
        try:
            if self.closing:
                return

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
            size_recv = sck.recv(1024).decode("utf-8")
            size = int(size_recv)
            # Gui ten file
            sck.sendall(file_write.encode("utf-8"))

            # Progess bar GUI
            progress = Toplevel(self)
            progress.title(f"Download '{tmp}' file")

            progress_bar = ttk.Progressbar(progress, orient="horizontal", length=300, mode="determinate", maximum=size)
            progress_bar.pack(pady = 20)

            progress_label = Label(progress, text="0%")
            progress_label.pack(pady = 10)

            progress_closed = False # Cờ để kiểm tra trạng thái thanh progress

            def onClose():
                nonlocal progress_closed
                progress_closed = True
                progress.destroy()

            progress.protocol("WM_DELETE_WINDOW", onClose)
            
            # Tuong tu nhu upload file o sever
            ofs = open(file_write, "wb")
            sw = 0
            while size > sw:
                data = sck.recv(1024)
                ofs.write(data)
                sw += len(data)

                if progress_closed:
                    break
                
                if progress.winfo_exists():
                    try:
                        progress_bar["value"] = sw
                        progress_label.config(text=f"{(sw/size) * 100:.2f}%")
                        progress.update_idletasks()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error updating progress bar: {e}")
                        return
                else:
                    break
                # ---------------------

                sck.sendall(str(sw).encode("utf-8"))
            ofs.close()

            # ------ GUI ---------
            if not progress_closed:
                time.sleep(1)
                progress.destroy()
            # --------------------
                

            # Nhan thong bao tu sever
            resp = sck.recv(1024).decode("utf-8")
            if resp == "Success":
                messagebox.showinfo("Success", "Download successfully")
            else:
                messagebox.showinfo("Unsuccess", "Download unsuccessfully")
        except Exception as e:
            if not self.closing:
                messagebox.showerror("Error", f"An error occured: {e}")
            return

    def downloadSupportGUI(self, curFrame: Frame, sck: socket):
        
        try:
            msg = "downloadFile"
            sck.sendall(msg.encode("utf-8"))
            if self.closing:
                return
            # Kiem tra xem client truoc day co tung co file tai loi khong
            before_error_download = sck.recv(1024).decode("utf-8")
            #*Kiểm tra có lỗi hay không
            #*Nếu có File tải lỗi trước đó
            if before_error_download != "NoError":
                #*Lấy tên của File bị lỗi và hiển thị ra màn hình để hỏi Client có muốn tải lại File khoong
                error_file = getErrorDownload(before_error_download)
                message = f"Last time when you were downloading file '{error_file}', it was interrupted. Would you like to download it again before downloading file '{curFrame.entry_path.get()}'?"
                result  = messagebox.askyesno("Confirmation", message)
                #*Nếu Client muốn tải lại File
                if result:
                    #*Gửi hồi đáp rằng muốn tải File lỗi trước đó đến Server
                    sck.sendall("Y".encode("utf-8"))
                    time.sleep(0.1)
                    #*Gửi tên File lỗi đến Server, để thực hiện tải file
                    sck.sendall(error_file.encode("utf-8"))
                    # Bien nhan file ton tai
                    is_exist = sck.recv(1024).decode("utf-8")
                    sck.sendall("Receive".encode("utf-8"))
                    self.downloadFile(sck, error_file)
                #*Nếu Client không muốn tải lại File
                else:
                    #*Gửi hồi đáp rằng không muốn tải File lỗi trước đó đến Server
                    sck.sendall("N".encode("utf-8"))
                    time.sleep(0.1)
                    #*Thực hiện tải File
                    flag = True
                    while 1:
                        #*Nhập tên File cần tải, hoặc thoát công việc tải File
                        print("Type 'CANCEL' to return to the menu!!!")
                        msg = curFrame.entry_path.get()
                        if msg == "CANCEL":
                            sck.sendall(msg.encode("utf-8"))
                            flag = False
                            break
                        sck.sendall(msg.encode("utf-8"))
                        # Nhan trang thai xem file co ton tai tren sever hay co bi cam tai khong
                        check_status = sck.recv(1024).decode("utf-8")
                        if check_status == "forbidden file":
                            print("Sever: File is in list forbidden file. Can't download this file")
                            messagebox.showwarning("Warning", "Forbidden file")
                            continue
                        if check_status == "Not exist":
                            messagebox.showinfo("Infor", "File not exist")
                            continue
                        else:
                            resp = "Received"
                            sck.sendall(resp.encode("utf-8"))
                        break
                    if flag == True:
                        #*Tiến hành tải File
                        self.downloadFile(sck, msg)
            # Neu khong co file tai loi truoc do thi tai file
            else:
                #*Thực hiện tải File
                flag = True
                while 1:
                    #*Nhập tên File cần tải, hoặc thoát công việc tải File
                    print("Type 'CANCEL' to return to the menu!!!")
                    msg = curFrame.entry_path.get()
                    if msg == "CANCEL":
                        sck.sendall(msg.encode("utf-8"))
                        flag = False
                        break
                    sck.sendall(msg.encode("utf-8"))
                    # Nhan trang thai xem file co ton tai tren sever hay co bi cam tai khong
                    check_status = sck.recv(1024).decode("utf-8")
                    if check_status == "forbidden file":
                        messagebox.showwarning("Warning", "Forbidden file")
                        continue
                    if check_status == "Not exist":
                        messagebox.showinfo("Information", "File not exist!!")
                        continue
                    else:
                        resp = "Received"
                        sck.sendall(resp.encode("utf-8"))
                    break
                if flag == True:
                    #*Tiến hành tải File
                    self.downloadFile(sck, msg)
        except Exception as e:
            if not self.closing:
                messagebox.showerror("Error", f"An error occured: {e}")
    
    def uploadFile(self, sck: socket, msg: str):
        size = os.path.getsize(msg)
        sck.sendall(str(size).encode("utf-8"))
        sizeResp = sck.recv(1024).decode("utf-8")
        
        # Gui - Progress bar
        progress = Toplevel(self)
        progress.title("Upload")

        progress_bar = ttk.Progressbar(progress, orient="horizontal", length=300, mode="determinate", maximum=size)
        progress_bar.pack(pady = 20)
        
        progress_label = Label(progress, text="0%")
        progress_label.pack(pady = 10)
        # -------------------------------

        uploaded_size = 0
        #ifs = open(msg, "rb")
        with open(msg, "rb") as ifs:
            while 1:
                data = ifs.read(1024)
                if not data:
                    break

                uploaded_size += len(data)

                if progress.winfo_exists():
                    progress_bar["value"] = uploaded_size
                    progress_label.config(text=f"{(uploaded_size/size) * 100:.2f}%")
                    progress.update_idletasks()
                
                try:
                    sck.sendall(data)
                except Exception as e:
                    messagebox.showerror("Error", f"There was an error when uploading file {msg} / Connect Error with sever.")
                    return False
                try:
                    resp = sck.recv(1024).decode("utf-8")
                except Exception as e:
                    messagebox.showerror("Error", f"There was an error when uploading file {msg} / Connect Error with sever.")
                    return False
        #ifs.close()
        sck.sendall("xong".encode("utf-8"))

        time.sleep(1)

        if progress.winfo_exists:
            progress.destroy() # GUI : progress bar
        
        resp_sta = sck.recv(1024).decode("utf-8")
        sck.sendall("da nhan".encode("utf-8"))
        resp = sck.recv(1024).decode("utf-8")
        if resp == "Success":
            messagebox.showinfo("Inform", f"Sever: The file {msg} has been successfully uploaded to the server. {resp_sta}")
        else:
            messagebox.showinfo("Inform", f"Sever: The file {msg} has been unsuccessfully uploaded to the server. {resp_sta}")
    
    def uploadFileThread(self, curFrame: Frame, sck: socket):
        # Tạo một luồng mới để chạy hàm download mà không làm đơ UI
        upload_file_thread = threading.Thread(target=self.uploadFileSupportGUI, args=(curFrame, sck))
        upload_file_thread.start()
    
    def uploadFileSupportGUI(self, curFrame: Frame, sck: socket):
        msg = "uploadFile"
        # Gui thong bao se upload file den sever
        sck.sendall(msg.encode("utf-8"))
        before_error_upload = sck.recv(1024).decode("utf-8")
        if before_error_upload != "NoError":
            # Lay ten file tai loi
            error_file = getErrorUpload(before_error_upload)
            message = f"Last time when you were uploading file '{error_file}', it was interrupted. Would you like to upload it again before uploading file '{curFrame.entry_path.get()}'?"
            result  = messagebox.askyesno("Confirmation", message)
            # Gui yeu cau tiep tuc va tiep tuc tai
            if result:
                sck.sendall("Y".encode("utf-8"))
                time.sleep(0.1)
                sck.sendall(error_file.encode("utf-8"))
                # Bien nhan file ton tai
                is_exist = sck.recv(1024).decode("utf-8")
                #sck.sendall("Receive".encode("utf-8"))
                self.uploadFile(sck, error_file)
            # Gui yeu cau khong tiep tuc va tiep tuc tai file khac
            else:
                sck.sendall("N".encode("utf-8"))
                time.sleep(0.1)
                # Dat co de neu sck nhap CANCEL thi se khong thuc hien upload
                flag = True
                # Nhan yeu cau nhap duong dan tu sever
                resp = sck.recv(1024).decode("utf-8")
                # Nhap yeu cau gui toi sever
                while 1:
                    print("Type 'CANCEL' to return to the menu!!!")
                    msg = curFrame.entry_path.get()
                    if msg == "CANCEL":
                        sck.sendall(msg.encode("utf-8"))
                        rec = sck.recv(1024).decode("utf-8")
                        flag = False
                        break
                    if not checkExist(msg):
                        messagebox.showwarning("ERROR", "File not exist")
                        continue
                    sck.sendall(msg.encode("utf-8"))
                    rec = sck.recv(1024).decode("utf-8")
                    break

                # Neu nhap duong dan dung thi thuc hien upload
                if flag == True:
                    self.uploadFile(sck, msg)
        else:
                # Dat co de neu sck nhap CANCEL thi se khong thuc hien upload
                flag = True
                # Nhan yeu cau nhap duong dan tu sever
                resp = sck.recv(1024).decode("utf-8")
                # Nhap yeu cau gui toi sever
                while 1:
                    print("Type 'CANCEL' to return to the menu!!!")
                    # msg = input(f"(Sever request) - {resp}")
                    msg = curFrame.entry_path.get()
                    if msg == "CANCEL":
                        sck.sendall(msg.encode("utf-8"))
                        rec = sck.recv(1024).decode("utf-8")
                        flag = False
                        break
                    if not checkExist(msg):
                        print("The file does not exist. Please enter again!!!")
                        messagebox.showinfo("Inform", "File not exist. Enter again!!")
                        continue
                    sck.sendall(msg.encode("utf-8"))
                    rec = sck.recv(1024).decode("utf-8")
                    break

                # Neu nhap duong dan dung thi thuc hien upload
                if flag == True:
                    self.uploadFile(sck, msg)

    def _handleFileSelection(self, curFrame: Frame, sck: socket):
        msg = curFrame.entry_path.get()  # Lấy đường dẫn từ Entry
        if msg == "CANCEL":
            sck.sendall(msg.encode("utf-8"))
            sck.recv(1024)  # Nhận phản hồi từ server
            return
        if not checkExist(msg):
            messagebox.showinfo("Inform", "File does not exist. Please correct the file path!")
            return  # Thoát để người dùng chỉnh sửa đường dẫn
        sck.sendall(msg.encode("utf-8"))
        rec = sck.recv(1024).decode("utf-8")
        self.uploadFile(sck, msg)

    def uploadFilesInFolderSequentially(self, sck: socket, msg: str):
        # Lay danh sach cac ten file trong folder
        fileName = os.listdir(msg)
        # Gui so luong file cho sever
        sck.sendall(str(len(fileName)).encode("utf-8"))
        size_resp = sck.recv(1024).decode("utf-8")
        # Nhan trang thai khong thanh cong neu so luong file la 0
        if size_resp != "Received":
            print(f"Sever: {size_resp}")
            return
        # Gui ten file va upload file
        for file in fileName:
            sck.sendall(file.encode("utf-8"))
            fileRep = sck.recv(1024).decode("utf-8")
            self.uploadFile(sck, msg + "/" + file)
        # Gui thong bao da gui xong
        sck.sendall("Success".encode("utf-8"))
        # Nhan trang thai tu sever gui ve
        res = sck.recv(1024).decode("utf-8")
        print(res)
    

    def uploadFolderSupportGUI(self, curFrame: Frame, sck: socket):
        msg = "uploadFilesInFolderSequentially"
        sck.sendall(msg.encode("utf-8"))
        flag = True
        #Nhan yeu cau nhap duong dan folder tu sever
        resp = sck.recv(1024).decode("utf-8")
        while 1:
            print("Type 'CANCEL' to return to the menu!!!")
            # msg = input(f"(Sever request) - {resp}")
            msg = curFrame.entry_path.get()
            if msg == "CANCEL":
                sck.sendall(msg.encode("utf-8"))
                rec = sck.recv(1024).decode("utf-8")
                flag = False
                break
            if not checkFolderExist(msg):
                print("The folder does not exist. Please enter again!")
                continue
            sck.sendall(msg.encode("utf-8"))
            rec = sck.recv(1024).decode("utf-8")
            break
        if flag == True:
            self.uploadFilesInFolderSequentially(sck, msg)

    def exit(self, curFrame: Frame, sck: socket):
        msg = "exit"
        sck.sendall(msg.encode("utf-8"))
        app.destroy()
        sck.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Ket noi thanh cong voi sever!!!")
app = App()
app.protocol("WM_DELETE_WINDOW", app.onCloseGlobal)
app.mainloop()
client.close()