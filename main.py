import pygame
import sys
from config import *
from game_objects import *


class GameState:
    """Базовый класс для состояний игры"""

    def __init__(self, game):
        #Сохраняем ссылку на главный объект игры
        self.game = game

    def handle_events(self, events):
        """Обработка событий"""
        pass  #Базовый метод, переопределяется в дочерних классах

    def update(self):
        """Обновление состояния"""
        pass  #Базовый метод, переопределяется в дочерних классах

    def draw(self, screen):
        """Отрисовка"""
        pass  #Базовый метод, переопределяется в дочерних классах


class TitleScreenState(GameState):
    """Состояние заставки"""

    def __init__(self, game):
        #Вызываем конструктор родительского класса
        super().__init__(game)
        #Таймер для анимаций на заставке
        self.timer = TITLE_SCREEN_DURATION
        #Прямоугольник области заставки по центру экрана
        self.title_rect = pygame.Rect(
            (SCREEN_WIDTH - TITLE_WIDTH) // 2,  #Центрируем по горизонтали
            (SCREEN_HEIGHT - TITLE_HEIGHT) // 2,  #Центрируем по вертикали
            TITLE_WIDTH,  #Ширина заставки
            TITLE_HEIGHT  #Высота заставки
        )

    def handle_events(self, events):
        """Обработка событий заставки"""
        #Перебираем все события в очереди
        for event in events:
            #Если событие - клик мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #Если клик был по области заставки
                if self.title_rect.collidepoint(event.pos):
                    #Сбрасываем игру и переходим к игровому процессу
                    self.game.reset_game()
                    self.game.change_state("gameplay")

    def update(self):
        """Обновление заставки"""
        #Уменьшаем таймер каждый кадр
        self.timer -= 1
        #Если таймер достиг нуля, сбрасываем его
        if self.timer <= 0:
            self.timer = TITLE_SCREEN_DURATION

    def draw(self, screen):
        """Отрисовка заставки"""
        #Заливаем экран черным цветом (неподвижный фон)
        screen.fill(BLACK)

        #Динамический фон (движущиеся астероиды)
        for i in range(5):
            #Разные скорости и стартовые позиции для каждого астероида
            speed_offset = i * 37  #Разные скорости для каждого астероида
            height_offset = i * 73  #Разные стартовые высоты
            #Вычисляем позицию X с учетом времени для движения влево
            x_pos = SCREEN_WIDTH - (pygame.time.get_ticks() // (50 + i * 5) + speed_offset) % (SCREEN_WIDTH + 300)
            #Вычисляем позицию Y с циклическим движением по вертикали
            y_pos = 50 + (height_offset + i * 60) % (SCREEN_HEIGHT - 100)
            #Рисуем астероид как серый круг с контуром
            pygame.draw.circle(screen, GRAY, (x_pos, y_pos), 25 + i * 3, 1)

        #Рисуем прямоугольник заставки с белым контуром
        pygame.draw.rect(screen, WHITE, self.title_rect, 2)
        #Создаем шрифт для заголовка
        font = pygame.font.Font(None, 48)
        #Создаем текстовую поверхность с названием игры
        title_text = font.render("ASTEROIDS", True, WHITE)
        #Отображаем заголовок по центру заставки
        screen.blit(title_text, (self.title_rect.centerx - title_text.get_width() // 2,
                                self.title_rect.centery - 30))

        #Создаем шрифт для инструкции
        instruction_font = pygame.font.Font(None, 24)
        #Создаем текстовую поверхность с инструкцией
        instruction_text = instruction_font.render("Нажмите чтобы начать", True, WHITE)
        #Отображаем инструкцию под заголовком
        screen.blit(instruction_text, (self.title_rect.centerx - instruction_text.get_width() // 2,
                                      self.title_rect.centery + 20))

        #Отображение счета и жизней (если игра была)
        if self.game.score > 0 or self.game.lives < INITIAL_LIVES:
            #Создаем шрифт для статистики
            score_font = pygame.font.Font(None, 36)
            #Создаем текстовую поверхность счета (зеленый цвет)
            score_text = score_font.render(f"Счёт: {self.game.score}", True, GREEN)
            #Создаем текстовую поверхность жизней (красный цвет)
            lives_text = score_font.render(f"Жизни: {self.game.lives}", True, RED)

            #Отображаем счет в левом верхнем углу
            screen.blit(score_text, (20, 20))
            #Отображаем жизни в правом верхнем углу
            screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class GameplayState(GameState):
    """Состояние активной игры"""

    def __init__(self, game):
        #Вызываем конструктор родительского класса
        super().__init__(game)
        #Создаем корабль в центре экрана
        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        #Список активных астероидов
        self.asteroids = []
        #Список активных ракет
        self.missiles = []
        #Список активных взрывов
        self.explosions = []
        #Таймер для спавна новых астероидов
        self.asteroid_timer = 0

        #Создание начальных астероидов
        for _ in range(ASTEROID_COUNT):
            self.spawn_asteroid()

    def spawn_asteroid(self):
        """Создание нового астероида в случайном месте"""
        #Случайно выбираем сторону появления (0-3)
        side = random.randint(0, 3)
        if side == 0:  #Сверху
            x = random.randint(0, SCREEN_WIDTH)
            y = -ASTEROID_MAX_SIZE
        elif side == 1:  #Справа
            x = SCREEN_WIDTH + ASTEROID_MAX_SIZE
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  #Снизу
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + ASTEROID_MAX_SIZE
        else:  #Слева
            x = -ASTEROID_MAX_SIZE
            y = random.randint(0, SCREEN_HEIGHT)

        #Добавляем новый астероид в список
        self.asteroids.append(Asteroid(x, y))

    def handle_events(self, events):
        """Обработка событий игры"""
        #Перебираем все события в очереди
        for event in events:
            #Если событие - нажатие клавиши
            if event.type == pygame.KEYDOWN:
                #Если нажат пробел
                if event.key == pygame.K_SPACE:
                    #Создаем новую ракету и добавляем в список
                    new_missile = self.ship.fire_missile()
                    self.missiles.append(new_missile)

    def update(self):
        """Обновление игрового состояния"""
        #Получаем состояние всех клавиш
        keys = pygame.key.get_pressed()
        #Вращение корабля влево при нажатии стрелки влево
        if keys[pygame.K_LEFT]:
            self.ship.rotate(-1)
        #Вращение корабля вправо при нажатии стрелки вправо
        if keys[pygame.K_RIGHT]:
            self.ship.rotate(1)
        #Включение двигателей при нажатии стрелки вверх
        if keys[pygame.K_UP]:
            self.ship.thrust()
        else:
            #Выключение двигателей при отпускании стрелки вверх
            self.ship.stop_thrust()

        #Обновление позиции корабля
        self.ship.update()

        #Обновление всех астероидов
        for asteroid in self.asteroids[:]:  # Используем копию списка для безопасного удаления
            asteroid.update()

        #Обновление всех ракет и удаление неактивных
        for missile in self.missiles[:]:
            missile.update()
            #Если время жизни ракеты истекло, удаляем ее
            if not missile.active:
                self.missiles.remove(missile)

        #Обновление всех взрывов и удаление завершенных
        for explosion in self.explosions[:]:
            explosion.update()
            #Если анимация взрыва завершена, удаляем ее
            if not explosion.active:
                self.explosions.remove(explosion)

        #Увеличиваем таймер спавна астероидов
        self.asteroid_timer += 1
        #Если таймер достиг порога, создаем новый астероид
        if self.asteroid_timer >= ASTEROID_SPAWN_RATE:
            self.spawn_asteroid()
            self.asteroid_timer = 0

        #Проверка столкновений ракет с астероидами
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:
                #Если ракета столкнулась с астероидом
                if missile.collides_with(asteroid):
                    #Создаем анимацию взрыва на месте астероида
                    self.explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))

                    #Удаляем ракету и астероид
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)

                    #Увеличиваем счет игрока
                    self.game.score += 1
                    break  #Прерываем внутренний цикл после столкновения

        #Проверка столкновений корабля с астероидами
        for asteroid in self.asteroids[:]:
            #Если корабль столкнулся с астероидом
            if self.ship.collides_with(asteroid):
                #Создаем анимацию взрыва на месте астероида
                self.explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))

                #Удаляем астероид
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)

                #Уменьшаем количество жизней
                self.game.lives -= 1

                #Если жизни закончились
                if self.game.lives <= 0:
                    #Переходим на заставку (конец игры)
                    self.game.change_state("title")
                else:
                    #Создаем новый корабль в центре экрана
                    self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                break  #Прерываем цикл после столкновения

    def draw(self, screen):
        """Отрисовка игрового состояния"""
        #Заливаем экран черным цветом
        screen.fill(BLACK)

        #Динамический фон (движущиеся астероиды на заднем плане)
        for i in range(3):
            #Вычисляем позицию X для движения влево
            x_pos = SCREEN_WIDTH - (pygame.time.get_ticks() // 40 + i * 200) % (SCREEN_WIDTH + 200)
            #Рисуем серый круг как фоновый астероид
            pygame.draw.circle(screen, (50, 50, 50), (x_pos, 100 + i * 150), 20, 1)

        #Отрисовка всех игровых астероидов
        for asteroid in self.asteroids:
            asteroid.draw(screen)

        #Отрисовка всех ракет
        for missile in self.missiles:
            missile.draw(screen)

        #Отрисовка всех взрывов
        for explosion in self.explosions:
            explosion.draw(screen)

        #Отрисовка корабля
        self.ship.draw(screen)

        #Отображение интерфейса
        font = pygame.font.Font(None, 36)
        #Создаем текстовую поверхность счета
        score_text = font.render(f"Счет: {self.game.score}", True, GREEN)
        #Создаем текстовую поверхность жизней
        lives_text = font.render(f"Жизни: {self.game.lives}", True, RED)

        #Отображаем счет в левом верхнем углу
        screen.blit(score_text, (20, 20))
        #Отображаем жизни в правом верхнем углу
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 20))


class AsteroidsGame:
    """Основной класс игры Астероиды"""

    def __init__(self):
        #Инициализируем pygame
        pygame.init()
        #Создаем окно игры с заданными размерами
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #Устанавливаем заголовок окна
        pygame.display.set_caption("Asteroids")
        #Создаем объект для контроля FPS
        self.clock = pygame.time.Clock()

        #Игровые переменные
        self.score = 0  # Начальный счет
        self.lives = INITIAL_LIVES  # Начальное количество жизней

        #Создаем словарь состояний игры
        self.states = {
            "title": TitleScreenState(self),  #Состояние заставки
            "gameplay": GameplayState(self)   #Состояние игрового процесса
        }
        #Устанавливаем начальное состояние - заставка
        self.current_state = self.states["title"]

    def change_state(self, state_name):
        """Смена состояния игры"""
        #Устанавливаем текущее состояние по имени
        self.current_state = self.states[state_name]

    def reset_game(self):
        """Сброс игры к начальным значениям"""
        #Сбрасываем счет и жизни
        self.score = 0
        self.lives = INITIAL_LIVES
        #Пересоздаем состояние игрового процесса
        self.states["gameplay"] = GameplayState(self)

    def run(self):
        """Главный игровой цикл"""
        running = True  #Флаг работы игры

        #Главный игровой цикл
        while running:
            #Получаем все события из очереди
            events = pygame.event.get()
            #Обрабатываем каждое событие
            for event in events:
                #Если событие - закрытие окна
                if event.type == pygame.QUIT:
                    #Завершаем игровой цикл
                    running = False

            #Обрабатываем события в текущем состоянии
            self.current_state.handle_events(events)
            #Обновляем логику в текущем состоянии
            self.current_state.update()
            #Отрисовываем текущее состояние
            self.current_state.draw(self.screen)
            #Обновляем экран
            pygame.display.flip()

            #Ограничиваем FPS 60 кадрами в секунду
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AsteroidsGame()
    game.run()
