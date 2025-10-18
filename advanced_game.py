#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная 3D игра на Panda3D с коллизиями и эффектами
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    Vec3, Vec4, Point3, AmbientLight, DirectionalLight,
    TextNode
)
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, LerpColorInterval
import random
import math

class AdvancedGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Отключаем стандартное управление камерой
        self.disableMouse()
        
        # Настройки игры
        self.player_pos = Vec3(0, 0, 1)
        self.player_speed = 15
        self.camera_distance = 12
        self.camera_height = 8
        self.score = 0
        self.coins = []
        
        # Настройка освещения и сцены
        self.setup_lighting()
        self.setup_scene()
        self.setup_player()
        self.setup_controls()
        self.setup_camera()
        self.setup_ui()
        self.setup_collectibles()
        
        # Запуск игрового цикла
        self.taskMgr.add(self.update_game, "update_game")
        self.taskMgr.add(self.animate_coins, "animate_coins")
    
    def setup_lighting(self):
        """Улучшенное освещение"""
        # Окружающий свет
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.4, 0.4, 0.6, 1))
        alightNP = self.render.attachNewNode(alight)
        self.render.setLight(alightNP)
        
        # Основной направленный свет
        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(-2, -2, -1))
        dlight.setColor(Vec4(0.8, 0.8, 0.7, 1))
        dlightNP = self.render.attachNewNode(dlight)
        self.render.setLight(dlightNP)
        
        # Дополнительный свет для подсветки
        dlight2 = DirectionalLight('directionalLight2')
        dlight2.setDirection(Vec3(2, 2, -1))
        dlight2.setColor(Vec4(0.3, 0.3, 0.4, 1))
        dlight2NP = self.render.attachNewNode(dlight2)
        self.render.setLight(dlight2NP)
    
    def setup_scene(self):
        """Создание детализированной сцены"""
        # Земля
        self.ground = self.loader.loadModel("models/box")
        if self.ground:
            self.ground.reparentTo(self.render)
            self.ground.setScale(30, 30, 0.5)
            self.ground.setPos(0, 0, -0.5)
            self.ground.setColor(0.2, 0.6, 0.2, 1)
        
        # Создаем лабиринт из стен
        self.create_maze()
        
        # Декоративные элементы
        self.create_decorations()
    
    def create_maze(self):
        """Создание простого лабиринта"""
        wall_positions = [
            # Внешние стены
            (0, 15, 2), (0, -15, 2), (15, 0, 2), (-15, 0, 2),
            # Внутренние стены
            (5, 5, 2), (-5, -5, 2), (5, -5, 2), (-5, 5, 2),
            (10, 10, 2), (-10, -10, 2), (10, -10, 2), (-10, 10, 2),
            (0, 8, 2), (8, 0, 2), (0, -8, 2), (-8, 0, 2)
        ]
        
        self.walls = []
        for pos in wall_positions:
            wall = self.loader.loadModel("models/box")
            if wall:
                wall.reparentTo(self.render)
                wall.setScale(1, 1, 4)
                wall.setPos(pos[0], pos[1], pos[2])
                wall.setColor(0.6, 0.4, 0.2, 1)  # Коричневый цвет
                self.walls.append(wall)
    
    def create_decorations(self):
        """Создание декоративных элементов"""
        # Создаем несколько "деревьев"
        tree_positions = [
            (12, 12, 0), (-12, -12, 0), (12, -12, 0), (-12, 12, 0),
            (6, 12, 0), (-6, -12, 0), (12, 6, 0), (-12, -6, 0)
        ]
        
        for pos in tree_positions:
            # Ствол
            trunk = self.loader.loadModel("models/box")
            if trunk:
                trunk.reparentTo(self.render)
                trunk.setScale(0.5, 0.5, 3)
                trunk.setPos(pos[0], pos[1], 1.5)
                trunk.setColor(0.4, 0.2, 0.1, 1)
            
            # Крона
            crown = self.loader.loadModel("models/box")
            if crown:
                crown.reparentTo(self.render)
                crown.setScale(2, 2, 2)
                crown.setPos(pos[0], pos[1], 4)
                crown.setColor(0.1, 0.5, 0.1, 1)
    
    def setup_player(self):
        """Настройка игрока с улучшенным внешним видом"""
        self.player = self.loader.loadModel("models/box")
        if self.player:
            self.player.reparentTo(self.render)
            self.player.setScale(0.8, 0.8, 1.6)
            self.player.setPos(self.player_pos)
            self.player.setColor(0.2, 0.5, 1, 1)  # Синий цвет
            
            # Добавляем "голову" игрока
            head = self.loader.loadModel("models/box")
            if head:
                head.reparentTo(self.player)
                head.setScale(0.6, 0.6, 0.6)
                head.setPos(0, 0, 1.2)
                head.setColor(1, 0.8, 0.6, 1)  # Цвет кожи
    
    def setup_collectibles(self):
        """Создание предметов для сбора"""
        coin_positions = [
            (3, 3, 1), (-3, -3, 1), (3, -3, 1), (-3, 3, 1),
            (7, 7, 1), (-7, -7, 1), (7, -7, 1), (-7, 7, 1),
            (0, 5, 1), (5, 0, 1), (0, -5, 1), (-5, 0, 1)
        ]
        
        for pos in coin_positions:
            coin = self.loader.loadModel("models/box")
            if coin:
                coin.reparentTo(self.render)
                coin.setScale(0.5, 0.5, 0.1)
                coin.setPos(pos[0], pos[1], pos[2])
                coin.setColor(1, 1, 0, 1)  # Золотой цвет
                self.coins.append(coin)
    
    def setup_camera(self):
        """Настройка камеры с плавным следованием"""
        self.update_camera()
    
    def setup_controls(self):
        """Настройка управления"""
        self.keys = {
            'w': False, 'a': False, 's': False, 'd': False,
            'up': False, 'left': False, 'down': False, 'right': False
        }
        
        # WASD управление
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        
        # Стрелки как альтернатива
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_left", self.set_key, ["left", True])
        self.accept("arrow_left-up", self.set_key, ["left", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        self.accept("arrow_right", self.set_key, ["right", True])
        self.accept("arrow_right-up", self.set_key, ["right", False])
        
        self.accept("escape", self.exit_game)
    
    def setup_ui(self):
        """Улучшенный пользовательский интерфейс"""
        self.title = OnscreenText(
            text="3D Приключение",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(0, 0.9),
            scale=0.1
        )
        
        self.instructions = OnscreenText(
            text="WASD/Стрелки - движение\nСобирайте золотые монеты!\nESC - выход",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(-1.3, -0.8),
            scale=0.05,
            align=TextNode.ALeft
        )
        
        self.score_text = OnscreenText(
            text=f"Счёт: {self.score}",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(1.2, 0.9),
            scale=0.07,
            align=TextNode.ARight
        )
    
    def set_key(self, key, value):
        """Обработка нажатий клавиш"""
        self.keys[key] = value
    
    def update_camera(self):
        """Плавное обновление камеры"""
        target_x = self.player_pos.x - self.camera_distance * 0.7
        target_y = self.player_pos.y - self.camera_distance * 0.7
        target_z = self.player_pos.z + self.camera_height
        
        current_pos = self.camera.getPos()
        new_x = current_pos.x + (target_x - current_pos.x) * 0.1
        new_y = current_pos.y + (target_y - current_pos.y) * 0.1
        new_z = current_pos.z + (target_z - current_pos.z) * 0.1
        
        self.camera.setPos(new_x, new_y, new_z)
        self.camera.lookAt(self.player_pos)
    
    def check_coin_collision(self):
        """Проверка столкновений с монетами"""
        for coin in self.coins[:]:  # Создаем копию списка для безопасного удаления
            coin_pos = coin.getPos()
            distance = (self.player_pos - coin_pos).length()
            
            if distance < 2:  # Дистанция для сбора монеты
                coin.removeNode()
                self.coins.remove(coin)
                self.score += 10
                self.score_text.setText(f"Счёт: {self.score}")
                
                # Проверяем, собраны ли все монеты
                if not self.coins:
                    self.show_victory()
    
    def check_wall_collision(self, new_pos):
        """Простая проверка столкновений со стенами"""
        for wall in self.walls:
            wall_pos = wall.getPos()
            distance = (new_pos - wall_pos).length()
            
            if distance < 2:  # Дистанция столкновения
                return True
        return False
    
    def show_victory(self):
        """Показ сообщения о победе"""
        victory_text = OnscreenText(
            text="ПОБЕДА!\nВы собрали все монеты!",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(0, 0),
            scale=0.15,
            align=TextNode.ACenter
        )
        
        # Анимация победного текста
        victory_seq = Sequence(
            LerpColorInterval(victory_text, 0.5, Vec4(1, 0, 0, 1)),
            LerpColorInterval(victory_text, 0.5, Vec4(1, 1, 0, 1)),
            LerpColorInterval(victory_text, 0.5, Vec4(0, 1, 0, 1)),
            LerpColorInterval(victory_text, 0.5, Vec4(1, 1, 0, 1))
        )
        victory_seq.loop()
    
    def animate_coins(self, task):
        """Анимация монет"""
        time = task.time
        for i, coin in enumerate(self.coins):
            original_pos = coin.getPos()
            # Вращение
            coin.setH(time * 90 + i * 45)
            # Плавание вверх-вниз
            offset = math.sin(time * 2 + i) * 0.3
            coin.setZ(1 + offset)
        
        return task.cont
    
    def update_game(self, task):
        """Главный игровой цикл"""
        dt = self.globalClock.getDt()
        new_pos = Vec3(self.player_pos)
        
        # Обработка движения
        move_speed = self.player_speed * dt
        
        if self.keys['w'] or self.keys['up']:
            new_pos.y += move_speed
        if self.keys['s'] or self.keys['down']:
            new_pos.y -= move_speed
        if self.keys['a'] or self.keys['left']:
            new_pos.x -= move_speed
        if self.keys['d'] or self.keys['right']:
            new_pos.x += move_speed
        
        # Проверка столкновений перед движением
        if not self.check_wall_collision(new_pos):
            self.player_pos = new_pos
            if self.player:
                self.player.setPos(self.player_pos)
        
        # Проверка сбора монет
        self.check_coin_collision()
        
        # Обновление камеры
        self.update_camera()
        
        return task.cont
    
    def exit_game(self):
        """Выход из игры"""
        print(f"Игра завершена! Финальный счёт: {self.score}")
        self.userExit()

# Запуск улучшенной игры
if __name__ == "__main__":
    game = AdvancedGame()
    game.run()