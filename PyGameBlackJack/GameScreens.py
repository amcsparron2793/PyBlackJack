from pathlib import Path
from PyGameBlackJack.card_renderer import draw_hand, get_renderer_status

class StartScreen:
    def __init__(self, game_settings, screen):
        self.screen = screen
        self.game_settings = game_settings
        # TODO: settings/config for text colors
        self.title_surface = self.game_settings.font.render("Welcome to PyBlackJack", True,
                                                            self.game_settings.game_font_color)
        self.instruction_surface = self.game_settings.font.render("Press any key to start", True,
                                                                  self.game_settings.game_font_color)

        # Center text on the screen
        self.title_rect = self.title_surface.get_rect(center=self.screen.get_rect().center)
        instruction_rect_center_placement = (self.screen.get_rect().center[0],
                                                                   self.screen.get_rect().center[1] + 50)
        self.instruction_rect = self.instruction_surface.get_rect(center=instruction_rect_center_placement)

    def draw(self, screen):
        screen.fill(self.game_settings.game_screen_bg_color)  # Black background

        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.instruction_surface, self.instruction_rect)


class GameOverScreen(StartScreen):
    def __init__(self, game_settings, screen):
        super().__init__(game_settings, screen)
        self.game_over_surface = self.game_settings.font.render("Game Over! Press any key to exit.",
                                                           True, self.game_settings.game_font_color)
        self.game_over_rect = self.game_over_surface.get_rect(center=self.screen.get_rect().center)

    def draw(self, screen):
        screen.fill(self.game_settings.game_over_screen_bg_color)
        screen.blit(self.game_over_surface, self.game_over_rect)


class GameScreen(StartScreen):
    def __init__(self, game_settings, screen, player, dealer):
        super().__init__(game_settings, screen)
        self.player = player
        self.dealer = dealer
        self.player_name = getattr(player, 'player_display_name', '')
        self.player_text_surface = self.game_settings.font.render(
            f"Player: {self.player_name}", True, self.game_settings.game_font_color
        )
        self.dealer_text_surface = self.game_settings.font.render(
            "Dealer", True, self.game_settings.game_font_color
        )
        self.instructions_surface = self.game_settings.font.render(
            "H=Hit  S=Stay  R=Reveal  N=New Hand  Esc=Quit", True, self.game_settings.game_font_color
        )
        self.card_back_svg = Path(self.game_settings.card_back_location)
        self.dealer_revealed = False
        self.card_target_height = 180

    def draw(self, screen):
        screen.fill(self.game_settings.game_screen_bg_color)

        # Titles/labels
        screen.blit(self.player_text_surface, (10, screen.get_height() - 10 - self.player_text_surface.get_height()))
        screen.blit(self.dealer_text_surface, (10, 10))
        screen.blit(self.instructions_surface, (screen.get_width()//2 - self.instructions_surface.get_width()//2, 10))

        # Compute positions
        top_margin = 50
        bottom_margin = 60

        # Dealer hand
        if hasattr(self.player, '_translate_card'):
            translate = self.player._translate_card  # reuse existing translator
        else:
            translate = lambda c: Path("")  # type: ignore

        if getattr(self, 'dealer_revealed', False):
            dealer_paths = [translate(c) for c in getattr(self.dealer, 'hand', [])]
        else:
            # Show back of first card, rest face up
            remaining = list(getattr(self.dealer, 'hand', []))[1:]
            dealer_paths = [self.card_back_svg] + [translate(c) for c in remaining]

        draw_hand(screen, dealer_paths, (10, top_margin), target_height=self.card_target_height, x_spacing=28)

        # Player hand
        if hasattr(self.player, 'get_translated_hand'):
            player_paths = self.player.get_translated_hand()
        else:
            player_paths = []
        draw_hand(
            screen,
            player_paths,
            (10, screen.get_height() - bottom_margin - self.card_target_height),
            target_height=self.card_target_height,
            x_spacing=28,
        )

        # Diagnostics overlay: show active renderer and guidance
        try:
            status = get_renderer_status()
            backend = status.get('backend', 'unknown')
            avail = status.get('available_backends', {})
            base_y = screen.get_height() - bottom_margin - self.card_target_height - 40

            # Always show which renderer is active
            info_surface = self.game_settings.font.render(f"Renderer: {backend}", True, (200, 200, 200))
            screen.blit(info_surface, (10, max(10, base_y)))

            if backend == "placeholder":
                # No working rasterizer found; provide guidance
                warn_lines = [
                    "No SVG rasterizer found. Install ANY ONE of:",
                    " - pip install cairosvg  OR  rsvg-convert  OR  ImageMagick (magick)  OR  Inkscape",
                ]
                for i, line in enumerate(warn_lines, start=1):
                    warn_surface = self.game_settings.font.render(line, True, (255, 80, 80))
                    screen.blit(warn_surface, (10, max(10, base_y - 20 * i)))

                # Show which tools are currently detected
                try:
                    detected = [name for name, ok in avail.items() if ok]
                    det_text = f"Detected: {', '.join(detected) if detected else 'none'}"
                    det_surface = self.game_settings.font.render(det_text, True, (255, 180, 180))
                    screen.blit(det_surface, (10, max(10, base_y + 24)))
                except Exception:
                    pass
        except Exception:
            pass
