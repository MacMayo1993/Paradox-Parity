"""
The Parity Paradox - A topological puzzle game
Navigate a non-orientable space, flip parity by crossing seams,
and confuse an HMM-powered boss that tries to predict your moves.
"""

import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 50
CELL_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GOLD = (255, 215, 0)
GREEN = (100, 255, 100)
PURPLE = (200, 100, 255)
GRAY = (128, 128, 128)

# FPS
FPS = 60


class Player:
    """Player character that navigates the topological space."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parity = 0  # 0 = normal, 1 = flipped
        self.color = BLUE

    def move(self, dx, dy, parity):
        """Move player, applying parity inversion if needed."""
        if parity == 1:
            # Invert controls when parity is flipped
            dx, dy = -dx, -dy

        # Update position (with bounds checking can be added here)
        self.x += dx
        self.y += dy

        # Keep within grid bounds
        self.x = max(0, min(GRID_SIZE - 1, self.x))
        self.y = max(0, min(GRID_SIZE - 1, self.y))

    def draw(self, screen, camera_x, camera_y):
        """Draw the player on screen."""
        screen_x = self.x * CELL_SIZE - camera_x + WINDOW_WIDTH // 2
        screen_y = self.y * CELL_SIZE - camera_y + WINDOW_HEIGHT // 2
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), CELL_SIZE // 3)


class SeamLine:
    """The golden seam that flips parity when crossed."""

    def __init__(self, orientation='vertical'):
        self.orientation = orientation
        if orientation == 'vertical':
            self.position = GRID_SIZE // 2
        else:
            self.position = GRID_SIZE // 2

    def check_crossing(self, old_x, old_y, new_x, new_y):
        """Check if player crossed the seam."""
        if self.orientation == 'vertical':
            return (old_x < self.position <= new_x) or (old_x > self.position >= new_x)
        else:
            return (old_y < self.position <= new_y) or (old_y > self.position >= new_y)

    def draw(self, screen, camera_x, camera_y):
        """Draw the seam line."""
        if self.orientation == 'vertical':
            screen_x = self.position * CELL_SIZE - camera_x + WINDOW_WIDTH // 2
            pygame.draw.line(screen, GOLD, (screen_x, 0), (screen_x, WINDOW_HEIGHT), 3)
        else:
            screen_y = self.position * CELL_SIZE - camera_y + WINDOW_HEIGHT // 2
            pygame.draw.line(screen, GOLD, (0, screen_y), (WINDOW_WIDTH, screen_y), 3)


class AntipodeGhost:
    """Ghost that appears at the antipodal point of the player."""

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y):
        """Update antipode position based on player position."""
        # Antipodal point in topological space
        self.x = (self.grid_size - 1) - player_x
        self.y = (self.grid_size - 1) - player_y

    def draw(self, screen, camera_x, camera_y):
        """Draw the antipode ghost."""
        screen_x = self.x * CELL_SIZE - camera_x + WINDOW_WIDTH // 2
        screen_y = self.y * CELL_SIZE - camera_y + WINDOW_HEIGHT // 2
        pygame.draw.circle(screen, PURPLE, (int(screen_x), int(screen_y)), CELL_SIZE // 4, 2)


class HMMBoss:
    """
    Boss that uses a Hidden Markov Model to predict player movement.
    Gets confused when parity flips.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prediction_x = x
        self.prediction_y = y
        self.movement_history = []
        self.last_parity = 0
        self.confusion_level = 0
        self.max_history = 10

    def observe_player(self, player_x, player_y, current_parity):
        """Observe player movement and update predictions."""
        # Detect parity flip - causes confusion
        if current_parity != self.last_parity:
            self.confusion_level = min(100, self.confusion_level + 30)
        else:
            self.confusion_level = max(0, self.confusion_level - 5)

        # Track movement
        if len(self.movement_history) > 0:
            last_x, last_y = self.movement_history[-1]
            dx = player_x - last_x
            dy = player_y - last_y
            self.movement_history.append((player_x, player_y))
        else:
            self.movement_history.append((player_x, player_y))

        # Keep history bounded
        if len(self.movement_history) > self.max_history:
            self.movement_history.pop(0)

        self.last_parity = current_parity

        # Simple prediction: assume player continues in same direction
        if len(self.movement_history) >= 2:
            dx = self.movement_history[-1][0] - self.movement_history[-2][0]
            dy = self.movement_history[-1][1] - self.movement_history[-2][1]

            # Add noise based on confusion level
            noise_factor = self.confusion_level / 100.0
            dx += random.uniform(-noise_factor, noise_factor) * 2
            dy += random.uniform(-noise_factor, noise_factor) * 2

            self.prediction_x = player_x + int(dx * 2)
            self.prediction_y = player_y + int(dy * 2)

    def draw(self, screen, camera_x, camera_y):
        """Draw the boss and its prediction."""
        # Draw boss
        screen_x = self.x * CELL_SIZE - camera_x + WINDOW_WIDTH // 2
        screen_y = self.y * CELL_SIZE - camera_y + WINDOW_HEIGHT // 2
        pygame.draw.rect(screen, RED,
                        (screen_x - CELL_SIZE//2, screen_y - CELL_SIZE//2,
                         CELL_SIZE, CELL_SIZE), 3)

        # Draw prediction (faded if confused)
        pred_screen_x = self.prediction_x * CELL_SIZE - camera_x + WINDOW_WIDTH // 2
        pred_screen_y = self.prediction_y * CELL_SIZE - camera_y + WINDOW_HEIGHT // 2
        alpha = max(50, 255 - self.confusion_level * 2)
        color = (alpha, 50, 50)
        pygame.draw.circle(screen, color,
                         (int(pred_screen_x), int(pred_screen_y)),
                         CELL_SIZE // 3, 1)


class ParityGame:
    """Main game class."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Parity Paradox")
        self.clock = pygame.time.Clock()

        # Game objects
        self.player = Player(GRID_SIZE // 4, GRID_SIZE // 2)
        self.seam = SeamLine('vertical')
        self.antipode = AntipodeGhost(GRID_SIZE)
        self.boss = HMMBoss(3 * GRID_SIZE // 4, GRID_SIZE // 2)

        # Game state
        self.parity = 0
        self.camera_x = 0
        self.camera_y = 0
        self.running = True

        # Stats
        self.seam_crossings = 0
        self.frames = 0

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False

        # Movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        if dx != 0 or dy != 0:
            old_x, old_y = self.player.x, self.player.y
            self.player.move(dx, dy, self.parity)

            # Check for seam crossing
            if self.seam.check_crossing(old_x, old_y, self.player.x, self.player.y):
                self.parity = 1 - self.parity  # Flip parity
                self.seam_crossings += 1

    def update(self):
        """Update game state."""
        # Update antipode position
        self.antipode.update(self.player.x, self.player.y)

        # Boss observes player
        self.boss.observe_player(self.player.x, self.player.y, self.parity)

        # Update camera to follow player
        self.camera_x = self.player.x * CELL_SIZE
        self.camera_y = self.player.y * CELL_SIZE

        self.frames += 1

    def draw(self):
        """Draw everything."""
        self.screen.fill(BLACK)

        # Draw grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                screen_x = x * CELL_SIZE - self.camera_x + WINDOW_WIDTH // 2
                screen_y = y * CELL_SIZE - self.camera_y + WINDOW_HEIGHT // 2
                pygame.draw.rect(self.screen, GRAY,
                               (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

        # Draw seam
        self.seam.draw(self.screen, self.camera_x, self.camera_y)

        # Draw antipode ghost
        self.antipode.draw(self.screen, self.camera_x, self.camera_y)

        # Draw boss
        self.boss.draw(self.screen, self.camera_x, self.camera_y)

        # Draw player
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Draw UI elements."""
        font = pygame.font.Font(None, 36)

        # Parity indicator
        parity_text = "PARITY: " + ("FLIPPED" if self.parity == 1 else "NORMAL")
        parity_color = RED if self.parity == 1 else GREEN
        text_surface = font.render(parity_text, True, parity_color)
        self.screen.blit(text_surface, (10, 10))

        # Boss confusion level
        confusion_text = f"Boss Confusion: {self.boss.confusion_level}%"
        confusion_surface = font.render(confusion_text, True, WHITE)
        self.screen.blit(confusion_surface, (10, 50))

        # Seam crossings
        crossings_text = f"Seam Crossings: {self.seam_crossings}"
        crossings_surface = font.render(crossings_text, True, GOLD)
        self.screen.blit(crossings_surface, (10, 90))

        # Instructions
        small_font = pygame.font.Font(None, 24)
        instructions = [
            "Arrow keys: Move",
            "Cross golden seam to flip parity",
            "Confuse the boss!",
            "ESC/Q: Quit"
        ]
        for i, instruction in enumerate(instructions):
            inst_surface = small_font.render(instruction, True, WHITE)
            self.screen.blit(inst_surface, (10, WINDOW_HEIGHT - 100 + i * 25))

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ParityGame()
    game.run()
