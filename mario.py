import pygame
from player import *
from blocks import *
from monsters import *
from settings import WIN_WIDTH, WIN_HEIGHT, DISPLAY, BACKGROUND_COLOR, FPS, SCREEN_START, \
    FILE_PATH, MUSIC_PATH


class Camera:
    def __init__(self, camera_fn, width, height):
        self.camera_fn = camera_fn
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_fn(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = - l + WIN_WIDTH / 2, - t + WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


player_x = 0
player_y = 0


def load_level():
    global player_x, player_y
    level_file = open(FILE_PATH)
    line = " "
    # commands = []

    while line[0] != '/':
        line = level_file.readline()
        if line[0] == '[':
            while line[0] != ']':
                line = level_file.readline()
                if line[0] != ']':
                    end_line = line.find('|')
                    level.append(line[0: end_line])

        if line[0] != '':
            commands = line.split()
            if len(commands) > 1:
                if commands[0] == 'player':
                    player_x = int(commands[1])
                    player_y = int(commands[2])

                if commands[0] == 'portal':
                    tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                    entities.add(tp)
                    platforms.append(tp)
                    animated_entities.add(tp)

                if commands[0] == 'monster':
                    mn = Monster(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]),
                                 int(commands[5]), int(commands[6]))
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)


def music():
    mixer.init()
    mixer.music.load(MUSIC_PATH)
    mixer.music.set_volume = 0.1
    mixer.music.play(-1)


def main():
    load_level()
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption('Super Mario')
    bg = Surface((WIN_WIDTH,WIN_HEIGHT))
    bg.fill(Color(BACKGROUND_COLOR))

    music()

    left = right = up = running = False

    hero = Player(player_x, player_y)
    entities.add(hero)

    timer = pygame.time.Clock()

    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "P":
                pr = Princess(x, y)
                entities.add(pr)
                platforms.append(pr)
                animated_entities.add(pr)

            x += PLATFORM_WIDTH
        y += PLATFORM_WIDTH
        x = 0

    total_level_width = len(level[0]) * PLATFORM_WIDTH
    total_level_height = len(level) * PLATFORM_HEIGHT
    camera = Camera(camera_configure, total_level_width, total_level_height)

    while not hero.winner:
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit('QUIT')

            if event.type == KEYDOWN:
                if event.key == pygame.K_UP:
                    up = True
                if event.key == pygame.K_LEFT:
                    left = True
                if event.key == pygame.K_RIGHT:
                    right = True
                if event.key == pygame.K_LSHIFT:
                    running = True

            if event.type == KEYUP:
                if event.key == pygame.K_UP:
                    up = False
                if event.key == pygame.K_LEFT:
                    left = False
                if event.key == pygame.K_RIGHT:
                    right = False
                if event.key == pygame.K_LSHIFT:
                    running = False

        screen.blit(bg, SCREEN_START)
        animated_entities.update()
        monsters.update(platforms)
        camera.update(hero)
        hero.update(left, right, up, running, platforms)

        for entity in entities:
            screen.blit(entity.image, camera.apply(entity))

        timer.tick(FPS)
        pygame.display.update()


level = []
platforms = []
entities = pygame.sprite.Group()
animated_entities = pygame.sprite.Group()
monsters = pygame.sprite.Group()

if __name__ == '__main__':
    main()
