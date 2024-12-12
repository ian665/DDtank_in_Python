import socket
import threading
import pygame
import math
import random

player_role = [None]
player_x, player_y = 100, 400
player2_x, player2_y = 400, 400
player_image = pygame.image.load("高速婆婆-removebg-preview.png")
player_image_scaled = pygame.transform.scale(player_image, (200, 100))
player2_image = pygame.image.load("bell-Photoroom.png")
player2_image_scaled = pygame.transform.scale(player2_image, (200, 100))

def receive_messages(client_socket):
	global player_x, player_y, player2_x, player2_y, player_image_scaled, player2_image_scaled
	while True:
		data = client_socket.recv(1024)
		if not data:
			print("伺服器關閉")
		print(f"伺服器訊息: {data.decode()}")
		message = data.decode()
		if message.startswith("玩家"):
			if "玩家1" in message:
				player_role[0] = "player1"
			elif "玩家2" in message:
				player_role[0] = "player2"
		elif message.startswith("新位置"):
			parts = message.split("x:")
			x_part = parts[1].split(",")[0].strip()
			y_part = parts[2].strip()
			new_x = int(x_part)
			new_y = int(y_part)
			if player_role[0] == "player1":
					player_x, player_y = new_x, new_y
			elif player_role[0] == "player2":
					player2_x, player2_y = new_x, new_y
			print(f"新位置: x = {player_x}, y = {player_y}")
			
		if message.startswith("發射"):
			parts = message.split(":")
			if len(parts) > 4:
				pos_info = parts[4].strip()
				if 'x' in pos_info and 'y' in pos_info:
				# Extract x and y positions
					x_part = pos_info.split(",")[0].strip()
					y_part = pos_info.split(",")[1].strip()
					new_x = int(x_part.split("x:")[1].strip())
					new_y = int(y_part.split("y:")[1].strip())
					print(f"New Position: x = {new_x}, y = {new_y}")
			else:
					print(f"位置資料格式錯誤: {pos_info}")
	
	
		
def attack_messages(client_socket, angle, power, x, y):
	try:
		message = f"發射 角度: {angle} 力量: {power} x: {x} y: {y}"
		client_socket.send(message.encode('utf-8'))
	except socket.error as e:
		print(f"socket error {e}")

def position_messages(client_socket, x, y):
	try:
		message = f" 位置 x: {x} y: {y}"
		client_socket.send(message.encode('utf-8'))
	except socket.error as e:
		print(f"{e}")
			


def start_client():
	try:
		pygame.init()
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.0.0.1', 12345)
		global player_x, player_y, player2_x, player2_y, player_image_scaled, player2_image_scaled
		player_angle = 45
		player_hp = 100
		player2_angle = 45
		player2_hp = 100
		player_bullets = []
		player2_bullets = []
		player_bullet_count = 0
		player2_bullet_count = 0
		explosions = []
		clock = pygame.time.Clock()
		player2_turn = False
		font = pygame.font.Font(None, 36)
		power = 50
		g = 9.8
		running = True
		player_last_position = (player_x, player_y)
		player2_last_position = (player2_x, player2_y)
		client_socket.connect(server_address)
		client_address = client_socket.getsockname()
		print(f"{client_address}")
		
		receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
		receive_thread.start()

		screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("204204 - test")
		
		while running:
			for event in pygame.event.get():    
				if event.type == pygame.QUIT:
					running = False
				screen.fill((135, 100, 235))
				pygame.draw.rect(screen, (200, 0, 100), (0, 500, 300, 100))
				pygame.draw.rect(screen, (200, 0, 100), (500, 500, 400, 100))
				pygame.draw.circle(screen, (0, 255, 0), (400, 300), 100)
				
				player2_angle_text = font.render(f"angle: {player2_angle}", True, (0, 0, 0))
				player2_hp_text = font.render(f"Player2 HP: {player2_hp}", True, (0, 0, 0))
				angle_text = font.render(f"angle: {player_angle}", True, (0, 0, 0))
				player_hp_text = font.render(f"Player HP: {player_hp}", True, (0, 0, 0))
				screen.blit(angle_text, (10, 50))
				screen.blit(player2_angle_text, (600, 50))
				screen.blit(player2_hp_text, (600, 10))
				screen.blit(player_hp_text, (10, 10))
				keys = pygame.key.get_pressed()
				if event.type == pygame.KEYDOWN:
					if player_role[0] == "player1" and player2_turn == False:
						print("player1 turn")
						if keys[pygame.K_LEFT]:
							if player_x < -50:
								player_x = player_x
							else:
								player_x -= 10
						if keys[pygame.K_RIGHT]:
							if player_x > 160:
								player_x = player_x
							else:
								player_x += 10
						if keys[pygame.K_UP]:
							player_angle += 5
							screen.blit(angle_text, (10, 50))
						if keys[pygame.K_DOWN]:
							player_angle -= 5
							screen.blit(angle_text, (10, 50))
						if keys[pygame.K_SPACE] :
							attack_messages(client_socket, player_angle, power, player_x, player_y)
							player_bullets.append({"x": player_x+150, "y": player_y+30, "power": power, "angle": player_angle, "time": 0})
							player2_turn = True
					if (player_x, player_y) != player_last_position:
						position_messages(client_socket, player_x, player_y)
						player_last_position = (player_x, player_y)
					elif player_role[0] == "player2" and player2_turn == True:#player2判斷
						print("player2 turn")
						if keys[pygame.K_a]:
							if player2_x <= 440:
								player2_x = player2_x
							else:
								player2_x -= 10
						if keys[pygame.K_d]:
							if player2_x >= 650:
								player2_x = player2_x
							else:
								player2_x += 10
						if keys[pygame.K_w]:
							player2_angle += 5
							screen.blit(player2_angle_text, (600, 50))
						if keys[pygame.K_s]:
							player2_angle -= 5
							screen.blit(player2_angle_text, (600, 50))
						if keys[pygame.K_j] :
							attack_messages(client_socket, player2_angle, power, player2_x, player2_y)
							if len(player2_bullets) == 0:
								player2_bullets.append({"x": player2_x+75, "y": player2_y+10, "power": power, "angle": 180 - player2_angle, "time": 0})
								player2_bullet_count += 1
								if player2_bullet_count == 1:
									player2_bullet_count == 0
									player2_turn == False
					if (player2_x, player2_y) != player2_last_position:
						position_messages(client_socket, player2_x, player2_y)
						player2_last_position = (player2_x, player2_y)
				screen.blit(player_image_scaled,(player_x, player_y))
				screen.blit(player2_image_scaled,(player2_x, player2_y))
				for bullet in player_bullets:
					bullet["time"] += 0.050
					t = bullet["time"]
					bullet["x"] += bullet["power"] * math.cos(math.radians(bullet["angle"]))* 0.1
					bullet["y"] -= bullet["power"] * math.sin(math.radians(bullet["angle"])) * 0.1 - 0.5*g*(t**2)
					pygame.draw.circle(screen, (0, 0, 255 ), (int(bullet["x"]), int(bullet["y"])), 5)
					if bullet["x"] > 800 or bullet["y"] > 600:
						player_bullets.remove(bullet)
					if player2_x <= bullet["x"] <= player2_x + 150 and player2_y <= bullet["y"] <= player2_y + 100:
						player2_hp -= 20
						pygame.display.flip()
						screen.blit(player2_hp_text, (600, 10))
						player_bullets.remove(bullet)
						explosions.append({"x": bullet["x"], "y": bullet["y"], "time": 0})
						if player2_hp <= 0:
							pygame.display.flip()
							running = False
							
				for player2_bullet in player2_bullets:
					player2_bullet["time"] += 0.050
					t = player2_bullet["time"]
					player2_bullet["x"] += player2_bullet["power"] * math.cos(math.radians(player2_bullet["angle"]))*0.1
					player2_bullet["y"] -= player2_bullet["power"] * math.sin(math.radians(player2_bullet["angle"]))*0.1 - 0.5*g*(t**2)
					pygame.draw.circle(screen, (0, 255, 255 ), (int(player2_bullet["x"]), int(player2_bullet["y"])), 5)
					if player2_bullet["x"] > 800 or player2_bullet["y"] > 600:
						player2_bullets.remove(player2_bullet)
					if player_x <= player2_bullet["x"] <= player_x + 200 and player_y <= player2_bullet["y"] <= player2_y+70:
						player_hp -= 50
						pygame.display.flip()
						explosions.append({"x": player2_bullet["x"], "y": player2_bullet["y"], "time": 0})
						player2_bullets.remove(player2_bullet)
						screen.blit(player_hp_text, (10, 10))
						if player_hp <= 0:
							pygame.display.flip()
							running = False

				for explosion in explosions:
					explosion["time"] += 1
					if explosion["time"] < 20:
						pygame.draw.circle(screen, (255, 165, 0), (int(explosion["x"]), int(explosion["y"])), explosion["time"]*2)
					else:
						explosions.remove(explosion)
				pygame.display.flip()
				clock.tick(90)
				
	
	except socket.error as e:
		print(f"{e}")

if __name__ == "__main__":
	start_client()


