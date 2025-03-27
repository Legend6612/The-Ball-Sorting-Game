import pygame
import sys
import random
import time
import os

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
CYAN = (0, 255, 255)  # New color for higher levels
LIGHT_BLUE = (173, 216, 230)

# Define levels with increasing complexity
LEVELS = [
    {"colors": [RED, BLUE, YELLOW], "balls_per_color": 2, "compartments": 4, "move_limit": None},  # Level 1: 3 colors, 2 balls each (6 balls), 4 compartments
    {"colors": [RED, BLUE, YELLOW, PURPLE], "balls_per_color": 2, "compartments": 5, "move_limit": None},  # Level 2: 4 colors, 2 balls each (8 balls), 5 compartments
    {"colors": [RED, BLUE, YELLOW, PURPLE], "balls_per_color": 3, "compartments": 5, "move_limit": None},  # Level 3: 4 colors, 3 balls each (12 balls), 5 compartments
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE], "balls_per_color": 3, "compartments": 6, "move_limit": 30},  # Level 4: 5 colors, 3 balls each (15 balls), 6 compartments, 30 moves
    {"colors": [RED, BLUE, YELLOW, PURPLE, ORANGE, CYAN], "balls_per_color": 4, "compartments": 7, "move_limit": 40},  # Level 5: 6 colors, 4 balls each (24 balls), 7 compartments, 40 moves
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
COMPARTMENT_SIZE = 80  # Reduced size to fit more compartments
BALL_RADIUS = 15  # Reduced size to fit in smaller compartments
TIME_LIMIT = 180

# Fonts
FONT = pygame.font.SysFont("Arial", 30)
NOTIFICATION_FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# Text constants
WRITEUP_TEXT = "This project is designed by Biodun (https://x.com/janetwoss) to participate in SuperSeed Tesla powered by SuperSeed the only loan payback."
START_NOTE = "Keep clicking to start game"

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
            ball_x = self.x + COMPARTMENT_SIZE // 2
            ball_y = self.y + COMPARTMENT_SIZE - BALL_RADIUS - (i * ball_spacing)
            pygame.draw.circle(WINDOW, color, (ball_x, ball_y), BALL_RADIUS)
            self.balls[i] = (color, (ball_x, ball_y))

    def can_add_ball(self, color):
        return len(self.balls) == 0 or (all(ball[0] == color for ball in self.balls) and len(self.balls) < 5)

    def can_remove_ball(self, color):
        return len(self.balls) > 0

# Initialize level function with updated layout
def initialize_level(level):
    level_data = LEVELS[level - 1]
    num_compartments = level_data["compartments"]
    compartments = []

    # Adjust layout based on the number of compartments
    if num_compartments == 4:
        for row in range(2):
            for col in range(2):
                x = col * (COMPARTMENT_SIZE + 50) + 150
                y = row * (COMPARTMENT_SIZE + 50) + 150
                compartments.append(Compartment(x, y))
    elif num_compartments == 5:
        positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
        for row, col in positions:
            x = col * (COMPARTMENT_SIZE + 20) + 120
            y = row * (COMPARTMENT_SIZE + 50) + 150
            compartments.append(Compartment(x, y))
    elif num_compartments == 6:
        for row in range(2):
            for col in range(3):
                x = col * (COMPARTMENT_SIZE + 20) + 90
                y = row * (COMPARTMENT_SIZE + 50) + 150
                compartments.append(Compartment(x, y))
    elif num_compartments == 7:  # For Level 5
        # 3 rows: 3 compartments on top, 2 in middle, 2 at bottom
        positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
        for row, col in positions:
            x = col * (COMPARTMENT_SIZE + 20) + 90
            y = row * (COMPARTMENT_SIZE + 20) + 100
            compartments.append(Compartment(x, y))

    # Place balls randomly, ensuring at least one compartment is empty
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
move_count = 0  # Track number of moves
move_limit = None  # Will be set per level

# Buttons
end_button = Button(150, 450, 100, 50, "End Game", GREEN)
restart_button = Button(350, 450, 100, 50, "Restart", GREEN)
next_level_button = Button(200, 350, 100, 50, "Next Level", GREEN)
exit_button = Button(300, 350, 100, 50, "Exit", GREEN)

# Main game loop
clock = pygame.time.Clock()
running = True
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
                                move_count += 1  # Increment move count
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

        elapsed_time = time.time() - start_time
        if elapsed_time >= TIME_LIMIT and not game_won and not time_up and not game_over:
            time_up = True

        if not game_won and not time_up and not game_over and is_stuck(compartments):
            game_over = True

        # Check move limit
        if move_limit is not None and move_count >= move_limit and not game_won and not time_up and not game_over:
            game_over = True

    # Draw
    if not game_started:
        WINDOW.fill(LIGHT_BLUE)
        
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
            pygame.draw.circle(WINDOW, selected_ball[2], (mouse_x, mouse_y), BALL_RADIUS)

        if not game_won and not time_up and not game_over:
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            if move_limit is not None:
                moves_remaining = max(0, move_limit - move_count)
                timer_text = FONT.render(f"Level {current_level} | Time: {remaining_time:.2f}s | Moves: {moves_remaining}", True, BLACK)
            else:
                timer_text = FONT.render(f"Level {current_level} | Time: {remaining_time:.2f}s", True, BLACK)
            WINDOW.blit(timer_text, (10, 10))
        elif time_up:
            timer_text = FONT.render("Time's Up!", True, BLACK)
            WINDOW.blit(timer_text, (10, 10))
            end_button.draw()
            restart_button.draw()
        elif game_over:
            notification_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
            pygame.draw.rect(WINDOW, WHITE, notification_rect)
            pygame.draw.rect(WINDOW, BLACK, notification_rect, 3)
            if move_limit is not None and move_count >= move_limit:
                game_over_message = NOTIFICATION_FONT.render("Out of Moves!", True, BLACK)
            else:
                game_over_message = NOTIFICATION_FONT.render("Game Over!", True, BLACK)
            WINDOW.blit(game_over_message, (WIDTH // 2 - game_over_message.get_width() // 2, HEIGHT // 2 - 80))
            end_button.draw()
            restart_button.draw()

        if win_popup:
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