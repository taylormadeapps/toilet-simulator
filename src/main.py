"""Toilet Simulator — Entry Point."""

import sys
import math

import pygame

from game.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
    BLACK,
    WHITE,
    DARK_BLUE,
    GOLD,
    GREY,
    YELLOW,
)


def draw_splash(screen: pygame.Surface, font_large: pygame.font.Font,
                font_small: pygame.font.Font, frame: int) -> None:
    """Draw the splash screen with a pulsing title."""
    screen.fill(DARK_BLUE)

    # Pulsing title effect
    pulse = math.sin(frame * 0.05) * 0.1 + 1.0
    title_size = max(1, int(64 * pulse))
    title_font = pygame.font.SysFont("Arial", title_size, bold=True)

    # Title: "TOILET"
    title_top = title_font.render("TOILET", True, WHITE)
    title_top_rect = title_top.get_rect(
        centerx=SCREEN_WIDTH // 2,
        centery=SCREEN_HEIGHT // 3 - 20,
    )
    screen.blit(title_top, title_top_rect)

    # Title: "SIMULATOR"
    title_bot = title_font.render("SIMULATOR", True, GOLD)
    title_bot_rect = title_bot.get_rect(
        centerx=SCREEN_WIDTH // 2,
        centery=SCREEN_HEIGHT // 3 + 50,
    )
    screen.blit(title_bot, title_bot_rect)

    # Toilet emoji / icon placeholder — simple ASCII-art style
    toilet_text = font_large.render("🚽", True, WHITE)
    toilet_rect = toilet_text.get_rect(
        centerx=SCREEN_WIDTH // 2,
        centery=SCREEN_HEIGHT // 2 + 40,
    )
    screen.blit(toilet_text, toilet_rect)

    # Blinking "Press SPACE to start" text
    if (frame // 30) % 2 == 0:
        prompt = font_small.render("Press SPACE to start", True, YELLOW)
        prompt_rect = prompt.get_rect(
            centerx=SCREEN_WIDTH // 2,
            centery=SCREEN_HEIGHT - 100,
        )
        screen.blit(prompt, prompt_rect)

    # Subtitle
    subtitle = pygame.font.SysFont("Arial", 16).render(
        "An irreverent take on PowerWash Simulator", True, GREY,
    )
    subtitle_rect = subtitle.get_rect(
        centerx=SCREEN_WIDTH // 2,
        centery=SCREEN_HEIGHT - 50,
    )
    screen.blit(subtitle, subtitle_rect)


def main() -> None:
    """Initialise pygame-ce and run the splash screen."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Pre-load fonts (never create fonts in the loop)
    font_large = pygame.font.SysFont("Arial", 48)
    font_small = pygame.font.SysFont("Arial", 28)

    frame = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

        draw_splash(screen, font_large, font_small, frame)
        pygame.display.flip()
        clock.tick(FPS)
        frame += 1

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
