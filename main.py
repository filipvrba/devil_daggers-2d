from ursina import *


class Arena(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,
            model = 'quad',
            scale = 8,
            texture = 'assets/arena_bg',
            color = color.white,
            z = 0.1
        )


class Player(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,
            model = 'quad',
            scale = 0.8,
            texture = 'assets/player_light',
            color = color.white,
            
        )
        self.move_speed = 1.5
        self.vec_normal = Vec2.zero
        self.is_roll = False
        self.velocity = Vec2(0, 0)
        self.rotate_normal = Vec2(0, 0)
        self.shoot_timer = Sequence(0.05, Func(self.shoot), loop = True)

        self.collider = SphereCollider(self, center=self.position, radius=2),

    
    def update(self):
        mouse_pos = mouse.position * 10
        self.look_at_2d(mouse_pos)
        pos = mouse_pos - self.world_position
        dis = distance2d(mouse_pos, self.position)

        if dis > 0.1:
            self.vec_normal = Vec2(held_keys['w'] - held_keys['s'], held_keys['a'] - held_keys['d'])
        else:
            self.vec_normal = Vec2(-held_keys['s'], 0)
        self.velocity = self.vec_normal * self.move_speed
        self.rotate_normal = self.rotated(self.velocity, math.atan2(pos.y, pos.x))
        self.velocity = self.rotate_normal
        
        self.position += self.velocity * time.dt
        self.velocity = Vec2(0, 0)
        self.projectiles = []


    def input(self, key):
        if key == 'space' and not self.is_roll:
            self.roll()
        
        if key == 'left mouse down':
            self.shoot()
            self.shoot_timer.start()
        elif key == 'left mouse up':
            self.shoot_timer.pause()
        elif key == 'right mouse down':
            self.double_shoot()
            

    def shoot(self):
        projectile = Projectile(self.position, (mouse.position * 10) - self.world_position, 0)
        self.projectiles.append(projectile)
    

    def double_shoot(self):
        for index in range(8):
            projectile = Projectile(self.position, (mouse.position * 10) - self.world_position, 1)
            self.projectiles.append(projectile)
    

    def roll(self):
        pass
    

    def rotated(self, position, radius):
        sine = math.sin(radius)
        cosi = math.cos(radius)
        x = position.x * cosi - position.y * sine
        y = position.x * sine + position.y * cosi
        return Vec2(x, y)


class Projectile(Entity):
    def __init__(self, pos, direction, ran):
        super().__init__(
            parent = scene,
            model = 'quad',
            scale = 0.2,
            texture = 'assets/dagger-projectile-v2.png',
            color = color.white,
            position = pos,
            rotation = (0, 0, math.degrees(math.atan2(direction.x, direction.y)))
        )

        self.magnitude = 10
        self.animate_position(self.position + (direction.normalized() *
                self.magnitude) + Vec2(random.randint(-ran, ran),
                random.randint(-ran, ran)), curve = curve.linear, duration = 1)
        destroy(self, 1)


class EnemySpawnerOne(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,
            model = 'quad',
            scale = 0.7,
            texture = 'assets/enemy_spawner-01.png',
            color = color.white,
            position = Vec3(0, 0, -0.1),
            x = 2,
        )
        trigger = Trigger(parent=self, trigger_targets=(player, ), model='circle', scale=0.8,
                alpha = 0, position=self.position)
        trigger.on_trigger_enter = Func(game_over)

        self.crystal = Crystal(self)
        self.animate_rotation(Vec3(0, 0, 360), curve = curve.linear, duration = 17, loop = True)


class Crystal(Entity):
    def __init__(self, parent):
        super().__init__(
            model = 'quad',
            scale = 0.4,
            texture = 'assets/crystal.png',
            color = color.white,
            position = Vec3(0, -0.37, -.1)
        )

        self.parent = parent
        pos = Vec3(parent.x + self.position.x, parent.y + self.position.y, parent.z + self.position.z)
        trigger = Trigger(parent=self, trigger_targets=(player,), model='quad', scale=0.7,
                alpha = 0, rotation_z = 45, position=pos, triggerers=player.projectiles)
        #trigger.on_trigger_enter = Func()


def game_over():
    """Settings all variables witch quit game and open up interface."""
    player.disable()


if __name__ == "__main__":
    app = Ursina()
    window.borderless = False
    window.title = 'Devil Daggers 2D'
    window.exit_button.visible = False
    window.color = color.black
    window.vsync = False

    # Objects
    arena = Arena()
    player = Player()
    enemy_spawner_one = EnemySpawnerOne()

    app.run()