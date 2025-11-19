import pygame
import sys
from config import *
from game_objects import *


class GameState:
    """Базовый класс для состояний игры"""

    def __init__(self, game):
        # Ссылка на главный объект игры
        self.game = game

    def handle_events(self, events):
        """Обработка событий"""
        # Пустая реализация - будет переопределена в дочерних классах
        pass

    def update(self):
        """Обновление состояния"""
        # Пустая реализация - будет переопределена в дочерних классах
        pass

    def draw(self, screen):
        """Отрисовка"""
        # Пустая реализация - будет переопределена в дочерних классах
        pass


class TitleScreenState(GameState):
    """Состояние заставки"""

    def __init__(self, game):
        # Вызов конструктора родительского класса
        super().__init__(game)
        # Таймер для отображения заставки
        self.timer = TITLE_SCREEN_DURATION
        # Создание прямоугольника для области заставки
        self.title_rect = pygame.Rect(
            # Вычисление координаты X для центрирования
            (SCREEN_WIDTH - TITLE_WIDTH) // 2,
            # Вычисление координаты Y для центрирования
            (SCREEN_HEIGHT - TITLE_HEIGHT) // 2,
            # Ширина заставки
            TITLE_WIDTH,
            # Высота заставки
            TITLE_HEIGHT
        )

    def handle_events(self, events):
        """Обработка событий заставки"""
        # Перебор всех событий
        for event in events:
            # Проверка типа события - нажатие кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Проверка клика по области заставки
                if self.title_rect.collidepoint(event.pos):
                    # Сброс игры
                    self.game.reset_game()
                    # Переход в состояние игрового процесса
                    self.game.change_state("gameplay")

    def update(self):
        """Обновление заставки"""
        # Уменьшение таймера
        self.timer -= 1
        # Сброс таймера при достижении нуля
        if self.timer <= 0:
            self.timer = TITLE_SCREEN_DURATION

    def draw(self, screen):
        """Отрисовка заставки"""
        # Заливка экрана черным цветом
        screen.fill(BLACK)

        # Динамический фон (движущиеся астероиды)
        # Создание 5 астероидов
        for i in range(5):
            # Вычисление позиции Y с анимацией движения
            y_pos = (pygame.time.get_ticks() // 50 + i * 100) % SCREEN_HEIGHT
            # Отрисовка астероида в виде круга
            pygame.draw.circle(screen, GRAY,
                              (100 + i * 150, y_pos), 30, 1)

        # Отрисовка рамки заставки
        pygame.draw.rect(screen, WHITE, self.title_rect, 2)
        # Создание шрифта размера 48
        font = pygame.font.Font(None, 48)
        # Создание текста "ASTEROIDS"
        title_text = font.render("ASTEROIDS", True, WHITE)
        # Отображение текста по центру заставки
        screen.blit(title_text, (self.title_rect.centerx - title_text.get_width() // 2,
                                self.title_rect.centery - 30))

        # Создание шрифта для инструкции
        instruction_font = pygame.font.Font(None, 24)
        # Создание текста инструкции
        instruction_text = instruction_font.render("Click to Start", True, WHITE)
        # Отображение инструкции под заголовком
        screen.blit(instruction_text, (self.title_rect.centerx - instruction_text.get_width() // 2,
                                      self.title_rect.centery + 20))
        
        # Проверка, была ли уже игра
        if self.game.score > 0 or self.game.lives < INITIAL_LIVES:
            # Создание шрифта для статистики
            score_font = pygame.font.Font(None, 36)
            # Создание текста счета
            score_text = score_font.render(f"Score: {self.game.score}", True, WHITE)
            # Создание текста количества жизней
            lives_text = score_font.render(f"Lives: {self.game.lives}", True, WHITE)

            # Отображение счета в левом верхнем углу
            screen.blit(score_text, (20, 20))
            # Отображение жизней в правом верхнем углу
            screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class GameplayState(GameState):
    """Состояние активной игры"""

    def __init__(self, game):
        # Вызов конструктора родительского класса
        super().__init__(game)
        # Создание корабля в центре экрана
        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # Список астероидов
        self.asteroids = []
        # Список ракет
        self.missiles = []
        # Список взрывов
        self.explosions = []
        # Таймер для спавна астероидов
        self.asteroid_timer = 0

        # Создание начальных астероидов
        for _ in range(ASTEROID_COUNT):
            self.spawn_asteroid()

    def spawn_asteroid(self):
        """Создание нового астероида в случайном месте"""
        # Случайный выбор стороны появления (0-3)
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

        # Добавление нового астероида в список
        self.asteroids.append(Asteroid(x, y))

    def handle_events(self, events):
        """Обработка событий игры"""
        for event in events:
            # Проверка нажатия клавиши
            if event.type == pygame.KEYDOWN:
                # Проверка нажатия пробела
                if event.key == pygame.K_SPACE:
                    # Выстрел ракетой
                    new_missile = self.ship.fire_missile()
                    # Добавление ракеты в список
                    self.missiles.append(new_missile)

    def update(self):
        """Обновление игрового состояния"""
        # Получение состояния всех клавиш
        keys = pygame.key.get_pressed()
        # Проверка нажатия стрелки влево
        if keys[pygame.K_LEFT]:
            # Поворот корабля против часовой стрелки
            self.ship.rotate(-1)
        # Проверка нажатия стрелки вправо
        if keys[pygame.K_RIGHT]:
            # Поворот корабля по часовой стрелке
            self.ship.rotate(1)
        # Проверка нажатия стрелки вверх
        if keys[pygame.K_UP]:
            # Включение двигателя
            self.ship.thrust()
        else:
            # Выключение двигателя
            self.ship.stop_thrust()

        # Обновление положения корабля
        self.ship.update()

        # Обновление всех астероидов
        for asteroid in self.asteroids[:]:
            asteroid.update()

        # Обновление всех ракет и удаление неактивных
        for missile in self.missiles[:]:
            missile.update()
            # Проверка активности ракеты
            if not missile.active:
                self.missiles.remove(missile)

        # Обновление всех взрывов и удаление завершенных
        for explosion in self.explosions[:]:
            explosion.update()
            # Проверка активности взрыва
            if not explosion.active:
                self.explosions.remove(explosion)

        # Увеличение таймера спавна астероидов
        self.asteroid_timer += 1
        # Проверка необходимости спавна нового астероида
        if self.asteroid_timer >= ASTEROID_SPAWN_RATE:
            self.spawn_asteroid()
            # Сброс таймера
            self.asteroid_timer = 0

        # Проверка столкновений ракет с астероидами
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:
                # Проверка столкновения
                if missile.collides_with(asteroid):
                    # Создание взрыва на месте астероида
                    self.explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))

                    # Удаление объектов
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)

                    # Начисление очков
                    self.game.score += 1
                    # Прерывание внутреннего цикла
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

                # Проверка окончания игры
                if self.game.lives <= 0:
                    # Переход к заставке
                    self.game.change_state("title")
                else:
                    # Возрождение корабля в центре
                    self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                break

    def draw(self, screen):
        """Отрисовка игрового состояния"""
        # Очистка экрана черным цветом
        screen.fill(BLACK)

        # Динамический фон (движущиеся звезды)
        for i in range(3):
            # Вычисление позиции X с анимацией движения
            x_pos = (pygame.time.get_ticks() // 20 + i * 200) % SCREEN_WIDTH
            # Отрисовка звезды
            pygame.draw.circle(screen, (30, 30, 30),
                              (x_pos, 100 + i * 150), 20, 1)

        # Отрисовка всех астероидов
        for asteroid in self.asteroids:
            asteroid.draw(screen)

        # Отрисовка всех ракет
        for missile in self.missiles:
            missile.draw(screen)

        # Отрисовка всех взрывов
        for explosion in self.explosions:
            explosion.draw(screen)

        # Отрисовка корабля
        self.ship.draw(screen)

        # Отображение HUD (интерфейса)
        font = pygame.font.Font(None, 36)
        # Создание текста счета
        score_text = font.render(f"Score: {self.game.score}", True, WHITE)
        # Создание текста жизней
        lives_text = font.render(f"Lives: {self.game.lives}", True, WHITE)

        # Отображение счета слева сверху
        screen.blit(score_text, (20, 20))
        # Отображение жизней справа сверху
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class AsteroidsGame:
    """Основной класс игры Астероиды"""

    def __init__(self):
        # Инициализация pygame
        pygame.init()
        # Создание игрового окна
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Установка заголовка окна
        pygame.display.set_caption("Астероиды")
        # Создание объекта часов для контроля FPS
        self.clock = pygame.time.Clock()

        # Игровые переменные
        self.score = 0
        self.lives = INITIAL_LIVES

        # Состояния игры
        self.states = {
            "title": TitleScreenState(self),
            "gameplay": GameplayState(self)
        }
        # Установка начального состояния
        self.current_state = self.states["title"]

    def change_state(self, state_name):
        """Смена состояния игры"""
        self.current_state = self.states[state_name]

    def reset_game(self):
        """Сброс игры к начальным значениям"""
        self.score = 0
        self.lives = INITIAL_LIVES
        # Пересоздание состояния геймплея
        self.states["gameplay"] = GameplayState(self)

    def run(self):
        """Главный игровой цикл"""
        running = True

        while running:
            # Получение всех событий
            events = pygame.event.get()
            # Обработка событий
            for event in events:
                # Проверка события закрытия окна
                if event.type == pygame.QUIT:
                    running = False

            # Обработка событий текущего состояния
            self.current_state.handle_events(events)
            # Обновление текущего состояния
            self.current_state.update()

            # Отрисовка текущего состояния
            self.current_state.draw(self.screen)
            # Обновление дисплея
            pygame.display.flip()

            # Ограничение FPS до 60 кадров в секунду
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AsteroidsGame()
    game.run()
