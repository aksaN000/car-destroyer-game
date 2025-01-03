# Car Destroyer

Car Destroyer is an action-packed arcade-style game where players navigate through traffic while destroying enemy vehicles and facing challenging boss battles. The game features both single-player and multiplayer modes with increasing difficulty as you progress.

## Game Modes

### Single Player
- Control a single car and compete for the highest score
- Navigate through traffic while shooting enemy vehicles
- Face challenging boss battles

### Multiplayer
- Two-player split-screen action
- Competitive scoring system
- Shared screen space with independent controls
- Different colored cars for easy identification (Red for P1, Blue for P2)

## Core Features

### Player Controls
- **Player 1:**
  - WASD keys for movement
  - SPACE to shoot
  - P to pause game

- **Player 2:**
  - Arrow keys for movement
  - END key to shoot

### Health System
- Players and enemy vehicles have health bars
- Health bars are displayed above vehicles
- Regular cars: 3 health points
- Boss vehicles: 10 health points
- Health bars change color based on remaining health **In not working state. not fully functional**
- Instant death on collision with other vehicles

### Combat System
- Shoot bullets to destroy enemy vehicles
- Different bullet types:
  - Player bullets: Normal speed
  - Boss bullets: Enhanced speed
- Collision detection for bullets and vehicles
- Score points for successful hits and destructions

### Visual Effects
- Dynamic explosion particles system
- Multiple particle effects with:
  - Random directions
  - Varying colors (orange, red, yellow)
  - Different particle sizes
  - Fade-out effect
  - Physics-based movement

### Scoring System
- Points awarded for:
  - Regular car destruction: 150 points
  - Boss car destruction: 1000 points
  - Survival time: +1 point per frame
- Independent scoring in multiplayer mode
- High score tracking
- Level progression based on score

### Difficulty System
- Dynamic difficulty scaling based on score
- Difficulty increases every 1000 points
- Affects multiple game aspects:
  - Traffic density (30% to 60%)
  - Vehicle speeds
  - Boss spawn frequency
  - Boss attack patterns

### Traffic System
- Two-way traffic flow
- Multiple lanes
- Random vehicle spawning
- Different vehicle types
- Traffic density adjustment based on difficulty
- Safe distance maintenance between vehicles

### Boss Battles
- Special boss vehicles with unique features:
  - Enhanced health (10 HP)
  - Larger size
  - Distinct appearance (red coloring)
  - Special attack patterns
- Boss mechanics:
  - Automatic shooting at nearest player
  - Respawn system
  - Shooting cooldown
  - Strategic positioning

### Environmental Features
- Multi-lane highway
- Animated lane markers
- Central divider
- Dynamic road scrolling
- Clear lane separation

### UI Features
- Health bars for all vehicles
- Score display
- Current level indicator
- Pause menu with options:
  - Resume
  - Restart
  - Exit to Menu
- Game over screen with:
  - Final scores
  - Winner announcement (multiplayer)
  - Return to menu option
- Initial controls display
- Menu system with game mode selection

### Performance Optimizations
- Efficient bullet management
- Limited maximum number of vehicles
- Optimized collision detection
- Frame rate control
- Memory management for particles and effects

## Technical Details

- Window Size: 800x600 pixels
- Frame Rate: 60 FPS
- OpenGL-based rendering
- Custom drawing algorithms for:
  - Line drawing (Midpoint algorithm)
  - Circle drawing (Midpoint circle algorithm)
- Collision detection system
- Particle physics system

## Development Info

Built using:
- Python
- OpenGL
- GLUT (OpenGL Utility Toolkit)
- GLU (OpenGL Utility Library)

The game employs efficient algorithms and optimizations to ensure smooth gameplay while maintaining visual quality and responsive controls.
