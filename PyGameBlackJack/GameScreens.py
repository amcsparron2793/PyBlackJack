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
    def __init__(self, game_settings, screen, player_name):
        super().__init__(game_settings, screen)
        self.player_name = player_name
        self.player_text_surface = self.game_settings.font.render(f"Player: {self.player_name}", True,
                                                                  self.game_settings.game_font_color)
        self.game_screen_rect = self.player_text_surface.get_rect(center=self.screen.get_rect().center)

    def draw(self, screen):
        screen.fill(self.game_settings.game_screen_bg_color)
        screen.blit(self.player_text_surface, (10, 10))  # Render player name in the top-left corner
