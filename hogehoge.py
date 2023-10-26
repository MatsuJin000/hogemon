import pygame
import pymunk
import pymunk.pygame_util
import math
import sys, random
from pygame.locals import *
import fruits
# import stage

def draw_fruit(fruit, screen, color):
    pos = int(fruit.body.position.x), 600 - int(fruit.body.position.y)
    pygame.draw.circle(screen, color, pos, int(fruit.radius))
    
    # debug
    text = pygame.font.SysFont(None, 20).render(str(int(fruit.radius)), True, (0, 0, 0))
    screen.blit(text, (fruit.body.position.x-7, 600 - fruit.body.position.y - 5))
    
def add_floor(space, screen):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)  
    shape = pymunk.Segment(body, (200, 10), (600, 10), 5)  
    shape.friction = 1
    space.add(body, shape)
    return shape

def draw_floor(screen, floor, white):
    body = floor.body
    pv1 = body.position + floor.a.rotated(body.angle)
    pv2 = body.position + floor.b.rotated(body.angle)
    p1 = pv1.x, 600 - pv1.y
    p2 = pv2.x, 600 - pv2.y
    pygame.draw.lines(screen, white, False, [p1, p2])

def add_wall(space, screen):
    body1 = pymunk.Body(body_type=pymunk.Body.STATIC)  
    body2 = pymunk.Body(body_type=pymunk.Body.STATIC)  
    shape1 = pymunk.Segment(body1, (200, 10), (200, 500), 5)  
    shape2 = pymunk.Segment(body2, (600, 10), (600, 500), 5)  
    shape1.friction = 1
    shape2.friction = 1
    space.add(body1, shape1)
    space.add(body2, shape2)
    return shape1, shape2
    
def draw_wall(screen, wall1, wall2, white):
    body1 = wall1.body
    body2 = wall2.body
    pv1 = body1.position + wall1.a.rotated(body1.angle)
    pv2 = body1.position + wall1.b.rotated(body1.angle)
    pv3 = body2.position + wall2.a.rotated(body2.angle)
    pv4 = body2.position + wall2.b.rotated(body2.angle)
    p1 = pv1.x, 600 - pv1.y
    p2 = pv2.x, 600 - pv2.y
    p3 = pv3.x, 600 - pv3.y
    p4 = pv4.x, 600 - pv4.y
    pygame.draw.lines(screen, white, False, [p1, p2])
    pygame.draw.lines(screen, white, False, [p3, p4])
    
def collision(space, fruits_list):
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
        
                j += 1
            else:
                j += 1
        i += 1
        
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
    
    x = 400
    
    fruit_radius = [10, 20, 30]
    fruits_list = []
    
    # ステージの追加
    floor = add_floor(space, screen)
    wall1, wall2 = add_wall(space, screen)
    
    while True:
        screen.fill(black)
        
        for event in pygame.event.get():
            # 終了処理
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # クリックしたら果物を追加
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                r = random.choice(fruit_radius)
                newFruit = fruits.Fruits(x, screen_height-50, r, space)
                fruit_shape = newFruit.add_fruit()
                fruits_list.append(fruit_shape)
        
        # ステージの描画
        draw_floor(screen, floor, white)
        draw_wall(screen, wall1, wall2, white)
        
        # 果物の描画
        for fruit in fruits_list:
            draw_fruit(fruit, screen, white)
            
        # 果物の衝突
        collision(space, fruits_list)
        
        # 果物の削除
        for fruit in fruits_list:
            if fruit.radius >= 80:
                space.remove(fruit.body, fruit)
                fruits_list.remove(fruit)
        
        pygame.display.update()
        space.step(1/60)
        clock.tick(60)

if __name__ == '__main__':
    main()