# Gamedev Response
## Example Output
```
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
