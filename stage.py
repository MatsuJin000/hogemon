import pygame 
import pymunk

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
    pygame.draw.lines(screen, white, False, [p1, p2])
    pygame.draw.lines(screen, white, False, [p3, p4])