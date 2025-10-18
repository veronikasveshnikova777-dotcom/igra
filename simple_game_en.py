#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple 3D Game on Panda3D (English version)
Controls: WASD for movement, ESC to exit
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import Vec3, Vec4, Point3
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
import sys
import os

class SimpleGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Disable default camera control
        self.disableMouse()
        
        # Setup lighting
        self.setup_lighting()
        
        # Create scene
        self.setup_scene()
        
        # Setup player
        self.setup_player()
        
        # Setup controls
        self.setup_controls()
        
        # Setup camera
        self.setup_camera()
        
        # Setup UI
        self.setup_ui()
        
        # Start main game loop
        self.taskMgr.add(self.update_game, "update_game")
    
    def setup_lighting(self):
        """Setup scene lighting"""
        # Ambient light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = self.render.attachNewNode(alight)
        self.render.setLight(alightNP)
        
        # Directional light (sun)
        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(-5, -5, -5))
        dlight.setColor(Vec4(1, 1, 1, 1))
        dlightNP = self.render.attachNewNode(dlight)
        self.render.setLight(dlightNP)
    
    def setup_scene(self):
        """Create game scene"""
        # Load environment (use built-in model)
        self.environ = self.loader.loadModel("environment")
        if self.environ:
            self.environ.reparentTo(self.render)
            self.environ.setScale(2, 2, 2)
            self.environ.setPos(0, 0, 0)
        else:
            # If environment model not found, create simple scene
            self.create_simple_scene()
    
    def create_simple_scene(self):
        """Create simple scene from primitives"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        if ground:
            ground.reparentTo(self.render)
            ground.setScale(20, 20, 1)
            ground.setPos(0, 0, -1)
            ground.setColor(0.3, 0.8, 0.3, 1)  # Green color
        
        # Create some cubes as obstacles
        for i in range(5):
            cube = self.loader.loadModel("models/box")
            if cube:
                cube.reparentTo(self.render)
                cube.setScale(2, 2, 3)
                cube.setPos(i * 8 - 16, 10, 0)
                cube.setColor(0.8, 0.3, 0.3, 1)  # Red color
    
    def setup_player(self):
        """Setup player"""
        self.player_pos = Vec3(0, -10, 0)
        self.player_speed = 10
        self.player_rotation = 0
        
        # Create simple player (cube)
        self.player = self.loader.loadModel("models/box")
        if self.player:
            self.player.reparentTo(self.render)
            self.player.setScale(1, 1, 2)
            self.player.setPos(self.player_pos)
            self.player.setColor(0.3, 0.3, 0.8, 1)  # Blue color
    
    def setup_camera(self):
        """Setup third-person camera"""
        self.camera_distance = 15
        self.camera_height = 5
        self.camera_angle = 0
        self.update_camera()
    
    def setup_controls(self):
        """Setup controls"""
        self.keys = {
            'w': False,
            'a': False,
            's': False,
            'd': False
        }
        
        # Key bindings
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        
        # Exit game
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Setup user interface"""
        self.title = OnscreenText(
            text="Simple 3D Game on Panda3D",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(0, 0.9),
            scale=0.08
        )
        
        self.instructions = OnscreenText(
            text="WASD - movement, ESC - exit",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(-1.3, -0.9),
            scale=0.05,
            align=TextNode.ALeft
        )
    
    def set_key(self, key, value):
        """Handle key presses"""
        self.keys[key] = value
    
    def update_camera(self):
        """Update camera position"""
        # Camera follows player
        camera_x = self.player_pos.x - self.camera_distance * 0.7
        camera_y = self.player_pos.y - self.camera_distance * 0.7
        camera_z = self.player_pos.z + self.camera_height
        
        self.camera.setPos(camera_x, camera_y, camera_z)
        self.camera.lookAt(self.player_pos)
    
    def update_game(self, task):
        """Main game loop"""
        dt = self.globalClock.getDt()
        
        # Handle player movement
        if self.keys['w']:
            self.player_pos.y += self.player_speed * dt
        if self.keys['s']:
            self.player_pos.y -= self.player_speed * dt
        if self.keys['a']:
            self.player_pos.x -= self.player_speed * dt
        if self.keys['d']:
            self.player_pos.x += self.player_speed * dt
        
        # Update player position
        if self.player:
            self.player.setPos(self.player_pos)
        
        # Update camera
        self.update_camera()
        
        return task.cont

# Start game
if __name__ == "__main__":
    game = SimpleGame()
    game.run()