class StartScreen:
    def __init__(self, game_settings, screen):
        self.screen = screen
        self.game_settings = game_settings
        # TODO: settings/config for text colors
        self.title_surface = self.game_settings.font.render("Welcome to PyBlackJack", True, 'WHITE')
        self.instruction_surface = self.game_settings.font.render("Press any key to start", True, 'WHITE')

        # Center text on the screen
        self.title_rect = self.title_surface.get_rect(center=self.screen.get_rect().center)
        instruction_rect_center_placement = (self.screen.get_rect().center[0],
                                                                   self.screen.get_rect().center[1] + 50)
        self.instruction_rect = self.instruction_surface.get_rect(center=instruction_rect_center_placement)

    def draw(self, screen):
        screen.fill(self.game_settings.bg_color)  # Black background

        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.instruction_surface, self.instruction_rect)