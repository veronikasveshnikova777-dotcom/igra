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
        else:
            self.create_procedural_world()
    
    def create_procedural_world(self):
        """Create a procedural world when models aren't available"""
        print("Creating procedural world...")
        
        # Ground plane
        try:
            ground = self.loader.loadModel("models/box")
            if ground:
                ground.reparentTo(self.render)
                ground.setScale(25, 25, 0.5)
                ground.setPos(0, 0, -0.5)
                ground.setColor(0.2, 0.7, 0.2, 1)
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
                    self.obstacles.append(wall)
            except:
                continue
        
        # Decorative elements
        self.create_decorations()
    
    def create_decorations(self):
        """Add decorative elements to the world"""
        decoration_positions = [
            (8, 8, 0), (-8, -8, 0), (8, -8, 0), (-8, 8, 0),
            (4, 10, 0), (-4, -10, 0), (10, 4, 0), (-10, -4, 0)
        ]
        
        for i, pos in enumerate(decoration_positions):
            try:
                # Create tree-like structures
                trunk = self.loader.loadModel("models/box")
                if trunk:
                    trunk.reparentTo(self.render)
                    trunk.setScale(0.3, 0.3, 2)
                    trunk.setPos(pos[0], pos[1], 1)
                    trunk.setColor(0.4, 0.2, 0.1, 1)
                
                crown = self.loader.loadModel("models/box")
                if crown:
                    crown.reparentTo(self.render)
                    crown.setScale(1.5, 1.5, 1.5)
                    crown.setPos(pos[0], pos[1], 3)
                    crown.setColor(0.1, 0.6, 0.1, 1)
                    
                    # Animate the crown
                    spin = LerpHprInterval(crown, 10 + i, Vec3(360, 0, 0))
                    spin.loop()
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
                
                # Add player details
                head = self.loader.loadModel("models/box")
                if head:
                    head.reparentTo(self.player)
                    head.setScale(0.5, 0.5, 0.5)
                    head.setPos(0, 0, 1)
                    head.setColor(1, 0.8, 0.6, 1)
        except:
            print("Player model not available")
            self.player = None
    
    def setup_collectibles(self):
        """Create coins and power-ups"""
        coin_positions = [
            (4, 4, 1.5), (-4, -4, 1.5), (4, -4, 1.5), (-4, 4, 1.5),
            (8, 0, 1.5), (-8, 0, 1.5), (0, 8, 1.5), (0, -8, 1.5),
            (6, -2, 1.5), (-6, 2, 1.5), (2, 6, 1.5), (-2, -6, 1.5)
        ]
        
        for i, pos in enumerate(coin_positions):
            try:
                coin = self.loader.loadModel("models/box")
                if coin:
                    coin.reparentTo(self.render)
                    coin.setScale(0.4, 0.4, 0.1)
                    coin.setPos(pos[0], pos[1], pos[2])
                    coin.setColor(1, 1, 0, 1)
                    self.coins.append(coin)
                    
                    # Animate coin rotation
                    spin = LerpHprInterval(coin, 2, Vec3(360, 0, 0))
                    spin.loop()
            except:
                continue
    
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