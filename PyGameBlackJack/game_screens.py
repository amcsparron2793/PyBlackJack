from pathlib import Path
from PyGameBlackJack.card_renderer import get_renderer_status

class StartScreen:
    WELCOME_MSG = "Welcome to PyBlackJack!"
    GAME_OVER_MSG = "Game Over! Press any key to exit."
    START_SCREEN_INSTRUCTIONS = "Press any key to start"
    GAME_SCREEN_INSTRUCTIONS = "H=Hit  S=Stay  R=Reveal  N=New Hand  Esc=Quit"

    def __init__(self, game_settings, screen):
        self.screen = screen
        self.game_settings = game_settings
        self.edge_buffer_pixels = 10

        self.title_surface = self.game_settings.font.render(self.__class__.WELCOME_MSG, True,
                                                            self.game_settings.game_font_color)
        self.instruction_surface = self.game_settings.font.render(self.__class__.START_SCREEN_INSTRUCTIONS, True,
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
        self.game_over_surface = self.game_settings.font.render(self.__class__.GAME_OVER_MSG,
                                                           True, self.game_settings.game_font_color)
        self.game_over_rect = self.game_over_surface.get_rect(center=self.screen.get_rect().center)

    def draw(self, screen):
        screen.fill(self.game_settings.game_over_screen_bg_color)
        screen.blit(self.game_over_surface, self.game_over_rect)


class GameScreen(StartScreen):
    PLACEHOLDER_WARN_LINES = warn_lines = [
            "No SVG rasterizer found. Install ANY ONE of:",
            " - pip install cairosvg  OR  rsvg-convert  OR  ImageMagick (magick)  OR  Inkscape",
        ]
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
        self.instructions_surface = self.game_settings.font.render(self.__class__.GAME_SCREEN_INSTRUCTIONS,
                                                                   True, self.game_settings.game_font_color)
        self.card_back_svg = Path(self.game_settings.card_back_location)
        self.dealer_revealed = False
        self.card_target_height = 180

        self.card_x_spacing = 28
        self.card_top_margin = 50
        self.card_bottom_margin = 60

    def _title_label_placement(self, screen):

        # Titles/labels
        player_text_y = screen.get_height() - self.edge_buffer_pixels - self.player_text_surface.get_height()
        instruction_text_x = screen.get_width() // 2 - self.instructions_surface.get_width() // 2

        player_text_placement_dest = (self.edge_buffer_pixels, player_text_y)
        dealer_text_placement_dest = (self.edge_buffer_pixels, self.edge_buffer_pixels)

        instruction_placement_dest = (instruction_text_x, self.edge_buffer_pixels)

        return player_text_placement_dest, dealer_text_placement_dest, instruction_placement_dest

    def draw(self, screen):
        screen.fill(self.game_settings.game_screen_bg_color)

        (player_text_placement_dest,
         dealer_text_placement_dest,
         instruction_placement_dest) = self._title_label_placement(screen)

        screen.blit(self.player_text_surface, player_text_placement_dest)
        screen.blit(self.dealer_text_surface, dealer_text_placement_dest)
        screen.blit(self.instructions_surface, instruction_placement_dest)

        # Dealer hand via class method
        if hasattr(self.dealer, 'print_hand'):
            self.dealer.print_hand(
                screen=screen,
                start_xy=(self.edge_buffer_pixels, self.card_top_margin),
                target_height=self.card_target_height,
                x_spacing=self.card_x_spacing,
                reveal_all=getattr(self, 'dealer_revealed', False),
                card_back_path=self.card_back_svg,
            )

        # Player hand via class method
        if hasattr(self.player, 'print_hand'):
            player_start_y = screen.get_height() - self.card_bottom_margin - self.card_target_height
            self.player.print_hand(
                screen=screen,
                start_xy=(self.edge_buffer_pixels, player_start_y),
                target_height=self.card_target_height,
                x_spacing=self.card_x_spacing,
            )
        self.draw_dx_overlay(screen, bottom_margin=self.card_bottom_margin)

    def _get_dx_info(self, screen, **kwargs):
        status = get_renderer_status()
        bottom_margin = kwargs.get('bottom_margin', self.card_bottom_margin)
        backend = status.get('backend', 'unknown')
        avail = status.get('available_backends', {})
        base_y = screen.get_height() - bottom_margin - self.card_target_height - 40
        return backend, avail, base_y

    def draw_dx_overlay(self, screen, **kwargs):
        bottom_margin = kwargs.get('bottom_margin', self.card_bottom_margin)
        # Diagnostics overlay: show active renderer and guidance
        try:
            backend, avail, base_y = self._get_dx_info(screen, bottom_margin=bottom_margin)

            # Always show which renderer is active
            info_surface = self.game_settings.font.render(f"Renderer: {backend}",
                                                          True, self.game_settings.dx_font_color)
            info_surface_placement = (self.edge_buffer_pixels, max(self.edge_buffer_pixels, base_y))
            screen.blit(info_surface, info_surface_placement)

            if backend == "placeholder":
                self.placeholder_fallback(screen, base_y=base_y, avail=avail)
        except Exception:
            pass

    def placeholder_fallback(self, screen, avail=None, **kwargs):
        base_y = kwargs.get('base_y', self.card_bottom_margin)
        # No working rasterizer found; provide guidance
        if avail is None:
            avail = dict()

        for i, line in enumerate(self.__class__.PLACEHOLDER_WARN_LINES, start=1):
            warn_surface = self.game_settings.font.render(line, True, self.game_settings.dx_font_error_color)
            warn_surface_placement = (self.edge_buffer_pixels, max(self.edge_buffer_pixels, base_y - 20 * i))
            screen.blit(warn_surface, warn_surface_placement)

        # Show which tools are currently detected
        try:
            detected = [name for name, ok in avail.items() if ok]
            det_text = f"Detected: {', '.join(detected) if detected else 'none'}"
            det_surface = self.game_settings.font.render(det_text, True, self.game_settings.dx_detected_surface_color)
            det_surface_placement = (self.edge_buffer_pixels, max(self.edge_buffer_pixels, base_y + 24))
            screen.blit(det_surface, det_surface_placement)
        except Exception:
            pass