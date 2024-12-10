from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import threading
# from tkinter import Label, Toplevel
import socket
import os
import time

FONT = "Inter"
BTN_COLOR = "#A1EEBD"
MAIN_COLOR = "#6c63ff"
WIDTH_BTN = 18 # width of featured buttons
HOST = socket.gethostname()
PORT = 12000
PathClient = "DataClient"
PathSever = "DataServer"  
PathUsers = "users.csv"

# Các hàm để xử lý đường dẫn
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

def cleanScreen():
    os.system("cls")

def checkExist(path):
    if os.path.isfile(path):
        return True
    return False

def checkFolderExist(path):
    if os.path.isdir(path):
        return True
    return False

def client_send(client, data):
    try:
        client.sendall(data.encode('utf-8'))
    except socket.error: #BẮT LỖI TIME-OUT, SERVER TỰ NGẮT KẾT NỐI BẰNG CLOSE()
        print(f"Server: Đã ngắt kết nối.")
        client.close()
    except ConnectionResetError:
        print(f"Server đột ngột ngắt kết nối.")
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi gửi dữ liệu đến Server.")
        client.close()

def client_receive(client):
    try:
        data = client.recv(1024).decode('utf-8')
        if not data:
            print("Server đã đóng kết nối.")
            client.close()
        else:
            #print(f"Server: {data}.")
            return data
    except socket.error: #BẮT LỖI TIME-OUT, SERVER TỰ NGẮT KẾT NỐI BẰNG CLOSE()
        print(f"Server: Đã ngắt kết nối.")
        client.close()
    except ConnectionResetError:
        print("Server đột ngột ngắt kết nối.")
        client.close()
    except Exception as e:
        print(f"Có lỗi {e} khi nhận dữ liệu từ Server.")
        client.close()
    return None


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
    
    def click_button(self, filename:str, app_pointer):
        if filename != "":
            app_pointer.downloadFile_thread(self, client)
    
    def clickBack(self, app_pointer, name_page: Frame):
        app_pointer.geometry("860x600")
        app_pointer.show_page(name_page)
            
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
                                 bd = 0.01, command = lambda: self.click_button(self.entry_path.get(), app_pointer))
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

    def browse_folder(self, entry_var: StringVar):
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
            self.browse_folder(entry_var)

    def click_button(self, current_choice_in_combobox: str, filename: str, app_pointer):
        if(current_choice_in_combobox == "Upload File"):
            if filename != "":
                app_pointer.uploadFile_support_gui(self, client)
        elif current_choice_in_combobox == "Upload Folder":
            if(filename != ""):
                app_pointer.uploadFolder_support_gui(self, client)

    def clickBack(self, app_pointer, name_page: Frame):
        app_pointer.geometry("860x600")
        app_pointer.show_page(name_page)

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
                                 bd = 0.01, command = lambda: self.click_button(self.combo_box.get(), self.entry_path.get(), app_pointer))
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

# # class UploadFolderPage(Frame):
#     def __init__(self, parent, app_pointer):
#         Frame.__init__(self, parent)
#         # Main label
#         mainLabel = Label(self, text="Upload Folder Page", font=(FONT, 22, "bold"))
#         mainLabel.place(x = 100, y = 70) # 50
#         # Note label
#         lb_note = Label(self, text = "Path", font = (FONT, 12, "bold"))
#         lb_note.place(x = 20, y = 150)

#         # Notice label
#         self.lb_notice = Label(self, text = "", font = (FONT, 10), fg = "red")
#         self.lb_notice.place(x = 10, y = 185)

#         # Entry path file
#         self.folder_path = StringVar()
#         self.entry_path_upFolder = Entry(self, width = 40, font = (FONT, 10), fg = "blue", textvariable = self.folder_path)
#         self.entry_path_upFolder.focus()
#         self.entry_path_upFolder.place(x = 75, y = 150, height = 24)

#         # Button 
#         btn_select_file = Button(self, text = "Select file", width = WIDTH_BTN, font = (FONT, 13, "bold"), bg = BTN_COLOR,
#                                  command = lambda: app_pointer.uploadFolder_support_gui(self, client))
#         btn_select_file.place(x = 125, y = 225)

#         btn_back = Button(self, text = "Back", font = (FONT, 13, "bold"), bg = BTN_COLOR, width = WIDTH_BTN,
#                           command = lambda: app_pointer.show_page(MainMenu))
#         btn_back.place(x = 125, y = 265)

#         # File Explorer StringVar -> to get filename
#         btn_explore = Button(self, text = "...", font = (FONT, 5, "bold"), fg = "blue",
#                              command = lambda: self.browse_folder())
#         btn_explore.place(x = 400, y = 158)

#     def browse_folder(self):
#         foldername = filedialog.askdirectory(initialdir="/", title="Select a Directory")
#         if foldername:
#             self.folder_path.set(foldername)  # Cập nhật StringVar với đường dẫn đã chọn

class MainMenu(Frame): # 860x600
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)

        self["bg"] = "white"
        # ----------------- Widget --------------------------
        lb_main = Label(self, text = "Main Menu", font = (FONT, 22, "bold"), bg = "white", fg = MAIN_COLOR)
        lb_main.place(x = 340, y = 30)

        # Button
        # btn_download_file = Button(self, text = "Download file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN,
        #                             command = lambda: app_pointer.show_page(DownloadFilePage))
        # btn_download_file.place(x = 130, y = 120)

        # btn_download_folder = Button(self, text = "Download folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        # btn_download_folder.place(x = 130, y = 160)

        # btn_upload_file = Button(self, text = "Upload file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN,
        #                             command = lambda: app_pointer.show_page(UploadFilePage))
        # btn_upload_file.place(x = 130, y = 200)

        # btn_upload_folder = Button(self, text = "Upload folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN,
        #                             command = lambda: app_pointer.show_page(UploadFolderPage))
        # btn_upload_folder.place(x = 130, y = 240)

        # btn_exit = Button(self, text = "Exit", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN,
        #                     command = lambda: app_pointer.exit(self, client))
        # btn_exit.place(x = 130, y = 280)

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
                            command = lambda: self.resize_geometry(app_pointer, DownloadFilePage))
        btn_download.place(x = 170 - 30, y = 450)

        # Button upload
        btn_upload = Button(self, text = "Upload", font = (FONT, 14, "bold"), bg = MAIN_COLOR, width = 10, fg = "white", bd = 0.01,
                            command = lambda: self.resize_geometry(app_pointer, UploadFilePage))
        btn_upload.place(x = 610 - 30, y = 450)
    
    def resize_geometry(self, app_pointer, name_page):
        app_pointer.geometry("450x550")
        app_pointer.show_page(name_page)

 
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

        # def click_operation(self, sck: socket):



        btn_login = Button(self, text = "Sign in", font = (FONT, 14, "bold"), bg = MAIN_COLOR, width = 10, fg = "white",
                           command = lambda: app_pointer.login(self, client), bd = 0.01)
        btn_login.place(x = 177, y = 406)

        # Image


class App(Tk):
    def __init__(self):
        Tk.__init__(self)

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

    def show_page(self, class_name):
        self.frames[class_name].tkraise()

    # def login(self, curFrame: Frame, sck: socket):
    #     # Nhận yêu cầu từ server để nhập thông tin
    #     request = sck.recv(1024).decode('utf-8')
    #     print(request)
    #     try:
    #         username = curFrame.entry_username.get()
    #         password = curFrame.entry_password.get()

    #         if username == "" or password == "":
    #             curFrame.lb_notice["text"] = "Fields cannot be empty"
    #             return

    #         print(username, password)
    #         login_information = f"{username},{password}"
    #         sck.sendall(login_information.encode('utf-8'))

    #         # # Nhận phản hồi từ server
    #         resp = sck.recv(1024).decode('utf-8')
    #         if resp == "Successful":
    #             self.show_page(MainMenu)
    #             return True
    #         else:
    #             curFrame.lb_notice["text"] = "Invalid username/password"
    #             return False
    #     except:
    #         print("Server is not responding")

    def login(self, curFrame: Frame, sck: socket):
        status = client_receive(sck)
        os.system('cls')
        print(status)
        res = client_send(sck, "da nhan")
        reply = client_receive(sck)
        print(reply)
        try:
            username = curFrame.entry_username.get()
            password = curFrame.entry_password.get()

            if username == "" or password == "":
                curFrame.lb_notice["text"] = "Fields cannot be empty"
                return

            login_information = f"{username},{password}"
            client_send(sck, login_information)

            # Nhận phản hồi từ server
            resp = client_receive(sck)
            if resp == "Successful":
                self.geometry("860x600")
                self.show_page(MainMenu)
            else:
                curFrame.lb_notice["text"] = "Invalid username/password"
        except:
            print("Server is not responding")
    # ------------------------------------------------
    def downloadFile_thread(self, curFrame: Frame, sck: socket):
        # Tạo một luồng mới để chạy hàm download mà không làm đơ UI
        download_thread = threading.Thread(target=self.downloadFile, args=(curFrame, sck))
        download_thread.start()

    def downloadFile(self, curFrame: Frame, sck: socket):
        # Send request for server
        data_send = "downloadFile"
        sck.sendall(data_send.encode('utf-8'))

       #Nhan yeu cau nhap duong dan tu sever
        resp = sck.recv(10240).decode("utf-8")
        print("Nhap CANCEL de thoat!!!")
        #nhap vao ten file
        msg = curFrame.entry_path.get()
        if msg == "CANCEL":
            sck.sendall(msg.encode("utf-8"))
            return
        #gui ten file hoac duong dan
        sck.sendall(msg.encode("utf-8"))
        #gui trang thai xem file co ton tai tren sever hay khong
        checkStatus = sck.recv(10240).decode("utf-8")
        if checkStatus == "ff":
            print("File is in list forbidden file. Can't download this file")
            return
        if checkStatus == "Not exist":
            print("File khong ton tai!!!")
            return
        else:
            resp = "Da nhan duoc"
            sck.sendall(resp.encode("utf-8"))
        #tao duong dan den noi luu tru file
        tmp = name(msg)
        if not check(tmp):
            tmp = "/" + tmp
        nameWithNotExten = getNameWithNotExten(tmp)
        exten = getExten(tmp)
        fileWrite = PathClient + tmp
        #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
        i = 1
        while os.path.isfile(PathClient + tmp):
                tmp = nameWithNotExten + "(" + str(i) + ")" + exten
                fileWrite = PathClient + tmp
                i += 1
        sizeRecv = sck.recv(10240).decode("utf-8")
        size = int(sizeRecv)
        sizeResp = "Nhan thanh cong"
        sck.sendall(sizeResp.encode("utf-8"))

        # Progess bar GUI
        progress = Toplevel(self)
        progress.title("Download")

        progress_bar = ttk.Progressbar(progress, orient="horizontal", length=300, mode="determinate", maximum=size)
        progress_bar.pack(pady = 20)

        progress_label = Label(progress, text="0%")
        progress_label.pack(pady = 10)
        # ---------------------------

        ofs = open(fileWrite, "wb")
        sw = 0
        while size > sw:
            try:
                data = sck.recv(10240)
            except Exception as e:
                print(f"Co loi khi download file {msg}/ Connect Error with sever.")
                return False
            if not data:
                break
            ofs.write(data)
            sw += len(data)
            if progress.winfo_exists():
                progress_bar["value"] = sw
                progress_label.config(text=f"{(sw/size) * 100:.2f}%")
                progress.update_idletasks()
                # time.sleep(0.05)
            # ---------------------
            try:
                sck.sendall(str(sw).encode("utf-8"))
            except:
                print(f"Co loi khi download file {msg}/ Connect Error with sever.")
                return False
        ofs.close()

        # ofs.close()
        time.sleep(1)
        if progress.winfo_exists:
            progress.destroy() # GUI : progress bar
        
        resp = sck.recv(10240).decode("utf-8")
        if resp == "Success":
            curFrame.lb_notice["fg"] = "green"
            curFrame.lb_notice["text"] = f"Sever: File dang duoc luu tru tai {fileWrite}"
            print(f"Sever: Da download file thanh cong. File dang duoc luu tru tai {fileWrite} ")
        else:
            curFrame.lb_notice["text"] = "Download file that bai. Loi ket noi!"
            print(f"Sever: Download file that bai. Loi ket noi!")
    
    def uploadFile(self, sck: socket, msg: str):
        size = os.path.getsize(msg)
        sck.sendall(str(size).encode("utf-8"))
        sizeResp = sck.recv(10240).decode("utf-8")
        
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
                data = ifs.read(10240)
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
                    print(f"Co loi khi upload file {msg}/ Connect Error with sever.")
                    return False
                try:
                    resp = sck.recv(10240).decode("utf-8")
                except Exception as e:
                    print(f"Co loi khi upload file {msg}/ Connect Error with sever.")
                    return False
        #ifs.close()
        sck.sendall("xong".encode("utf-8"))

        time.sleep(1)
        if progress.winfo_exists:
            progress.destroy() # GUI : progress bar
        
        respSta = sck.recv(10240).decode("utf-8")
        sck.sendall("da nhan".encode("utf-8"))
        resp = sck.recv(10240).decode("utf-8")
        if resp == "Success":
            print(f"Sever: Da upload file {msg} len sever thanh cong. {respSta}")
        else:
            print(f"Sever: Upload file {msg} len sever that bai. {respSta}")
    
    def uploadFileThread(self, curFrame: Frame, sck: socket):
        # Tạo một luồng mới để chạy hàm download mà không làm đơ UI
        upload_file_thread = threading.Thread(target=self.uploadFile_support_gui, args=(curFrame, sck))
        upload_file_thread.start()
    
    def uploadFile_support_gui(self, curFrame: Frame, sck: socket):
        flag = True
        msg = "uploadFile"
        sck.sendall(msg.encode('utf-8'))
        #Nhan yeu cau nhap duong dan tu sever
        resp = sck.recv(1024).decode('utf-8')
        while 1:
            print("Nhap CANCEL de thoat!!!")
            # msg = input(f"(Sever request) - {resp}")
            msg = curFrame.entry_path.get()
            if msg == 'CANCEL':
                sck.sendall(msg.encode('utf-8'))
                Bin = client_receive(sck)
                flag = False
                break
            if not checkExist(msg):
                print("File khong ton tai. Yeu cau nhap lai!!!")
                continue
            sck.sendall(msg.encode('utf-8'))
            Bin = client_receive(sck)
            break
        if flag == True:
            self.uploadFile(sck, msg)

    def uploadFilesInFolderSequentially(self, sck: socket, msg: str):
        fileName = os.listdir(msg)
        sck.sendall(str(len(fileName)).encode('utf-8'))
        sizeResp = sck.recv(1024).decode('utf-8')
        if sizeResp != "da nhan":
            print(f"Sever: {sizeResp}")
            return
        for file in fileName:
            sck.sendall(file.encode('utf-8'))
            fileRep = sck.recv(1024).decode('utf-8')
            self.uploadFile(sck, msg + "/" + file)
        sck.sendall("da xong".encode('utf-8'))
        res = sck.recv(1024).decode('utf-8')
        print(res)

    def uploadFolder_support_gui(self, curFrame: Frame, sck: socket):
        msg = "uploadFilesInFolderSequentially"
        sck.sendall(msg.encode('utf-8'))
        flag = True
        #Nhan yeu cau nhap duong dan folder tu sever
        resp = sck.recv(1024).decode('utf-8')
        while 1:
            print("Nhap CANCEL de thoat!!!")
            # msg = input(f"(Sever request) - {resp}")
            msg = curFrame.entry_path.get()
            if msg == 'CANCEL':
                sck.sendall(msg.encode('utf-8'))
                Bin = client_receive(sck)
                flag = False
                break
            if not checkFolderExist(msg):
                print("Folder khong ton tai. Yeu cau nhap lai!!!")
                continue
            sck.sendall(msg.encode('utf-8'))
            Bin = client_receive(sck)
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
app.mainloop()
client.close()