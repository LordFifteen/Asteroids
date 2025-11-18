import pygame
import math
import random
from config import *


class GameObject:
    """Базовый класс для всех игровых объектов"""

    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = 0
        self.active = True

    def update(self):
        """Обновление позиции объекта"""
        self.x += self.vx
        self.y += self.vy

        # Тороидальная геометрия
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0

    def draw(self, screen):
        """Абстрактный метод для отрисовки объекта"""
        pass

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        pass

    def collides_with(self, other):
        """Проверка столкновения с другим объектом"""
        rect1 = self.get_rect()
        rect2 = other.get_rect()
        return rect1.colliderect(rect2)


class Ship(GameObject):
    """Класс корабля игрока"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.acceleration = 0
        self.thrusting = False
        self.size = SHIP_SIZE

    def rotate(self, direction):
        """Вращение корабля"""
        self.angle += direction * SHIP_ROTATION_SPEED

    def thrust(self):
        """Включение двигателей"""
        self.thrusting = True
        # Ускорение в направлении носа корабля
        angle_rad = math.radians(self.angle)
        self.acceleration = SHIP_ACCELERATION
        self.vx += math.sin(angle_rad) * self.acceleration
        self.vy += -math.cos(angle_rad) * self.acceleration

    def stop_thrust(self):
        """Выключение двигателей"""
        self.thrusting = False
        self.acceleration = 0

    def update(self):
        """Обновление состояния корабля"""
        # Применяем сопротивление среды при выключенных двигателях
        if not self.thrusting:
            self.vx *= SHIP_DRAG
            self.vy *= SHIP_DRAG

        super().update()

    def draw(self, screen):
        """Отрисовка корабля"""
        angle_rad = math.radians(self.angle)

        # Точки для треугольника корабля
        nose = (
            self.x + math.sin(angle_rad) * self.size,
            self.y - math.cos(angle_rad) * self.size
        )

        left_wing = (
            self.x - math.cos(angle_rad) * self.size / 2,
            self.y - math.sin(angle_rad) * self.size / 2
        )

        right_wing = (
            self.x + math.cos(angle_rad) * self.size / 2,
            self.y + math.sin(angle_rad) * self.size / 2
        )

        # Рисуем корпус корабля
        pygame.draw.polygon(screen, WHITE, [nose, left_wing, right_wing], 2)

        # Рисуем двигатель при ускорении
        if self.thrusting:
            # Точки для пламени двигателя
            flame_base = (
                self.x - math.sin(angle_rad) * self.size / 2,
                self.y + math.cos(angle_rad) * self.size / 2
            )

            flame_tip = (
                self.x - math.sin(angle_rad) * self.size,
                self.y + math.cos(angle_rad) * self.size
            )

            left_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 - math.cos(angle_rad) * self.size / 4,
                self.y + math.cos(angle_rad) * self.size / 1.5 - math.sin(angle_rad) * self.size / 4
            )

            right_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 + math.cos(angle_rad) * self.size / 4,
                self.y + math.cos(angle_rad) * self.size / 1.5 + math.sin(angle_rad) * self.size / 4
            )

            pygame.draw.polygon(screen, RED, [flame_base, left_flame, flame_tip, right_flame])

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size / 2, self.y - self.size / 2,
                           self.size, self.size)

    def fire_missile(self):
        """Создание ракеты"""
        angle_rad = math.radians(self.angle)
        missile_x = self.x + math.sin(angle_rad) * self.size
        missile_y = self.y - math.cos(angle_rad) * self.size
        missile_vx = math.sin(angle_rad) * MISSILE_SPEED + self.vx
        missile_vy = -math.cos(angle_rad) * MISSILE_SPEED + self.vy

        return Missile(missile_x, missile_y, missile_vx, missile_vy)


class Asteroid(GameObject):
    """Класс астероида"""

    def __init__(self, x, y, size=None):
        if size is None:
            size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)

        super().__init__(x, y)
        self.size = size
        self.rotation_speed = random.uniform(ASTEROID_MIN_ROTATION, ASTEROID_MAX_ROTATION)

        # Случайное направление и скорость
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Создание неправильной формы астероида
        self.points = []
        for i in range(8):
            angle_point = 2 * math.pi * i / 8
            distance = self.size * random.uniform(0.7, 1.3)
            self.points.append((
                math.cos(angle_point) * distance,
                math.sin(angle_point) * distance
            ))

    def update(self):
        """Обновление состояния астероида"""
        self.angle += self.rotation_speed
        super().update()

    def draw(self, screen):
        """Отрисовка астероида"""
        points_screen = []
        for px, py in self.points:
            # Поворот точки
            rotated_x = px * math.cos(math.radians(self.angle)) - py * math.sin(math.radians(self.angle))
            rotated_y = px * math.sin(math.radians(self.angle)) + py * math.cos(math.radians(self.angle))
            points_screen.append((self.x + rotated_x, self.y + rotated_y))

        pygame.draw.polygon(screen, WHITE, points_screen, 2)

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)


class Missile(GameObject):
    """Класс ракеты"""

    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy)
        self.lifetime = MISSILE_LIFETIME
        self.size = MISSILE_SIZE

    def update(self):
        """Обновление состояния ракеты"""
        super().update()
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def draw(self, screen):
        """Отрисовка ракеты"""
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)


class Explosion:
    """Класс анимации взрыва"""

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.duration = EXPLOSION_DURATION
        self.active = True

    def update(self):
        """Обновление состояния взрыва"""
        self.duration -= 1
        if self.duration <= 0:
            self.active = False

    def draw(self, screen):
        """Отрисовка взрыва"""
        progress = 1 - (self.duration / EXPLOSION_DURATION)
        current_size = self.size * (0.5 + progress * 0.5)

        # Рисуем несколько кругов для эффекта взрыва
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)),
                           int(current_size), 2)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)),
                           int(current_size * 0.7), 1)
