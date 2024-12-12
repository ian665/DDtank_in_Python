import pygame
import sys
import math
import random
import time


pygame.init()


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("204204 - test")
# music
pygame.mixer.music.load("lofi-song.mp3")
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound("gun-shot-1.mp3")
explosion_sound = pygame.mixer.Sound("dense-bomb.wav")
girl_sound = pygame.mixer.Sound("happy.mp3")
running = True
player_x, player_y = 100, 400
player_hp = 100
player2_x, player2_y = 600, 400
player2_bullets = []
player2_angle = 45
player2_hp = 100
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 150)
g = 9.8
bullets = []
bullets_max = 4
bullet_count = 0
player2_bullet_count = 0
explosions = []
angle = 45
clock = pygame.time.Clock()
show_turn_text = False
turn_start_time = 0
turn_display_duration = 3000
player2_turn = False




while running:
  for event in pygame.event.get():    
    if event.type == pygame.QUIT:
      running = False
    screen.fill((135, 100, 235))
    pygame.draw.rect(screen, (200, 0, 100), (0, 500, 300, 100))
    pygame.draw.rect(screen, (200, 0, 100), (500, 500, 400, 100))
    pygame.draw.circle(screen, (0, 255, 0), (400, 300), 100)
    player_image = pygame.image.load("°ª³t±C±C-removebg-preview.png")
    player_image_scaled = pygame.transform.scale(player_image, (200, 100))
    player2_image = pygame.image.load("bell-Photoroom.png")
    player2_image_scaled = pygame.transform.scale(player2_image, (200, 100))
    angle_text = font.render(f"angle: {angle}", True, (0, 0, 0))
    bullets_text = font.render(f"bullets: {len(bullets)}", True, (0, 0, 0))
    player_hp_text = font.render(f"Player HP: {player_hp}", True, (0, 0, 0))
    victory_text = big_font.render("VICTORY", True, (0, 0, 0))
    player2_angle_text = font.render(f"angle: {player2_angle}", True, (0, 0, 0))
    player2_hp_text = font.render(f"Player2 HP: {player2_hp}", True, (0, 0, 0))
    screen.blit(player2_angle_text, (600, 50))
    screen.blit(player2_hp_text, (600, 10))
    screen.blit(player_hp_text, (10, 10))
    screen.blit(angle_text, (10, 50))
    screen.blit(bullets_text, (10, 90))
    if show_turn_text:
      current_time = pygame.time.get_ticks()
      if current_time - turn_start_time < turn_display_duration:
        user_turn_text = big_font.render("Player1 Turn", True, (255, 255, 255))
        screen.blit(user_turn_text, (screen.get_width() // 2 - user_turn_text.get_width() // 2,
        screen.get_height() // 2 - user_turn_text.get_height() // 2))
      else:
        show_turn_text = False
    show_turn_text = True
    if player2_turn == False:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
        show_turn_text = False
        shoot_sound.play()
        if len(bullets) == 0:
          v = 50
          bullets.append({"x": player_x+150, "y": player_y+30, "v": v, "angle": angle, "time": 0})
          bullet_count += 1
          if bullet_count == 1:
            bullet_count = 0
            turn_start_time = pygame.time.get_ticks()
            player2_turn = True
      keys = pygame.key.get_pressed()
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
        angle += 5
        screen.blit(angle_text, (10, 50))
      if keys[pygame.K_DOWN]:
        angle -= 5
        screen.blit(angle_text, (10, 50))
    if player2_turn == True:
      show_turn_text = False
      if event.type == pygame.KEYDOWN and event.key == pygame.K_j and player2_turn == True:
        shoot_sound.play()
        if len(bullets) == 0:
          v = 50
          player2_bullets.append({"x": player2_x+75, "y": player2_y+10, "v": v, "angle": 180 - player2_angle, "time": 0})
          player2_bullet_count += 1
          if player2_bullet_count == 1:
            player2_bullet_count = 0
            turn_start_time = pygame.time.get_ticks()
            player2_turn = False
      keys = pygame.key.get_pressed()
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
    screen.blit(player2_image_scaled, (player2_x, player2_y))
    screen.blit(player_image_scaled, (player_x, player_y))
  for bullet in bullets:
    bullet["time"] += 0.019
    t = bullet["time"]
    bullet["x"] += bullet["v"] * math.cos(math.radians(bullet["angle"]))* 0.1
    bullet["y"] -= bullet["v"] * math.sin(math.radians(bullet["angle"])) * 0.1 - 0.5*g*(t**2)
    pygame.draw.circle(screen, (0, 0, 255 ), (int(bullet["x"]), int(bullet["y"])), 5)
    if bullet["x"] > 800 or bullet["y"] > 600:
      bullets.remove(bullet)
    if player2_x <= bullet["x"] <= player2_x + 150 and player2_y <= bullet["y"] <= player2_y + 100:
      explosion_sound.play()
      player2_hp -= 20
      pygame.display.flip()
      screen.blit(player2_hp_text, (600, 10))
      bullets.remove(bullet)
      explosions.append({"x": bullet["x"], "y": bullet["y"], "time": 0})
      if player2_hp <= 0:
        girl_sound.play()
        screen.blit(victory_text,(200, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
       
  for player2_bullet in player2_bullets:
    player2_bullet["time"] += 0.019
    t = player2_bullet["time"]
    player2_bullet["x"] += player2_bullet["v"] * math.cos(math.radians(player2_bullet["angle"]))*0.1
    player2_bullet["y"] -= player2_bullet["v"] * math.sin(math.radians(player2_bullet["angle"]))*0.1 - 0.5*g*(t**2)
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
        girl_sound.play()
        screen.blit(victory_text, (200, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False


  for explosion in explosions:
    explosion["time"] += 1
    if explosion["time"] < 20:
      pygame.draw.circle(screen, (255, 165, 0), (int(explosion["x"]), int(explosion["y"])), explosion["time"]*2)
    else:
      explosions.remove(explosion)


  pygame.display.flip()
  clock.tick(60)


pygame.quit()
sys.exit()

