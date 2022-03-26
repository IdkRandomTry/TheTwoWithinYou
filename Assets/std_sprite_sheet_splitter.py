import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite


class TextBox (pygame.sprite.Sprite):
    def __init__(self, caption, colour, x, y, text_size):
        super().__init__()
        self.caption = caption
        self.colour = colour
        self.font = pygame.font.Font('Assets/Bitstream Vera Sans Bold.ttf', text_size)
        self.image = self.font.render(self.caption, True, self.colour)
        self.rect = self.image.get_rect()           # gets rectangle of correct size
        self.rect.topleft = (x, y)


class Buttons (pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, x, y, margin=0):
        super().__init__()
        self.not_hover = image
        self.image = self.not_hover
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.center = self.rect.center
        self.margin = margin

    def mouse_hover (self, image_hover: pygame.Surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = image_hover
            return True
        else:
            self.image = self.not_hover
            return False

    def mouse_click (self):
        if pygame.mouse.get_pressed()[0]:           # If Right Click
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
            else:
                return False
        else:
            return False
