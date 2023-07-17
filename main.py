import pygame
import pygame_gui
import random

pygame.init()
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(image, (50, 50))  # scale down the image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = [random.uniform(-3, 3), random.uniform(-3, 3)]  # give the entity a constant velocity

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # make the entity bounce off the edges
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity[0] = -self.velocity[0] * random.uniform(0.8, 1.2)
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.velocity[1] = -self.velocity[1] * random.uniform(0.8, 1.2)

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


class Rock(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "rock.png")


class Paper(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "paper.png")


class Scissors(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "scissors.png")


class Game:
    def __init__(self, num_entities=10):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.all_sprites = pygame.sprite.Group()
        self.rocks = pygame.sprite.Group()
        self.papers = pygame.sprite.Group()
        self.scissors = pygame.sprite.Group()

        for _ in range(num_entities):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            rock = Rock(x, y)
            self.all_sprites.add(rock)
            self.rocks.add(rock)

            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            paper = Paper(x, y)
            self.all_sprites.add(paper)
            self.papers.add(paper)

            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            scissors = Scissors(x, y)
            self.all_sprites.add(scissors)
            self.scissors.add(scissors)

    def game_over_screen(self, winning_team, game_duration):
        # Create a semi-transparent surface
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black.

        font = pygame.font.Font(None, 36)
        game_over_text = font.render("Game Over!", 1, (255, 255, 255))
        winning_team_text = font.render(f"Winning team: {winning_team}", 1, (255, 255, 255))
        game_duration_text = font.render(f"Game duration: {game_duration:.2f} seconds", 1, (255, 255, 255))

        overlay.blit(game_over_text, (
            SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        overlay.blit(winning_team_text, (SCREEN_WIDTH // 2 - winning_team_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - winning_team_text.get_height() // 2 + 50))
        overlay.blit(game_duration_text, (SCREEN_WIDTH // 2 - game_duration_text.get_width() // 2,
                                          SCREEN_HEIGHT // 2 - game_duration_text.get_height() // 2 + 100))

        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.wait(5000)  # show the game over screen for 5 seconds

    def run(self):
        start_time = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.all_sprites.update()

            self.screen.fill((0, 0, 0))
            self.all_sprites.draw(self.screen)
            pygame.display.flip()

            self.check_collisions()

            # Check if all entities are of the same type
            if len(self.rocks) == len(self.all_sprites) or len(self.papers) == len(self.all_sprites) or len(
                    self.scissors) == len(self.all_sprites):
                end_time = pygame.time.get_ticks()
                game_duration = (end_time - start_time) / 1000  # convert milliseconds to seconds
                if len(self.rocks) == len(self.all_sprites):
                    winning_team = 'rocks'
                elif len(self.papers) == len(self.all_sprites):
                    winning_team = 'papers'
                else:
                    winning_team = 'scissors'
                self.game_over_screen(winning_team, game_duration)
                break

    def check_collisions(self):
        for rock in pygame.sprite.groupcollide(self.rocks, self.scissors, False, True):
            new_rock = Rock(rock.rect.x, rock.rect.y)
            self.all_sprites.add(new_rock)
            self.rocks.add(new_rock)
            rock_sound = pygame.mixer.Sound('sound_rock.mp3')
            rock_sound.play()

        for scissors in pygame.sprite.groupcollide(self.scissors, self.papers, False, True):
            new_scissors = Scissors(scissors.rect.x, scissors.rect.y)
            self.all_sprites.add(new_scissors)
            self.scissors.add(new_scissors)
            scissors_sound = pygame.mixer.Sound('sound_scissors.mp3')
            scissors_sound.play()

        for paper in pygame.sprite.groupcollide(self.papers, self.rocks, False, True):
            new_paper = Paper(paper.rect.x, paper.rect.y)
            self.all_sprites.add(new_paper)
            self.papers.add(new_paper)
            paper_sound = pygame.mixer.Sound('sound_paper.mp3')
            paper_sound.play()


class Menu:
    def __init__(self):
        self.game = None
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 100), (200, 50)),
            text="Rock Paper Scissors",
            manager=self.manager
        )

        self.description = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 200), (200, 50)),
            text="Enter number of entities",
            manager=self.manager
        )

        self.number_of_entities_text_entry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 250), (200, 50)),
            manager=self.manager
        )

        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 350), (200, 50)),
            text="Play",
            manager=self.manager
        )

        self.change_map_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 450), (200, 50)),
            text="Change Map",
            manager=self.manager
        )

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.manager.process_events(event)

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                        if event.ui_element == self.number_of_entities_text_entry:
                            num_entities = int(self.number_of_entities_text_entry.get_text())
                            self.game = Game(num_entities)
                            self.game.run()
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.play_button:
                            num_entities = int(self.number_of_entities_text_entry.get_text())
                            self.game = Game(num_entities)
                            self.game.run()

            self.manager.update(time_delta)

            self.screen.fill((0, 0, 0))
            self.manager.draw_ui(self.screen)
            pygame.display.update()


if __name__ == "__main__":
    menu = Menu()
    menu.run()
