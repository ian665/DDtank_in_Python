import socket
import threading
import pygame
import math
import time
import random
import tkinter as tk
import customtkinter 
import sys
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from customtkinter import CTkImage


class ChatClient:
	def __init__(self, username, address):
		self.username = username
		self.address = address
		self.client_socket = None

	def connect(self):
		try:
			self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client_socket.connect(('localhost', 12345))  # 連接伺服器端口
			print("已成功連接到伺服器")
		except socket.error as e:
			print(f"無法連接到伺服器: {e}")
						
	def login(self, username, password):
		self.username = username
		message = f"LOGIN account: {username}, password: {password}"
		self.client_socket.sendall(message.encode())
		response = self.client_socket.recv(1024).decode()
		print(f"{response}")
		return response
	
	def register(self, username, password):
		self.username = username
		message = f"REGISTER account: {username}, password: {password}"
		self.client_socket.sendall(message.encode())
		response = self.client_socket.recv(1024).decode()  # Get response from server
		return response

def check_login():
	username = username_var.get()
	password = password_var.get()
	reply = client.login(username, password)
	print(f"reply {reply}")
	if "successfully" in reply:
		app.quit()
		time.sleep(1)
		login_frame.pack_forget()
		start_client()
	else:
		messagebox.showerror("Login Failed", "Incorrect username or password.")

def check_register():
	username = username_var.get()
	password = password_var.get()
	reply = client.register(username, password)
	if "successfully" in reply:
		messagebox.showinfo("Registration Successful", "Account created successfully!")
	else:
		messagebox.showerror("Registration Failed", "Account already exists.")

def show_winner(loser):
		messagebox.showinfo("遊戲結束", f"{loser} 獲敗！")
pygame.mixer.init()
yoro_sound = pygame.mixer.Sound("yoro.mp3")
ei_sound = pygame.mixer.Sound("ei.mp3")
ita_sound = pygame.mixer.Sound("ita.mp3")
mitome_sound = pygame.mixer.Sound("mito.mp3")
sorry_sound = pygame.mixer.Sound("sorry.mp3")
darega_sound = pygame.mixer.Sound("darega.mp3")
hajima_sound = pygame.mixer.Sound("hajoma.mp3")
player_role = [None]
player_x, player_y = 150, 425
player2_x, player2_y = 650, 425
old_x, old_y, old_x2, old_y2 = 0, 0, 0, 0
player_hp, player2_hp = 100, 100
player_angle, player2_angle = 45, 45
player_bullets, player2_bullets, fly_objects = [], [], []
explosions = []
power = 0
fly, fly_time, fly_state, flying = False, 0, 0, False
player2_turn = False
player_falling, player2_falling, falling_speed = False, False, 5
player_direction, player2_direction = True, True #向右
player_countdown, player2_countdown = True, False
is_space_pressed, is_z_pressed, is_x_pressed = False, False, False
is_j_pressed, is_k_pressed, is_l_pressed = False, False, False
total_time = 20*1000
countdown_start_time1, countdown_start_time2 = pygame.time.get_ticks(), pygame.time.get_ticks()
player_remain_time1, player_remain_time2 = total_time, total_time
wait_connect, login = True, False
message_to_display, message_display_time, message_duration, current_time_display, who_say = None, 0, 3000, 0, None #訊息傳送
state, lose_time, disconnect_time = 0 , None, None #伺服器狀態 遊戲結束時間計算 掉線
def receive_messages(client):
	global player_x, player_y, player2_x, player2_y, player_hp, player2_hp, player_bullets, player2_bullets, power, player2_turn, explosions, fly_objects, fly_state, old_x, old_y, old_x2, old_y2, flying, player_direction, player2_direction, player_countdown, player2_countdown, is_space_pressed, is_z_pressed, is_j_pressed, is_k_pressed, countdown_start_time1, player_remain_time1, countdown_start_time2, player_remain_time2, wait_connect, login, screen, message_to_display, message_display_time, message_duration, who_say, state, lose_time, disconnect_time, is_x_pressed, is_l_pressed
	while True:
		data = client.recv(1024)
		if not data:
			print("伺服器關閉")
			state = 2
		print(f"伺服器訊息: {data.decode()}")
		message = data.decode()
		if message.startswith("你是"):
			if "玩家1" in message:
				player_role[0] = "player1"
			elif "玩家2" in message:
				player_role[0] = "player2"
				wait_connect = False
			else:
				player_role[0] = "audience"
		
		if "完成連線" in message:
			state = 1
			print(f"完成連線 in message {state}")
		
		if "等待" in message:
			login = True
			print(f"等待 in message {login}")
			
		if "新位置" in message:
			position_part = message.split("新位置:")[1].strip()
			player = position_part.split("player:")[1].split(",")[0].strip()
			x_part = float(position_part.split("x:")[1].split(",")[0].strip())
			y_part = float(position_part.split("y:")[1].split(",")[0].strip())
			direction = message.split("direction:")[1].split()[0]
			if player == "玩家1":
				player_x, player_y, player_direction = x_part, y_part, direction
			elif player == "玩家2":
				player2_x, player2_y, player2_direction = x_part, y_part, direction
			
		if "發射" in message:
			who1 = message.split("玩家:")[1].split(",")[0].strip()
			angle1 = float(message.split("角度:")[1].split(",")[0].strip())
			power1 = float(message.split("力量:")[1].split(",")[0].strip())
			where_part = message.split("在")[1].split(",")
			where_x = float(where_part[0])
			where_y = float(where_part[1])
			bullet_part = message.split("命中:")[1].strip().split()
			if "擊中" in message:
				bullet_x1 = float(bullet_part[1])
				bullet_y1 = float(bullet_part[2])
			else:
				bullet_x1, bullet_y1 = None, None
			health1 = int(message.split("血量:")[1].split(",")[0].strip())
			if "玩家1" in message:
				print("玩家1射出")
				player2_turn, player2_countdown = True, True
				is_space_pressed, player_countdown = False, False
				countdown_start_time2 = pygame.time.get_ticks()
				player_remain_time1 = total_time
				player_bullets.append({"x": where_x+40, "y": where_y, "power": power1, "angle": angle1, "time": 0})
				if "擊中" in message:
					player2_hp = int(health1)
					print(f"血量: player2_hp = {health1}")
					if player2_hp <= 0:
						state = 2 
			elif "玩家2" in message:
				player2_turn, player2_countdown = False, False
				player_countdown, is_j_pressed = True, False
				countdown_start_time1 = pygame.time.get_ticks()
				player_remain_time2 = total_time
				player2_bullets.append({"x": where_x+40, "y": where_y, "power": power1, "angle": int(angle1), "time": 0})
				if "擊中" in message:
					player_hp = int(health1)
					if health1 <= 0:
						state = 2
					print(f"血量: player1_hp = {health1}")
		 
		if "多重" in message:
			who1 = message.split("玩家:")[1].split(",")[0].strip()
			angle1 = float(message.split("角度:")[1].split(",")[0].strip())
			power1 = float(message.split("力量:")[1].split(",")[0].strip())
			where_part = message.split("在")[1].split(",")
			where_x = float(where_part[0])
			where_y = float(where_part[1])
			bullet_part = message.split("命中:")[1].strip().split()
			if "擊中" in message:
				bullet_x1 = float(bullet_part[1])
				bullet_y1 = float(bullet_part[2])
			else:
				bullet_x1, bullet_y1 = None, None
			health1 = int(message.split("血量:")[1].split(",")[0].strip())
			if "玩家1" in message:
				print("玩家1射出")
				player2_turn, player2_countdown = True, True
				is_x_pressed, player_countdown = False, False
				countdown_start_time2 = pygame.time.get_ticks()
				player_remain_time1 = total_time
				for i in range(4):
					angle_offset = 5*(i-5//2)
					player_bullets.append({"x": where_x+40, "y": where_y, "power": power1, "angle": angle1+angle_offset, "time": 0})
				if "擊中" in message:
					player2_hp = int(health1)
					print(f"血量: player2_hp = {health1}")
					if player2_hp <= 0:
						state = 2
			elif "玩家2" in message:
				print("玩家2射出")
				player2_turn, player2_countdown = False, False
				player_countdown, is_l_pressed = True, False
				player_remain_time2 = total_time
				countdown_start_time1 = pygame.time.get_ticks()
				for i in range(4):
					angle_offset = 5*(i-5//2)
					player2_bullets.append({"x": where_x+40, "y": where_y, "power": power1, "angle": angle1+angle_offset, "time": 0})
				if "擊中" in message:
					player_hp = int(health1)
					print(f"血量: player1_hp = {player_hp}")
					if player_hp <= 0:
						state = 2
		 
		if "飛行" in message:
			global fly_time
			fly_player = message.split("飛行玩家:")[1].split(",")[0].strip()
			fly_angle = float(message.split("fly_angle:")[1].split(",")[0].strip())
			fly_power = float(message.split("fly_power:")[1].split(",")[0].strip())
			fly_x = float(message.split("fly_x:")[1].split(",")[0].strip())
			fly_y = float(message.split("fly_y:")[1].split(",")[0].strip())
			fly_objects.append({
				"player": fly_player,
				"x": fly_x,
				"y": fly_y,
				"angle": fly_angle,
				"power": fly_power,
				"time": 0
			})
			if "player1" in message:
				player_countdown = False
				player2_turn, player2_countdown, is_z_pressed = True, True, False
				countdown_start_time2 = pygame.time.get_ticks()
				player_remain_time1= total_time
			else:
				player2_countdown = False 
				player2_turn = False
				player_countdown = True
				is_k_pressed = False
				countdown_start_time1 = pygame.time.get_ticks()
				player_remain_time2 = total_time

		if "原始地點" in message:
			old_x = float(message.split("xp1:")[1].split()[0].strip(','))
			old_y = float(message.split("yp1:")[1].split()[0].strip(','))
			old_x2 = float(message.split("xp2:")[1].split()[0].strip(','))
			old_y2 = float(message.split("yp2:")[1].split()[0].strip(','))
			print(f"---------old_x {old_x} old_y {old_y} old_2x {old_x2} old_y2 {old_y2}")

		if "誰說" in message:
			who_say = message.split("誰說:")[1].split()[0].strip(',')
			text = message.split("訊息:")[1]
			font = pygame.font.Font(None, 80)
			player_text = font.render(f"{text}", True, (255, 255, 255))
			print(f"player_role[0] {player_role[0]} {player_text}")
			message_to_display = player_text
			message_display_time = pygame.time.get_ticks()
			if "yoro" in message:
				yoro_sound.play()
			if "ei" in message: 
				ei_sound.play()
			if "ita" in message:
				ita_sound.play()
			if "mito" in message:
				mitome_sound.play()
			if "ha" in message:
				hajima_sound.play()
		if "敗北者" in message:
			who = message.split("敗北者:")[1]
			if who =='玩家1': who = 'player1'
			elif who == '玩家2': who = 'player2'
			result_text = f"{who}'ve been defeated!"
			font = pygame.font.Font(None, 150)
			lose_text = font.render(f"{result_text}", True, (255, 255, 255))
			screen.blit(lose_text, (180, 150))
			if lose_time is None:
				lose_time = pygame.time.get_ticks()
			if lose_time is not None and pygame.time.get_ticks() - lose_time >= 5000:
				state = 2  # 切換到新狀態
				darega_sound.play()
				lose_time = None  # 重置計時器，避免重複執行
				print(f"State changed to {state}")
		
		if "disconnect" in message:
			font = pygame.font.Font(None, 150)
			disconnect_text = font.render(f"{message}", True, (255, 255, 255))
			print(f"disconnect_text {message}")
			screen.blit(disconnect_text, (180, 150))
			if disconnect_time is None:
				disconnect_time = pygame.time.get_ticks()
			if disconnect_time is not None and pygame.time.get_ticks() - disconnect_time >= 2000:
				state = 2  # 切換到新狀態
				sorry_sound.play()
				disconnect_time = None  # 重置計時器，避免重複執行
				print(f"State changed to {state}")
			
def attack_messages(client, angle, power, x, y):
	try:
		if player_role[0] == "player1":
			message = f"發射 角度: {angle} 力量: {power} x: {x} y: {y}"
		else:
			message = f"發射 角度: {180-int(angle)} 力量: {power} x: {x} y: {y}"
		print("發射")
		client.send(message.encode('utf-8'))
	except socket.error as e:
		print(f"socket error {e}")
		
def multi_attack_messages(client_socket, angle, power, x, y):
	try:
		if player_role[0] == "player1":
			message = f"多重 角度: {angle} 力量: {power} x: {x} y: {y}"
		else:
			message = f"多重 角度: {180-int(angle)} 力量: {power} x: {x} y: {y}"
		print(f"{player_role[0]}多重射擊")
		client_socket.send(message.encode('utf-8'))
	except socket.error as e:
		print(f"socket error {e}")

def position_messages(client, x, y, direction):
	try:
		message = f" 位置 x: {x} y: {y} direction: {direction}"
		client.send(message.encode('utf-8'))
	except socket.error as e:
		print(f"{e}")
	 
def fly_messages(client, angle, power, x, y):
	global fly, fly_time
	fly_time += 0.1
	message = f"飛行 angle: {angle}, power: {power}, x: {x}, y: {y} "
	client.send(message.encode('utf-8'))
	return x, y
		 
def old_messages(client, player_x, player_y, player2_x, player2_y):
	message = f"原始地點 old_xp1:{player_x}, old_yp1: {player_y}, old_xp2: {player2_x}, old_yp2: {player2_y}"
	client.send(message.encode('utf-8'))

def hello_messages(client):
	if isinstance(client, socket.socket):
		message = f"whoami?"
		client.send(message.encode('utf-8'))
	else:
		print("client 不是套接字物件")

def disconnect(client):
	try:
		message = f"REMOVE_PLAYER"
		client.send(message.encode())
		print("玩家已從伺服器中刪除")
	except Exception as e:
		print(f"關閉時發送訊息錯誤: {e}")

def lose_message(client_socket):
	message = "LOSE"
	client_socket.send(message.encode())
	
def sent_message(client_socket, text):
	global message_to_display, message_display_time, current_time_display
	message = f"玩家訊息: {text}"
	client_socket.send(message.encode())

def display_message():
	global message_to_display, message_display_time, current_time_display, who_say
	if message_to_display and message_display_time :
		current_time_display = pygame.time.get_ticks()
	if current_time_display - message_display_time < message_duration:
		if message_to_display != None:
			if who_say == "玩家1":
				screen.blit(message_to_display, (player_x + 50, player_y - 10))
			elif who_say == "玩家2":
				screen.blit(message_to_display, (player2_x + 50, player2_y - 10))
	else:
		message_to_display = None
		message_display_time = 0

def goodbye_message(client_socket):
	message = f"再見"
	client_socket.send(message.encode())

def start_client():
	try:
		pygame.init()
		pygame.mixer.init()
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.0.0.1', 12345)  # 伺服器地址
		global player_x, player_y, player2_x, player2_y, player_image_scaled, player2_image_scaled, player_hp, player2_hp, player_angle, player2_angle, player_bullets, player2_bullets, player2_turn, explosions, fly_state, old_x, old_y, old_x2, old_y2, player_falling, player2_falling, flying, player_direction, player2_direction, power, player_countdown, player2_countdown, is_space_pressed, is_z_pressed, is_j_pressed, is_k_pressed,is_x_pressed, is_l_pressed, countdown_start_time1, player_remain_time1, player_remain_time2, countdown_start_time2, wait_connect, login, screen, state
		player_bullet_count = 0
		player2_bullet_count = 0
  
		clock = pygame.time.Clock()
		font = pygame.font.Font(None, 36)
		bigfont = pygame.font.Font(None, 50)
		metafont = pygame.font.Font(None, 70)
		power1, power2, powerz, powerk, powerx, powerl = 0, 0, 0, 0, 0, 0
		g = 9.8
		max_power = 300
		power_reset_time = 3
		last_time_space, last_time_j, last_time_z, last_time_k, last_time_x, last_time_l = 0, 0, 0, 0, 0, 0
		total_time = 15*1000
		running = True
		end_background_color = [0, 0, 0]  # RGB 顏色
		end_text_color = (255, 255, 255)#結束動畫
		end_text = "Thank you!"
		end_font = pygame.font.Font(None, 100)
		end_text_surface = end_font.render(end_text, True, end_text_color)
		end_text_rect = end_text_surface.get_rect(center=(400, 600))  # 初始位置：畫面底部
		end_text_speed = -2  # 文字向上移動速度
		pygame.mixer.music.load("lofi-song.mp3")
		pygame.mixer.music.play(-1)
		shoot_sound = pygame.mixer.Sound("gun-shot-1.mp3")
		explosion_sound = pygame.mixer.Sound("dense-bomb.wav")
		cat1_sound = pygame.mixer.Sound("cat.mp3")
		cat2_sound = pygame.mixer.Sound("cat1.mp3")
		wind_sound = pygame.mixer.Sound("wind.mp3")
		wind2_sound = pygame.mixer.Sound("wind2.mp3")
		angry_sound = pygame.mixer.Sound("angry.mp3")
		byebye_sound = pygame.mixer.Sound("byebye.mp3")
		aaa_sound = pygame.mixer.Sound("aaa.mp3")
		iya_sound = pygame.mixer.Sound("iya.mp3")
		player_shoot_sound = pygame.mixer.Sound("playershoot.mp3")
		player2_shoot_sound = pygame.mixer.Sound("player2shoot.mp3")
		timer_sound = pygame.mixer.Sound("timer.mp3")
		highspeedtimer_sound = pygame.mixer.Sound("highspeedtimer.mp3")
		player_last_position = (player_x, player_y)
		player2_last_position = (player2_x, player2_y)
		client_socket.connect(server_address)  # 正確的用法
		client_address = client_socket.getsockname()
		print(f"{client_address}")
		player_image = pygame.image.load("images1.png")
		player_image_scaled = pygame.transform.scale(player_image, (90, 75))
		player_image_flipped = pygame.transform.flip(player_image_scaled, True, False)
		player2_image = pygame.image.load("images2.png")
		player2_image_scaled = pygame.transform.scale(player2_image, (100, 75))
		player2_image_flipped = pygame.transform.flip(player2_image_scaled, True, False)
		street_background = pygame.image.load("street.png")
		street_background_scaled = pygame.transform.scale(street_background, (800, 600))
		japan_street_background = pygame.image.load("japanstreet.png")
		japan_street_background_scaled =  pygame.transform.scale(japan_street_background, (800, 600))
		player_image_touse = player_image_flipped
		player2_image_touse = player2_image_scaled
		input_box = pygame.Rect(560, 530, 60, 30)
		color_inactive = pygame.Color('lightskyblue3')
		color_active = pygame.Color('dodgerblue2')
		color = color_inactive
		active = False
		current_dot = 0
		last_jump_time = pygame.time.get_ticks()
		text = ''  # 用來儲存玩家輸入的文字
		output_text = ''  # 用來儲存要顯示的輸出文字
		receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
		receive_thread.start()
		screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("彈彈堂 - test")
		hello_messages(client_socket)
		clock = pygame.time.Clock()
		start_time = time.time()
		while running:
			while state == 0:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
						break
					# 填充背景色
					screen.blit(street_background_scaled,(0, 0))
					wait_text = metafont.render("waiting", True, (51, 102, 102))
					screen.blit(wait_text, (380, 500+30))
					for i in range(4):  # 五個小點
						dot_x = 585 + i * 50
						if i == current_dot:  # 如果是當前跳動的小點
							pygame.draw.circle(screen, (51, 102, 102), (dot_x, 540), 7)
						else:
							pygame.draw.circle(screen, (51, 102, 102), (dot_x, 565), 7)
					current_time = pygame.time.get_ticks()
					if current_time - last_jump_time > 200:
						current_dot = (current_dot + 1) % 5  # 讓索引在 0 到 4 之間循環
						last_jump_time = current_time
					# 更新畫面
					pygame.display.flip()
					clock.tick(60)
			while state == 1:
				for event in pygame.event.get():    
					if event.type == pygame.QUIT:
						print(f"disconnect {client_socket}")
						disconnect(client_socket)
						running = False
						client_socket.close()
					screen.blit(japan_street_background_scaled,(0, 0))
					pygame.draw.rect(screen, (200, 0, 100), (0, 500, 300, 100))
					pygame.draw.rect(screen, (200, 0, 100), (500, 500, 400, 100))
					player2_angle_text = font.render(f"angle: {player2_angle}", True, (0, 0, 153))
					player2_hp_text = font.render(f"Player2 HP: {player2_hp}", True, (0, 0, 153))
					angle_text = font.render(f"angle: {player_angle}", True, (0, 0, 153))
					player_hp_text = font.render(f"Player HP: {player_hp}", True, (0, 0, 153))
					player_role_text = metafont.render(f"{player_role}", True, (255, 255, 250))
					screen.blit(player_role_text, (280, 100))
					screen.blit(angle_text, (10, 50))
					screen.blit(player2_angle_text, (600, 50))
					screen.blit(player2_hp_text, (600, 10))
					screen.blit(player_hp_text, (10, 10))
					player_line_x, player_line_y, player2_line_x, player2_line_y = math.cos(math.radians(player_angle)), -math.sin(math.radians(player_angle)), math.cos(math.radians(180-player2_angle)), -math.sin(math.radians(180-player2_angle))
					keys = pygame.key.get_pressed()
					if event.type == pygame.QUIT:
						running = False
					# 檢查是否點擊了輸入框
					if event.type == pygame.MOUSEBUTTONDOWN:
						print(f"Mouse clicked at: {event.pos}")
						if input_box.collidepoint(event.pos):
							print("Input box clicked!")
							active = not active
						else:
							active = False
						if input_box.collidepoint(event.pos):
								print(f"Clicked inside input box at {event.pos}")
						else:
								print(f"Clicked outside input box at {event.pos}")
						color = color_active if active else color_inactive
					# 捕捉鍵盤按鍵事件
					if event.type == pygame.KEYDOWN:
						if active:
							if event.key == pygame.K_RETURN:  # 按下回車鍵
								output_text = text  # 儲存輸入的文字
								sent_message(client_socket, output_text)
								text = ''  # 清空文字框
							elif event.key == pygame.K_BACKSPACE:  # 按下刪除鍵
								text = text[:-1]  # 刪除最後一個字符
							else:
								text += event.unicode  # 加入當前字符
					# 顯示輸入框
					txt_surface = font.render(text, True, color)
					width = max(200, txt_surface.get_width()+10)
					input_box.w = width
					screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
					pygame.draw.rect(screen, color, input_box, 2)
					display_message()
					current_time = pygame.time.get_ticks()
					countdown_time = current_time
					if player_countdown and not player2_turn and not is_z_pressed and not is_space_pressed and not is_x_pressed:
						passing_time = countdown_time - countdown_start_time1
						#print(f"passing_time {passing_time} countdown_time {countdown_time} countdown_start_time1 {countdown_start_time1} total_time {total_time}")
						player_remain_time1 = max(0, total_time - passing_time) # 計算剩餘時間
						if player_remain_time1 == 4:
							highspeedtimer_sound.play
						if player_remain_time1 == 2:
							highspeedtimer_sound.play
						if player_remain_time1 == 0 or is_space_pressed or is_z_pressed:
							print("玩家1結束回合")
							player_countdown = False  # 關閉玩家1倒數
							player2_turn, player2_countdown = True, True 
							is_space_pressed, is_z_pressed, is_x_pressed = False, False, False 
							power1, powerx = 0, 0  # 重置力量
							countdown_start_time2 = pygame.time.get_ticks()
							player_remain_time1 = total_time
					# 玩家2的倒數邏輯
					if player2_countdown and player2_turn and not is_j_pressed and not is_k_pressed and not is_l_pressed:
						passing_time = countdown_time - countdown_start_time2
						player_remain_time2 = max(0, total_time - passing_time)
						if player_remain_time2 == 4:
							highspeedtimer_sound.play()
						if player_remain_time2 == 2:
							highspeedtimer_sound.play()  
						if player_remain_time2 == 0 or is_j_pressed or is_k_pressed:
							print("玩家2結束回合")
							player2_countdown = False  
							player2_turn = False 
							player_countdown = True 
							is_j_pressed, is_k_pressed, is_l_pressed = False, False, False 
							power2, powerl = 0, 0
							countdown_start_time1 = pygame.time.get_ticks()
							player_remain_time2 = total_time
					if (player_x < -55 or player_x > 800 or (440 > player_x > 260)) and flying == False:  #掉落判斷
						byebye_sound.play()
						player_falling = True
						lose_message(client_socket)
						if player_falling:
							player_y += falling_speed
							if player_y >= 650:
								player_y = 650
								player_falling = False
					elif (player2_x < -60 or player2_x > 765 or (450 > player2_x > 260)) and flying == False:#掉落判斷
						player2_falling = True
						lose_message(client_socket)
						aaa_sound.play()
						if player2_falling:
							player2_y += falling_speed
							if player2_y >= 650:
								player2_y = 650
								player2_falling = False
					else:
						if player_role[0] == "player1" and player2_turn == False:
							pygame.draw.line(screen, (255, 255, 255), (player_x+50, player_y+5), (player_x+player_line_x*20+50, player_y+player_line_y*20), 2)
							if keys[pygame.K_SPACE]:
								if not is_space_pressed:
									last_time_space = current_time
									is_space_pressed = True
								power1 = min(max_power, (current_time - last_time_space)/15)
							else:
								if is_space_pressed:  
									attack_messages(client_socket, player_angle, power1, player_x, player_y)
									player_shoot_sound.play()
									power1 = 0
									is_space_pressed = False
							if keys[pygame.K_z]:
								if not is_z_pressed:
									last_time_z = current_time
									is_z_pressed = True
								powerz = min(max_power, (current_time - last_time_z)/15)
							else:
								if is_z_pressed:  
									wind_sound.play()
									fly_messages(client_socket, player_angle, powerz, player_x, player_y)
									old_messages(client_socket, player_x, player_y, player2_x, player2_y)
									is_z_pressed, powerz = False, 0
							if keys[pygame.K_x]:  #多重射擊
								if not is_x_pressed:
									last_time_x = current_time
									is_x_pressed = True
								powerx = min(max_power, (current_time - last_time_x)/15)
							else:
								if is_x_pressed:
									multi_attack_messages(client_socket, player_angle, powerx, player_x, player_y)
									is_x_pressed, powerx = False, 0
									player_bullet_count += 1
							if keys[pygame.K_LEFT]:
								player_x -= 5
								player_direction = False
							if keys[pygame.K_RIGHT]:  
								player_x += 5
								player_direction = True
							if keys[pygame.K_UP]:
								player_angle += 1
								screen.blit(angle_text, (10, 50))
							if keys[pygame.K_DOWN]:
								player_angle -= 1
								screen.blit(angle_text, (10, 50))
							if (player_x, player_y) != player_last_position:
								cat1_sound.play()
								position_messages(client_socket, player_x, player_y, player_direction)
								player_last_position = (player_x, player_y)
						if player_role[0] == "player2" and player2_turn == True: #player2判斷
							pygame.draw.line(screen, (255, 255, 255), (player2_x+50, player2_y+5), (player2_x+player2_line_x*20+40, player2_y+player2_line_y*20), 2)
							if keys[pygame.K_j] :
								if not is_j_pressed:
									last_time_j = current_time
									is_j_pressed = True
								power2 = min(max_power, (current_time - last_time_j)/15)
							else:
								if is_j_pressed:
									attack_messages(client_socket, player2_angle, power2, player2_x, player2_y)
									player2_shoot_sound.play()
									player2_bullet_count += 1
									is_j_pressed = False
									player2_bullet_count, power2 = 0, 0
									player2_turn = False
							if keys[pygame.K_k]:
								if not is_k_pressed:
									last_time_k = current_time
									is_k_pressed = True
								powerk = min(max_power, (current_time - last_time_k)/15)
							else:
								if is_k_pressed:    
									wind2_sound.play()
									fly_messages(client_socket, 180-player2_angle, powerk, player2_x, player2_y)
									old_messages(client_socket, player_x, player_y, player2_x, player2_y)
									is_k_pressed, powerk = False, 0
							if keys[pygame.K_l]:  #多重射擊
								if not is_l_pressed:
									last_time_l = current_time
									is_l_pressed = True
								powerl = min(max_power, (current_time - last_time_l)/15)
							else:
								if is_l_pressed:
									multi_attack_messages(client_socket, player2_angle, powerl, player2_x, player2_y)
									is_l_pressed, powerl = False, 0
									player2_bullet_count += 1
							if keys[pygame.K_a]:
								player2_x -= 5
								player2_direction = False
							if keys[pygame.K_d]:
								player2_x += 5
								player2_direction = True
							if keys[pygame.K_w]:
								player2_angle += 1
								screen.blit(player2_angle_text, (600, 50))
							if keys[pygame.K_s]:
								player2_angle -= 1
								screen.blit(player2_angle_text, (600, 50))
							if (player2_x, player2_y) != player2_last_position:
								cat2_sound.play()
								position_messages(client_socket, player2_x, player2_y, player2_direction) 
								player2_last_position = (player2_x, player2_y)

						if player_direction == "True" : 
							player_image_touse = player_image_flipped
						elif player_direction == "False": 
							player_image_touse = player_image_scaled 
						if player2_direction == "True": 
							player2_image_touse = player2_image_flipped
						elif player2_direction == "False": 
							player2_image_touse = player2_image_scaled   
					if powerz == 0 and powerx == 0: power1_text = font.render(f"Power: {int(power1)}", True, (0, 0, 0)) # 顯示力量數值
					elif power1 == 0 and powerx == 0: power1_text = font.render(f"Power: {int(powerz)}", True, (0, 0, 0))
					else: power1_text = font.render(f"Power: {int(powerx)}", True, (0, 0, 0))
					if powerk == 0 and powerl == 0: power2_text = font.render(f"Power: {int(power2)}", True, (0, 0, 0))
					elif power2 == 0 and powerk == 0: power2_text = font.render(f"Power: {int(powerl)}", True, (0, 0, 0))
					else: power2_text = font.render(f"Power: {int(powerk)}", True, (0, 0, 0))
					player_time_text = bigfont.render(f"{player_remain_time1 // 1000}s", True, (255, 255, 255))
					player2_time_text = bigfont.render(f"{player_remain_time2 // 1000}s", True, (255, 255, 255))
					if player_role[0] == 'player1' and player2_turn == False:
						screen.blit(player_time_text, (370, 10))
					elif player_role[0] == 'player2' and player2_turn == True:
						screen.blit(player2_time_text, (370, 10))
					screen.blit(power1_text, (10, 90))
					screen.blit(power2_text, (600, 90))
					screen.blit(player_image_touse,(player_x, player_y))
					screen.blit(player2_image_touse,(player2_x, player2_y))
					for bullet in player_bullets:
						bullet["time"] += 0.09
						t = bullet["time"]
						bullet["x"] = float(bullet["x"])
						bullet["y"] = float(bullet["y"])
						bullet["power"] = float(bullet["power"])
						bullet["angle"] = float(bullet["angle"])
						bullet["x"] += bullet["power"] * math.cos(math.radians(bullet["angle"]))* 0.1
						bullet["y"] -= bullet["power"] * math.sin(math.radians(bullet["angle"])) * 0.1 - 0.5*g*(t**2)
						pygame.draw.circle(screen, (0, 0, 255 ), (bullet["x"], bullet["y"]), 5)
						if bullet["x"] > 800 or bullet["y"] > 600:
							player_bullets.remove(bullet)
						if player2_x+5 <= bullet["x"] <= player2_x + 75 and player2_y <= bullet["y"] <= player2_y + 75:
							explosions.append({"x": bullet["x"], "y": bullet["y"], "time": 0})
							explosion_sound.play()
							screen.blit(player2_hp_text, (600, 10))
							player_bullets.remove(bullet)
							angry_sound.play()
							pygame.display.flip()
						
					for player2_bullet in player2_bullets:
						player2_bullet["time"] += 0.09
						t = player2_bullet["time"]
						player2_bullet["x"] += player2_bullet["power"] * math.cos(math.radians(player2_bullet["angle"]))*0.1
						player2_bullet["y"] -= player2_bullet["power"] * math.sin(math.radians(player2_bullet["angle"]))*0.1 - 0.5*g*(t**2)
						pygame.draw.circle(screen, (0, 255, 255 ), (player2_bullet["x"], player2_bullet["y"]), 5)
						if player2_bullet["x"] > 800 or player2_bullet["y"] > 600:
							player2_bullets.remove(player2_bullet)
						if player_x+5 <= player2_bullet["x"] <= player_x + 75 and player_y <= player2_bullet["y"] <= player2_y+75:
							explosions.append({"x": player2_bullet["x"], "y": player2_bullet["y"], "time": 0})
							explosion_sound.play()
							screen.blit(player2_hp_text, (10, 10))
							player2_bullets.remove(player2_bullet)
							explosions.append({"x": player2_bullet["x"], "y": player2_bullet["y"], "time": 0})
							iya_sound.play()
							pygame.display.flip()
					
					for explosion in explosions:
						explosion["time"] += 1
						if explosion["time"] < 20:
							pygame.draw.circle(screen, (255, 165, 0), (int(explosion["x"]), int(explosion["y"])), explosion["time"]*1.2)
						else:
							explosions.remove(explosion)
				
					for fly_object in fly_objects:
						flying = True
						fly_object["time"] += 0.09
						t = fly_object["time"]
						fly_object["x"] += fly_object["power"] * math.cos(math.radians(fly_object["angle"])) * 0.1
						fly_object["y"] -= fly_object["power"] * math.sin(math.radians(fly_object["angle"])) * 0.1 - 0.5 * 9.8 * (t ** 2)
						if fly_object["player"] == "player1":
							player_x = int(fly_object["x"])
							player_y = int(fly_object["y"])
						elif fly_object["player"] == "player2":
							player2_x = int(fly_object["x"])
							player2_y = int(fly_object["y"])
						if fly_object["y"] > 440 or -55 > fly_object["x"] or fly_object["x"] > 800:
							fly_objects.remove(fly_object)
							flying = False
							player_y, player2_y = 425, 425
							if fly_object["x"] > 800 or -55 > fly_object["x"]:
								player_x, player_y = old_x, 425
								print(f"player1 {player_x, player_y} = {old_x, old_y}")
								player2_x, player2_y = old_x2, 425
								print(f"player2 {player2_x, player2_y} = {old_x2, old_y2}")         
					pygame.display.flip()
					clock.tick(60)
			while state == 2:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:  # 點擊視窗關閉按鈕
						running = False
						state = 0
						goodbye_message(client_socket)
					if event.type == pygame.MOUSEBUTTONDOWN:  # 點擊螢幕
						running = False
						state = 0
						goodbye_message(client_socket)
				# 更新背景顏色
				end_background_color[0] = (end_background_color[0] + 1) % 256
				end_background_color[1] = (end_background_color[1] + 2) % 256
				end_background_color[2] = (end_background_color[2] + 3) % 256

				# 更新文字位置
				end_text_rect.y += end_text_speed
				if end_text_rect.bottom < 0:  # 當文字移出畫面時重置位置
						end_text_rect.y = 600 + 50
				screen.fill(end_background_color)
				screen.blit(end_text_surface, end_text_rect)
				pygame.display.flip()
				clock.tick(60)
			
	except socket.error as e:
		print(f"{e}")
		print("斷線")

if __name__ == "__main__":  
	client = ChatClient(username=None, address='localhost:12345')
	client.connect()
	customtkinter.set_appearance_mode("dark")
	app = customtkinter.CTk()
	app.title("Login System")
	window_width, window_height = 400, 300 
	screen_width = app.winfo_screenwidth()
	screen_height = app.winfo_screenheight()
	position_top = int(screen_height / 2 - window_height / 2)
	position_right = int(screen_width / 2 - window_width / 2)
	app.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
	background = "background.png"
	background_image = CTkImage(light_image=Image.open(background),
		dark_image=Image.open(background),
		size=( 400, 270))
	image1 = "gakuya.png"
	street_background = "street.png"
	my_image = CTkImage(light_image=Image.open(image1),
		dark_image=Image.open(image1),
		size=(window_width/2.5, int(window_height / 2.1)))
	login_frame = customtkinter.CTkFrame(app)
	login_frame.pack(fill="both", expand=True)
	main_frame = customtkinter.CTkFrame(app)
	background_label = customtkinter.CTkLabel(login_frame, image=background_image)
	background_label.place(x=0, y=0)
	image_label = customtkinter.CTkLabel(login_frame, image=my_image)
	image_label.place(x=270, y=160)
	image2 = "elfshooter.png"
	my_image2 = CTkImage(light_image=Image.open(image2),
		dark_image=Image.open(image2),
		size=(window_width/3.5, int(window_height)/1.9))
	image_label2 = customtkinter.CTkLabel(login_frame, image=my_image2)
	image_label2.place(x=5, y=140)
	customtkinter.CTkLabel(login_frame, text="Username:").place(x=90, y=90)
	customtkinter.CTkLabel(login_frame, text="Password:").place(x=90, y=130)
	username_var = tk.StringVar()
	password_var = tk.StringVar()
	customtkinter.CTkEntry(login_frame, textvariable=username_var).place(x=190, y=90)
	customtkinter.CTkEntry(login_frame, show="*", textvariable=password_var).place(x=190, y=130)

	customtkinter.CTkButton(login_frame, text="Login", command=check_login, width=70, height=30).place(x=220, y=180)
	customtkinter.CTkButton(login_frame, text="Register", command=check_register, width=70, height=30).place(x=130, y=180)

	login_frame.pack(fill="both", expand=True)
	app.mainloop()