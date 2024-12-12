import socket
import threading
import math
import sqlite3
from datetime import datetime
players = {}
player1 = {'health': 100}
player2 = {'health': 100}
waiting_for_player = True
hello_time = 0
missing_player = None
def init_db():
  conn = sqlite3.connect('game.db')
  cursor = conn.cursor()
  cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      health INTEGER DEFAULT 100,
                      player_type TEXT NOT NULL,
                      position_x INTEGER DEFAULT 0,
                      position_y INTEGER DEFAULT 0,
                      angle INTEGER DEFAULT 0,
                      power INTEGER DEFAULT 0,
                      is_deleted INTEGER DEFAULT 0
                  )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS rounds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id INTEGER,
                        round_number INTEGER,
                        angle INTEGER,
                        power INTEGER,
                        shot_x INTEGER,
                        shot_y INTEGER,
                        hit_player INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (player_id) REFERENCES players(id)
                    )''')
  cursor.execute('''CREATE TABLE IF NOT EXISTS hits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        round_id INTEGER,
                        hit_player_id INTEGER,
                        damage INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (round_id) REFERENCES rounds(id),
                        FOREIGN KEY (hit_player_id) REFERENCES players(id)
                    )''')
  conn.commit()
  conn.close()
init_db()

def register_player(username, password):
  conn = sqlite3.connect('game.db')
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
  existing_player = cursor.fetchone()
  if existing_player:
    print(f"玩家 {username} 已經存在")
    conn.close()
    return "Account already exists"  # Inform the client that the account exists
  try:
    cursor.execute("INSERT INTO players (username, password, player_type) VALUES (?, ?, ?)", (username, password, "玩家"))
    conn.commit()
    print(f"玩家 {username} 註冊成功")
    conn.close()
    return "Account created Successfully"  # Inform the client about successful registration
  except sqlite3.IntegrityError:
    print(f"Error in registration for {username}")
    conn.close()
    return "Registration failed"

def login_player(username, password):
  conn = sqlite3.connect('game.db')
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM players WHERE username = ? AND password = ?", (username, password))
  player = cursor.fetchone()
  conn.close()
  return player

def log_round(player_id, round_number, angle, power, shot_x, shot_y, hit_player):
  conn = sqlite3.connect('game.db')
  cursor = conn.cursor()
  cursor.execute('''INSERT INTO rounds (player_id, round_number, angle, power, shot_x, shot_y, hit_player) VALUES (?, ?, ?, ?, ?, ?, ?)''', (player_id, round_number, angle, power, shot_x, shot_y, hit_player))
  conn.commit()
  conn.close()

def process_shot(player, angle, power, x,  y):
  global player1, player2
  player_bullets = []
  bullet_x, bullet_y = None, None
  hit_player = False
  player_bullets.append({"x": x+40, "y": y, "power": power, "angle": angle, "time": 0})
  for bullet in player_bullets:
    while bullet["y"] < 600 and 0 < bullet["x"] and bullet["x"] < 800:
      bullet["time"] += 0.09
      t = bullet["time"]
      bullet["x"] += bullet["power"] * math.cos(math.radians(bullet["angle"]))* 0.1
      bullet["y"] -= bullet["power"] * math.sin(math.radians(bullet["angle"])) * 0.1 - 0.5*9.8*(t**2)
      if bullet["x"] > 800 or bullet["y"] > 600:
        player_bullets.remove(bullet)
      if player['player'] == "玩家1":
        for address, player_2 in players.items():
          if player_2['player'] == "玩家2":
            if player_2['position'][0]+5 <= bullet["x"] <= player_2['position'][0] + 75 and player_2['position'][1]  <= bullet["y"] <= player_2['position'][1] + 75:
              hit_player = True
              bullet_x, bullet_y = bullet["x"], bullet["y"]
              player_2['health'] -= 8
              player2['health'] = player_2['health']  
              print(f"玩家2被擊中 剩餘血量: {player_2['health']}")
              print(f"{player_2['player']} player['position'][0]: {player_2['position'][0]} player['position'][1]: {player_2['position'][1]}")
              break
      else:
        for address, player_1 in players.items():
          if player_1['player'] == "玩家1":
            if player_1['position'][0]+5 <= bullet["x"] <= player_1['position'][0] + 75 and player_1['position'][1]  <= bullet["y"] <= player_1['position'][1] + 75:
              hit_player = True
              bullet_x, bullet_y = bullet["x"], bullet["y"]
              player_1['health'] -= 8
              player1['health'] = player_1['health'] 
              print(f"玩家1被擊中 剩餘血量: {player1['health']}")
              break
  return  bullet_x, bullet_y, hit_player

def process_multi_shot(shooter, angle, power, x,  y):
  global player1, player2
  player_bullets = []
  bullet_x, bullet_y = None, None
  hit_player = False
  for i in range(4):
    angle_offset = 5*(i-5//2)
    player_bullets.append({"x": x+40, "y": y, "power": power, "angle": angle+angle_offset, "time": 0})
  for bullet in player_bullets:
    while bullet["y"] < 600 and 0 < bullet["x"] and bullet["x"] < 800:
      bullet["time"] += 0.09
      t = bullet["time"]
      bullet["x"] += bullet["power"] * math.cos(math.radians(bullet["angle"]))* 0.1
      bullet["y"] -= bullet["power"] * math.sin(math.radians(bullet["angle"])) * 0.1 - 0.5*9.8*(t**2)
      if bullet["x"] > 800 or bullet["y"] > 600:
        player_bullets.remove(bullet)
      if shooter['player'] == "玩家1":
        for address, player_1 in players.items():
          if player_1['player'] == "玩家2":
            if player_1['position'][0]+5 <= bullet["x"] <= player_1['position'][0] + 75 and player_1['position'][1]  <= bullet["y"] <= player_1['position'][1] + 75:
              hit_player = True
              bullet_x, bullet_y = bullet["x"], bullet["y"]
              player_1['health'] -= 2  
              player2['health'] = player_1['health']
              print(f"玩家2被擊中 剩餘血量: {player_1['health']}")
              print(f"{player_1['player']} player['position'][0]: {player_1['position'][0]} player['position'][1]: {player_1['position'][1]}")
              break
      else:
        for address, player_2 in players.items():
          if player_2['player'] == "玩家1":
            if player_2['position'][0]+5 <= bullet["x"] <= player_2['position'][0] + 75 and player_2['position'][1]  <= bullet["y"] <= player_2['position'][1] + 75:
              hit_player = True
              bullet_x, bullet_y = bullet["x"], bullet["y"]
              player_2['health'] -= 2
              player1['health'] = player_2['health'] 
              print(f"玩家1被擊中 剩餘血量: {player_2['health']}")
              break
  return  bullet_x, bullet_y, hit_player

# 處理每個客戶端連接的函數
def handle_client(client_socket, client_address):
  global hello_time, missing_player, player1, player2
  print(f"客戶端 {client_address} 已連接")
  players[client_address] = {
    'player': None,
    'health': 100,
    'position': (0,0),
    'angle': 0,
    'power': 0,
    'socket': client_socket
  }
  fly_time = 0

  try:
    while True:
      data = client_socket.recv(1024)
      if not data:
        print("客戶端已關閉")
        break
      message = data.decode()
      print(f"客戶端訊息: {message}")
      if message.startswith("LOSE"):
        message = f"敗北者: {players[client_address]['player']}"
        for address, player in players.items():
          player['socket'].sendall(message.encode())
          print(f"{message}")
          
      if message.startswith("REMOVE_PLAYER"):
        missing_player = players[client_address]['player']
        print(F"missing_player = {players[client_address]['player']}")
        for address, player in players.items():
          if missing_player == '玩家1':
            message = "player1 disconnect"
            print(f"玩家1 {message}")
            player['socket'].sendall(message.encode())
          elif missing_player == '玩家2':
            message = "player2 disconnect"
            print(f"玩家2 {message}")
            player['socket'].sendall(message.encode())  
        hello_time = 0
        client_socket.close()

      if "REGISTER" in message:
        try:
          account = message.split("account:")[1].split()[0]
          password = message.split("password:")[1].split()[0]
          result = register_player(account, password)
          client_socket.sendall(result.encode())
          print("result {result}")
        except IndexError:
          print("請檢查訊息格式")
          client_socket.sendall("Invalid username or password".encode())
      if "LOGIN" in message:
        try:
          account = message.split("account:")[1].split()[0]
          password = message.split("password:")[1].split()[0]
          player = login_player(account, password)
          print(f"{player}")
          if player is not None:
            players[client_address]['socket'].sendall("LOGIN successfully".encode())
            for address, player in players.items():
              player['socket'].sendall("LOGIN successfully".encode())
              print(f"{player['socket']} LOGIN successfully")
          else:
            client_socket.sendall("Invalid username or password".encode())
            print("Invalid username or password")
        except IndexError:
          print("請檢查訊息格式")
          client_socket.sendall("Invalid username or password".encode())
      
      if "再見" in message:
        hello_time = 0
      
      if "whoami" in message:
        print(f"hello time: {hello_time}")
        if hello_time == 0:
          players[client_address]['position'] = (150, 425)
          players[client_address]['player'] = '玩家1'
          print(f"{players[client_address]['socket']} {players[client_address]['player']}")
          players[client_address]['socket'].sendall("等待".encode())
          hello_time += 1
        elif hello_time == 1:
          players[client_address]['position'] = (650, 425)
          players[client_address]['player'] = '玩家2'
          print(f"{players[client_address]['socket']} {players[client_address]['player']} hello_time {hello_time}")
          hello_time += 1
        else: 
          players[client_address]['player'] = missing_player
          print(f"{players[client_address]['socket']} missing_player = {players[client_address]['player']}")
        if hello_time >=2:#等待人數
          print(hello_time)
          try:
            for address, player in players.items():
              if player['player'] == '玩家1':
                print(f"{player['socket']} 你是 玩家1")
                player['socket'].sendall("你是 玩家1".encode())
              elif player['player'] == '玩家2':
                print(f"{player['socket']} 你是 玩家2")
                player['socket'].sendall("你是 玩家2".encode())
              else:
                player['socket'].sendall("你是 名額已滿".encode())
                print(f"{player['socket']} {player['player']} 你是 名額已滿")
            for address, player in players.items():
              if players[client_address]['player'] == '玩家1':
                player['socket'].sendall("你是 玩家1完成連線".encode())
              player['socket'].sendall("完成連線".encode())  
              print(f"{player['socket']} 完成連線")
          except KeyError as e:
            print(f"KeyError: {e}")
          except Exception as e:
              print(f"發生錯誤: {e}")
      if "發射" in message:
        try:
          angle = int(message.split("角度:")[1].split()[0])
          power = float(message.split("力量:")[1].split()[0])
          x = float(message.split("x:")[1].split()[0])
          y = float(message.split("y:")[1].split()[0])
          players[client_address]['angle'] = angle
          players[client_address]['power'] = power
          bullet_x, bullet_y, hit_player = process_shot(players[client_address], angle, power, x, y)
          print(f"{players[client_address]['player']} bullet_x: {bullet_x} bullet_y: {bullet_y} hit_player: {hit_player}")
          if hit_player == True:
            shoot = "擊中"
          else: shoot = "未命中"
          for address, player in players.items():
            print("進入players.items======")
            if players[client_address]['player'] == "玩家1":
              player['socket'].sendall(f"發射了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在{x}, {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player2['health']}".encode())
              print(f"發射了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在: {x} {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player2['health']}")
            else:
              player['socket'].sendall(f"發射了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在{x}, {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player1['health']}".encode())
              print(f"發射了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在: {x} {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player1['health']}")
        except ValueError:
          response = "無效發射"
      
      if "多重" in message:
        try:
          angle = int(message.split("角度:")[1].split()[0])
          power = float(message.split("力量:")[1].split()[0])
          x = float(message.split("x:")[1].split()[0])
          y = float(message.split("y:")[1].split()[0])
          players[client_address]['angle'] = angle
          players[client_address]['power'] = power
          bullet_x, bullet_y, hit_player = process_multi_shot(players[client_address], angle, power, x, y)#改到這裡
          print(f"{players[client_address]['player']} bullet_x: {bullet_x} bullet_y: {bullet_y} hit_player: {hit_player}")
          if hit_player == True:
            shoot = "擊中"
          else: shoot = "未命中"
          for address, player in players.items():
            print("進入players.items======")
            if players[client_address]['player'] == "玩家1":
              player['socket'].sendall(f"多重了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在{x}, {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player2['health']}".encode())
              print(f"多重了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在: {x} {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player2['health']}")
            else:
              player['socket'].sendall(f"多重了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在{x}, {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player1['health']}".encode())
              print(f"多重了 玩家: {players[client_address]['player']}, 角度: {angle}, 力量: {power}, 在: {x} {y}, 命中: {shoot} {bullet_x} {bullet_y} 血量: {player1['health']}")
        except ValueError:
          response = "無效發射"    
         
      elif "位置" in message:
        x = float(message.split("x:")[1].split()[0])
        y = float(message.split("y:")[1].split()[0])
        direction = message.split("direction:")[1].split()[0]
        players[client_address]['position'] = (x, y)
        print(f"['position'] = ({x}, {y})")
        for address, player in players.items():
          message = f"新位置: player: {players[client_address]['player']}, x: {x}, y: {y}, direction: {direction} "
          player['socket'].sendall(message.encode())
        response = "無效"
       
      elif "飛行" in message:
        fly_angle = int(message.split("angle:")[1].split()[0].strip(','))
        fly_power = float(message.split("power:")[1].split()[0].strip(','))
        fly_x = float(message.split("x:")[1].split()[0].strip(','))
        fly_y = float(message.split("y:")[1].split()[0].strip(','))
        new_x, new_y = fly_x, fly_y
        while(new_y <= 450):
          fly_time += 0.09
          new_x += + fly_power * math.cos(math.radians(fly_angle)) * 0.1
          new_y -=  fly_power * math.sin(math.radians(fly_angle)) * 0.1 - 0.5 * 9.8 * (fly_time ** 2)
        if players[client_address]['player'] == '玩家1':
          for address, player in players.items():
            message = f"飛行玩家: player1, fly_angle: {fly_angle}, fly_power: {fly_power}, fly_x: {fly_x}, fly_y: {fly_y}, "
            player['socket'].sendall(message.encode())
        elif players[client_address]['player'] == '玩家2':
          for address, player in players.items():
            message = f"飛行玩家: player2,  fly_angle: {fly_angle}, fly_power: {fly_power}, fly_x: {fly_x}, fly_y: {fly_y}, "
            player['socket'].sendall(message.encode())
            
      elif "原始地點" in message:
        old_x = float(message.split("xp1:")[1].split()[0].strip(','))
        old_y = float(message.split("yp1:")[1].split()[0].strip(','))
        old_x2 = float(message.split("xp2:")[1].split()[0].strip(','))
        old_y2 = float(message.split("yp2:")[1].split()[0].strip(','))
        message = f"原始地點 old_xp1:{old_x}, old_yp1: {old_y}, old_xp2: {old_x2}, old_yp2: {old_y2}, "
        for address, player in players.items():
          player['socket'].sendall(message.encode())
      
      elif "玩家訊息" in message:
        text = message.split("訊息:")[1]
        
        message = f"誰說: {players[client_address]['player']},  玩家訊息: {text} "
        for address, player in players.items():
          player['socket'].sendall(message.encode())
         
  except socket.error as e:
    print(f"處理客戶端 {players[client_address]} 時發生錯誤：{e}")
  finally:
    client_socket.close()
    print(f"客戶端 {players[client_address]} 連接已關閉")
    hello_time = 0

def start_server():
  try:
    conn = sqlite3.connect('game.db')
    conn.close()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 12345)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print("伺服端已啟動，等待客戶端連接...")
    while True:
      # 等待並接受客戶端的連接
      client_socket, client_address = server_socket.accept()
      print(f"{client_address} 已連接")
      # 為每個客戶端連接啟動一個新線程
      client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
      client_thread.start()
  except socket.error as e:
      print(f"伺服端錯誤：{e}")
  finally:
      # 確保伺服端套接字關閉
      server_socket.close()
if __name__ == "__main__":
    start_server()