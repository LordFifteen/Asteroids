import pygame      
import math       
import random     
from config import *  


class GameObject:
    """Базовый класс для всех игровых объектов"""

    def __init__(self, x, y, vx=0, vy=0):
        self.x = x          # Координата X на экране
        self.y = y          # Координата Y на экране
        self.vx = vx        # Скорость по оси X (пикселей за кадр)
        self.vy = vy        # Скорость по оси Y (пикселей за кадр)
        self.angle = 0      # Угол поворота объекта в градусах
        self.active = True  # Флаг активности объекта (False - подлежит удалению)

    def update(self):
        """Обновление позиции объекта"""
        # Двигаем объект согласно его скорости
        self.x += self.vx   # Изменяем X на значение скорости по X
        self.y += self.vy   # Изменяем Y на значение скорости по Y

        if self.x < 0:                      # Если объект вышел за левую границу
            self.x = SCREEN_WIDTH           # Появляется у правой границы
        elif self.x > SCREEN_WIDTH:         # Если объект вышел за правую границу
            self.x = 0                      # Появляется у левой границы
        if self.y < 0:                      # Если объект вышел за верхнюю границу
            self.y = SCREEN_HEIGHT          # Появляется у нижней границы
        elif self.y > SCREEN_HEIGHT:        # Если объект вышел за нижнюю границу
            self.y = 0                      # Появляется у верхней границы

    def draw(self, screen):
        """Абстрактный метод для отрисовки объекта"""
        pass  # Должен быть реализован в дочерних классах

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        pass  # Должен быть реализован в дочерних классах

    def collides_with(self, other):
        """Проверка столкновения с другим объектом"""
        rect1 = self.get_rect()    # Получаем прямоугольник текущего объекта
        rect2 = other.get_rect()   # Получаем прямоугольник другого объекта
        return rect1.colliderect(rect2)  # Проверяем пересечение прямоугольников с помощью Pygame


class Ship(GameObject):
    """Класс корабля игрока"""

    def __init__(self, x, y):
        super().__init__(x, y)     # Вызов конструктора родительского класса GameObject
        self.acceleration = 0      # Текущее значение ускорения
        self.thrusting = False     # Флаг работы двигателей (True - двигатели включены)
        self.size = SHIP_SIZE      # Размер корабля (берется из конфига)

    def rotate(self, direction):
        """Вращение корабля"""
        # direction: -1 - вращение влево, 1 - вращение вправо
        self.angle += direction * SHIP_ROTATION_SPEED  # Изменяем угол на скорость вращения

    def thrust(self):
        """Включение двигателей"""
        self.thrusting = True      # Устанавливаем флаг работы двигателей
        # Ускорение в направлении носа корабля
        angle_rad = math.radians(self.angle)          # Переводим угол из градусов в радианы
        self.acceleration = SHIP_ACCELERATION         # Устанавливаем ускорение из конфига
        # Добавляем к скорости компоненты ускорения по направлению носа корабля
        self.vx += math.sin(angle_rad) * self.acceleration    # X-компонента ускорения
        self.vy += -math.cos(angle_rad) * self.acceleration   # Y-компонента ускорения (минус из-за системы координат Pygame)

    def stop_thrust(self):
        """Выключение двигателей"""
        self.thrusting = False     # Выключаем флаг работы двигателей
        self.acceleration = 0      # Обнуляем ускорение

    def update(self):
        """Обновление состояния корабля"""
        if not self.thrusting:             # Если двигатели выключены
            self.vx *= SHIP_DRAG           # Умножаем скорость X на коэффициент сопротивления
            self.vy *= SHIP_DRAG           # Умножаем скорость Y на коэффициент сопротивления

        super().update()  # Вызываем метод update родительского класса

    def draw(self, screen):
        """Отрисовка корабля"""
        angle_rad = math.radians(self.angle)  # Переводим угол в радианы для вычислений

        # Точки для треугольника корабля
        # Нос корабля - вперед по направлению угла
        nose = (
            self.x + math.sin(angle_rad) * self.size,    # X координата носа
            self.y - math.cos(angle_rad) * self.size     # Y координата носа
        )

        # Левое крыло корабля
        left_wing = (
            self.x - math.cos(angle_rad) * self.size / 2,    # X координата левого крыла
            self.y - math.sin(angle_rad) * self.size / 2     # Y координата левого крыла
        )

        # Правое крыло корабля
        right_wing = (
            self.x + math.cos(angle_rad) * self.size / 2,    # X координата правого крыла
            self.y + math.sin(angle_rad) * self.size / 2     # Y координата правого крыла
        )

        # Рисуем корпус корабля - белый треугольник с толщиной линии 2 пикселя
        pygame.draw.polygon(screen, WHITE, [nose, left_wing, right_wing], 2)

        # Рисуем двигатель при ускорении
        if self.thrusting:
            # Точки для пламени двигателя
            # Основание пламени (у кормы корабля)
            flame_base = (
                self.x - math.sin(angle_rad) * self.size / 2,    # X основания пламени
                self.y + math.cos(angle_rad) * self.size / 2     # Y основания пламени
            )

            # Кончик пламени (самая дальняя точка)
            flame_tip = (
                self.x - math.sin(angle_rad) * self.size,        # X кончика пламени
                self.y + math.cos(angle_rad) * self.size         # Y кончика пламени
            )

            # Левая точка пламени (для создания объемного эффекта)
            left_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 - math.cos(angle_rad) * self.size / 4,  # X левой точки
                self.y + math.cos(angle_rad) * self.size / 1.5 - math.sin(angle_rad) * self.size / 4   # Y левой точки
            )

            # Правая точка пламени (для создания объемного эффекта)
            right_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 + math.cos(angle_rad) * self.size / 4,  # X правой точки
                self.y + math.cos(angle_rad) * self.size / 1.5 + math.sin(angle_rad) * self.size / 4   # Y правой точки
            )

            # Рисуем красный многоугольник пламени
            pygame.draw.polygon(screen, RED, [flame_base, left_flame, flame_tip, right_flame])

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        # Создаем прямоугольник с центром в позиции корабля
        return pygame.Rect(self.x - self.size / 2,   # Левый край (X центра - половина размера)
                           self.y - self.size / 2,   # Верхний край (Y центра - половина размера)
                           self.size,                # Ширина прямоугольника
                           self.size)                # Высота прямоугольника

    def fire_missile(self):
        """Создание ракеты"""
        angle_rad = math.radians(self.angle)  # Переводим угол в радианы
        # Позиция выстрела - перед носом корабля
        missile_x = self.x + math.sin(angle_rad) * self.size    # X позиции ракеты
        missile_y = self.y - math.cos(angle_rad) * self.size    # Y позиции ракеты
        # Скорость ракеты = скорость выстрела + скорость корабля (для сохранения инерции)
        missile_vx = math.sin(angle_rad) * MISSILE_SPEED + self.vx  # X-компонента скорости ракеты
        missile_vy = -math.cos(angle_rad) * MISSILE_SPEED + self.vy # Y-компонента скорости ракеты

        # Создаем и возвращаем новый объект ракеты
        return Missile(missile_x, missile_y, missile_vx, missile_vy)


class Asteroid(GameObject):
    """Класс астероида"""

    def __init__(self, x, y, size=None):
        # Если размер не указан, генерируем случайный размер
        if size is None:
            size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)  # Случайный размер в заданном диапазоне

        super().__init__(x, y)  # Вызов конструктора родительского класса
        self.size = size        # Размер астероида
        # Случайная скорость вращения в заданном диапазоне
        self.rotation_speed = random.uniform(ASTEROID_MIN_ROTATION, ASTEROID_MAX_ROTATION)

        # Случайное направление и скорость движения
        angle = random.uniform(0, 2 * math.pi)  # Случайный угол в радианах (0-360 градусов)
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)  # Случайная скорость
        # Разложение скорости на компоненты X и Y
        self.vx = math.cos(angle) * speed  # X-компонента скорости
        self.vy = math.sin(angle) * speed  # Y-компонента скорости

        # Создание неправильной формы астероида
        self.points = []  # Список для хранения точек контура астероида
        for i in range(8):  # Создаем 8 точек для формы астероида
            angle_point = 2 * math.pi * i / 8  # Равномерное распределение углов (0°, 45°, 90°...)
            # Случайное расстояние от центра (для создания неровной формы)
            distance = self.size * random.uniform(0.7, 1.3)
            # Добавляем точку в локальные координаты (относительно центра)
            self.points.append((
                math.cos(angle_point) * distance,  # X координата точки
                math.sin(angle_point) * distance   # Y координата точки
            ))

    def update(self):
        """Обновление состояния астероида"""
        self.angle += self.rotation_speed  # Вращаем астероид
        super().update()  # Вызываем метод update родительского класса

    def draw(self, screen):
        """Отрисовка астероида"""
        points_screen = []  # Список для точек в экранных координатах
        for px, py in self.points:  # Проходим по всем точкам контура
            # Поворот точки согласно текущему углу астероида
            # Формулы поворота точки вокруг начала координат:
            rotated_x = px * math.cos(math.radians(self.angle)) - py * math.sin(math.radians(self.angle))  # Повернутый X
            rotated_y = px * math.sin(math.radians(self.angle)) + py * math.cos(math.radians(self.angle))  # Повернутый Y
            # Добавляем точку в экранные координаты (с учетом позиции астероида)
            points_screen.append((self.x + rotated_x, self.y + rotated_y))

        # Рисуем астероид как белый многоугольник с толщиной линии 2 пикселя
        pygame.draw.polygon(screen, WHITE, points_screen, 2)

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        # Создаем прямоугольник, охватывающий весь астероид
        return pygame.Rect(self.x - self.size,    # Левый край (X центра - размер)
                           self.y - self.size,    # Верхний край (Y центра - размер)
                           self.size * 2,         # Ширина (2 * размер)
                           self.size * 2)         # Высота (2 * размер)


class Missile(GameObject):
    """Класс ракеты"""

    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy)  # Вызов конструктора родительского класса
        self.lifetime = MISSILE_LIFETIME  # Время жизни ракеты в кадрах
        self.size = MISSILE_SIZE          # Размер ракеты

    def update(self):
        """Обновление состояния ракеты"""
        super().update()      # Вызываем метод update родительского класса (движение)
        self.lifetime -= 1    # Уменьшаем время жизни на 1 кадр
        if self.lifetime <= 0:  # Если время жизни истекло
            self.active = False # Помечаем ракету как неактивную (для удаления)

    def draw(self, screen):
        """Отрисовка ракеты"""
        # Рисуем ракету как белый круг
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        # Создаем прямоугольник, охватывающий ракету
        return pygame.Rect(self.x - self.size,    # Левый край (X центра - размер)
                           self.y - self.size,    # Верхний край (Y центра - размер)
                           self.size * 2,         # Ширина (2 * размер)
                           self.size * 2)         # Высота (2 * размер)


class Explosion:
    """Класс анимации взрыва"""

    def __init__(self, x, y, size):
        self.x = x                  # Координата X центра взрыва
        self.y = y                  # Координата Y центра взрыва
        self.size = size            # Базовый размер взрыва
        self.duration = EXPLOSION_DURATION  # Длительность анимации в кадрах
        self.active = True          # Флаг активности взрыва

    def update(self):
        """Обновление состояния взрыва"""
        self.duration -= 1          # Уменьшаем оставшееся время
        if self.duration <= 0:      # Если время истекло
            self.active = False     # Помечаем взрыв как неактивный

    def draw(self, screen):
        """Отрисовка взрыва"""
        # Прогресс анимации (0 в начале, 1 в конце)
        progress = 1 - (self.duration / EXPLOSION_DURATION)
        # Текущий размер взрыва (увеличивается со временем)
        current_size = self.size * (0.5 + progress * 0.5)

        # Рисуем несколько кругов для эффекта взрыва
        # Внешний красный круг
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)),
                           int(current_size), 2)  # Круг с толщиной линии 2 пикселя
        # Внутренний белый круг
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)),
                           int(current_size * 0.7), 1)  # Круг с толщиной линии 1 пиксель
