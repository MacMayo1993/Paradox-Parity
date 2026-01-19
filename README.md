# The Parity Paradox

Topological puzzle dungeon crawler built with Pygame.
Navigate a Möbius/Klein board, flip parity by crossing seams, confuse an HMM-powered boss that predicts your path, and outsmart the non-orientable world.

## Gameplay
- Arrow keys: Move (controls invert when parity flips!)
- Cross the golden seam line to flip parity → boss prediction breaks
- Survive / confuse the boss by exploiting model mismatch
- Antipode ghost mirrors your position topologically

## Installation & Run
1. Clone the repo:
   ```
   git clone https://github.com/MacMayo1993/parity-paradox.git
   cd parity-paradox
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the game:
   ```
   python src/main.py
   ```

## Controls
- ← → ↑ ↓ : Move (inverts on parity flip)
- Esc / Q : Quit

## Development
- main.py: Core game loop, seam logic, HMM boss
- Future: Add levels, collectibles, sound

Made with ❤️ in 2026 – exploring non-orientable HMMs through play.
