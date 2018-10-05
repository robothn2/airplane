#coding: utf-8
import pygame, sys
from pygame.locals import *
import random

class GameObject(pygame.sprite.Sprite):
    def __init__(self, screen, image):
        super().__init__()
        self.hp = 1
        self.screen = screen
        self.screenWidth = screen.get_width()
        self.image = image.convert()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect()
    def update(self, ctx):
        if self.rect.right < -self.screenWidth or self.rect.left > self.screenWidth * 2:
            self.kill()
    def draw(self, ctx):
        self.screen.blit(self.image, self.rect)

class Player(GameObject):
    def __init__(self, screen, image):
        super().__init__(screen, image)
        self.hp = self.hpMax = 3
        self.tick = 0
        self.speed = 5
        self.image.set_colorkey((246, 246, 246), RLEACCEL)

    def update(self, ctx):
        super().update(ctx)
        self.tick += 1

        keys = ctx.keys
        if keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        if keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
        if keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        if keys[K_RCTRL]:
            if self.tick > 10:
                self.tick = 0
                bullet = Bullet(self.screen, ctx.imageBullet,
                                (self.rect.right, self.rect.top),
                                (1, 0), 25)
                ctx.playerBullets.add(bullet)
                bullet = Bullet(self.screen, ctx.imageBullet,
                                (self.rect.right, self.rect.bottom),
                                (1, 0), 25)
                ctx.playerBullets.add(bullet)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.screen.get_width():
            self.rect.right = self.screen.get_width()
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= self.screen.get_height():
            self.rect.bottom = self.screen.get_height()

    def decHp(self):
        self.hp -= 1
        return self.hp > 0

    def draw(self, ctx):
        self.screen.blit(self.image, self.rect)
        rectHp = pygame.Rect(self.rect.left, self.rect.top - 10, self.rect.width, 6)
        self.screen.fill((0,0,0), rectHp)
        rectHp.width = int(self.rect.width * self.hp / self.hpMax)
        self.screen.fill((200, 200, 0), rectHp)
        #self.drawText(ctx, str(self.hp), (self.rect.x, self.rect.y - 20))

    def drawText(self, ctx, text, pos, fontColor=(0, 0, 0), backgroudColor=(255, 255, 255)):
        textSurface = ctx.font.render(text, True, fontColor, backgroudColor)
        self.screen.blit(textSurface, textSurface.get_rect(center=pos))

class EnemyPlane(GameObject):
    def __init__(self, screen, image):
        super().__init__(screen, image)
        self.image.set_colorkey((246, 246, 246), RLEACCEL)
        self.rect = self.image.get_rect(
            center=(random.randint(screen.get_width() - 80, screen.get_width()), random.randint(0, screen.get_height()))
        )
        self.speed = random.randint(2, 4)
        self.tick = 0
        self.hp = random.randint(1, 2)

    def update(self, ctx):
        super().update(ctx)
        self.rect.move_ip(-self.speed, 0)

        self.tick += 1
        if self.tick > 40:
            self.tick = 0
            bullet = Bullet(self.screen, ctx.imageBullet,
                        self.rect.center,
                        (-1, 0), random.randint(10, 15))
            ctx.enemyBullets.add(bullet)

    def draw(self, ctx):
        self.screen.blit(self.image, self.rect)
    def decHp(self):
        self.hp -= 1
        return self.hp > 0

class Bullet(GameObject):
    def __init__(self, screen, image, pos, direction, speed):
        super().__init__(screen, image)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.direction = direction
        self.screenWidth = self.screen.get_width()

    def update(self, ctx):
        super().update(ctx)
        self.rect.move_ip(self.speed * self.direction[0], self.speed * self.direction[1])

class Background(GameObject):
    def __init__(self, screen, image):
        super().__init__(screen, image)
        rect = image.get_rect()
        self.size = rect.width, rect.height
        self.speed = 1
        self.offset = 0

    def update(self, ctx):
        self.offset += self.speed
        if self.offset >= self.size[0]:
            self.offset = 0

    def draw(self, ctx):
        #draw right part of background
        rectDst = pygame.Rect(0, 0, self.size[0] - self.offset, self.size[1])
        rectSrc = pygame.Rect(self.offset, 0, self.size[0] - self.offset, self.size[1])
        self.screen.blit(self.image, rectDst, rectSrc)

        #draw left part of background
        if self.offset > 0:
            rectDst = pygame.Rect(self.size[0] - self.offset, 0, self.offset, self.size[1])
            rectSrc = pygame.Rect(0, 0, self.offset, self.size[1])
            self.screen.blit(self.image, rectDst, rectSrc)

class Game():
    def __init__(self):
        pygame.init()

        imageBack = pygame.image.load('bk3.jpg')
        self.imagePlayer = pygame.image.load('plane_1.png')
        self.imageBullet = pygame.image.load('bullet_2.png')
        self.imageEnemy = pygame.image.load('enemy_1.png')
        self.font = pygame.font.Font('arial.ttf', 16)
        rect = imageBack.get_rect()
        self.size = rect.width, rect.height
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Flight")

        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, 1000)

        self.background = Background(self.screen, imageBack)
        self.player = Player(self.screen, self.imagePlayer)
        self.playerBullets = pygame.sprite.Group()
        self.enemyBullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                elif event.type == self.ADDENEMY:
                    enemy = EnemyPlane(self.screen, self.imageEnemy)
                    self.enemies.add(enemy)

            self.keys = pygame.key.get_pressed()
            self.player.update(self)
            self.playerBullets.update(self)
            self.enemyBullets.update(self)
            self.enemies.update(self)
            self.background.update(self)

            self.background.draw(self)

            #print(len(self.playerBullets), len(self.enemyBullets), len(self.enemies))

            self.player.draw(self)
            for sprite in self.playerBullets:
                sprite.draw(self)
            for sprite in self.enemyBullets:
                sprite.draw(self)
            for sprite in self.enemies:
                sprite.draw(self)

            collideEnemy = pygame.sprite.spritecollideany(self.player, self.enemyBullets)
            if collideEnemy:
                collideEnemy.kill()
                if not self.player.decHp():
                    break
            collideEnemy = pygame.sprite.spritecollideany(self.player, self.enemies)
            if collideEnemy:
                collideEnemy.kill()
                self.player.kill()
                break
            pygame.sprite.groupcollide(self.playerBullets, self.enemies, True, True)

            pygame.display.flip()
            self.clock.tick(40)

        pygame.quit()

if __name__ == '__main__':
    Game().run()