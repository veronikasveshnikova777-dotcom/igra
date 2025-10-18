#!/usr/bin/env python3
"""
Working Simple 3D Game on Panda3D
Controls: WASD for movement, ESC to exit
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import Vec3, Vec4, TextNode
from direct.gui.OnscreenText import OnscreenText
import sys

class WorkingGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Disable default camera control
        self.disableMouse()
        
        # Initialize player
        self.player_pos = Vec3(0, -10, 0)
        self.player_speed = 10
        
        # Movement keys
        self.keys = {'w': False, 'a': False, 's': False, 'd': False}
        
        # Setup everything
        self.setup_lighting()
        self.setup_scene()
        self.setup_player()
        self.setup_controls()
        self.setup_camera()
        self.setup_ui()
        
        # Start game loop
        self.taskMgr.add(self.update_game, "update_game")
    
    def setup_lighting(self):
        """Setup basic lighting"""
        # Ambient light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.6, 0.6, 0.6, 1))
        alightNP = self.render.attachNewNode(alight)
        self.render.setLight(alightNP)
        
        # Directional light
        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(-5, -5, -5))
        dlight.setColor(Vec4(1, 1, 1, 1))
        dlightNP = self.render.attachNewNode(dlight)
        self.render.setLight(dlightNP)
    
    def setup_scene(self):
        """Create a simple scene"""
        # Try to load environment model, if not available create simple scene
        self.environ = self.loader.loadModel("environment")
        if self.environ:
            self.environ.reparentTo(self.render)
            self.environ.setScale(2, 2, 2)
            self.environ.setPos(0, 0, 0)
        else:
            # Create simple ground
            try:
                ground = self.loader.loadModel("models/box")
                if ground:
                    ground.reparentTo(self.render)
                    ground.setScale(20, 20, 1)
                    ground.setPos(0, 0, -1)
                    ground.setColor(0.3, 0.8, 0.3, 1)
                
                # Create some obstacles
                for i in range(3):
                    cube = self.loader.loadModel("models/box")
                    if cube:
                        cube.reparentTo(self.render)
                        cube.setScale(2, 2, 3)
                        cube.setPos(i * 10 - 10, 15, 0)
                        cube.setColor(0.8, 0.3, 0.3, 1)
            except:
                print("No models available, using empty scene")
    
    def setup_player(self):
        """Create player"""
        try:
            self.player = self.loader.loadModel("models/box")
            if self.player:
                self.player.reparentTo(self.render)
                self.player.setScale(1, 1, 2)
                self.player.setPos(self.player_pos)
                self.player.setColor(0.3, 0.3, 0.8, 1)
        except:
            print("Player model not available")
            self.player = None
    
    def setup_camera(self):
        """Position camera"""
        self.camera.setPos(self.player_pos.x - 10, self.player_pos.y - 10, 5)
        self.camera.lookAt(self.player_pos)
    
    def setup_controls(self):
        """Setup keyboard controls"""
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Setup user interface"""
        self.title = OnscreenText(
            text="3D Game Demo",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(0, 0.9),
            scale=0.1
        )
        
        self.instructions = OnscreenText(
            text="WASD - move, ESC - exit",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(-1.3, -0.9),
            scale=0.06,
            align=TextNode.ALeft
        )
    
    def set_key(self, key, value):
        """Handle key events"""
        self.keys[key] = value
    
    def update_camera(self):
        """Update camera to follow player"""
        camera_x = self.player_pos.x - 10
        camera_y = self.player_pos.y - 10
        camera_z = self.player_pos.z + 5
        
        self.camera.setPos(camera_x, camera_y, camera_z)
        self.camera.lookAt(self.player_pos)
    
    def update_game(self, task):
        """Main game update loop"""
        # Simple movement without delta time for now
        move_speed = 0.3
        
        if self.keys['w']:
            self.player_pos.y += move_speed
        if self.keys['s']:
            self.player_pos.y -= move_speed
        if self.keys['a']:
            self.player_pos.x -= move_speed
        if self.keys['d']:
            self.player_pos.x += move_speed
        
        # Update player position
        if self.player:
            self.player.setPos(self.player_pos)
        
        # Update camera
        self.update_camera()
        
        return task.cont

# Run the game
if __name__ == "__main__":
    print("Starting 3D Game...")
    print("Controls: WASD to move, ESC to exit")
    game = WorkingGame()
    game.run()