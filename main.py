import pygame
import sys

screen_w = 800
screen_h = 600
screen = pygame.display.set_mode((screen_w, screen_h))

clock = pygame.time.Clock()

fps = 60
dt = 1

friction = 0.2

balls = []
walls = []

class Ball:
    def __init__(self, x, y, r, m, elasticity=1, player=False):
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
        self.accel = 4
        self.player = player
    
    def draw(self, screen):
        pygame.draw.circle(screen, "#ff0000", (self.pos.x, self.pos.y), self.r)

    def update(self, dt):
        if self.acc.length() > 0:
            self.acc = self.acc.normalize()*self.accel*dt

        self.vel += self.acc*dt
        self.vel -= self.vel*friction*dt

        self.pos += self.vel*dt

class Wall:
    def __init__(self, start_x, start_y, end_x, end_y):
        walls.append(self)
        self.start = pygame.Vector2(start_x, start_y)
        self.end = pygame.Vector2(end_x, end_y)

    def draw(self, screen):
        pygame.draw.line(screen, "#000000", self.start, self.end, 4)

# Ball(200, 200, 100, 10)
Ball(100, 300, 40, 4, player=True)

Wall(300, 100, 500, 500)

def bb_col(a, b):
    dist = pygame.Vector2(a.pos-b.pos)
    if a.r+b.r >= dist.length():
        return True
    return False

def bb_pen(a, b):
    dist = pygame.Vector2(a.pos-b.pos)
    depth = a.r+b.r-dist.length()
    res = pygame.Vector2(0, 0)
    if dist.length() > 0:
        res = dist.normalize()*(depth/(a.inv_m+b.inv_m))
    a.pos += res*a.inv_m
    b.pos -= res*b.inv_m

def bb_res(a, b):
    dist = pygame.Vector2(a.pos-b.pos)
    normal = pygame.Vector2(0, 0)
    if dist.length() > 0:
        normal = dist.normalize()
    rel_vel = a.vel-b.vel
    sep_vel = rel_vel.dot(normal)
    new_sep_vel = -sep_vel*min(a.elasticity, b.elasticity)
    
    sep_vel_diff = new_sep_vel-sep_vel
    impulse = sep_vel_diff/(a.inv_m+b.inv_m)
    impulse_vec = normal*impulse

    a.vel += impulse_vec*a.inv_m
    b.vel -= impulse_vec*b.inv_m

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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    dt = clock.tick(fps)/1000*60
    screen.fill("#ffffff")

    for i, ball in enumerate(balls):
        if ball.player:
            key_control(dt, ball)
        for other in balls[i+1:]:
            if bb_col(ball, other):
                bb_pen(ball, other)
                bb_res(ball, other)
        ball.update(dt)
        ball.draw(screen)

    for wall in walls:
        wall.draw(screen)

    pygame.display.update()