from tkinter import Tk, Canvas, PhotoImage, W
from random import randrange
import pyglet

pyglet.options['shadow_window'] = False

root = Tk()
root.title('MyPang')

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
ROOT_WIDTH = SCREEN_WIDTH / 2.
ROOT_HEIGHT = SCREEN_HEIGHT / 2.
POSITION_X = (SCREEN_WIDTH - ROOT_WIDTH) / 2.
POSITION_Y = (SCREEN_HEIGHT - ROOT_HEIGHT) / 2.
root.geometry('%dx%d+%d+%d' % (ROOT_WIDTH, ROOT_HEIGHT, POSITION_X, POSITION_Y))

ACCELERATION, FRICTION = 0.1, 0.001

class ImageInfo(object):
    def __init__(self, size=[], animated=False):
        self.size = size
        self.animated = animated

BALLOON_INFO = ImageInfo(size=[100, 100])
HARPOON_INFO = ImageInfo(size=[8, 420])
CHRACTER_INFO = ImageInfo(size=[64, 64], animated=True)

IMAGE_DIR = '.\\images\\'
BG_IMAGE_PATH = IMAGE_DIR + 'bg.gif'
BG_IMAGE = PhotoImage(file=BG_IMAGE_PATH)

BALLOONS = {1: (1, 1), 2: (2, 1), 3: (1, 2), 4: (2, 2), 5: (1, 3), 6: (2, 3), 7: (3, 3)}
BALLOON_IMAGES = []
BALLOONS_NUM = 8
for i in range(BALLOONS_NUM):
    image_path = IMAGE_DIR + 'ball' + str(i) + '.gif'
    BALLOON_IMAGES.append(PhotoImage(file=image_path))
balloons_list = []

HARPOON_IMAGE_PATH = IMAGE_DIR + 'harpoon.gif'
HARPOON_IMAGE = PhotoImage(file=HARPOON_IMAGE_PATH)

CHARACTER_IMAGE_PATH = IMAGE_DIR + 'character.gif'
CHARACTER_IMAGE_TILED = PhotoImage(file=CHARACTER_IMAGE_PATH)
TILE_NUM = 9

def split_image(source_img, x1, y1, x2, y2):
    subimage = PhotoImage()
    root.tk.call(subimage, 'copy', source_img, '-from', x1, y1, x2, y2, '-to', 0, 0)
    return subimage

CHARACTER_IMAGE_LIST = [[split_image(CHARACTER_IMAGE_TILED, CHRACTER_INFO.size[0] * i, CHRACTER_INFO.size[1] * j, CHRACTER_INFO.size[0] * (i+1), CHRACTER_INFO.size[1] * (j+1)) for i in range(TILE_NUM)] for j in range(3)]

SOUND_DIR = '.\\sounds\\'
HARPOON_SOUND_PATH = SOUND_DIR + 'arrow_shot.wav'
HARPOON_SOUND = pyglet.media.load(HARPOON_SOUND_PATH, streaming=False)

POP_SOUND_PATH = SOUND_DIR + 'pop.wav'
POP_SOUND = pyglet.media.load(POP_SOUND_PATH, streaming=False)

BG_MUSIC_PATH = SOUND_DIR + 'bgm.wav'
BG_MUSIC = pyglet.media.load(BG_MUSIC_PATH)

playing, life, score, level = False, 5, 0, 1

class Sprite(object):
    def __init__(self, image='', image_info='', position=[], velosity=[], rate=1, acceleration=False):
        self.image = image
        self.size = image_info.size
        self.pos = position
        self.vel = velosity
        self.rate = rate
        self.is_accelerated = acceleration
        self.ID = 0

    def add_vectors(self, p, q):
        return list(map(sum, zip(p, q)))

    def is_collided(self, obj):
        box_tuple = c.bbox(self.ID)
        return obj.ID in c.find_overlapping(*box_tuple)

    def resize(self, rate):
        self.size = list(map(lambda x: x * rate, self.size))
        if self.rate > 1:
            self.rate -= 1
        else:
            self.rate /= 2.

    def update(self):
        if self.is_accelerated:
            self.vel[1] += ACCELERATION
            self.vel[1] *= 1 - FRICTION
            if self.pos[1] > ROOT_HEIGHT-self.size[1]/2:
                self.vel[1] *= -1
            if (self.pos[0] < self.size[0]/2) or (self.pos[0] > ROOT_WIDTH-self.size[0]/2):
                self.vel[0] *= -1
        self.pos = self.add_vectors(self.pos, self.vel)

    def draw(self):
        self.ID = c.create_image(self.pos[0], self.pos[1], image=self.image)

class Character(Sprite):
    def __init__(self, image, image_info, position, velosity, margin=30, tiles=9):
        Sprite.__init__(self, image, image_info, position, velosity)
        self.is_shot = False
        self.tiles = tiles
        self.tile = 0
        self.direction = 1
        self.harpoon = None
        self.margin = margin
        self.RIGHT_OR_LEFT = {'Right': (7, 2), 'Left': (-7, 0)}
        c.bind('<Right>', self.update)
        c.bind('<Left>', self.update)
        c.bind('<space>', self.shoot)
        c.bind('<KeyRelease>', self.reset)
        c.focus_set()

    def shoot(self, e=None):
        if not self.is_shot and playing:
            self.is_shot = True
            harpoon_pos = [self.pos[0], ROOT_HEIGHT + HARPOON_INFO.size[1]/4]
            harpoon_vel = (0, -10)
            self.harpoon = Sprite(HARPOON_IMAGE, HARPOON_INFO, harpoon_pos, harpoon_vel)
            self.harpoon.draw()
            HARPOON_SOUND.play()

    def update(self, e=None):
        new_pos = self.pos[0] + self.vel[0]
        self.vel[0], self.direction = self.RIGHT_OR_LEFT[e.keysym]
        if self.margin < new_pos < (ROOT_WIDTH - self.margin):
            self.pos = self.add_vectors(self.pos, self.vel)
            c.move(self.ID, self.vel[0], 0)
        c.itemconfig(self.ID, image=CHARACTER_IMAGE_LIST[self.direction][self.tile])
        self.tile += 1
        self.tile = self.tile % self.tiles

    def reset(self, e=None):
        self.direction = 1
        c.itemconfig(self.ID, image=CHARACTER_IMAGE_LIST[self.direction][4])

class MyPang(object):
    def __init__(self):
        c.create_image(ROOT_WIDTH/2, ROOT_HEIGHT/3, image=BG_IMAGE)
        self.score_board = c.create_text((50, 30), text='SCORE: ' + str(score), font=12, fill='blue', anchor=W)
        self.life_board = c.create_text((50, 50), text='LIFE: ' + str(life), font=12, fill='red', anchor=W)
        self.level_board = c.create_text((50, 70), text='LEVEL: ' + str(level), font=12, fill='black', anchor=W)
        self.message_a = 'Welcome to MyPang'
        self.message_b = 'Click to Start'
        c.bind("<ButtonPress-1>", self.on_click)
        c.pack()
        self.character = Character(CHARACTER_IMAGE_LIST[1][4], CHRACTER_INFO, [ROOT_WIDTH / 2, ROOT_HEIGHT - 27], [0, 0])
        self.character.draw()
        self.playbgm()

    def run(self):
        global life, score, level, playing, balloons_list
        if playing:
            h = self.character.harpoon
            if self.character.is_shot:
                c.move(h.ID, h.vel[0], h.vel[1])
                h.update()
                for i in balloons_list:
                    if h.is_collided(i):
                        POP_SOUND.play()
                        if i.rate > .2:
                            rate = i.rate
                            for b in range(2):
                                new_balloon = self.zoom_func(BALLOON_IMAGES[randrange(BALLOONS_NUM)], rate)
                                self.pop(new_balloon, (-1)**b, i.pos, i.vel, rate)
                        balloons_list.remove(i)
                        c.delete(h.ID)
                        self.character.is_shot = False
                        score += 10 * level
                        break
                if h.pos[1] < -h.size[1]/2:
                    c.delete(h.ID)
                    self.character.is_shot = False
            if not balloons_list:
                playing = False
                level += 1
                if level > len(BALLOONS):
                    self.message_board('You Win!', 'Total Score: ' + str(score))
                    return self.new_game()
                else:
                    self.message_board('Good Job!', 'Next Level:' + str(level))
            for i in balloons_list:
                i.update()
                c.move(i.ID, i.vel[0], i.vel[1])
                if self.character.is_collided(i):
                    life -= 1
                    if h:
                        self.character.is_shot = False
                        c.delete(h.ID)
                    self.message_board('Balloon Popped!', 'Click to Continue')
                    balloons_list = []
            c.itemconfig(self.score_board, text='SCORE: ' + str(score))
            c.itemconfig(self.life_board, text='LIFE: ' + str(life))
            c.itemconfig(self.level_board, text='LEVEL: ' + str(level))
        else:
            if not life:
                self.message_board('Game Over! Click to Start', 'Total Score: ' + str(score))
                return self.new_game()
            x, y = POSITION_X, POSITION_Y
            c.create_polygon(x-200, y-100, x+200, y-100, x+200, y+100, x-200, y+100, fill='black', tag='m')
            c.create_text(x, y-25, text=self.message_a, font=12, fill='gold', tag='m')
            c.create_text(x, y+25, text=self.message_b, font=12, fill='gold', tag='m')
        root.after(10, self.run)

    def new_game(self):
        global life, score, level
        life, score, level = 5, 0, 1
        self.run()

    def pop(self, balloon, n, pos, vel, rate):
        new_vel = [n * randrange(2, 4), -abs(vel[1])]
        balloons_list.append(Sprite(balloon, BALLOON_INFO, pos, new_vel, rate = rate, acceleration=True))
        balloons_list[-1].resize(rate)
        balloons_list[-1].draw()

    def start(self):
        num, rate = BALLOONS[level]
        for i in range(num):
            new_balloon = BALLOON_IMAGES[randrange(BALLOONS_NUM)].zoom(rate, rate)
            self.pop(new_balloon, (-1)**i, [(i+1)*(ROOT_WIDTH/(num+1)), 100], [0, 3], rate)

    def message_board(self, message_a, message_b):
        global playing
        self.message_a, self.message_b = message_a, message_b
        playing = False

    def on_click(self, e=None):
        global playing
        if not playing:
            c.delete('m')
            playing = True
            self.start()

    def zoom_func(self, image, rate):
        if rate < 1:
            rate = int(1 / rate)
            return image.subsample(rate, rate)
        return image.zoom(rate, rate)

    def bgm(self):
        # group = pyglet.media.SourceGroup()
        # # group.queue(BG_MUSIC)
        # group.loop = True
        # BG_MUSIC.play()
        player = pyglet.media.Player()
        player.loop = True
        player.queue(BG_MUSIC)
        player.play()
        pyglet.app.run()

    def playbgm(self):
        from threading import Thread
        global player_thread
        player_thread = Thread(target=self.bgm)
        player_thread.start()

c = Canvas(root, width=ROOT_WIDTH, height=ROOT_HEIGHT)
mypang = MyPang()
mypang.new_game()
def exit():
    pyglet.app.exit()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', exit)
root.mainloop()
