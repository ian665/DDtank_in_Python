import tkinter as tk
import customtkinter
from client import start_client
from tkinter import messagebox, simpledialog
from hw2_client import ChatClient

# 創建 ChatClient 實例
client = ChatClient(username=None, address='localhost:3410')

# 創建主視窗
app = customtkinter.CTk()
app.title("Application")
app.geometry("400x700+100+50")

# 登入頁面 Frame
login_frame = customtkinter.CTkFrame(app)
login_frame.pack(fill="both", expand=True)

# 主應用頁面 Frame
main_frame = customtkinter.CTkFrame(app)

# 切換到主頁面的函數
def open_main_window():
		login_frame.pack_forget()  # 隱藏登入頁面
		main_frame.pack(fill="both", expand=True)  # 顯示主頁面

# 登入檢查函數
def check_login():
		username = username_var.get()
		password = password_var.get()
		reply = client.login(username, password)
		if "successfully" in reply:
				open_main_window()  # 驗證成功後切換到主頁面
				app.after(500, start_client)
		else:
				messagebox.showerror("Login Failed", "Incorrect username or password.")

# 註冊檢查函數
def check_register():
		username = username_var.get()
		password = password_var.get()
		reply = client.register(username, password)
		if "successfully" in reply:
				messagebox.showinfo("Registration Successful", "Account created successfully!")
				open_main_window()  # 註冊成功後切換到主頁面
		else:
				messagebox.showerror("Registration Failed", "Account already exists.")

# 設置登入頁面內容
customtkinter.CTkLabel(login_frame, text="Username:").place(x=100, y=150)
customtkinter.CTkLabel(login_frame, text="Password:").place(x=100, y=200)

username_var = tk.StringVar()
password_var = tk.StringVar()
customtkinter.CTkEntry(login_frame, textvariable=username_var).place(x=190, y=150)
customtkinter.CTkEntry(login_frame, show="*", textvariable=password_var).place(x=190, y=200)

# 登入和註冊按鈕
customtkinter.CTkButton(login_frame, text="Login", command=check_login, width=70, height=30).place(x=220, y=250)
customtkinter.CTkButton(login_frame, text="Register", command=check_register, width=70, height=30).place(x=130, y=250)

# 設置主頁面內容
customtkinter.CTkLabel(main_frame, text="Welcome to Chat Room", font=("Helvetica", 16)).pack(pady=20)

output_text = customtkinter.CTkTextbox(main_frame, height=200, width=400)
output_text.pack(fill="both", expand=True, padx=10, pady=10)

# 主頁面功能按鈕
def list_topics_action():
		topics = client.list_topics()
		if not topics:
			output_text.insert(tk.END, "No topics.\n")		
		else:
			output_text.insert(tk.END, "Topics:\n" + "\n".join(topics) + "\n")
			
	
def create_topic_action():
		title = simpledialog.askstring("Title", "Enter topic title:")
		content = simpledialog.askstring("Content", "Enter topic content:\n")
		if title and content:
				reply = client.create_topic(title, content)
				output_text.insert(tk.END, f"Created {title} successfully.\n")

def show_topic_action():
		topic_id = simpledialog.askinteger("Topic ID", "Enter topic ID to show:")
		if topic_id is not None:
				reply = client.show_topic(topic_id)
				output_text.insert(tk.END, reply+"\n")

def reply_action():
		title = simpledialog.askstring("Title", "Enter topic number:")
		content = simpledialog.askstring("Content", "Enter reply content:")
		reply = client.reply_topic(title, content)
		output_text.insert(tk.END, reply+'\n')

def delete_topic_action():
		item_id = simpledialog.askinteger("Item ID", "Enter topicID to delete:")
		if item_id is not None:
				reply = client.delete_topic(item_id)
				output_text.insert(tk.END, reply+'\n')

def show_history():
		actions = client.history()
		if actions:
				output_text.insert(tk.END, f"{username_var}\n")
				for action in actions:
					output_text.insert(tk.END, f"{action}\n")
		else:
			output_text.insert(tk.END, "No history.\n")

# 設置主頁面按鈕
customtkinter.CTkButton(main_frame, text="List Topics", command=list_topics_action).pack(pady=5)
customtkinter.CTkButton(main_frame, text="Create Topic", command=create_topic_action).pack(pady=5)
customtkinter.CTkButton(main_frame, text="Show Topic", command=show_topic_action).pack(pady=5)
customtkinter.CTkButton(main_frame, text="Delete Topic",command=delete_topic_action).pack(pady=5)
customtkinter.CTkButton(main_frame, text="Reply",command=reply_action).pack(pady=5)
customtkinter.CTkButton(main_frame, text="History", command=show_history).pack(pady=5)

# 登出按鈕
customtkinter.CTkButton(main_frame, text="Logout", command=lambda: show_login_window()).pack(pady=20)

# 切換回登入頁面的函數
def show_login_window():
		main_frame.pack_forget()  # 隱藏主頁面
		login_frame.pack(fill="both", expand=True)  # 顯示登入頁面

# 開始顯示登入頁面
login_frame.pack(fill="both", expand=True)
app.mainloop()
