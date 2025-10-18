#!/usr/bin/env python3
"""
Enhanced 3D Adventure Game
Collect coins, avoid obstacles, explore the world!
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight, DirectionalLight, Vec3, Vec4, TextNode,
    CollisionTraverser, CollisionSphere, CollisionNode,
    CollisionHandlerEvent
)
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, LerpHprInterval
import sys
import random
import math

class AdventureGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Disable default camera control
        self.disableMouse()
        
        # Game variables
        self.player_pos = Vec3(0, 0, 1)
        self.player_speed = 12
        self.score = 0
        self.coins = []
        self.obstacles = []
        self.current_house = None
        
        # Movement keys
        self.keys = {
            'w': False, 'a': False, 's': False, 'd': False,
            'up': False, 'left': False, 'down': False, 'right': False
        }
        
        # Setup game
        self.setup_lighting()
        self.setup_scene()
        self.setup_player()
        self.setup_collectibles()
        self.setup_controls()
        self.setup_camera()
        self.setup_ui()
        
        # Start game loops
        self.taskMgr.add(self.update_game, "update_game")
        self.taskMgr.add(self.animate_scene, "animate_scene")
    
    def setup_lighting(self):
        """Enhanced lighting setup"""
        # Warm ambient light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.4, 0.4, 0.5, 1))
        alightNP = self.render.attachNewNode(alight)
        self.render.setLight(alightNP)
        
        # Main directional light
        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(-2, -2, -1))
        dlight.setColor(Vec4(0.9, 0.8, 0.7, 1))
        dlightNP = self.render.attachNewNode(dlight)
        self.render.setLight(dlightNP)
        
        # Secondary light for depth
        dlight2 = DirectionalLight('directionalLight2')
        dlight2.setDirection(Vec3(2, 1, -1))
        dlight2.setColor(Vec4(0.3, 0.3, 0.4, 1))
        dlight2NP = self.render.attachNewNode(dlight2)
        self.render.setLight(dlight2NP)
    
    def setup_scene(self):
        """Create detailed game world"""
        # Load environment or create fallback
        self.environ = self.loader.loadModel("environment")
        if self.environ:
            self.environ.reparentTo(self.render)
            self.environ.setScale(1.5, 1.5, 1.5)
            self.environ.setPos(0, 0, 0)
            self.environ.setShaderAuto()
        else:
            self.create_procedural_world()
    
    def create_procedural_world(self):
        """Create a procedural world when models aren't available"""
        print("Creating procedural world...")
        
        # Ground plane with better texture
        try:
            ground = self.loader.loadModel("models/box")
            if ground:
                ground.reparentTo(self.render)
                ground.setScale(25, 25, 0.5)
                ground.setPos(0, 0, -0.5)
                ground.setColor(0.3, 0.7, 0.3, 1)
                ground.setShaderAuto()
        except:
            pass
        
        # Create maze-like structure
        wall_positions = [
            # Outer walls
            (12, 0, 2), (-12, 0, 2), (0, 12, 2), (0, -12, 2),
            # Inner maze
            (6, 6, 2), (-6, -6, 2), (6, -6, 2), (-6, 6, 2),
            (9, 3, 2), (-9, -3, 2), (3, 9, 2), (-3, -9, 2)
        ]
        
        for pos in wall_positions:
            try:
                wall = self.loader.loadModel("models/box")
                if wall:
                    wall.reparentTo(self.render)
                    wall.setScale(1, 1, 3)
                    wall.setPos(pos[0], pos[1], pos[2])
                    wall.setColor(0.6, 0.4, 0.2, 1)
                    wall.setShaderAuto()
                    self.obstacles.append(wall)
            except:
                continue
        
        # Decorative elements
        self.create_decorations()
    
    def create_decorations(self):
        """Add decorative elements to the world"""
        # Создаём дома
        self.create_houses()
        
        # Создаём деревья
        tree_positions = [
            (8, 8, 0), (-8, -8, 0), (4, 10, 0), (-4, -10, 0)
        ]
        
        for i, pos in enumerate(tree_positions):
            try:
                # Create tree-like structures
                trunk = self.loader.loadModel("models/box")
                if trunk:
                    trunk.reparentTo(self.render)
                    trunk.setScale(0.3, 0.3, 2)
                    trunk.setPos(pos[0], pos[1], 1)
                    trunk.setColor(0.4, 0.2, 0.1, 1)
                    trunk.setShaderAuto()
                
                crown = self.loader.loadModel("models/box")
                if crown:
                    crown.reparentTo(self.render)
                    crown.setScale(1.5, 1.5, 1.5)
                    crown.setPos(pos[0], pos[1], 3)
                    crown.setColor(0.1, 0.6, 0.1, 1)
                    crown.setShaderAuto()
                    
                    # Animate the crown
                    spin = LerpHprInterval(crown, 10 + i, Vec3(360, 0, 0))
                    spin.loop()
            except:
                continue
        
        # Добавляем фонтан в центре
        self.create_fountain()
        
        # Добавляем фонари
        self.create_lanterns()
    
    def create_houses(self):
        """Создаём интерактивные дома"""
        house_data = [
            {'pos': (-10, 8, 0), 'color': (0.8, 0.3, 0.2), 'name': 'Красный дом'},
            {'pos': (10, 8, 0), 'color': (0.3, 0.5, 0.8), 'name': 'Синий дом'},
            {'pos': (-10, -10, 0), 'color': (0.9, 0.9, 0.6), 'name': 'Жёлтый дом'},
            {'pos': (10, -4, 0), 'color': (0.6, 0.4, 0.8), 'name': 'Фиолетовый дом'}
        ]
        
        self.houses = []
        
        for house_info in house_data:
            try:
                # Основа дома
                house_base = self.loader.loadModel("models/box")
                if house_base:
                    house_base.reparentTo(self.render)
                    house_base.setScale(2.5, 2.5, 3)
                    house_base.setPos(house_info['pos'][0], house_info['pos'][1], 1.5)
                    house_base.setColor(*house_info['color'], 1)
                    house_base.setShaderAuto()
                    self.houses.append({'model': house_base, 'name': house_info['name'], 'pos': house_info['pos']})
                
                # Крыша
                roof = self.loader.loadModel("models/box")
                if roof:
                    roof.reparentTo(self.render)
                    roof.setScale(3, 3, 0.5)
                    roof.setPos(house_info['pos'][0], house_info['pos'][1], 3.5)
                    roof.setColor(0.5, 0.2, 0.1, 1)
                    roof.setHpr(0, 0, 45)
                    roof.setShaderAuto()
                
                # Дверь
                door = self.loader.loadModel("models/box")
                if door:
                    door.reparentTo(self.render)
                    door.setScale(0.6, 0.1, 1.2)
                    door.setPos(house_info['pos'][0], house_info['pos'][1] + 1.3, 0.6)
                    door.setColor(0.3, 0.15, 0.05, 1)
                    door.setShaderAuto()
                
                # Окно
                window = self.loader.loadModel("models/box")
                if window:
                    window.reparentTo(self.render)
                    window.setScale(0.5, 0.1, 0.5)
                    window.setPos(house_info['pos'][0] + 0.8, house_info['pos'][1] + 1.3, 2)
                    window.setColor(0.6, 0.8, 1, 1)
                    window.setShaderAuto()
            except:
                continue
    
    def create_fountain(self):
        """Создаём декоративный фонтан"""
        try:
            # База фонтана
            fountain_base = self.loader.loadModel("models/box")
            if fountain_base:
                fountain_base.reparentTo(self.render)
                fountain_base.setScale(2, 2, 0.5)
                fountain_base.setPos(0, 0, 0.25)
                fountain_base.setColor(0.4, 0.4, 0.5, 1)
                fountain_base.setShaderAuto()
            
            # Бассейн фонтана
            fountain_pool = self.loader.loadModel("models/box")
            if fountain_pool:
                fountain_pool.reparentTo(self.render)
                fountain_pool.setScale(1.5, 1.5, 0.3)
                fountain_pool.setPos(0, 0, 0.65)
                fountain_pool.setColor(0.3, 0.6, 0.9, 0.7)
                fountain_pool.setShaderAuto()
            
            # Центральная колонна
            fountain_pillar = self.loader.loadModel("models/box")
            if fountain_pillar:
                fountain_pillar.reparentTo(self.render)
                fountain_pillar.setScale(0.3, 0.3, 2)
                fountain_pillar.setPos(0, 0, 1.5)
                fountain_pillar.setColor(0.7, 0.7, 0.8, 1)
                fountain_pillar.setShaderAuto()
            
            # Верх фонтана
            fountain_top = self.loader.loadModel("models/box")
            if fountain_top:
                fountain_top.reparentTo(self.render)
                fountain_top.setScale(0.5, 0.5, 0.5)
                fountain_top.setPos(0, 0, 2.7)
                fountain_top.setColor(0.2, 0.5, 0.8, 1)
                fountain_top.setShaderAuto()
                
                # Анимация вращения
                spin = LerpHprInterval(fountain_top, 4, Vec3(360, 0, 0))
                spin.loop()
        except:
            pass
    
    def create_lanterns(self):
        """Создаём декоративные фонари"""
        lantern_positions = [
            (5, 5, 0), (-5, -5, 0), (5, -5, 0), (-5, 5, 0)
        ]
        
        for pos in lantern_positions:
            try:
                # Столб фонаря
                pole = self.loader.loadModel("models/box")
                if pole:
                    pole.reparentTo(self.render)
                    pole.setScale(0.15, 0.15, 3)
                    pole.setPos(pos[0], pos[1], 1.5)
                    pole.setColor(0.2, 0.2, 0.2, 1)
                    pole.setShaderAuto()
                
                # Лампа фонаря
                lamp = self.loader.loadModel("models/box")
                if lamp:
                    lamp.reparentTo(self.render)
                    lamp.setScale(0.4, 0.4, 0.5)
                    lamp.setPos(pos[0], pos[1], 3.2)
                    lamp.setColor(1, 0.9, 0.5, 1)
                    lamp.setShaderAuto()
            except:
                continue
    
    def setup_player(self):
        """Create player character"""
        try:
            self.player = self.loader.loadModel("models/box")
            if self.player:
                self.player.reparentTo(self.render)
                self.player.setScale(0.8, 0.8, 1.6)
                self.player.setPos(self.player_pos)
                self.player.setColor(0.2, 0.5, 1, 1)
                self.player.setShaderAuto()
                
                # Add player details
                head = self.loader.loadModel("models/box")
                if head:
                    head.reparentTo(self.player)
                    head.setScale(0.5, 0.5, 0.5)
                    head.setPos(0, 0, 1)
                    head.setColor(1, 0.8, 0.6, 1)
                    head.setShaderAuto()
        except:
            print("Player model not available")
            self.player = None
    
    def setup_collectibles(self):
        """Create coins and power-ups"""
        coin_positions = [
            (4, 4, 1.5), (-4, -4, 1.5), (4, -4, 1.5), (-4, 4, 1.5),
            (8, 0, 1.5), (-8, 0, 1.5), (0, 8, 1.5), (0, -8, 1.5),
            (6, -2, 1.5), (-6, 2, 1.5), (2, 6, 1.5)
        ]
        
        for i, pos in enumerate(coin_positions):
            try:
                coin = self.loader.loadModel("models/box")
                if coin:
                    coin.reparentTo(self.render)
                    coin.setScale(0.4, 0.4, 0.1)
                    coin.setPos(pos[0], pos[1], pos[2])
                    # Красивый золотой цвет с блеском
                    coin.setColor(1, 0.85, 0, 1)
                    coin.setShaderAuto()
                    self.coins.append(coin)
                    
                    # Animate coin rotation
                    spin = LerpHprInterval(coin, 2, Vec3(360, 0, 0))
                    spin.loop()
            except:
                continue
        
        # Последняя монетка на пьедестале
        try:
            special_coin_pos = (-2, -6, 3.5)
            
            # Создаём красивый пьедестал
            pedestal_base = self.loader.loadModel("models/box")
            if pedestal_base:
                pedestal_base.reparentTo(self.render)
                pedestal_base.setScale(1.5, 1.5, 0.3)
                pedestal_base.setPos(-2, -6, 0.3)
                pedestal_base.setColor(0.3, 0.3, 0.3, 1)
                pedestal_base.setShaderAuto()
            
            # Столб пьедестала
            pedestal_pillar = self.loader.loadModel("models/box")
            if pedestal_pillar:
                pedestal_pillar.reparentTo(self.render)
                pedestal_pillar.setScale(0.4, 0.4, 2.5)
                pedestal_pillar.setPos(-2, -6, 1.5)
                pedestal_pillar.setColor(0.5, 0.5, 0.5, 1)
                pedestal_pillar.setShaderAuto()
            
            # Верхняя площадка
            pedestal_top = self.loader.loadModel("models/box")
            if pedestal_top:
                pedestal_top.reparentTo(self.render)
                pedestal_top.setScale(0.8, 0.8, 0.2)
                pedestal_top.setPos(-2, -6, 3.2)
                pedestal_top.setColor(0.7, 0.6, 0.2, 1)
                pedestal_top.setShaderAuto()
            
            # Особая монетка
            special_coin = self.loader.loadModel("models/box")
            if special_coin:
                special_coin.reparentTo(self.render)
                special_coin.setScale(0.5, 0.5, 0.15)
                special_coin.setPos(special_coin_pos[0], special_coin_pos[1], special_coin_pos[2])
                # Яркий золотой цвет для особой монетки
                special_coin.setColor(1, 0.9, 0.1, 1)
                special_coin.setShaderAuto()
                self.coins.append(special_coin)
                
                # Медленное вращение для эффектности
                spin = LerpHprInterval(special_coin, 3, Vec3(360, 0, 0))
                spin.loop()
        except:
            pass
    
    def setup_camera(self):
        """Setup third-person camera"""
        self.camera_distance = 15
        self.camera_height = 8
        self.update_camera()
    
    def setup_controls(self):
        """Setup comprehensive controls"""
        # WASD controls
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        
        # Arrow keys as alternative
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_left", self.set_key, ["left", True])
        self.accept("arrow_left-up", self.set_key, ["left", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        self.accept("arrow_right", self.set_key, ["right", True])
        self.accept("arrow_right-up", self.set_key, ["right", False])
        
        self.accept("escape", self.exit_game)
        self.accept("r", self.reset_game)
    
    def setup_ui(self):
        """Create game interface"""
        self.title = OnscreenText(
            text="3D Adventure Quest",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(0, 0.9),
            scale=0.1
        )
        
        self.instructions = OnscreenText(
            text="WASD/Arrows: Move\\nCollect all coins!\\nR: Reset, ESC: Exit",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(-1.3, -0.7),
            scale=0.05,
            align=TextNode.ALeft
        )
        
        self.update_score_display()
    
    def update_score_display(self):
        """Update score and progress display"""
        if hasattr(self, 'score_text'):
            self.score_text.destroy()
        
        coins_left = len(self.coins)
        self.score_text = OnscreenText(
            text=f"Score: {self.score}\\nCoins left: {coins_left}",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(1.2, 0.8),
            scale=0.06,
            align=TextNode.ARight
        )
    
    def set_key(self, key, value):
        """Handle key input"""
        self.keys[key] = value
    
    def update_camera(self):
        """Smooth camera following"""
        target_x = self.player_pos.x - self.camera_distance * 0.6
        target_y = self.player_pos.y - self.camera_distance * 0.6
        target_z = self.player_pos.z + self.camera_height
        
        self.camera.setPos(target_x, target_y, target_z)
        self.camera.lookAt(self.player_pos.x, self.player_pos.y, self.player_pos.z + 1)
    
    def check_coin_collection(self):
        """Check if player collected any coins"""
        for coin in self.coins[:]:
            coin_pos = coin.getPos()
            distance = (self.player_pos - coin_pos).length()
            
            if distance < 1.5:
                coin.removeNode()
                self.coins.remove(coin)
                self.score += 100
                self.update_score_display()
                print(f"Coin collected! Score: {self.score}")
                
                if not self.coins:
                    self.show_victory()
    
    def check_house_interaction(self):
        """Проверка взаимодействия с домами"""
        if not hasattr(self, 'houses'):
            return
        
        for house in self.houses:
            house_pos = Vec3(house['pos'][0], house['pos'][1], 0)
            distance = (self.player_pos - house_pos).length()
            
            # Если игрок рядом с домом, показываем подсказку
            if distance < 4:
                if not hasattr(self, 'house_hint') or self.current_house != house['name']:
                    if hasattr(self, 'house_hint'):
                        self.house_hint.destroy()
                    
                    self.house_hint = OnscreenText(
                        text=f"Рядом: {house['name']}\\nПодойдите ближе, чтобы узнать больше",
                        style=1,
                        fg=(1, 1, 1, 1),
                        pos=(0, -0.8),
                        scale=0.05,
                        align=TextNode.ACenter
                    )
                    self.current_house = house['name']
                return
        
        # Если игрок ушёл от всех домов, убираем подсказку
        if hasattr(self, 'house_hint'):
            self.house_hint.destroy()
            delattr(self, 'house_hint')
            self.current_house = None
    
    def check_collision_with_obstacles(self, new_pos):
        """Simple collision detection"""
        for obstacle in self.obstacles:
            obs_pos = obstacle.getPos()
            distance = (new_pos - obs_pos).length()
            
            if distance < 2:
                return True
        return False
    
    def show_victory(self):
        """Display victory message"""
        if hasattr(self, 'victory_text'):
            return
            
        self.victory_text = OnscreenText(
            text="CONGRATULATIONS!\\nYou collected all coins!\\nPress R to play again",
            style=1,
            fg=(1, 1, 0, 1),
            pos=(0, 0),
            scale=0.1,
            align=TextNode.ACenter
        )
        print("Victory! All coins collected!")
    
    def reset_game(self):
        """Reset the game"""
        print("Resetting game...")
        self.score = 0
        self.player_pos = Vec3(0, 0, 1)
        
        # Remove victory text
        if hasattr(self, 'victory_text'):
            self.victory_text.destroy()
            delattr(self, 'victory_text')
        
        # Recreate coins
        for coin in self.coins:
            coin.removeNode()
        self.coins.clear()
        self.setup_collectibles()
        
        self.update_score_display()
    
    def animate_scene(self, task):
        """Animate various scene elements"""
        time = task.time
        
        # Animate remaining coins
        for i, coin in enumerate(self.coins):
            if coin:
                base_pos = coin.getPos()
                # Floating motion
                float_offset = math.sin(time * 3 + i) * 0.2
                coin.setZ(base_pos.z + float_offset)
        
        return task.cont
    
    def update_game(self, task):
        """Main game update loop"""
        # Movement
        move_speed = 0.4
        new_pos = Vec3(self.player_pos)
        
        # Handle input
        if self.keys['w'] or self.keys['up']:
            new_pos.y += move_speed
        if self.keys['s'] or self.keys['down']:
            new_pos.y -= move_speed
        if self.keys['a'] or self.keys['left']:
            new_pos.x -= move_speed
        if self.keys['d'] or self.keys['right']:
            new_pos.x += move_speed
        
        # Check collisions before moving
        if not self.check_collision_with_obstacles(new_pos):
            self.player_pos = new_pos
            if self.player:
                self.player.setPos(self.player_pos)
        
        # Check coin collection
        self.check_coin_collection()
        
        # Check house interaction
        self.check_house_interaction()
        
        # Update camera
        self.update_camera()
        
        return task.cont
    
    def exit_game(self):
        """Exit the game"""
        print(f"Game Over! Final Score: {self.score}")
        sys.exit()

# Launch the adventure!
if __name__ == "__main__":
    print("=== 3D Adventure Quest ===")
    print("Collect all the golden coins!")
    print("Use WASD or arrow keys to move")
    print("Press R to reset, ESC to exit")
    print("Starting game...")
    
    game = AdventureGame()
    game.run()