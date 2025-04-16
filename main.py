import pygame
import sys
import random

screen_w = 800
screen_h = 600
screen = pygame.display.set_mode((screen_w, screen_h))

clock = pygame.time.Clock()

fps = 60
dt = 1

friction = 0.05

balls = []
walls = []

class Ball:
    def __init__(self, x, y, r, m, elasticity=1):
        balls.append(self)
        self.pos = pygame.Vector2(x, y)
        self.r = r
        self.m = m
        self.inv_m = 0
        if self.m > 0:
            self.inv_m = 1/m
        self.elasticity = elasticity
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.accel = 1
        self.player = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, "#ff0000", (self.pos.x, self.pos.y), self.r)

    def update(self, dt):
        if self.acc.length() > 0:
            self.acc = self.acc.normalize()*self.accel*dt

        self.vel += self.acc*dt
        self.vel *= (1-friction)*dt

        self.pos += self.vel*dt

class Wall:
    def __init__(self, start_x, start_y, end_x, end_y):
        walls.append(self)
        self.start = pygame.Vector2(start_x, start_y)
        self.end = pygame.Vector2(end_x, end_y)

    def draw(self, screen):
        pygame.draw.line(screen, "#000000", self.start, self.end, 4)

    def unit(self):
        dist = self.end-self.start
        if dist.length() > 0:
            return dist.normalize()

for i in range(4):
    Ball(random.randint(100, screen_w-100), random.randint(100, screen_h-100), random.randint(30, 100), random.randint(5, 15), random.randint(1, 10)/10)

balls[0].player = True

Wall(300, 100, 400, 300)

Wall(0, 0, screen_w, 0)
Wall(0, 0, 0, screen_h)
Wall(screen_w, 0, screen_w, screen_h)
Wall(0, screen_h, screen_w, screen_h)

def bb_col(b1, b2):
    dist = pygame.Vector2(b1.pos-b2.pos)
    if b1.r+b2.r >= dist.length():
        return True
    return False

def bb_pen(b1, b2):
    dist = pygame.Vector2(b1.pos-b2.pos)
    depth = b1.r+b2.r-dist.length()
    res = pygame.Vector2(0, 0)
    if dist.length() > 0:
        res = dist.normalize()*(depth/(b1.inv_m+b2.inv_m))
    b1.pos += res*b1.inv_m
    b2.pos -= res*b2.inv_m

def bb_res(b1, b2):
    dist = pygame.Vector2(b1.pos-b2.pos)
    normal = pygame.Vector2(0, 0)
    if dist.length() > 0:
        normal = dist.normalize()
    rel_vel = b1.vel-b2.vel
    sep_vel = rel_vel.dot(normal)
    new_sep_vel = -sep_vel*min(b1.elasticity, b2.elasticity)
    
    sep_vel_diff = new_sep_vel-sep_vel
    impulse = sep_vel_diff/(b1.inv_m+b2.inv_m)
    impulse_vec = normal*impulse

    b1.vel += impulse_vec*b1.inv_m
    b2.vel -= impulse_vec*b2.inv_m

def bw_closest(b1, w1):
    ball_to_wall_start = w1.start-b1.pos
    if w1.unit().dot(ball_to_wall_start) > 0:
        return w1.start
    wall_end_to_ball = b1.pos-w1.end
    if w1.unit().dot(wall_end_to_ball) > 0:
        return w1.end
    
    closest_dist = w1.unit().dot(ball_to_wall_start)
    closest_vec = w1.unit()*closest_dist
    return w1.start-closest_vec

def bw_col(b1, w1):
    if (bw_closest(b1, w1)-b1.pos).length() <= b1.r:
        return True
    return False

def bw_pen(b1, w1):
    pen_vec = b1.pos-bw_closest(b1, w1)
    if pen_vec.length() > 0:
        b1.pos += pen_vec.normalize()*(b1.r-pen_vec.length())

def bw_res(b1, w1):
    pen_vec = b1.pos-bw_closest(b1, w1)
    if pen_vec.length() > 0:
        normal = pen_vec.normalize()
        sep_vel = b1.vel.dot(normal)
        new_sep_vel = -sep_vel*b1.elasticity
        sep_vel_diff = sep_vel-new_sep_vel
        b1.vel += normal*(-sep_vel_diff)

def key_control(dt, ball):
    keys = pygame.key.get_pressed()
    right, left, up, down = keys[pygame.K_RIGHT], keys[pygame.K_LEFT], keys[pygame.K_UP], keys[pygame.K_DOWN]
    if right:
        ball.acc.x = ball.accel
    if left:
        ball.acc.x = -ball.accel
    if up:
        ball.acc.y = -ball.accel
    if down:
        ball.acc.y = ball.accel
    
    if not right and not left:
        ball.acc.x = 0
    if not up and not down:
        ball.acc.y = 0

def draw_vec(pos, vec):
    pygame.draw.line(screen, "#ff0000", pos, vec, 2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    dt = clock.tick(fps)/1000*60
    screen.fill("#faf2cd")

    for i, ball in enumerate(balls):
        if ball.player:
            key_control(dt, ball)
        for wall in walls:
            if bw_col(ball, wall):
                bw_pen(ball, wall)
                bw_res(ball, wall)
        for other in balls[i+1:]:
            if bb_col(ball, other):
                bb_pen(ball, other)
                bb_res(ball, other)
        ball.draw(screen)
        ball.update(dt)

    for wall in walls:
        wall.draw(screen)

    # draw_vec(ball.pos, bw_closest(ball, wall))

    pygame.display.update()