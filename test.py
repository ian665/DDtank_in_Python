if keys[pygame.K_m]:  # 按下 M 键触发多重射击
  if not is_m_pressed:
    is_m_pressed = True
    bullet_count = 5  # 发射 5 个子弹
    angle_spread = 20  # 每个子弹之间的角度差
    center_angle = player_angle  # 中心角度（玩家的当前角度）
    
    for i in range(bullet_count):
      angle_offset = angle_spread * (i - bullet_count // 2)  # 计算每颗子弹的角度偏移
      bullet = {
        "x": player_x,
        "y": player_y,
        "power": 15,  # 子弹初始速度
        "angle": center_angle + angle_offset,
        "time": 0
      }
      player_bullets.append(bullet)  # 将子弹添加到子弹列表
else:
  is_m_pressed = False
