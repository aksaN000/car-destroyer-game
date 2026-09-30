from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import sys
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

#Shooter properties
shooter_x = 400
shooter_y = 50
shooter_width = 50
shooter_height = 10
shooter_speed = 300

#Bullet properties
bullets = []
bullet_speed = 500

#Circle properties
circles = []
circle_radius = 20
circle_base_speed = 100
bonus_circle_prob = 0.12
expanding_circles = []

#Game state
score = 0
missed_circles = 0
game_over = False
paused = False

#Timing
last_frame_time = time.time()

#Button properties
button_width = 40
button_height = 40
button_gap = 20
buttons = [
    {"label": "<-", "x": WINDOW_WIDTH - 3 * (button_width + button_gap), "y": WINDOW_HEIGHT - button_height - 10, "action": "restart", "color": (1, 1, 1)},
    {"label": "||", "x": WINDOW_WIDTH - 2 * (button_width + button_gap), "y": WINDOW_HEIGHT - button_height - 10, "action": "toggle_pause", "color": (1, 1, 1)},
    {"label": "X", "x": WINDOW_WIDTH - (button_width + button_gap), "y": WINDOW_HEIGHT - button_height - 10, "action": "exit", "color": (1, 1, 1)},
]

def draw_button_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def midpoint_line(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    glBegin(GL_POINTS)
    while True:
        glVertex2f(x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    glEnd()

def midpoint_circle(xc, yc, r):
    x, y = 0, r
    p = 1 - r
    plot_circle_points(xc, yc, x, y)
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        plot_circle_points(xc, yc, x, y)

def plot_circle_points(xc, yc, x, y):
    glBegin(GL_POINTS)
    points = [
        (xc + x, yc + y), (xc - x, yc + y),
        (xc + x, yc - y), (xc - x, yc - y),
        (xc + y, yc + x), (xc - y, yc + x),
        (xc + y, yc - x), (xc - y, yc - x)
    ]
    for px, py in points:
        glVertex2f(px, py)
    glEnd()

def draw_shooter():
    glColor3f(1, 0, 0)
    midpoint_line(shooter_x, shooter_y, shooter_x + shooter_width, shooter_y)
    midpoint_line(shooter_x + shooter_width, shooter_y, shooter_x + shooter_width, shooter_y + shooter_height)
    midpoint_line(shooter_x + shooter_width, shooter_y + shooter_height, shooter_x, shooter_y + shooter_height)
    midpoint_line(shooter_x, shooter_y + shooter_height, shooter_x, shooter_y)

def draw_bullets():
    glColor3f(1, 1, 0)
    glBegin(GL_POINTS)
    for bullet in bullets:
        glVertex2f(bullet[0], bullet[1])
    glEnd()

def draw_circles():
    for circle in circles:
        if circle.get("bonus"):
            glColor3f(0, 0, 1)
        else:
            glColor3f(1, 1, 1)
        midpoint_circle(circle["x"], circle["y"], circle["radius"])

def update_expanding_circles():
    global expanding_circles
    for circle in expanding_circles:
        if circle["growing"]:
            circle["radius"] += 0.5
            if circle["radius"] >= 30:
                circle["growing"] = False
        else:
            circle["radius"] -= 0.5
            if circle["radius"] <= 15:
                circle["growing"] = True

    for circle in circles:
        if circle.get("bonus"):
            matching_bonus = next((c for c in expanding_circles if c["x"] == circle["x"] and c["y"] == circle["y"]), None)
            if matching_bonus:
                circle["radius"] = matching_bonus["radius"]

def draw_score():
    glColor3f(1, 1, 1)
    glRasterPos2f(10, WINDOW_HEIGHT - 30)
    score_text = f"Score: {score}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def restart_game():
    global shooter_x, bullets, circles, score, missed_circles, game_over, expanding_circles, circle_base_speed
    shooter_x = 400
    bullets.clear()
    circles.clear()
    expanding_circles.clear()
    score = 0
    missed_circles = 0
    circle_base_speed = 100
    game_over = False
    print("Game restarted successfully.")

def update_positions(delta_time):
    global bullets, circles, score, missed_circles, game_over, circle_base_speed
    if paused:
        return

    circle_speed = circle_base_speed + (score * 5)

    bullets = [(x, y + bullet_speed * delta_time) for x, y in bullets if y < WINDOW_HEIGHT]
    new_circles = []
    for circle in circles:
        circle["y"] -= circle_speed * delta_time
        if circle["y"] < 0:
            missed_circles += 1
            if missed_circles >= 3:
                game_over = True
        elif (
            shooter_x - circle["radius"] <= circle["x"] <= shooter_x + shooter_width + circle["radius"] and
            shooter_y - circle["radius"] <= circle["y"] <= shooter_y + shooter_height + circle["radius"]
        ):
            game_over = True
        else:
            new_circles.append(circle)
    circles = new_circles
    check_collisions()

def check_collisions():
    global bullets, circles, score
    new_bullets = []
    new_circles = []
    for circle in circles:
        hit = False
        for bullet in bullets:
            if (bullet[0] - circle["x"])**2 + (bullet[1] - circle["y"])**2 <= circle["radius"]**2:
                score += 5 if circle.get("bonus") else 1
                print(f"Score: {score}")
                hit = True
                break
        if not hit:
            new_circles.append(circle)
        else:
            bullets.remove(bullet)
    circles = new_circles

def spawn_circle():
    global circles, expanding_circles
    x = random.randint(circle_radius, WINDOW_WIDTH - circle_radius)
    y = WINDOW_HEIGHT
    bonus = random.random() < bonus_circle_prob
    for circle in circles:
        if (x - circle["x"])**2 + (y - circle["y"])**2 < (2 * circle_radius)**2:
            return
    new_circle = {"x": x, "y": y, "radius": circle_radius, "bonus": bonus}
    if bonus:
        new_circle["growing"] = True
        expanding_circles.append(new_circle)
    circles.append(new_circle)

def display():
    global game_over
    glClear(GL_COLOR_BUFFER_BIT)
    if game_over:
        draw_game_over()
    else:
        draw_shooter()
        draw_bullets()
        draw_circles()
        draw_score()
    draw_buttons()
    glutSwapBuffers()

def keyboard(key, x, y):
    global shooter_x, bullets, paused, game_over

    if game_over:
        if key == b'r':
            print("Restarting game...")
            restart_game()
        elif key == b'q':
            print("Exiting game...")
            glutLeaveMainLoop()
        return

    if key == b'a' and shooter_x > 0:
        shooter_x -= shooter_speed * (5 / 60)
    elif key == b'd' and shooter_x + shooter_width < WINDOW_WIDTH:
        shooter_x += shooter_speed * (5/ 60)
    elif key == b' ':
        bullets.append((shooter_x + shooter_width // 2, shooter_y + shooter_height))
    elif key == b'p':
        paused = not paused
    elif key == b'x':
        print("Exiting game...")
        glutLeaveMainLoop()

def mouse(button, state, x, y):
    global paused, game_over
    y = WINDOW_HEIGHT - y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        for btn in buttons:
            if (
                btn["x"] <= x <= btn["x"] + button_width and
                btn["y"] <= y <= btn["y"] + button_height
            ):
                if btn["action"] == "restart":
                    restart_game()
                elif btn["action"] == "toggle_pause":
                    paused = not paused
                elif btn["action"] == "exit":
                    print("Goodbye")
                    glutLeaveMainLoop()

def draw_game_over():

    glColor3f(1, 1, 1)
    glRasterPos2f(300, 300)
    for char in "GAME OVER!":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glRasterPos2f(300, 250)
    for char in f"Your Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glRasterPos2f(300, 200)
    for char in "Press 'R' to Restart or 'Q' to Quit":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_buttons():
    for button in buttons:
        glColor3f(1, 1, 1)
        midpoint_line(button["x"], button["y"], button["x"] + button_width, button["y"])
        midpoint_line(button["x"], button["y"], button["x"], button["y"] + button_height)
        midpoint_line(button["x"], button["y"] + button_height, button["x"] + button_width, button["y"] + button_height)
        midpoint_line(button["x"] + button_width, button["y"], button["x"] + button_width, button["y"] + button_height)
        glColor3f(0, 1, 0)
        draw_button_text(button["x"] + 12, button["y"] + 15, button["label"])

def timer(value):
    global last_frame_time
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time

    if not paused and not game_over:
        update_positions(delta_time)
        update_expanding_circles()
        if random.random() < 0.01:  #Adjusting spawn rate
            spawn_circle()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  #60 FPS

def init():
    glClearColor(0, 0, 0, 1)
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutCreateWindow(b"Circle Shooting")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutTimerFunc(16, timer, 0)
glutMainLoop()
