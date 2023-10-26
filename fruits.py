import pygame
import pymunk

class Fruits:
    
    def __init__(self, x, y, r, space):
        self.x = x
        self.y = y
        self.r = r
        self.space = space
        
    def add_fruit(self):
        mass = 100
        body = pymunk.Body()
        body.position = self.x, self.y
        radius = self.r
        shape = pymunk.Circle(body, radius)
        shape.mass = mass
        shape.friction = 1
        self.space.add(body, shape)
        return shape