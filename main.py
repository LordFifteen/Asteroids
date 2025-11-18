import pygame
import sys
from config import *
from game_objects import *


class GameState:
    """Базовый класс для состояний игры"""

    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Обработка событий"""
        pass

    def update(self):
        """Обновление состояния"""
        pass

    def draw(self, screen):
        """Отрисовка"""
        pass


class TitleScreenState(GameState):
    """Состояние заставки"""

    def __init__(self, game):
        super().__init__(game)
        self.timer = TITLE_SCREEN_DURATION
        self.title_rect = pygame.Rect(
            (SCREEN_WIDTH - TITLE_WIDTH) // 2,
            (SCREEN_HEIGHT - TITLE_HEIGHT) // 2,
            TITLE_WIDTH,
            TITLE_HEIGHT
        )

    def handle_events(self, events):
        """Обработка событий заставки"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.title_rect.collidepoint(event.pos):
                    self.game.reset_game()
                    self.game.change_state("gameplay")

    def update(self):
        """Обновление заставки"""
        self.timer -= 1
        if self.timer <= 0:
            self.timer = TITLE_SCREEN_DURATION

    def draw(self, screen):
        """Отрисовка заставки"""
        # Неподвижный фон
        screen.fill(BLACK)

        # Динамический фон (движущиеся астероиды)
        for i in range(5):
            y_pos = (pygame.time.get_ticks() // 50 + i * 100) % SCREEN_HEIGHT
            pygame.draw.circle(screen, GRAY,
                              (100 + i * 150, y_pos), 30, 1)

        # Заставка
        pygame.draw.rect(screen, WHITE, self.title_rect, 2)
        font = pygame.font.Font(None, 48)
        title_text = font.render("ASTEROIDS", True, WHITE)
        screen.blit(title_text, (self.title_rect.centerx - title_text.get_width() // 2,
                                self.title_rect.centery - 30))

        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Click to Start", True, WHITE)
        screen.blit(instruction_text, (self.title_rect.centerx - instruction_text.get_width() // 2,
                                      self.title_rect.centery + 20))

        # Отображение счета и жизней (если игра была)
        if self.game.score > 0 or self.game.lives < INITIAL_LIVES:
            score_font = pygame.font.Font(None, 36)
            score_text = score_font.render(f"Score: {self.game.score}", True, WHITE)
            lives_text = score_font.render(f"Lives: {self.game.lives}", True, WHITE)

            screen.blit(score_text, (20, 20))
            screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class GameplayState(GameState):
    """Состояние активной игры"""

    def __init__(self, game):
        super().__init__(game)
        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.asteroids = []
        self.missiles = []
        self.explosions = []
        self.asteroid_timer = 0

        # Создание начальных астероидов
        for _ in range(ASTEROID_COUNT):
            self.spawn_asteroid()

    def spawn_asteroid(self):
        """Создание нового астероида в случайном месте"""
        side = random.randint(0, 3)
        if side == 0:  # Сверху
            x = random.randint(0, SCREEN_WIDTH)
            y = -ASTEROID_MAX_SIZE
        elif side == 1:  # Справа
            x = SCREEN_WIDTH + ASTEROID_MAX_SIZE
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Снизу
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + ASTEROID_MAX_SIZE
        else:  # Слева
            x = -ASTEROID_MAX_SIZE
            y = random.randint(0, SCREEN_HEIGHT)

        self.asteroids.append(Asteroid(x, y))

    def handle_events(self, events):
        """Обработка событий игры"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Выстрел ракетой
                    new_missile = self.ship.fire_missile()
                    self.missiles.append(new_missile)

    def update(self):
        """Обновление игрового состояния"""
        # Управление кораблем
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.ship.rotate(-1)
        if keys[pygame.K_RIGHT]:
            self.ship.rotate(1)
        if keys[pygame.K_UP]:
            self.ship.thrust()
        else:
            self.ship.stop_thrust()

        # Обновление объектов
        self.ship.update()

        for asteroid in self.asteroids[:]:
            asteroid.update()

        for missile in self.missiles[:]:
            missile.update()
            if not missile.active:
                self.missiles.remove(missile)

        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        # Спавн новых астероидов
        self.asteroid_timer += 1
        if self.asteroid_timer >= ASTEROID_SPAWN_RATE:
            self.spawn_asteroid()
            self.asteroid_timer = 0

        # Проверка столкновений ракет с астероидами
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:
                if missile.collides_with(asteroid):
                    # Создание взрыва
                    self.explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))

                    # Удаление объектов
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)

                    # Начисление очков
                    self.game.score += 1
                    break

        # Проверка столкновений корабля с астероидами
        for asteroid in self.asteroids[:]:
            if self.ship.collides_with(asteroid):
                # Создание взрыва
                self.explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))

                # Удаление астероида
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)

                # Потеря жизни
                self.game.lives -= 1

                if self.game.lives <= 0:
                    # Конец игры
                    self.game.change_state("title")
                else:
                    # Возрождение корабля
                    self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                break

    def draw(self, screen):
        """Отрисовка игрового состояния"""
        screen.fill(BLACK)

        # Динамический фон
        for i in range(3):
            x_pos = (pygame.time.get_ticks() // 20 + i * 200) % SCREEN_WIDTH
            pygame.draw.circle(screen, (30, 30, 30),
                              (x_pos, 100 + i * 150), 20, 1)

        # Отрисовка объектов
        for asteroid in self.asteroids:
            asteroid.draw(screen)

        for missile in self.missiles:
            missile.draw(screen)

        for explosion in self.explosions:
            explosion.draw(screen)

        self.ship.draw(screen)

        # Отображение HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.game.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.game.lives}", True, WHITE)

        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class AsteroidsGame:
    """Основной класс игры Астероиды"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Астероиды")
        self.clock = pygame.time.Clock()

        # Игровые переменные
        self.score = 0
        self.lives = INITIAL_LIVES

        # Состояния игры
        self.states = {
            "title": TitleScreenState(self),
            "gameplay": GameplayState(self)
        }
        self.current_state = self.states["title"]

    def change_state(self, state_name):
        """Смена состояния игры"""
        self.current_state = self.states[state_name]

    def reset_game(self):
        """Сброс игры к начальным значениям"""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.states["gameplay"] = GameplayState(self)

    def run(self):
        """Главный игровой цикл"""
        running = True

        while running:
            # Обработка событий
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            # Обновление состояния
            self.current_state.handle_events(events)
            self.current_state.update()

            # Отрисовка
            self.current_state.draw(self.screen)
            pygame.display.flip()

            # Контроль FPS
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AsteroidsGame()
    game.run()
