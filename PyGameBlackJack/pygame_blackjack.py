import pygame

from Backend.enum import GameStates
from Backend.settings import PyGameSettings
from PyBlackJack.Bank.Cage import Cage
from PyBlackJack.py_blackjack import Game
from PyBlackJack.Players.Players import PyGamePlayer, PyGameDatabasePlayer, PyGameDealer
from PyBlackJack.Bank.Cage import DatabaseCage
from PyGameBlackJack.game_screens import StartScreen, GameOverScreen, GameScreen


class PyGameBlackJack(Game):
    NON_DATABASE_PLAYER_CLASS = PyGamePlayer
    NON_DATABASE_CAGE_CLASS = Cage
    NON_DATABASE_DEALER_CLASS = PyGameDealer
    DATABASE_PLAYER_CLASS = PyGameDatabasePlayer
    DATABASE_CAGE_CLASS = DatabaseCage
    DATABASE_DEALER_CLASS = PyGameDealer
    def __init__(self, **kwargs):
        pygame.init()
        self.game_settings = kwargs.pop('game_settings', PyGameSettings())
        super().__init__(game_settings=self.game_settings, **kwargs)

        pygame.display.set_caption("PyBlackJack")

        self.screen = pygame.display.set_mode(size=self.game_settings.screen_size)
        self.clock = pygame.time.Clock()

        self.running = True

        self._state = GameStates.START  # Game states: START, PLAYING, GAME_OVER
        self.start_screen = StartScreen(self.game_settings, screen=self.screen)
        self.game_over_screen = GameOverScreen(self.game_settings, screen=self.screen)
        self.game_screen = GameScreen(self.game_settings, screen=self.screen,
                                      player=self.player, dealer=self.dealer)

        # ensure GameScreen references current player/dealer after re-init
        self.game_screen.player = self.player
        self.game_screen.dealer = self.dealer
        self.game_screen.dealer_revealed = False
        self.player.print_hand()


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value in GameStates:
            self._state = value
        else:
            raise ValueError(f"Invalid game state: {value}")

    def _keydown_events(self, event):
        if event.key == pygame.K_SPACE:
            # Reserved for future use (e.g., animations)
            pass
        elif event.key == pygame.K_ESCAPE:
            self.state = GameStates.GAME_OVER
        elif event.key == pygame.K_h:  # Player hits
            self.hit(self.player)
        elif event.key == pygame.K_s:  # Player stays
            self.stay(self.player)
        # TODO: finish/dont use this?
        elif event.key == pygame.K_r:  # Reveal dealer hand toggle
            if hasattr(self.game_screen, 'dealer_revealed'):
                self.game_screen.dealer_revealed = not self.game_screen.dealer_revealed
        elif event.key == pygame.K_n:  # New hand
            self.setup_new_hand()
            if hasattr(self.game_screen, 'dealer_revealed'):
                self.game_screen.dealer_revealed = False

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameStates.GAME_OVER
            elif event.type == pygame.KEYDOWN:
                self._keydown_events(event)

    def _start_screen(self):
        """
        Render the start screen.
        """
        self.start_screen.draw(self.screen)
        pygame.display.flip()  # Update the screen

        # Wait for the player to press any key to continue
        self._wait_for_key()

    def _wait_for_key(self):
        """
        Wait for a key press to continue.
        """
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def play(self):
        """
        Main game loop.
        """
        while self.running:
            # Handle game states
            if self.state == GameStates.START:
                self._start_screen()
                self.state = GameStates.PLAYING  # Transition to the playing state

            elif self.state == GameStates.PLAYING:
                self.setup_new_hand()
                self._game_loop()

            elif self.state == GameStates.GAME_OVER:
                self._game_over_screen()
                self.running = False  # Exit loop after displaying game over

        self._quit_game()

    def _game_loop(self):
        """
        The main game-playing loop.
        """
        while self.state == GameStates.PLAYING:
            # Event handling
            self.check_events()

            # TODO: Update game logic
            #  Add functionality such as checking for a bust, dealer actions, etc.
            # Render game screen
            self._render_game_screen()

            # Limit frame rate to 60 FPS
            self.clock.tick(60)

    def _render_game_screen(self):
        """
        Render the main game playing screen.
        """
        self.game_screen.draw(self.screen)
        pygame.display.flip()  # Update the display

    def _game_over_screen(self):
        """
        Display the game over screen.
        """
        self.game_over_screen.draw(self.screen)
        pygame.display.flip()  # Update the screen

        # Wait for the player to press any key to continue
        self._wait_for_key()

    def _quit_game(self):
        """
        Properly shut down the game.
        """
        pygame.quit()
        exit()


if __name__ == '__main__':
    game = PyGameBlackJack()
    game.play()