import pygame

class Sprite():
    def __init__(self, path, animation_duration):
        self.image = pygame.image.load(path).convert_alpha()
        self.timer = 0
        self.animation_duration = animation_duration

    def get_image(self, frame, width, height, scale, color):
        image =  pygame.Surface((width, height)).convert_alpha()
        image.blit(self.image, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)
        return image
    
    def update(self):
        self.timer = pygame.time.get_ticks() - self.timer
    
    def animate(self, begin, end):
        return self.get_image(int(begin + (self.timer) / self.animation_duration % (end - begin)), 100, 100, 1, (0,0,0))
