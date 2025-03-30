import pygame
import sys
import random
import time
import os
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 600
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Sorting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
LIGHT_BLUE = (173, 216, 230)

# Define levels
LEVELS = [
    {"colors": [RED, BLUE, YELLOW], "balls_per_color": 2, "compartments": 4, "move_limit": None},
    {"colors": [RED, BLUE, YELLOW, PURPLE], "balls_per_color": 2, "compartments": 5, "move_limit": None},
    {"colors": [RED, BLUE, YELLOW, PURPLE], "balls_per_color": 3, "compartments": 5, "move_limit": None},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE], "balls_per_color": 3, "compartments": 6, "move_limit": 30},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN], "balls_per_color": 4, "compartments": 7, "move_limit": 40},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN], "balls_per_color": 4, "compartments": 8, "move_limit": 45},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN, LIGHT_BLUE], "balls_per_color": 4, "compartments": 9, "move_limit": 50},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN, LIGHT_BLUE, GRAY], "balls_per_color": 4, "compartments": 10, "move_limit": 55},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN, LIGHT_BLUE, GRAY, BLACK], "balls_per_color": 4, "compartments": 11, "move_limit": 60},
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN, LIGHT_BLUE, GRAY, BLACK], "balls_per_color": 5, "compartments": 12, "move_limit": 70},
]

# Load assets
BASE_PATH = r"C:\Users\me\Documents\python"
BACKGROUND = pygame.image.load(os.path.join(BASE_PATH, "background.png")) if os.path.exists(os.path.join(BASE_PATH, "background.png")) else None
if BACKGROUND:
    BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))
LOGO = pygame.image.load(os.path.join(BASE_PATH, "super_seed_logo.png")) if os.path.exists(os.path.join(BASE_PATH, "super_seed_logo.png")) else None
if LOGO:
    LOGO = pygame.transform.scale(LOGO, (200, 50))

# Game settings
COMPARTMENT_SIZE = 80
BALL_RADIUS = 15
BALL_SIZE = (BALL_RADIUS * 2, BALL_RADIUS * 2)  # Size for scaling images (30x30 pixels)
TIME_LIMIT = 180

# Load ball images
BALL_IMAGES = {}
color_to_filename = {
    RED: "red_ball.png",
    BLUE: "blue_ball.png",
    YELLOW: "yellow_ball.png",
    PURPLE: "purple_ball.png",
    ORANGE: "orange_ball.png",
    CYAN: "cyan_ball.png",
    GREEN: "green_ball.png",
    LIGHT_BLUE: "light_blue_ball.png",
    GRAY: "gray_ball.png",
    BLACK: "black_ball.png",
}

for color, filename in color_to_filename.items():
    file_path = os.path.join(BASE_PATH, filename)
    if os.path.exists(file_path):
        image = pygame.image.load(file_path).convert_alpha()
        BALL_IMAGES[color] = pygame.transform.scale(image, BALL_SIZE)
    else:
        print(f"Warning: {filename} not found. Using default circle for color {color}.")
        BALL_IMAGES[color] = None  # Fallback to drawing a circle if image is missing

# Fonts
FONT = pygame.font.SysFont("Arial", 30)
NOTIFICATION_FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# Text constants
WRITEUP_TEXT = "This project is designed by Biodun (https://x.com/janetwoss) to participate in SuperSeed Tesla powered by SuperSeed the only loan payback."
START_NOTE = "Keep clicking to start game"
HEART_EMOJI = "❤️"

# BallAnimation class for bouncing balls on the start screen
class BallAnimation:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = BALL_RADIUS
        self.speed_x = random.uniform(-3, 3)  # Random horizontal speed
        self.speed_y = random.uniform(-3, 3)  # Random vertical speed
        self.angle = random.uniform(0, 2 * math.pi)  # For slight wobble effect

    def update(self):
        # Update position
        self.x += self.speed_x
        self.y += self.speed_y

        # Add a slight wobble effect
        self.angle += 0.1
        wobble = math.sin(self.angle) * 2  # Small wobble amplitude
        self.x += wobble

        # Bounce off walls
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.speed_x = -self.speed_x
            self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.speed_y = -self.speed_y
            self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def draw(self):
        if BALL_IMAGES[self.color] is not None:
            WINDOW.blit(BALL_IMAGES[self.color], (int(self.x - self.radius), int(self.y - self.radius)))
        else:
            pygame.draw.circle(WINDOW, self.color, (int(self.x), int(self.y)), self.radius)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_surface = FONT.render(text, True, BLACK)

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect)
        WINDOW.blit(self.text_surface, (self.rect.x + (self.rect.width - self.text_surface.get_width()) // 2,
                                       self.rect.y + (self.rect.height - self.text_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Toggle class with click counter
class Toggle:
    def __init__(self, x, y, width, height, max_clicks=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.clicks = 0
        self.max_clicks = max_clicks
        self.progress = 0
        self.text_surface = SMALL_FONT.render("Toggle", True, BLACK)

    def draw(self):
        pygame.draw.rect(WINDOW, GRAY, self.rect)
        progress_width = (self.rect.width * self.clicks) // self.max_clicks
        pygame.draw.rect(WINDOW, GREEN, (self.rect.x, self.rect.y, progress_width, self.rect.height))
        WINDOW.blit(self.text_surface, (self.rect.x + (self.rect.width - self.text_surface.get_width()) // 2,
                                       self.rect.y + (self.rect.height - self.text_surface.get_height()) // 2))

    def click(self):
        if self.clicks < self.max_clicks:
            self.clicks += 1
            self.progress = self.clicks / self.max_clicks

    def is_full(self):
        return self.clicks >= self.max_clicks

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Compartment class
class Compartment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.balls = []

    def draw(self):
        pygame.draw.rect(WINDOW, WHITE, (self.x, self.y, COMPARTMENT_SIZE, COMPARTMENT_SIZE))
        pygame.draw.rect(WINDOW, BLACK, (self.x, self.y, COMPARTMENT_SIZE, COMPARTMENT_SIZE), 2)
        
        ball_spacing = COMPARTMENT_SIZE // 6
        for i, (color, _) in enumerate(self.balls):
            ball_x = self.x + COMPARTMENT_SIZE // 2 - BALL_RADIUS  # Center the image
            ball_y = self.y + COMPARTMENT_SIZE - BALL_RADIUS - (i * ball_spacing) - BALL_RADIUS
            if BALL_IMAGES[color] is not None:
                WINDOW.blit(BALL_IMAGES[color], (ball_x, ball_y))
            else:
                # Fallback to circle if image not found
                pygame.draw.circle(WINDOW, color, (ball_x + BALL_RADIUS, ball_y + BALL_RADIUS), BALL_RADIUS)
            self.balls[i] = (color, (ball_x + BALL_RADIUS, ball_y + BALL_RADIUS))

    def can_add_ball(self, color):
        return len(self.balls) == 0 or (all(ball[0] == color for ball in self.balls) and len(self.balls) < 5)

    def can_remove_ball(self, color):
        return len(self.balls) > 0

# Initialize level function
def initialize_level(level):
    level_data = LEVELS[level - 1]
    num_compartments = level_data["compartments"]
    compartments = []

    if num_compartments <= 6:
        rows = 2
        cols = (num_compartments + 1) // 2
        for row in range(rows):
            for col in range(cols):
                if row * cols + col < num_compartments:
                    x = col * (COMPARTMENT_SIZE + 20) + (WIDTH - (cols * (COMPARTMENT_SIZE + 20))) // 2
                    y = row * (COMPARTMENT_SIZE + 50) + 150
                    compartments.append(Compartment(x, y))
    else:
        rows = 3
        cols = (num_compartments + 2) // 3
        for row in range(rows):
            for col in range(cols):
                if row * cols + col < num_compartments:
                    x = col * (COMPARTMENT_SIZE + 10) + (WIDTH - (cols * (COMPARTMENT_SIZE + 10))) // 2
                    y = row * (COMPARTMENT_SIZE + 20) + 100
                    compartments.append(Compartment(x, y))

    balls = []
    for color in level_data["colors"]:
        for _ in range(level_data["balls_per_color"]):
            balls.append(color)
    random.shuffle(balls)
    num_balls = len(balls)
    num_filled_compartments = min(len(compartments) - 1, (num_balls + 4 - 1) // 4)
    for i, ball in enumerate(balls):
        compartment = compartments[i % num_filled_compartments]
        compartment.balls.append((ball, (0, 0)))
    return compartments

# is_stuck function
def is_stuck(compartments):
    has_empty = any(len(compartment.balls) == 0 for compartment in compartments)
    if has_empty:
        return False
    for i, source in enumerate(compartments):
        if not source.balls:
            continue
        top_ball_color = source.balls[-1][0]
        for j, target in enumerate(compartments):
            if i == j:
                continue
            if target.can_add_ball(top_ball_color):
                return False
    return True

# Game variables
game_started = False
start_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 50, "OK", GREEN)
start_toggle = Toggle(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 30, max_clicks=5)
current_level = 1
compartments = None
selected_ball = None
following = False
start_time = 0
game_won = False
time_up = False
game_over = False
win_popup = False
win_time = 0
move_count = 0
move_limit = None
lives = 1
running = True

# Buttons
end_button = Button(150, 450, 100, 50, "End Game", GREEN)
restart_button = Button(350, 450, 100, 50, "Restart", GREEN)
next_level_button = Button(200, 350, 100, 50, "Next Level", GREEN)
exit_button = Button(300, 350, 100, 50, "Exit", GREEN)
use_life_button = Button(250, 400, 100, 50, "Use Life", GREEN)

# Create animated balls for the start screen
animated_balls = []
all_colors = [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GREEN, LIGHT_BLUE, GRAY, BLACK]
for _ in range(10):  # Create 10 bouncing balls
    x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS)
    y = random.randint(BALL_RADIUS, HEIGHT - BALL_RADIUS)
    color = random.choice(all_colors)
    animated_balls.append(BallAnimation(x, y, color))

# Main game loop
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if not game_started:
                if start_toggle.is_clicked((mouse_x, mouse_y)):
                    start_toggle.click()
                if start_button.is_clicked((mouse_x, mouse_y)) and start_toggle.is_full():
                    game_started = True
                    compartments = initialize_level(current_level)
                    start_time = time.time()
                    move_limit = LEVELS[current_level - 1]["move_limit"]
                    move_count = 0
            elif not game_won and not time_up and not game_over:
                if not following:
                    for compartment in compartments:
                        for i, (color, pos) in enumerate(compartment.balls):
                            if ((mouse_x - pos[0]) ** 2 + (mouse_y - pos[1]) ** 2) <= BALL_RADIUS ** 2:
                                if compartment.can_remove_ball(color):
                                    selected_ball = (compartment, i, color)
                                    following = True
                                    break
                        if following:
                            break
                else:
                    for target_compartment in compartments:
                        if (target_compartment.x <= mouse_x <= target_compartment.x + COMPARTMENT_SIZE and
                            target_compartment.y <= mouse_y <= target_compartment.y + COMPARTMENT_SIZE):
                            color = selected_ball[2]
                            if target_compartment.can_add_ball(color):
                                ball = selected_ball[0].balls.pop(selected_ball[1])
                                target_compartment.balls.append(ball)
                                move_count += 1
                            else:
                                game_over = True
                            selected_ball = None
                            following = False
                            break
                    if following and not game_over:
                        selected_ball = None
                        following = False
            elif time_up or game_over:
                mouse_pos = pygame.mouse.get_pos()
                if end_button.is_clicked(mouse_pos):
                    running = False
                elif restart_button.is_clicked(mouse_pos):
                    current_level = 1
                    compartments = initialize_level(current_level)
                    start_time = time.time()
                    move_limit = LEVELS[current_level - 1]["move_limit"]
                    move_count = 0
                    game_won = False
                    time_up = False
                    game_over = False
                    selected_ball = None
                    following = False
                    lives = 1
                elif use_life_button.is_clicked(mouse_pos) and lives > 0:
                    lives -= 1
                    compartments = initialize_level(current_level)
                    start_time = time.time()
                    move_limit = LEVELS[current_level - 1]["move_limit"]
                    move_count = 0
                    game_won = False
                    time_up = False
                    game_over = False
                    selected_ball = None
                    following = False
            elif win_popup:
                mouse_pos = pygame.mouse.get_pos()
                if next_level_button.is_clicked(mouse_pos) and current_level < len(LEVELS):
                    current_level += 1
                    compartments = initialize_level(current_level)
                    start_time = time.time()
                    move_limit = LEVELS[current_level - 1]["move_limit"]
                    move_count = 0
                    game_won = False
                    win_popup = False
                    selected_ball = None
                    following = False
                elif exit_button.is_clicked(mouse_pos):
                    running = False

    # Game logic
    if game_started:
        if not game_won and not time_up and not game_over:
            all_sorted = True
            for compartment in compartments:
                if len(compartment.balls) > 0:
                    first_color = compartment.balls[0][0]
                    if not all(ball[0] == first_color for ball in compartment.balls):
                        all_sorted = False
                        break
            if all_sorted and all(len(compartment.balls) == 0 or len(compartment.balls) == LEVELS[current_level - 1]["balls_per_color"] for compartment in compartments):
                game_won = True
                win_popup = True
                win_time = time.time() - start_time
                lives += 1

        elapsed_time = time.time() - start_time
        if elapsed_time >= TIME_LIMIT and not game_won and not time_up and not game_over:
            time_up = True

        if not game_won and not time_up and not game_over and is_stuck(compartments):
            game_over = True

        if move_limit is not None and move_count >= move_limit and not game_won and not time_up and not game_over:
            game_over = True

    # Draw
    if not game_started:
        WINDOW.fill(LIGHT_BLUE)

        # Update and draw animated balls
        for ball in animated_balls:
            ball.update()
            ball.draw()
        
        writeup_lines = []
        words = WRITEUP_TEXT.split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if SMALL_FONT.render(test_line, True, BLACK).get_width() < WIDTH - 40:
                current_line = test_line
            else:
                writeup_lines.append(current_line)
                current_line = word
        if current_line:
            writeup_lines.append(current_line)
        
        total_height = (len(writeup_lines) + 1) * 25
        start_y = HEIGHT // 2 - total_height // 2
        for i, line in enumerate(writeup_lines):
            writeup_surface = SMALL_FONT.render(line, True, BLACK)
            WINDOW.blit(writeup_surface, (WIDTH // 2 - writeup_surface.get_width() // 2, start_y + i * 25))
        
        note_surface = SMALL_FONT.render(START_NOTE, True, BLACK)
        WINDOW.blit(note_surface, (WIDTH // 2 - note_surface.get_width() // 2, start_y + len(writeup_lines) * 25))
        
        start_toggle.draw()
        start_button.draw()
    else:
        if BACKGROUND:
            WINDOW.blit(BACKGROUND, (0, 0))
        else:
            WINDOW.fill(WHITE)

        if LOGO:
            WINDOW.blit(LOGO, (WIDTH // 2 - LOGO.get_width() // 2, 10))
        
        for compartment in compartments:
            compartment.draw()

        if following and selected_ball:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            color = selected_ball[2]
            if BALL_IMAGES[color] is not None:
                WINDOW.blit(BALL_IMAGES[color], (mouse_x - BALL_RADIUS, mouse_y - BALL_RADIUS))
            else:
                pygame.draw.circle(WINDOW, color, (mouse_x, mouse_y), BALL_RADIUS)

        if not game_won and not time_up and not game_over:
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            timer_color = RED if remaining_time < 30 else BLACK
            if move_limit is not None:
                moves_remaining = max(0, move_limit - move_count)
                timer_text = FONT.render(f"Level {current_level} | Time: {remaining_time:.2f}s | Moves: {moves_remaining}", True, timer_color)
            else:
                timer_text = FONT.render(f"Level {current_level} | Time: {remaining_time:.2f}s", True, timer_color)
            WINDOW.blit(timer_text, (10, 10))

            lives_text = FONT.render(f"{HEART_EMOJI} x {lives}", True, RED)
            WINDOW.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))

        elif time_up or game_over:
            if time_up:
                timer_text = FONT.render("Time's Up!", True, RED)
            else:
                timer_text = FONT.render("Game Over!", True, RED)
            WINDOW.blit(timer_text, (10, 10))
            
            lives_text = FONT.render(f"{HEART_EMOJI} Left: {lives}", True, RED)
            WINDOW.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
            
            notification_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 300)
            pygame.draw.rect(WINDOW, WHITE, notification_rect)
            pygame.draw.rect(WINDOW, BLACK, notification_rect, 3)
            if time_up:
                game_over_message = NOTIFICATION_FONT.render("Time's Up!", True, RED)
                tip_message1 = SMALL_FONT.render("Try to plan moves ahead", True, BLACK)
                tip_message2 = SMALL_FONT.render("and sort faster next time!", True, BLACK)
            elif move_limit is not None and move_count >= move_limit:
                game_over_message = NOTIFICATION_FONT.render("Out of Moves!", True, RED)
                tip_message1 = SMALL_FONT.render("Try to use fewer moves", True, BLACK)
                tip_message2 = SMALL_FONT.render("by planning better!", True, BLACK)
            else:
                game_over_message = NOTIFICATION_FONT.render("Game Over!", True, RED)
                tip_message1 = SMALL_FONT.render("Look for empty spaces", True, BLACK)
                tip_message2 = SMALL_FONT.render("to avoid getting stuck!", True, BLACK)
            WINDOW.blit(game_over_message, (WIDTH // 2 - game_over_message.get_width() // 2, HEIGHT // 2 - 100))
            WINDOW.blit(tip_message1, (WIDTH // 2 - tip_message1.get_width() // 2, HEIGHT // 2 - 40))
            WINDOW.blit(tip_message2, (WIDTH // 2 - tip_message2.get_width() // 2, HEIGHT // 2 - 20))
            end_button.draw()
            restart_button.draw()
            if lives > 0:
                use_life_button.draw()

        if win_popup:
            lives_text = FONT.render(f"{HEART_EMOJI} x {lives}", True, RED)
            WINDOW.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
            
            notification_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
            pygame.draw.rect(WINDOW, WHITE, notification_rect)
            pygame.draw.rect(WINDOW, BLACK, notification_rect, 3)
            win_message = NOTIFICATION_FONT.render("You Win!", True, BLACK)
            time_message = FONT.render(f"Time: {win_time:.2f}s", True, BLACK)
            WINDOW.blit(win_message, (WIDTH // 2 - win_message.get_width() // 2, HEIGHT // 2 - 80))
            WINDOW.blit(time_message, (WIDTH // 2 - time_message.get_width() // 2, HEIGHT // 2 - 30))
            if current_level < len(LEVELS):
                next_level_button.draw()
            exit_button.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()