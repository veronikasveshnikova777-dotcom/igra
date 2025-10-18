# Руководство по созданию 3D игр на Panda3D

## Основы Panda3D

Panda3D - это мощный и бесплатный игровой движок для создания 3D игр на Python.

### Базовая структура игры

```python
from direct.showbase.ShowBase import ShowBase

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Ваш код инициализации
        
    def update(self, task):
        # Игровой цикл
        return task.cont

game = MyGame()
game.run()
```

## Ключевые концепции

### 1. Загрузка моделей
```python
model = self.loader.loadModel("path/to/model")
model.reparentTo(self.render)  # Добавить в сцену
model.setPos(x, y, z)          # Позиция
model.setScale(x, y, z)        # Масштаб
model.setColor(r, g, b, a)     # Цвет
```

### 2. Освещение
```python
# Окружающий свет
alight = AmbientLight('ambient')
alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
alightNP = self.render.attachNewNode(alight)
self.render.setLight(alightNP)

# Направленный свет
dlight = DirectionalLight('directional')
dlight.setDirection(Vec3(-5, -5, -5))
dlightNP = self.render.attachNewNode(dlight)
self.render.setLight(dlightNP)
```

### 3. Управление камерой
```python
self.camera.setPos(x, y, z)       # Позиция камеры
self.camera.lookAt(x, y, z)       # Направление взгляда
self.disableMouse()               # Отключить стандартное управление
```

### 4. Обработка ввода
```python
self.accept("w", self.handle_key, ["w", True])
self.accept("w-up", self.handle_key, ["w", False])

def handle_key(self, key, value):
    self.keys[key] = value
```

### 5. Игровой цикл
```python
self.taskMgr.add(self.update_game, "update_game")

def update_game(self, task):
    # Обновление логики игры
    return task.cont  # Продолжить выполнение
```

### 6. Пользовательский интерфейс
```python
from direct.gui.OnscreenText import OnscreenText

text = OnscreenText(
    text="Hello World",
    pos=(0, 0.9),
    scale=0.1,
    fg=(1, 1, 1, 1)
)
```

### 7. Анимация
```python
from direct.interval.IntervalGlobal import LerpHprInterval

# Вращение объекта
spin = LerpHprInterval(object, 2, Vec3(360, 0, 0))
spin.loop()
```

## Полезные функции

### Векторы и позиции
```python
from panda3d.core import Vec3, Vec4

pos = Vec3(x, y, z)              # 3D позиция
color = Vec4(r, g, b, a)         # Цвет с альфа
distance = (pos1 - pos2).length()  # Расстояние между точками
```

### Коллизии (базовые)
```python
def check_collision(pos1, pos2, radius):
    distance = (pos1 - pos2).length()
    return distance < radius
```

## Структура проекта

```
game/
├── main.py              # Главный файл игры
├── models/              # 3D модели
├── textures/            # Текстуры
├── sounds/              # Звуки
└── config/              # Настройки
```

## Советы по разработке

### 1. Начните с простого
- Создайте базовую сцену
- Добавьте управление
- Постепенно усложняйте

### 2. Отладка
- Используйте `print()` для отслеживания значений
- Проверяйте загрузку моделей: `if model:`
- Обрабатывайте исключения

### 3. Производительность
- Не создавайте объекты в игровом цикле
- Удаляйте неиспользуемые объекты: `object.removeNode()`
- Оптимизируйте коллизии

### 4. Организация кода
```python
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setup_scene()
        self.setup_player()
        self.setup_controls()
        
    def setup_scene(self):
        # Настройка сцены
        pass
        
    def setup_player(self):
        # Настройка игрока
        pass
```

## Расширенные возможности

### Физика
```python
# Panda3D поддерживает физические движки
# Bullet Physics, ODE
```

### Аудио
```python
sound = self.loader.loadSfx("sound.wav")
sound.play()
```

### Шейдеры
```python
# Пользовательские шейдеры для продвинутой графики
shader = Shader.load(Shader.SL_GLSL, "vertex.glsl", "fragment.glsl")
object.setShader(shader)
```

## Ресурсы для изучения

1. **Официальная документация**: https://docs.panda3d.org/
2. **Примеры**: В папке samples установки Panda3D
3. **Сообщество**: Форумы Panda3D
4. **Туториалы**: YouTube каналы по Panda3D

## Частые ошибки

1. **Забыли вызвать `reparentTo(self.render)`**
2. **Неправильный импорт модулей**
3. **Не обработали случай отсутствия модели**
4. **Неправильное использование `task.cont`**

---

**Удачи в создании ваших 3D игр!** 🎮