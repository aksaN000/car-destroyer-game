from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

###############               TASK 1        ##################
width, height = 1200, 800
num_raindrops = 100
raindrops = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_raindrops)]
rain_dx = 0
rain_speed = 5
bend_factor = 2

bg_r, bg_g, bg_b = 0.0, 0.0, 0.2
color_step = 0.01

def draw_house():
    house_color = (1.0 - bg_r, 1.0 - bg_g, 1.0 - bg_b)
    glColor3f(*house_color)

    #House_boundary
    glBegin(GL_LINES)
    glVertex2f(300, 200)
    glVertex2f(500, 200)
    glVertex2f(300, 200)
    glVertex2f(300, 400)
    glVertex2f(500, 200)
    glVertex2f(500, 400)
    glVertex2f(300, 400)
    glVertex2f(500, 400)
    glEnd()

    #Roof
    glColor3f(house_color[0] * 0.8, house_color[1] * 0.4, house_color[2] * 0.4)
    glBegin(GL_TRIANGLES)
    glVertex2f(300, 400)
    glVertex2f(500, 400)
    glVertex2f(400, 500)
    glEnd()

    #Door
    glColor3f(0.5, 0.35, 0.05)
    glBegin(GL_LINES)
    glVertex2f(375, 200)
    glVertex2f(375, 300)
    glVertex2f(425, 200)
    glVertex2f(425, 300)
    glVertex2f(375, 300)
    glVertex2f(425, 300)
    glEnd()

    # Windows
    glColor3f(*house_color)
    glBegin(GL_LINES)
    # Left window
    glVertex2f(320, 320)
    glVertex2f(360, 320)
    glVertex2f(320, 280)
    glVertex2f(360, 280)
    glVertex2f(320, 280)
    glVertex2f(320, 320)
    glVertex2f(360, 280)
    glVertex2f(360, 320)
    # Right window
    glVertex2f(440, 320)
    glVertex2f(480, 320)
    glVertex2f(440, 280)
    glVertex2f(480, 280)
    glVertex2f(440, 280)
    glVertex2f(440, 320)
    glVertex2f(480, 280)
    glVertex2f(480, 320)
    glEnd()

def draw_raindrops():
    rain_color = (0.0, 0.0, 1.0 if bg_b > 0.5 else 0.8)  #Blue rain for night, lighter for day
    glColor3f(*rain_color)
    glBegin(GL_LINES)
    for x, y in raindrops:
        glVertex2f(x, y) #Top of raindrop
        glVertex2f(x + rain_dx * 0.1, y - 10) #Bottom of raindrop (slightly bent)
    glEnd()

def update_raindrops():
    global raindrops
    raindrops = [((x + rain_dx) % width, y - rain_speed if y > 0 else height) for x, y in raindrops]
    glutPostRedisplay()

def timer(value):
    update_raindrops()
    glutTimerFunc(33, timer, 0)

def Special_key(key, x, y):
    global rain_dx, bg_r, bg_g, bg_b
    #arrows to bend
    if key == GLUT_KEY_LEFT:
        rain_dx -= bend_factor
    elif key == GLUT_KEY_RIGHT:
        rain_dx += bend_factor

def normal_keys(key, x, y):
    global bg_r, bg_g, bg_b
    if key == b'n': # N = Night to day
        bg_r = min(bg_r + color_step, 0.5)
        bg_g = min(bg_g + color_step, 0.7)
        bg_b = max(bg_b - color_step, 0.8)
    elif key == b'd': # D = Day to night
        bg_r = max(bg_r - color_step, 0.0)
        bg_g = max(bg_g - color_step, 0.0)
        bg_b = min(bg_b + color_step, 0.2)

def display():
    glClearColor(bg_r, bg_g, bg_b, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    draw_house()
    draw_raindrops()
    glutSwapBuffers()

def init():
    glClearColor(bg_r, bg_g, bg_b, 1.0)
    gluOrtho2D(0, width, 0, height)


glutInit()
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"House with Raindrops")
init()
glutDisplayFunc(display)
glutSpecialFunc(Special_key)
glutKeyboardFunc(normal_keys)
glutTimerFunc(0, timer, 0)
glutMainLoop()

###############               TASK 2        ##################


width, height = 800, 600
points = []  #[(x, y, dx, dy, r, g, b, blink_state),...]
speed = 1.0
blink = False
frozen = False
last_blink_time = time.time()

def create_point(x, y):
    dx = random.choice([-1, 1])
    dy = random.choice([-1, 1])
    r, g, b = random.random(), random.random(), random.random()
    points.append([x, y, dx, dy, r, g, b, True])

def draw_points():
    for point in points:
        x, y, dx, dy, r, g, b, visible = point
        if visible:
            glColor3f(r, g, b)
        else:
            glColor3f(0.0, 0.0, 0.0)
        glPointSize(10)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()

def update_points():
    if frozen:
        return
    for point in points:
        point[0] += point[2] * speed
        point[1] += point[3] * speed
        #Bounce_back
        if point[0] <= 0 or point[0] >= width:
            point[2] = -point[2]
        if point[1] <= 0 or point[1] >= height:
            point[3] = -point[3]

def blink_points():
    global last_blink_time
    if frozen or not blink:
        return
    current_time = time.time()
    if current_time - last_blink_time >= 0.5:
        for point in points:
            point[7] = not point[7]
        last_blink_time = current_time

def keyboard(key, x, y):
    global speed, frozen, blink
    if key == b' ':
        frozen = not frozen
    elif not frozen:
        if key == b'\x1b':
            glutLeaveMainLoop()

def special_input(key, x, y):
    global speed
    if not frozen:
        if key == GLUT_KEY_UP:
            speed += 0.5
        elif key == GLUT_KEY_DOWN:
            speed = max(0.5, speed - 0.5)

def mouse(button, state, x, y):
    global blink
    if state == GLUT_DOWN and not frozen:
        if button == GLUT_RIGHT_BUTTON:
            create_point(x, height - y)
        elif button == GLUT_LEFT_BUTTON:
            blink = not blink

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_points()
    glutSwapBuffers()

def timer(value):
    update_points()
    blink_points()
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, width, 0, height)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"World of Points")
init()
glutDisplayFunc(display)
glutMouseFunc(mouse)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_input)
glutTimerFunc(0, timer, 0)
glutMainLoop()