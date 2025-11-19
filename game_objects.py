import pygame
import math
import random
from config import *


class GameObject:
    """Базовый класс для всех игровых объектов"""

    def __init__(self, x, y, vx=0, vy=0):
        self.x = x #Координата X объекта
        self.y = y #Координата Y объекта
        self.vx = vx #Скорость по оси X
        self.vy = vy #Скорость по оси Y
        self.angle = 0 #Угол поворота объекта
        self.active = True #Флаг активности объекта

    def update(self):
        """Обновление позиции объекта"""
        self.x += self.vx #Обновление позиции по X
        self.y += self.vy #Обновление позиции по Y

        if self.x < 0: #Если объект вышел за левую границу
            self.x = SCREEN_WIDTH #Появляется с правой стороны
        elif self.x > SCREEN_WIDTH: #Если объект вышел за правую границу
            self.x = 0 #Появляется с левой стороны
        if self.y < 0: #Если объект вышел за верхнюю границу
            self.y = SCREEN_HEIGHT #Появляется снизу
        elif self.y > SCREEN_HEIGHT: #Если объект вышел за нижнюю границу
            self.y = 0 #Появляется сверху

    def draw(self, screen):
        """Абстрактный метод для отрисовки объекта"""
        pass #Должен быть реализован в дочерних классах

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        pass #Должен быть реализован в дочерних классах

    def collides_with(self, other):
        """Проверка столкновения с другим объектом"""
        rect1 = self.get_rect() #Получаем прямоугольник текущего объекта
        rect2 = other.get_rect() #Получаем прямоугольник другого объекта
        return rect1.colliderect(rect2) #Проверяем пересечение прямоугольников


class Ship(GameObject):
    """Класс корабля игрока"""

    def __init__(self, x, y):
        super().__init__(x, y) #Вызов конструктора родительского класса
        self.acceleration = 0 #Текущее ускорение корабля
        self.thrusting = False #Флаг работы двигателей
        self.size = SHIP_SIZE #Размер корабля

    def rotate(self, direction):
        """Вращение корабля"""
        self.angle += direction * SHIP_ROTATION_SPEED #Изменение угла поворота

    def thrust(self):
        """Включение двигателей"""
        self.thrusting = True #Устанавливаем флаг работы двигателей
        #Ускорение в направлении носа корабля
        angle_rad = math.radians(self.angle) #Переводим угол в радианы
        self.acceleration = SHIP_ACCELERATION #Устанавливаем ускорение
        self.vx += math.sin(angle_rad) * self.acceleration #Ускорение по X
        self.vy += -math.cos(angle_rad) * self.acceleration #Ускорение по Y

    def stop_thrust(self):
        """Выключение двигателей"""
        self.thrusting = False #Сбрасываем флаг работы двигателей
        self.acceleration = 0 #Обнуляем ускорение

    def update(self):
        """Обновление состояния корабля"""
        #Применяем сопротивление среды при выключенных двигателях
        if not self.thrusting: #Если двигатели выключены
            self.vx *= SHIP_DRAG #Замедление по X
            self.vy *= SHIP_DRAG #Замедление по Y

        super().update() #Вызов родительского метода update

    def draw(self, screen):
        """Отрисовка корабля"""
        angle_rad = math.radians(self.angle) #Перевод угла в радианы

        #Точки для треугольника корабля
        nose = (
            self.x + math.sin(angle_rad) * self.size, #Нос корабля
            self.y - math.cos(angle_rad) * self.size
        )

        left_wing = (
            self.x - math.cos(angle_rad) * self.size / 2, #Левое крыло
            self.y - math.sin(angle_rad) * self.size / 2
        )

        right_wing = (
            self.x + math.cos(angle_rad) * self.size / 2, #Правое крыло
            self.y + math.sin(angle_rad) * self.size / 2
        )

        #Рисуем корпус корабля
        pygame.draw.polygon(screen, WHITE, [nose, left_wing, right_wing], 2)

        #Рисуем двигатель при ускорении
        if self.thrusting: #Если двигатели работают
            #Точки для пламени двигателя
            flame_base = (
                self.x - math.sin(angle_rad) * self.size / 2, #Основание пламени
                self.y + math.cos(angle_rad) * self.size / 2
            )

            flame_tip = (
                self.x - math.sin(angle_rad) * self.size, #Кончик пламени
                self.y + math.cos(angle_rad) * self.size
            )

            left_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 - math.cos(angle_rad) * self.size / 4, #Левое пламя
                self.y + math.cos(angle_rad) * self.size / 1.5 - math.sin(angle_rad) * self.size / 4
            )

            right_flame = (
                self.x - math.sin(angle_rad) * self.size / 1.5 + math.cos(angle_rad) * self.size / 4, #Правое пламя
                self.y + math.cos(angle_rad) * self.size / 1.5 + math.sin(angle_rad) * self.size / 4
            )

            pygame.draw.polygon(screen, RED, [flame_base, left_flame, flame_tip, right_flame]) #Рисуем пламя

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size / 2, self.y - self.size / 2,
                           self.size, self.size) #Прямоугольник вокруг корабля

    def fire_missile(self):
        """Создание ракеты"""
        angle_rad = math.radians(self.angle) #Угол в радианах
        missile_x = self.x + math.sin(angle_rad) * self.size #Позиция X ракеты
        missile_y = self.y - math.cos(angle_rad) * self.size #Позиция Y ракеты
        missile_vx = math.sin(angle_rad) * MISSILE_SPEED + self.vx #Скорость X ракеты
        missile_vy = -math.cos(angle_rad) * MISSILE_SPEED + self.vy #Скорость Y ракеты

        return Missile(missile_x, missile_y, missile_vx, missile_vy) #Создаем ракету


class Asteroid(GameObject):
    """Класс астероида"""

    def __init__(self, x, y, size=None):
        if size is None: #Если размер не указан
            size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE) #Случайный размер

        super().__init__(x, y) #Вызов конструктора родителя
        self.size = size #Размер астероида
        self.rotation_speed = random.uniform(ASTEROID_MIN_ROTATION, ASTEROID_MAX_ROTATION) #Случайная скорость вращения

        #Случайное направление и скорость
        angle = random.uniform(0, 2 * math.pi) #Случайный угол движения
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED) #Случайная скорость
        self.vx = math.cos(angle) * speed #Скорость по X
        self.vy = math.sin(angle) * speed #Скорость по Y

        #Создание неправильной формы астероида
        self.points = [] #Список точек формы
        for i in range(8): #8 точек для формы
            angle_point = 2 * math.pi * i / 8 #Угол текущей точки
            distance = self.size * random.uniform(0.7, 1.3) #Случайное расстояние от центра
            self.points.append(( #Добавляем точку
                math.cos(angle_point) * distance, #X координата точки
                math.sin(angle_point) * distance #Y координата точки
            ))

    def update(self):
        """Обновление состояния астероида"""
        self.angle += self.rotation_speed #Вращение астероида
        super().update() #Вызов родительского update

    def draw(self, screen):
        """Отрисовка астероида с текстурой"""
        points_screen = [] #Точки для отрисовки
        for px, py in self.points: #Для каждой точки формы
            #Поворот точки
            rotated_x = px * math.cos(math.radians(self.angle)) - py * math.sin(math.radians(self.angle)) #Повернутый X
            rotated_y = px * math.sin(math.radians(self.angle)) + py * math.cos(math.radians(self.angle)) #Повернутый Y
            points_screen.append((self.x + rotated_x, self.y + rotated_y)) #Добавляем точку на экран

        #Рисуем заполненный астероид
        pygame.draw.polygon(screen, (150, 150, 150), points_screen) #Серый заполненный
        pygame.draw.polygon(screen, WHITE, points_screen, 2) #Белый контур

        #Добавляем текстуру - линии на поверхности
        for i in range(4): #4 текстуры
            texture_angle = self.angle + i * 45 #Угол текстуры
            start_x = self.x + math.cos(math.radians(texture_angle)) * self.size * 0.3 #Начало линии X
            start_y = self.y + math.sin(math.radians(texture_angle)) * self.size * 0.3 #Начало линии Y
            end_x = self.x + math.cos(math.radians(texture_angle)) * self.size * 0.8 #Конец линии X
            end_y = self.y + math.sin(math.radians(texture_angle)) * self.size * 0.8 #Конец линии Y
            pygame.draw.line(screen, (100, 100, 100), (start_x, start_y), (end_x, end_y), 1) #Рисуем линию

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2) #Прямоугольник вокруг астероида


class Missile(GameObject):
    """Класс ракеты"""

    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy) #Вызов конструктора родителя
        self.lifetime = MISSILE_LIFETIME #Время жизни ракеты
        self.size = MISSILE_SIZE #Размер ракеты

    def update(self):
        """Обновление состояния ракеты"""
        super().update() #Вызов родительского update
        self.lifetime -= 1 #Уменьшаем время жизни
        if self.lifetime <= 0: #Если время жизни истекло
            self.active = False #Деактивируем ракету

    def draw(self, screen):
        """Отрисовка ракеты"""
        #Определяем направление движения
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1: #Если есть движение
            missile_angle = math.degrees(math.atan2(self.vy, self.vx)) #Угол по направлению движения
        else:
            missile_angle = 0 #Угол по умолчанию

        angle_rad = math.radians(missile_angle) #Перевод в радианы

        #Три линии для простого но стильного вида
        length = self.size * 3 #Длина центральной линии

        #Центральная линия
        end_x = self.x + math.cos(angle_rad) * length #Конец линии X
        end_y = self.y + math.sin(angle_rad) * length #Конец линии Y
        pygame.draw.line(screen, YELLOW, (self.x, self.y), (end_x, end_y), 3) #Рисуем центральную линию

        #Боковые линии (крылья)
        wing_length = self.size * 2 #Длина крыльев
        left_wing_x = self.x + math.cos(angle_rad) * wing_length / 2 + math.sin(angle_rad) * self.size #Левое крыло X
        left_wing_y = self.y + math.sin(angle_rad) * wing_length / 2 - math.cos(angle_rad) * self.size #Левое крыло Y
        right_wing_x = self.x + math.cos(angle_rad) * wing_length / 2 - math.sin(angle_rad) * self.size #Правое крыло X
        right_wing_y = self.y + math.sin(angle_rad) * wing_length / 2 + math.cos(angle_rad) * self.size #Правое крыло Y

        pygame.draw.line(screen, RED, (self.x, self.y), (left_wing_x, left_wing_y), 2) #Левое крыло
        pygame.draw.line(screen, RED, (self.x, self.y), (right_wing_x, right_wing_y), 2) #Правое крыло

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2) #Прямоугольник вокруг ракеты


class Explosion:
    """Класс анимации взрыва"""

    def __init__(self, x, y, size):
        self.x = x #Позиция X взрыва
        self.y = y #Позиция Y взрыва
        self.size = size #Размер взрыва
        self.duration = EXPLOSION_DURATION #Длительность анимации
        self.active = True #Флаг активности взрыва

    def update(self):
        """Обновление состояния взрыва"""
        self.duration -= 1 #Уменьшаем длительность
        if self.duration <= 0: #Если анимация завершена
            self.active = False #Деактивируем взрыв

    def draw(self, screen):
        """Отрисовка взрыва"""
        progress = 1 - (self.duration / EXPLOSION_DURATION) #Прогресс анимации (0-1)
        current_size = self.size * (0.5 + progress * 0.5) #Текущий размер взрыва

        #Рисуем несколько кругов для эффекта взрыва
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)),
                           int(current_size), 2) #Внешний красный круг
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)),
                           int(current_size * 0.7), 1) #Внутренний белый круг
