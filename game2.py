import pygame
import pymunk
import pymunk.pygame_util
import math
import cv2
import mediapipe as mp
import numpy as np
import time
import sys, random
from pygame.locals import *

# 自作モジュールのインポート
import fruits

def add_floor(space, pos1, pos2, screen):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)  
    shape = pymunk.Segment(body, pos1, pos2, 5)  
    shape.friction = 1
    space.add(body, shape)
    return shape

def draw_floor(screen, h, floor, white):
    body = floor.body
    pv1 = body.position + floor.a.rotated(body.angle)
    pv2 = body.position + floor.b.rotated(body.angle)
    p1 = pv1.x, h - pv1.y
    p2 = pv2.x, h - pv2.y
    pygame.draw.lines(screen, white, False, [p1, p2], 5)

def add_wall(space, screen):
    body1 = pymunk.Body(body_type=pymunk.Body.STATIC)  
    body2 = pymunk.Body(body_type=pymunk.Body.STATIC)  
    shape1 = pymunk.Segment(body1, (220, 10), (220, 500), 5)  
    shape2 = pymunk.Segment(body2, (580, 10), (580, 500), 5)  
    shape1.friction = 1
    shape2.friction = 1
    space.add(body1, shape1)
    space.add(body2, shape2)
    return shape1, shape2
    
def draw_wall(screen, h, wall1, wall2, white):
    body1 = wall1.body
    body2 = wall2.body
    pv1 = body1.position + wall1.a.rotated(body1.angle)
    pv2 = body1.position + wall1.b.rotated(body1.angle)
    pv3 = body2.position + wall2.a.rotated(body2.angle)
    pv4 = body2.position + wall2.b.rotated(body2.angle)
    p1 = pv1.x, h - pv1.y
    p2 = pv2.x, h - pv2.y
    p3 = pv3.x, h - pv3.y
    p4 = pv4.x, h - pv4.y
    pygame.draw.lines(screen, white, False, [p1, p2], 5)
    pygame.draw.lines(screen, white, False, [p3, p4], 5)
    
def draw_gameover_line(screen, h):
    pygame.draw.line(screen, (100, 100, 250), (220, 100), (580, 100), 2)

def select_img(r):
    if r == 30:
        img = "img/tamago.png"
    elif r == 40:
        img = "img/nazokusa.png"
    elif r == 50:
        img = "img/pamo.png"
    elif r == 70:
        img = "img/futachi.png"
    elif r == 90:
        img = "img/gon.png"
    elif r == 130:
        img = "img/gigas.png"       
        
    return img

def draw_fruit(fruit, h, screen, image, pos):
    img = pygame.image.load(select_img(fruit.radius))
    img = pygame.transform.scale(img, (int(fruit.radius*2), int(fruit.radius*2)))
    
    # 画像の回転
    rotate_img = pygame.transform.rotate(img, math.degrees(fruit.body.angle))
    rotate_rect = rotate_img.get_rect(center = pos)
    
    # 画像の描画
    screen.blit(rotate_img, rotate_rect.topleft)
    
    # debug
    text = pygame.font.SysFont(None, 20).render(str(int(fruit.radius)), True, (0, 0, 0))
    screen.blit(text, (fruit.body.position.x-7, h - fruit.body.position.y - 5))
    
def draw_fruit2(fruit, h, screen, image, pos):
    img = pygame.image.load(select_img(fruit.r))
    img = pygame.transform.scale(img, (int(fruit.r*2), int(fruit.r*2)))
    screen.blit(img, (pos[0]-fruit.r, pos[1]-fruit.r))
    # debug
    text = pygame.font.SysFont(None, 20).render(str(int(fruit.r)), True, (0, 0, 0))
    screen.blit(text, (pos[0]-7, pos[1] - 5))
    
def draw_line(screen, color, x):
    pygame.draw.line(screen, color, (x, 50), (x, 580), 3)
    
def max_fruit_size(fruits_list):
    max_size = 0
    for fruit in fruits_list:
        if fruit.radius > max_size:
            max_size = fruit.radius
    return max_size
    
def collision_fruit(space, fruits_list):    
    score = 0
    
    i = 0
    while i < len(fruits_list):
        j = i + 1
        while j < len(fruits_list):
            fruit1 = fruits_list[i]
            fruit2 = fruits_list[j]
            distance = fruit1.body.position.get_distance(fruit2.body.position)
            if distance <= fruit1.radius + fruit2.radius:
                if fruit1.radius == fruit2.radius:
                    # 新しい果物を作成
                    new_x = (fruit1.body.position.x + fruit2.body.position.x) / 2
                    new_y = (fruit1.body.position.y + fruit2.body.position.y) / 2
                    if fruit1.radius == 50:
                        new_r = 70
                    elif fruit1.radius == 70:
                        new_r = 90
                    elif fruit1.radius == 90:
                        new_r = 130
                    elif fruit1.radius == 130:
                        new_r = 150
                    else :
                        new_r = fruit1.radius + 10
                    newFruit = fruits.Fruits(new_x, new_y, new_r, space)
                    new_fruit_shape = newFruit.add_fruit()
                    
                    # 古い果物を削除
                    space.remove(fruit1.body, fruit1)
                    space.remove(fruit2.body, fruit2)
                    fruits_list.remove(fruit1)
                    fruits_list.remove(fruit2)
                    
                    # 新しい果物を追加
                    fruits_list.append(new_fruit_shape)
                    
                    score += fruit1.radius
        
                j += 1
            else:
                j += 1
        i += 1
        
    return score

# MediaPipeの手の追跡を設定
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

# 手の座標を取得する関数
def get_hand_position(image):
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # 右手のみ処理する
            if handedness.classification[0].label == 'Right':
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                return int(thumb_tip.x * screen_width), int(thumb_tip.y * screen_height)
    return None


#指の接触を検出する関数(人差し指、親指）
def detect_thumb_index_contact(hand_landmarks, threshold=0.05):
    index_finger_tip = np.array([hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x,
                                 hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y])
    thumb_tip = np.array([hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].x,
                          hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y])
    distance = np.linalg.norm(index_finger_tip - thumb_tip)
    return distance < threshold

# Webカメラの設定
cap = cv2.VideoCapture(0)

def main():
    
    # 初期化
    pygame.init()
    
    # 画面の大きさ
    global screen_width
    screen_width = 800
    global screen_height
    screen_height = 600
    
    # 画面の設定
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Suika")
    clock = pygame.time.Clock()
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (200, 100, 100)
    blue = (100, 100, 200)
    
    bkg = pygame.image.load("img/background.jpg")
    bkg = pygame.transform.scale(bkg, (screen_width, screen_height))
    
    # 物理空間の設定
    space = pymunk.Space()
    space.gravity = (0.0, -900.0)
    
    # スコアの初期化
    score = 0
    x = 400
    
    fruit_radius = [30, 40, 50]
    fruit_first_radius = [30]
    fruits_list = []
    
    # マウスクリックの制御変数
    click_flag = False
    frame_cnt = 0
    
    # 手の位置の初期化
    contact = False
    current_x, current_y = 400, 0

    # 前回のフレームでの接触状態を追跡する変数
    was_contact = False 

    # ステージの追加
    floor_pos1 = (220, 10)
    floor_pos2 = (580, 10)
    floor = add_floor(space, floor_pos1, floor_pos2, screen)
    
    wall1, wall2 = add_wall(space, screen)
    
    # 事前に果物の生成
    pre_fruit_list = [] # 表示予定の果物のリスト
    # 最初の果物を追加
    for i in range(2):
        r = random.choice(fruit_first_radius)
        newFruit = fruits.Fruits(x, screen_height-50, r, space)
        pre_fruit_list.append(newFruit)
        
    running = True
    
    while running:

        # Webカメラから画像を読み込む(手の位置)
        ret, frame = cap.read()
        if not ret:
                break
        
        hand_pos = get_hand_position(frame)
        
        # 手が認識されない場合
        if hand_pos is None :
            x, y = 400, 0
            click_flag = False
        # 手が認識されているが、指が接触していない場合
        elif not contact :
            x, y = current_x, current_y
            if click_flag:
                click_flag = True
            else :
                click_flag = False
        else :
            x, y = hand_pos[0], hand_pos[1]
            if click_flag:
                click_flag = True
            else :
                click_flag = False

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = hands.process(frame_rgb)
        
        contact = False  # このフレームでの接触状態
        if results.multi_hand_landmarks:
            for hand_landmarks, handness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handness.classification[0].label == "Right":  # 右手のみを検出
                    if detect_thumb_index_contact(hand_landmarks):
                        contact = True
                        if not was_contact:  # 前回接触していなくて、今回接触した場合
                            was_contact = True
                        break  # 右手での接触を検出したら、他の手のチェックはスキップ
        
        if not contact:
            was_contact = False  # このフレームでは接触がなかった場合、was_contactをリセット

        for event in pygame.event.get():
            # 終了処理
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
        if click_flag and not contact: 
            fruit_r = pre_fruit_list[0].r
            
            # 果物が画面外に出ないようにする
            if x <= 220 + fruit_r:
                x = 220 + fruit_r + 5
            elif x >= 580 - fruit_r:
                x = 580 - fruit_r - 5
            
            # 果物を落下させる
            clicked_fruit = pre_fruit_list.pop(0)
            clicked_fruit.x, clicked_fruit.y = x, screen_height - 101
            fruit_shape = clicked_fruit.add_fruit()
            fruits_list.append(fruit_shape)
            
            # 新しい果物をリストに追加
            # 半径が最大の果物より大きい果物は生成しない
            while True:
                # rは確率で決定
                # 低い半径が出やすいようにする
                r = random.choice(fruit_radius)
                if r == 60:
                    r = 80
                if len(fruits_list) <= 3:
                    minus = 0
                else :
                    minus = 10
                    
                if r <= max_fruit_size(fruits_list) - minus:
                    break
            newFruit = fruits.Fruits(x, screen_height-50, r, space)
            pre_fruit_list.append(newFruit)
            
            click_flag = False
                
        # 背景の描画
        screen.blit(bkg, (0, 0))
        
        # ステージの描画
        draw_floor(screen, screen_height, floor, white)
        draw_wall(screen, screen_height, wall1, wall2, white)
        draw_gameover_line(screen, screen_height)
                   
        # 果物の描画
        for fruit in fruits_list:
            pos = int(fruit.body.position.x), screen_height - int(fruit.body.position.y)
            draw_fruit(fruit, screen_height, screen, white, pos)
        
        # 操作する果物の描画
        current_x, current_y = x, y
        fruit_r = pre_fruit_list[0].r
        if current_x <= 220 + fruit_r:
            current_x = 220 + fruit_r + 5
        elif current_x >= 580 - fruit_r:
            current_x = 580 - fruit_r - 5
            
        pos_pre1 = (current_x, 50)
        if click_flag :
            draw_line(screen, red, current_x)
        else :
            draw_line(screen, blue, current_x)
        draw_fruit2(pre_fruit_list[0], screen_height, screen, white, pos_pre1)
            
        # 次の果物の描画
        pos_pre2 = (700, 50)
        draw_fruit2(pre_fruit_list[1], screen_height, screen, white, pos_pre2)
        
        # 果物の衝突
        score += collision_fruit(space, fruits_list)
        
        # スコアの描画 白色
        text = pygame.font.SysFont(None, 70).render(str(int(score)), True, white)
        screen.blit(text, (30, 30))
        
        for fruit in fruits_list:
            # 果物の削除
            if fruit.radius >= 150:
                space.remove(fruit.body, fruit)
                fruits_list.remove(fruit)
                clear = True
                running = False
            # ステージ外に出るとゲーム終了
            if fruit.body.position.y >= 500:
                clear = False
                running = False
                # pygame.quit()
                # sys.exit()          
                
        if frame_cnt % 100 == 0:
            click_flag = True      
                
        # マウスクリックの制御
        frame_cnt += 1
        
        pygame.display.update()
        space.step(1/60)
        clock.tick(60)

    while True:
        for event in pygame.event.get():
            # 終了処理
            if event.type == QUIT:
                pygame.quit()
                cap.release()
                sys.exit()
                
        if clear :
            str1 = "Clear!"
        else :
            str1 = "Game Over"
                
        screen.fill(black)
        text1 = pygame.font.SysFont(None, 70).render(str1, True, white)
        screen.blit(text1, (300, 200))
        text2 = pygame.font.SysFont(None, 50).render("Score: " + str(int(score)), True, white)
        screen.blit(text2, (300, 300))
        
        pygame.display.update()

    pygame.quit()
    cap.release()
    
if __name__ == '__main__':
    main()