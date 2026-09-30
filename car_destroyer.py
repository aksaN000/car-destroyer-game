from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ROAD_WIDTH = 600
LANE_COUNT = 5
TOTAL_LANES = LANE_COUNT * 2
CAR_WIDTH = 40
CAR_HEIGHT = 60
FPS = 60
FRAME_TIME = 1500 // FPS
SAFE_DISTANCE = CAR_HEIGHT * 1.2
BASE_TRAFFIC_DENSITY = 0.3
DIFFICULTY_INCREASE_INTERVAL = 1000
MAX_TRAFFIC_DENSITY = 0.6
BASE_CAR_SPEED = 2
MAX_CAR_SPEED = 8
BULLET_SPEED = 10
BULLET_SIZE = 5
EXPLOSION_DURATION = 15
EXPLOSION_PARTICLES = 15
BOSS_HEALTH = 10
BOSS_SPAWN_INTERVAL = 2
BOSS_SHOOT_INTERVAL = 30
BOSS_BULLET_SPEED = 8
STATE_MENU = 0
STATE_SINGLE_PLAYER = 1
STATE_MULTIPLAYER = 2
STATE_GAME_OVER = 3
STATE_PAUSED = 4


# Game states
STATE_MENU = 0
STATE_SINGLE_PLAYER = 1
STATE_MULTIPLAYER = 2
STATE_GAME_OVER = 3

def draw_line(x1, y1, x2, y2):
    """Midpoint line drawing algorithm"""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steep = dy > dx

    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = abs(y2 - y1)
    error = dx // 2
    y = y1
    y_step = 1 if y1 < y2 else -1

    glBegin(GL_POINTS)
    for x in range(x1, x2 + 1):
        glVertex2f(y, x) if steep else glVertex2f(x, y)
        error -= dy
        if error < 0:
            y += y_step
            error += dx
    glEnd()


def draw_circle(x_center, y_center, radius):
    """Midpoint circle drawing algorithm"""
    x = radius
    y = 0
    decision = 1 - radius

    glBegin(GL_POINTS)
    while x >= y:
        glVertex2f(x_center + x, y_center + y)
        glVertex2f(x_center - x, y_center + y)
        glVertex2f(x_center + x, y_center - y)
        glVertex2f(x_center - x, y_center - y)
        glVertex2f(x_center + y, y_center + x)
        glVertex2f(x_center - y, y_center + x)
        glVertex2f(x_center + y, y_center - x)
        glVertex2f(x_center - y, y_center - x)

        y += 1
        if decision <= 0:
            decision += 2 * y + 1
        else:
            x -= 1
            decision += 2 * (y - x) + 1
    glEnd()


class Bullet:
    def __init__(self, x, y, player_id=1, is_boss=False):
        self.x = x
        self.y = y
        self.speed = BOSS_BULLET_SPEED if is_boss else BULLET_SPEED
        self.is_boss = is_boss
        self.player_id = player_id  # 1 for red player, 2 for blue player

    def update(self):
        self.y += self.speed

    def draw(self):
        if self.is_boss:
            glColor3f(1.0, 0.5, 0.0)
        else:
            # Color bullets based on player
            if self.player_id == 1:
                glColor3f(1.0, 0.0, 0.0)  # Red
            else:
                glColor3f(0.0, 0.0, 1.0)  # Blue
        draw_circle(int(self.x), int(self.y), BULLET_SIZE)



class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 8)  # Increased speed range
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.lifetime = EXPLOSION_DURATION
        # Random color from a vibrant palette
        self.color = random.choice([
            (1.0, 0.3, 0.0),  # Orange
            (1.0, 0.0, 0.0),  # Red
            (1.0, 1.0, 0.0),  # Yellow
            (1.0, 0.5, 0.0),  # Light orange
            (0.8, 0.2, 0.0),  # Dark orange
        ])
        self.size = random.randint(2, 4)  # Random particle size

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.98  # Add slight deceleration
        self.dy *= 0.98
        self.lifetime -= 1

    def draw(self):
        alpha = self.lifetime / EXPLOSION_DURATION
        r, g, b = self.color
        glColor4f(r, g, b, alpha)
        # Draw larger particle using a small circle
        draw_circle(int(self.x), int(self.y), self.size)


class Car:
    def __init__(self, x, y, color, speed=0, direction=1, is_boss=False, is_player2=False):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.lane = LANE_COUNT - 1
        self.direction = direction
        self.health = BOSS_HEALTH if is_boss else 3
        self.explosion_particles = []
        self.is_boss = is_boss
        self.shoot_cooldown = 0
        self.is_player2 = is_player2
        self.score = 0
        self.is_exploded = False
        self.is_respawning = False
        self.respawn_timer = 0

    def hit(self):
        if self.is_exploded:
            return False

        self.health -= 1
        if self.health <= 0:
            self.is_exploded = True
            self.create_explosion()
            if self.is_boss:
                self.is_respawning = True
                self.respawn_timer = 120  # 2 seconds at 60 FPS
        return self.health <= 0

    def respawn(self):
        if not self.is_boss or not self.is_respawning:
            return False

        self.respawn_timer -= 1
        if self.respawn_timer <= 0:
            self.health = BOSS_HEALTH
            self.is_exploded = False
            self.is_respawning = False
            self.explosion_particles = []
            return True
        return False


    def create_explosion(self):
        self.explosion_particles = [ExplosionParticle(self.x, self.y)
                                  for _ in range(EXPLOSION_PARTICLES)]

    def draw(self):
        # Draw explosion particles if they exist
        for particle in self.explosion_particles[:]:
            particle.draw()
            particle.update()
            if particle.lifetime <= 0:
                self.explosion_particles.remove(particle)

        if self.health > 0:
            # Draw car body with boss modifications if it's a boss
            glColor3f(*self.color)
            x1 = int(self.x - CAR_WIDTH // 2)
            y1 = int(self.y - CAR_HEIGHT // 2)
            x2 = int(self.x + CAR_WIDTH // 2)
            y2 = int(self.y + CAR_HEIGHT // 2)

            # Draw car body
            draw_line(x1, y1, x2, y1)
            draw_line(x2, y1, x2, y2)
            draw_line(x2, y2, x1, y2)
            draw_line(x1, y2, x1, y1)

            # Draw windows
            glColor3f(0.7, 0.9, 1.0)
            window_height = CAR_HEIGHT // 4
            window_y = int(self.y + window_height // 2 if self.direction == 1
                           else self.y - window_height // 2)

            wx1 = int(self.x - CAR_WIDTH // 3)
            wx2 = int(self.x + CAR_WIDTH // 3)
            wy2 = window_y + window_height

            draw_line(wx1, window_y, wx2, window_y)
            draw_line(wx2, window_y, wx2, wy2)
            draw_line(wx2, wy2, wx1, wy2)
            draw_line(wx1, wy2, wx1, window_y)

            # Draw boss car modifications
            if self.is_boss:
                # Add extra width to boss car
                extra_width = 10
                glColor3f(*self.color)
                draw_line(x1 - extra_width, y1, x2 + extra_width, y1)
                draw_line(x2 + extra_width, y1, x2 + extra_width, y2)
                draw_line(x2 + extra_width, y2, x1 - extra_width, y2)
                draw_line(x1 - extra_width, y2, x1 - extra_width, y1)

            # Draw health bar with position based on direction
            health_ratio = self.health / (BOSS_HEALTH if self.is_boss else 3)
            health_width = int(CAR_WIDTH * health_ratio)
            if health_ratio > 0.6:
                glColor3f(0.0, 1.0, 0.0)
            elif health_ratio > 0.3:
                glColor3f(1.0, 0.85, 0.0)
            else:
                glColor3f(1.0, 0.2, 0.2)

            if self.direction == 1:  # Downward moving cars
                hx1 = int(self.x - CAR_WIDTH / 2)
                hy1 = int(self.y - CAR_HEIGHT / 2 - 8)
                hx2 = int(hx1 + health_width)
                hy2 = hy1 + 3
            else:  # Upward moving cars
                hx1 = int(self.x - CAR_WIDTH / 2)
                hy1 = int(self.y + CAR_HEIGHT / 2 + 5)
                hx2 = int(hx1 + health_width)
                hy2 = hy1 + 3

            draw_line(hx1, hy1, hx2, hy1)
            draw_line(hx2, hy1, hx2, hy2)
            draw_line(hx2, hy2, hx1, hy2)
            draw_line(hx1, hy2, hx1, hy1)

class Game:
    def __init__(self):
        self.lane_width = ROAD_WIDTH // TOTAL_LANES
        center_lane = LANE_COUNT - 1
        start_x = (WINDOW_WIDTH - ROAD_WIDTH) // 2 + (center_lane * self.lane_width) + (self.lane_width // 2)

        self.player = None
        self.player2 = None
        self.winner = None

        self.traffic_cars = []
        self.oncoming_cars = []
        self.bullets = []
        self.lane_offset = 0
        self.game_state = STATE_MENU
        self.last_update_time = time.time()
        self.last_boss_spawn = 0

        self.menu_options = ["Single Player", "Multiplayer"]
        self.selected_option = 0
        self.pause_options = ["Resume", "Restart", "Exit to Menu"]
        self.pause_selected = 0

        # Add control display timer
        self.show_controls = True
        self.control_timer = 180  # Show for 3 seconds (60 FPS * 3)

    def draw_pause_menu(self):
        # Draw semi-transparent overlay
        glColor4f(0.0, 0.0, 0.0, 0.5)
        draw_line(0, 0, WINDOW_WIDTH, 0)
        draw_line(WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        draw_line(WINDOW_WIDTH, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        draw_line(0, WINDOW_HEIGHT, 0, 0)

        # Draw PAUSED text
        glColor3f(1.0, 1.0, 1.0)
        pause_text = "PAUSED"
        text_width = len(pause_text) * 15
        x_pos = (WINDOW_WIDTH - text_width) // 2
        y_pos = WINDOW_HEIGHT // 2 + 50

        glRasterPos2f(x_pos, y_pos)
        for c in pause_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))

        # Draw pause menu options
        for i, option in enumerate(self.pause_options):
            if i == self.pause_selected:
                glColor3f(1, 1, 0)  # Yellow for selected option
            else:
                glColor3f(1, 1, 1)  # White for unselected options

            text_width = len(option) * 9
            x_pos = (WINDOW_WIDTH - text_width) // 2
            y_pos = WINDOW_HEIGHT // 2 - i * 30

            glRasterPos2f(x_pos, y_pos)
            for c in option:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))


    def get_current_difficulty(self):
        # Calculate difficulty based on highest player score
        max_score = max(self.player.score if self.player else 0,
                       self.player2.score if self.player2 else 0)
        difficulty_level = max_score // DIFFICULTY_INCREASE_INTERVAL

        # Calculate current traffic density
        traffic_density = min(
            BASE_TRAFFIC_DENSITY + (difficulty_level * 0.05),
            MAX_TRAFFIC_DENSITY
        )

        # Calculate speed range for new cars
        min_speed = BASE_CAR_SPEED + (difficulty_level * 0.5)
        max_speed = min(min_speed + 3, MAX_CAR_SPEED)

        return {
            'traffic_density': traffic_density * 0.7,  # Reduced for better performance
            'min_speed': min_speed,
            'max_speed': max_speed,
            'boss_shoot_interval': max(10, BOSS_SHOOT_INTERVAL - (difficulty_level * 0.5))
        }


    def get_lane_x(self, lane):
        road_left = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        return road_left + (lane * self.lane_width) + (self.lane_width // 2)

    def spawn_initial_traffic(self):
        colors = [(1, 1, 0), (0, 0.7, 1), (0, 0.8, 0.3), (0.8, 0, 0.8)]

        # Reduced initial traffic for better performance
        for _ in range(3):  # Reduced from 4
            lane = random.randint(0, LANE_COUNT - 1)
            x = self.get_lane_x(lane)
            y = WINDOW_HEIGHT + random.randint(100, 800)
            speed = random.uniform(2, 5)  # Reduced max speed
            car = Car(x, y, random.choice(colors), speed, 1)
            car.lane = lane
            self.traffic_cars.append(car)

        for _ in range(3):  # Reduced from 4
            lane = random.randint(LANE_COUNT, TOTAL_LANES - 1)
            x = self.get_lane_x(lane)
            y = random.randint(-800, -100)
            speed = random.uniform(2, 5)  # Reduced max speed
            car = Car(x, y, random.choice(colors), speed, -1)
            car.lane = lane
            self.oncoming_cars.append(car)

    def spawn_boss_car(self, is_traffic):
        """Fixed boss car spawning"""
        difficulty = self.get_current_difficulty()

        if is_traffic:
            lane = random.randint(0, LANE_COUNT - 1)
            x = self.get_lane_x(lane)
            y = WINDOW_HEIGHT + CAR_HEIGHT
            direction = 1
        else:
            lane = random.randint(LANE_COUNT, TOTAL_LANES - 1)
            x = self.get_lane_x(lane)
            y = -CAR_HEIGHT
            direction = -1

        # Make boss cars visually distinct
        color = (1.0, 0.0, 0.0)  # Bright red for boss cars
        speed = difficulty['min_speed'] * 0.75  # Boss cars move slower
        boss_car = Car(x, y, color, speed, direction, is_boss=True)
        boss_car.lane = lane
        boss_car.shoot_cooldown = 0
        boss_car.health = BOSS_HEALTH  # Ensure boss has full health

        if is_traffic:
            self.traffic_cars.append(boss_car)
        else:
            self.oncoming_cars.append(boss_car)

    def spawn_new_car(self, is_traffic):
        difficulty = self.get_current_difficulty()

        if is_traffic and len(self.traffic_cars) >= 10:
            return
        if not is_traffic and len(self.oncoming_cars) >= 10:
            return

        if is_traffic:
            lane = random.randint(0, LANE_COUNT - 1)
            x = self.get_lane_x(lane)
            y = WINDOW_HEIGHT + CAR_HEIGHT
            direction = 1
        else:
            lane = random.randint(LANE_COUNT, TOTAL_LANES - 1)
            x = self.get_lane_x(lane)
            y = -CAR_HEIGHT
            direction = -1

        color = (random.uniform(0.3, 1), random.uniform(0.3, 1), random.uniform(0.3, 1))
        speed = random.uniform(difficulty['min_speed'], difficulty['max_speed'])
        new_car = Car(x, y, color, speed, direction)
        new_car.lane = lane

        if is_traffic:
            self.traffic_cars.append(new_car)
        else:
            self.oncoming_cars.append(new_car)

    def check_collision(self, car1, car2):
        return (abs(car1.x - car2.x) < CAR_WIDTH * 0.8 and
                abs(car1.y - car2.y) < CAR_HEIGHT * 0.8)

    def draw_road(self):
        road_x = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        center_line_x = WINDOW_WIDTH // 2

        # Road surface
        glColor3f(0.3, 0.3, 0.3)
        for y in range(0, WINDOW_HEIGHT, 2):
            draw_line(road_x, y, road_x + ROAD_WIDTH, y)

        # Center line
        glColor3f(1, 1, 0)
        draw_line(center_line_x - 2, 0, center_line_x - 2, WINDOW_HEIGHT)
        draw_line(center_line_x + 2, 0, center_line_x + 2, WINDOW_HEIGHT)

        # Lane markers
        glColor3f(1, 1, 1)
        marker_height = 40
        marker_gap = 30
        offset = -self.lane_offset % (marker_height + marker_gap)

        for lane in range(1, TOTAL_LANES):
            if lane != LANE_COUNT:
                x = road_x + (lane * self.lane_width)
                for y in range(int(offset), WINDOW_HEIGHT, marker_height + marker_gap):
                    draw_line(x - 1, y, x - 1, y + marker_height)
                    draw_line(x + 1, y, x + 1, y + marker_height)

    def start_game(self, multiplayer=False):
        center_lane = LANE_COUNT - 1
        start_x = (WINDOW_WIDTH - ROAD_WIDTH) // 2 + (center_lane * self.lane_width) + (self.lane_width // 2)

        self.player = Car(start_x, WINDOW_HEIGHT // 4, (1, 0, 0))
        self.player.lane = center_lane
        self.player.score = 0

        if multiplayer:
            self.player2 = Car(start_x, WINDOW_HEIGHT // 4 - CAR_HEIGHT * 2, (0, 0, 1), is_player2=True)
            self.player2.lane = center_lane
            self.player2.score = 0
            self.game_state = STATE_MULTIPLAYER
        else:
            self.player2 = None
            self.game_state = STATE_SINGLE_PLAYER

        self.traffic_cars = []
        self.oncoming_cars = []
        self.bullets = []
        self.lane_offset = 0
        self.last_boss_spawn = 0
        self.winner = None
        self.spawn_initial_traffic()

        # Reset control display
        self.show_controls = True
        self.control_timer = 180

    def draw_menu(self):
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw title
        glColor3f(1, 1, 1)
        title = "CAR DESTROYER"
        glRasterPos2f(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100)
        for c in title:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))

        # Draw menu options
        for i, option in enumerate(self.menu_options):
            if i == self.selected_option:
                glColor3f(1, 1, 0)  # Yellow for selected option
            else:
                glColor3f(1, 1, 1)  # White for unselected options

            glRasterPos2f(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - i * 30)
            for c in option:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        glutSwapBuffers()

    def check_game_over(self):
        """Determine game over state and set winner in multiplayer mode"""
        if self.game_state == STATE_MULTIPLAYER:
            if not self.player.health and not self.player2.health:
                # Determine winner before changing state
                if self.player.score > self.player2.score:
                    self.winner = "Red"
                elif self.player2.score > self.player.score:
                    self.winner = "Blue"
                else:
                    self.winner = "Tie"
                self.game_state = STATE_GAME_OVER
                return True
        elif self.game_state == STATE_SINGLE_PLAYER:
            if not self.player.health:
                self.game_state = STATE_GAME_OVER
                return True
        return False

    def draw_game_over(self):
        """Draw game over screen with proper multiplayer scoring"""
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw_road()

        # Background overlay
        glColor3f(0.0, 0.0, 0.0)
        draw_line(0, 0, WINDOW_WIDTH, 0)
        draw_line(WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        draw_line(WINDOW_WIDTH, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        draw_line(0, WINDOW_HEIGHT, 0, 0)

        # Game Over text
        glColor3f(1.0, 0.0, 0.0)
        main_text = "Game Over!"
        x_pos = (WINDOW_WIDTH - len(main_text) * 15) // 2
        glRasterPos2f(x_pos, WINDOW_HEIGHT // 2 + 60)
        for c in main_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))

        # Multiplayer specific display
        if self.game_state == STATE_GAME_OVER and self.player2 is not None:
            glColor3f(1.0, 1.0, 1.0)
            # Player 1 score
            score1_text = f"Red Player: {self.player.score}"
            x_pos = (WINDOW_WIDTH - len(score1_text) * 10) // 2
            glRasterPos2f(x_pos, WINDOW_HEIGHT // 2)
            for c in score1_text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

            # Player 2 score
            score2_text = f"Blue Player: {self.player2.score}"
            x_pos = (WINDOW_WIDTH - len(score2_text) * 10) // 2
            glRasterPos2f(x_pos, WINDOW_HEIGHT // 2 - 30)
            for c in score2_text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

            # Winner announcement
            if self.winner == "Red":
                glColor3f(1.0, 0.0, 0.0)
                winner_text = "Red Player Wins!"
            elif self.winner == "Blue":
                glColor3f(0.0, 0.0, 1.0)
                winner_text = "Blue Player Wins!"
            else:
                glColor3f(1.0, 1.0, 0.0)
                winner_text = "It's a Tie!"

            x_pos = (WINDOW_WIDTH - len(winner_text) * 10) // 2
            glRasterPos2f(x_pos, WINDOW_HEIGHT // 2 - 60)
            for c in winner_text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
        else:
            # Single player score
            glColor3f(1.0, 1.0, 1.0)
            score_text = f"Final Score: {self.player.score}"
            x_pos = (WINDOW_WIDTH - len(score_text) * 10) // 2
            glRasterPos2f(x_pos, WINDOW_HEIGHT // 2 - 20)
            for c in score_text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        # Continue prompt
        glColor3f(1.0, 1.0, 1.0)
        continue_text = "Press ENTER to return to menu"
        x_pos = (WINDOW_WIDTH - len(continue_text) * 10) // 2
        glRasterPos2f(x_pos, WINDOW_HEIGHT // 2 - 100)
        for c in continue_text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        glutSwapBuffers()

    def draw_controls(self):
        if not self.show_controls:
            return

        # Semi-transparent overlay
        glColor4f(0.0, 0.0, 0.0, 0.7)
        draw_line(0, 0, WINDOW_WIDTH, 0)
        draw_line(WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        draw_line(WINDOW_WIDTH, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        draw_line(0, WINDOW_HEIGHT, 0, 0)

        glColor3f(1.0, 1.0, 1.0)
        controls = [
            "Player 1 Controls:",
            "WASD - Move",
            "SPACE - Shoot",
            "P - Pause"
        ]

        if self.game_state == STATE_MULTIPLAYER:
            controls.extend([
                "",
                "Player 2 Controls:",
                "Arrow Keys - Move",
                "END - Shoot"
            ])

        y_pos = WINDOW_HEIGHT // 2 + 100
        for line in controls:
            x_pos = (WINDOW_WIDTH - len(line) * 9) // 2
            glRasterPos2f(x_pos, y_pos)
            for c in line:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
            y_pos -= 30

        # Press any key message
        any_key = "Press any key to start"
        x_pos = (WINDOW_WIDTH - len(any_key) * 9) // 2
        glRasterPos2f(x_pos, y_pos - 30)
        for c in any_key:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    def update(self):
        if self.show_controls:
            self.control_timer -= 1
            if self.control_timer <= 0:
                self.show_controls = False
        if self.game_state in [STATE_MENU, STATE_PAUSED, STATE_GAME_OVER]:
            return
        if self.game_state == STATE_MENU:
            return

        # Check for game over first
        if self.check_game_over():
            return

        # Get list of active players
        active_players = [self.player]
        if self.player2 and self.player2.health > 0:
            active_players.append(self.player2)

        # Boss spawning logic
        max_score = max(self.player.score, self.player2.score if self.player2 else 0)
        if max_score - self.last_boss_spawn >= BOSS_SPAWN_INTERVAL * 100:  # Multiply by 100 since score increments by 1
            self.spawn_boss_car(random.choice([True, False]))
            self.last_boss_spawn = max_score

        # Update bullets in a single pass
        self.bullets = [bullet for bullet in self.bullets if bullet.y <= WINDOW_HEIGHT and bullet.y >= 0]

        # Limit max bullets for performance
        if len(self.bullets) > 20:
            self.bullets = self.bullets[-20:]  # Keep only most recent bullets

        for bullet in self.bullets[:]:
            bullet.update()

            if bullet.is_boss:
                # Boss bullets check against players only
                for player in active_players:
                    if (abs(bullet.x - player.x) < CAR_WIDTH / 2 and
                            abs(bullet.y - player.y) < CAR_HEIGHT / 2):
                        player.health -= 1
                        self.bullets.remove(bullet)
                        break
            else:
                # Player bullets check against cars only
                # Use simplified collision check for performance
                for car in self.traffic_cars + self.oncoming_cars:
                    if not car.is_exploded and car.health > 0:
                        if (abs(bullet.x - car.x) < CAR_WIDTH / 2 and
                                abs(bullet.y - car.y) < CAR_HEIGHT / 2):
                            if car.hit():
                                score = 1000 if car.is_boss else 150
                                if bullet.player_id == 1:
                                    self.player.score += score
                                else:
                                    self.player2.score += score
                            self.bullets.remove(bullet)
                            break

        # Optimize car updates
        max_cars = 8  # maximum cars for performance

        # Update traffic cars
        self.traffic_cars = [car for car in self.traffic_cars if car.y >= -CAR_HEIGHT]
        for car in self.traffic_cars:
            car.y -= car.speed
            if car.health > 0:
                for player in active_players:
                    if self.check_collision(player, car):
                        player.health = 0

        # Update oncoming cars
        self.oncoming_cars = [car for car in self.oncoming_cars if car.y <= WINDOW_HEIGHT + CAR_HEIGHT]
        for car in self.oncoming_cars:
            car.y += car.speed
            if car.health > 0:
                for player in active_players:
                    if self.check_collision(player, car):
                        player.health = 0

        # Update boss cars efficiently
        for car in self.traffic_cars + self.oncoming_cars:
            if car.is_boss and car.health > 0:
                car.shoot_cooldown -= 1
                if car.shoot_cooldown <= 0:
                    # Find closest player
                    closest_player = min(active_players,
                                         key=lambda p: abs(car.x - p.x) + abs(car.y - p.y),
                                         default=None)
                    if closest_player:
                        # Shoot at closest player
                        if len(self.bullets) < 20:  # Limit boss bullets
                            bullet = Bullet(car.x, car.y, is_boss=True)
                            bullet.speed = BOSS_BULLET_SPEED if closest_player.y > car.y else -BOSS_BULLET_SPEED
                            self.bullets.append(bullet)
                            car.shoot_cooldown = BOSS_SHOOT_INTERVAL

        # Handle boss respawning
        for car in self.traffic_cars + self.oncoming_cars:
            if car.is_boss and car.is_respawning:
                if car.respawn():
                    # Reset boss position when respawning
                    if car in self.traffic_cars:
                        car.y = WINDOW_HEIGHT + CAR_HEIGHT
                    else:
                        car.y = -CAR_HEIGHT

        # Spawn new cars only when needed and ensure boss cars remain
        difficulty = self.get_current_difficulty()

        if len(self.traffic_cars) < max_cars and random.random() < difficulty['traffic_density']:
            self.spawn_new_car(True)
        if len(self.oncoming_cars) < max_cars and random.random() < difficulty['traffic_density']:
            self.spawn_new_car(False)

        # Update scores
        if self.game_state == STATE_MULTIPLAYER:
            if self.player.health > 0:
                self.player.score += 1
            if self.player2 and self.player2.health > 0:
                self.player2.score += 1
        else:
            if self.player.health > 0:
                self.player.score += 1

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)

        if self.game_state == STATE_MENU:
            self.draw_menu()
            return

        if self.game_state == STATE_GAME_OVER:
            self.draw_game_over()
            return

        # Draw game state
        self.draw_road()

        # Draw all game objects
        all_cars = self.traffic_cars + self.oncoming_cars + [self.player]
        if self.player2:
            all_cars.append(self.player2)

        for car in sorted(all_cars, key=lambda x: x.y):
            car.draw()

        for bullet in self.bullets:
            bullet.draw()

        # Draw scores
        glColor3f(1, 1, 1)
        difficulty_level = max(self.player.score,
                             self.player2.score if self.player2 else 0) // DIFFICULTY_INCREASE_INTERVAL

        if self.game_state == STATE_MULTIPLAYER:
            glRasterPos2f(10, WINDOW_HEIGHT - 20)
            score_text = f"P1 Score: {self.player.score} | P2 Score: {self.player2.score} | Level: {difficulty_level + 1}"
        else:
            glRasterPos2f(10, WINDOW_HEIGHT - 20)
            score_text = f"Score: {self.player.score} | Level: {difficulty_level + 1}"

        for c in score_text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        if self.game_state == STATE_PAUSED:
            self.draw_pause_menu()
        elif self.show_controls:
            self.draw_controls()

        glutSwapBuffers()

    def keyboard(self, key, x, y):
        if self.show_controls:
            self.show_controls = False
            self.control_timer = 0
            return
        if key == b'p':  # Press 'P' to pause/unpause
            if self.game_state in [STATE_SINGLE_PLAYER, STATE_MULTIPLAYER]:
                self.game_state = STATE_PAUSED
            elif self.game_state == STATE_PAUSED:
                self.game_state = STATE_SINGLE_PLAYER if self.player2 is None else STATE_MULTIPLAYER
            return

        if self.game_state == STATE_PAUSED:
            if key == b'\r':  # Enter key
                if self.pause_selected == 0:  # Resume
                    self.game_state = STATE_SINGLE_PLAYER if self.player2 is None else STATE_MULTIPLAYER
                elif self.pause_selected == 1:  # Restart
                    self.start_game(multiplayer=(self.player2 is not None))
                else:  # Exit to menu
                    self.game_state = STATE_MENU
            elif key in (b'w', b's'):
                self.pause_selected = (self.pause_selected + 1) % len(self.pause_options)
            return

        # Handle other existing keyboard inputs
        if self.game_state == STATE_MENU:
            if key == b'\r':  # Enter key
                self.start_game(multiplayer=(self.selected_option == 1))
            elif key in (b'w', b's'):
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            return

        if self.game_state == STATE_GAME_OVER:
            if key == b'\r':  # Enter key
                self.game_state = STATE_MENU
                return

        if self.game_state in [STATE_SINGLE_PLAYER, STATE_MULTIPLAYER]:
            if key == b'a' and self.player.lane > 0:
                self.player.lane -= 1
                self.player.x = self.get_lane_x(self.player.lane)
            elif key == b'd' and self.player.lane < TOTAL_LANES - 1:
                self.player.lane += 1
                self.player.x = self.get_lane_x(self.player.lane)
            elif key == b'w' and self.player.y < WINDOW_HEIGHT - CAR_HEIGHT:
                self.player.y += 12
            elif key == b's' and self.player.y > 0:
                self.player.y -= 12
            elif key == b' ':  # Space bar to shoot
                bullet = Bullet(self.player.x, self.player.y + CAR_HEIGHT // 2, player_id=1)
                self.bullets.append(bullet)

    def special_keys(self, key, x, y):
        if self.game_state == STATE_MULTIPLAYER and self.player2:
            # Player 2 controls (Arrow keys + End)
            if key == GLUT_KEY_LEFT and self.player2.lane > 0:
                self.player2.lane -= 1
                self.player2.x = self.get_lane_x(self.player2.lane)
            elif key == GLUT_KEY_RIGHT and self.player2.lane < TOTAL_LANES - 1:
                self.player2.lane += 1
                self.player2.x = self.get_lane_x(self.player2.lane)
            elif key == GLUT_KEY_UP and self.player2.y < WINDOW_HEIGHT - CAR_HEIGHT:
                self.player2.y += 12
            elif key == GLUT_KEY_DOWN and self.player2.y > 0:
                self.player2.y -= 12
            elif key == GLUT_KEY_END:  # END to shoot
                bullet = Bullet(self.player2.x, self.player2.y + CAR_HEIGHT // 2, player_id=2)
                self.bullets.append(bullet)


def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def timer(value):
    current_time = time.time()
    game.update()
    glutPostRedisplay()
    # Maintain consistent frame rate
    next_frame = max(0, FRAME_TIME - int((time.time() - current_time) * 1000))
    glutTimerFunc(next_frame, timer, 0)

def main():
    global game

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Car Destroyer")

    init()
    game = Game()

    glutDisplayFunc(game.display)
    glutKeyboardFunc(game.keyboard)
    glutSpecialFunc(game.special_keys)
    glutTimerFunc(0, timer, 0)

    glutMainLoop()

if __name__ == "__main__":
    main()

