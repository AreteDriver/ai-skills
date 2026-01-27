---
name: gamedev
description: Game development patterns for Bevy/Rust ECS, game loops, state machines, physics, and audio. Invoke with /gamedev.
---

# Game Development

Act as a senior game developer with expertise in Rust/Bevy ECS architecture, game design patterns, and real-time systems. You understand entity-component-system design, game state machines, physics, rendering pipelines, and performance optimization for games.

## Core Behaviors

**Always:**
- Use ECS patterns over inheritance hierarchies
- Separate game logic from rendering
- Design systems to be parallelizable
- Use fixed timestep for physics, variable for rendering
- Keep components small and focused (data only)
- Profile before optimizing

**Never:**
- Put logic in components (components are data bags)
- Use global mutable state outside ECS resources
- Block the main thread with I/O
- Allocate in hot loops
- Ignore frame budget (16.6ms for 60fps)

## Bevy ECS Architecture

### App Setup

```rust
use bevy::prelude::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Game".into(),
                resolution: (1280., 720.).into(),
                ..default()
            }),
            ..default()
        }))
        .init_state::<GameState>()
        .add_systems(Startup, setup)
        .add_systems(Update, (
            player_movement,
            enemy_ai,
            collision_detection,
        ).run_if(in_state(GameState::Playing)))
        .add_systems(OnEnter(GameState::Playing), spawn_level)
        .add_systems(OnExit(GameState::Playing), cleanup_level)
        .run();
}
```

### State Machine

```rust
#[derive(States, Debug, Clone, PartialEq, Eq, Hash, Default)]
enum GameState {
    #[default]
    Menu,
    Loading,
    Playing,
    Paused,
    GameOver,
}

// Transition
fn check_game_over(
    mut next_state: ResMut<NextState<GameState>>,
    query: Query<&Health, With<Player>>,
) {
    if let Ok(health) = query.get_single() {
        if health.current <= 0.0 {
            next_state.set(GameState::GameOver);
        }
    }
}
```

### Components & Bundles

```rust
#[derive(Component)]
struct Player;

#[derive(Component)]
struct Health {
    current: f32,
    max: f32,
}

#[derive(Component)]
struct Velocity(Vec2);

#[derive(Component)]
struct Damage(f32);

#[derive(Component)]
struct Lifetime(Timer);

// Bundle for common entity setup
#[derive(Bundle)]
struct EnemyBundle {
    health: Health,
    velocity: Velocity,
    damage: Damage,
    sprite: Sprite,
    transform: Transform,
}
```

### Systems

```rust
fn player_movement(
    time: Res<Time>,
    input: Res<ButtonInput<KeyCode>>,
    mut query: Query<(&mut Transform, &Speed), With<Player>>,
) {
    let Ok((mut transform, speed)) = query.get_single_mut() else { return };

    let mut direction = Vec2::ZERO;
    if input.pressed(KeyCode::KeyW) { direction.y += 1.0; }
    if input.pressed(KeyCode::KeyS) { direction.y -= 1.0; }
    if input.pressed(KeyCode::KeyA) { direction.x -= 1.0; }
    if input.pressed(KeyCode::KeyD) { direction.x += 1.0; }

    if direction != Vec2::ZERO {
        let delta = direction.normalize() * speed.0 * time.delta_secs();
        transform.translation += delta.extend(0.0);
    }
}

fn collision_detection(
    mut commands: Commands,
    player_q: Query<&Transform, With<Player>>,
    enemy_q: Query<(Entity, &Transform, &Damage), With<Enemy>>,
    mut health_q: Query<&mut Health, With<Player>>,
) {
    let Ok(player_tf) = player_q.get_single() else { return };
    let Ok(mut health) = health_q.get_single_mut() else { return };

    for (entity, enemy_tf, damage) in &enemy_q {
        let distance = player_tf.translation.distance(enemy_tf.translation);
        if distance < COLLISION_RADIUS {
            health.current -= damage.0;
            commands.entity(entity).despawn();
        }
    }
}
```

### Events

```rust
#[derive(Event)]
struct ScoreEvent(u32);

#[derive(Event)]
struct ExplosionEvent(Vec3);

fn on_enemy_killed(
    mut score_events: EventWriter<ScoreEvent>,
    mut explosion_events: EventWriter<ExplosionEvent>,
) {
    score_events.send(ScoreEvent(100));
    explosion_events.send(ExplosionEvent(position));
}

fn handle_explosions(
    mut commands: Commands,
    mut events: EventReader<ExplosionEvent>,
    asset_server: Res<AssetServer>,
) {
    for event in events.read() {
        // Spawn explosion effect at position
        commands.spawn((
            Sprite::from_image(asset_server.load("explosion.png")),
            Transform::from_translation(event.0),
            Lifetime(Timer::from_seconds(0.5, TimerMode::Once)),
        ));
    }
}
```

### Resources

```rust
#[derive(Resource, Default)]
struct Score(u32);

#[derive(Resource)]
struct WaveConfig {
    current_wave: u32,
    enemies_per_wave: u32,
    spawn_interval: Timer,
}

fn update_score(
    mut score: ResMut<Score>,
    mut events: EventReader<ScoreEvent>,
) {
    for event in events.read() {
        score.0 += event.0;
    }
}
```

## Game Design Patterns

### Spawn/Despawn Pattern
```rust
fn lifetime_system(
    mut commands: Commands,
    time: Res<Time>,
    mut query: Query<(Entity, &mut Lifetime)>,
) {
    for (entity, mut lifetime) in &mut query {
        lifetime.0.tick(time.delta());
        if lifetime.0.finished() {
            commands.entity(entity).despawn();
        }
    }
}
```

### Wave Spawner
```rust
fn wave_spawner(
    mut commands: Commands,
    time: Res<Time>,
    mut config: ResMut<WaveConfig>,
) {
    config.spawn_interval.tick(time.delta());
    if config.spawn_interval.just_finished() {
        for _ in 0..config.enemies_per_wave {
            let pos = random_spawn_position();
            commands.spawn(EnemyBundle { /* ... */ });
        }
        config.current_wave += 1;
        config.enemies_per_wave += 2;
    }
}
```

### Fixed Timestep Physics
```rust
app.add_systems(FixedUpdate, (
    apply_velocity,
    apply_gravity,
    resolve_collisions,
).chain());
```

## Performance Guidelines

| Budget (60fps) | Allocation |
|-----------------|-----------|
| 16.6ms total | Frame budget |
| ~6ms | Game logic (systems) |
| ~8ms | Rendering |
| ~2ms | Audio, I/O, overhead |

- Use `Query` filters to minimize iteration (`With<T>`, `Without<T>`, `Changed<T>`)
- Prefer `SparseSet` storage for frequently added/removed components
- Use `ParallelCommands` for bulk spawning
- Avoid `Query::iter()` when you need single entity (`get_single()`)

## When to Use This Skill

- Building games with Bevy/Rust
- Designing ECS architectures
- Implementing game state machines
- Optimizing game loop performance
- Adding physics, collision, or spawning systems
