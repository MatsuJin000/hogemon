import pygame
import pymunk
import pymunk.pygame_util
import math
import sys, random
from pygame.locals import *

# 自作モジュールのインポート
import fruits
from stage import add_floor, draw_floor, add_wall, draw_wall

def draw_fruit(fruit, h, screen, image, pos):
    img = pygame.image.load("Orangestar01.png")
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
    img = pygame.image.load("Orangestar01.png")
    img = pygame.transform.scale(img, (int(fruit.r*2), int(fruit.r*2)))
    screen.blit(img, (pos[0]-fruit.r, pos[1]-fruit.r))
    # debug
    text = pygame.font.SysFont(None, 20).render(str(int(fruit.r)), True, (0, 0, 0))
    screen.blit(text, (pos[0]-7, pos[1] - 5))
    
def max_fruit_size(fruits_list):
    max_size = 0
    for fruit in fruits_list:
        if fruit.radius > max_size:
            max_size = fruit.radius
    return max_size
    
def collision(space, fruits_list):    
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
                    newFruit = fruits.Fruits(new_x, new_y, fruit1.radius+10, space)
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

def main():
    
    # 初期化
    pygame.init()
    
    # 画面の大きさ
    screen_width = 800
    screen_height = 600
    
    # 画面の設定
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Suika")
    clock = pygame.time.Clock()
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    # 物理空間の設定
    space = pymunk.Space()
    space.gravity = (0.0, -900.0)
    
    # スコアの初期化
    score = 0
    
    x = 400
    
    fruit_radius = [10, 20, 30, 40, 50]
    fruit_first_radius = [10, 20]
    fruits_list = []
    
    # ステージの追加
    floor_pos1 = (200, 10)
    floor_pos2 = (600, 10)
    floor = add_floor(space, floor_pos1, floor_pos2, screen)
    
    wall1, wall2 = add_wall(space, screen)
    
    # 事前に果物の生成
    pre_fruit_list = [] # 表示予定の果物のリスト
    # 最初の果物を追加
    for i in range(2):
        r = random.choice(fruit_first_radius)
        newFruit = fruits.Fruits(x, screen_height-50, r, space)
        pre_fruit_list.append(newFruit)
    
    while True:
        screen.fill(black)
        
        for event in pygame.event.get():
            # 終了処理
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # クリックしたら果物を落下
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                fruit_r = pre_fruit_list[0].r
                
                # 果物が画面外に出ないようにする
                if x <= 200 + fruit_r:
                    x = 200 + fruit_r + 5
                elif x >= 600 - fruit_r:
                    x = 600 - fruit_r - 5
                
                # 果物を落下させる
                clicked_fruit = pre_fruit_list.pop(0)
                clicked_fruit.x, clicked_fruit.y = x, screen_height - 50
                fruit_shape = clicked_fruit.add_fruit()
                fruits_list.append(fruit_shape)
                
                # 新しい果物をリストに追加
                # 半径が最大の果物より大きい果物は生成しない
                while True:
                    r = random.choice(fruit_radius)
                    if r <= max_fruit_size(fruits_list) - 10:
                        break
                newFruit = fruits.Fruits(x, screen_height-50, r, space)
                pre_fruit_list.append(newFruit)
        
        # ステージの描画
        draw_floor(screen, screen_height, floor, white)
        draw_wall(screen, screen_height, wall1, wall2, white)
                   
        # 果物の描画
        for fruit in fruits_list:
            pos = int(fruit.body.position.x), screen_height - int(fruit.body.position.y)
            draw_fruit(fruit, screen_height, screen, white, pos)
        
        # 操作する果物の描画
        pos_pre1 = (400, 50)
        draw_fruit2(pre_fruit_list[0], screen_height, screen, white, pos_pre1)
            
        # 次の果物の描画
        pos_pre2 = (100, 50)
        draw_fruit2(pre_fruit_list[1], screen_height, screen, white, pos_pre2)
            
        # 果物の衝突
        score += collision(space, fruits_list)
        
        # スコアの描画 白色
        text = pygame.font.SysFont(None, 50).render(str(int(score)), True, white)
        screen.blit(text, (10, 10))
        
        # 果物の削除
        for fruit in fruits_list:
            if fruit.radius >= 110:
                space.remove(fruit.body, fruit)
                fruits_list.remove(fruit)
        
        pygame.display.update()
        space.step(1/60)
        clock.tick(60)

if __name__ == '__main__':
    main()