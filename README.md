# ARENA

A custom first-person raycasting game engine made with Python, using TES: Arena assets. Heavily extended from https://www.youtube.com/watch?v=FLc6vUwyTdM. This project adds support for ceiling rendering, multiple wall textures, custom level structures, and minor gameplay elements, along with custom implementations of sprite sorting, animation handling, sprite angle correction, collision detection, a more robust shading system, and enemy visibility detection. 

This is a tech demo, not even close to an MVP. Most of the project is simply to explore raycasting and sprite handling. Some simple gameplay exists (attacking enemies, movement), but is not the main focus of the project.

## Technology and Methodology 

This project is made entirely with Python. No external game engines were used, and no libraries with built-in raycasting technologies were utilized. Numpy and the Numba NJIT compiler were used for performance gains and trigonometry functions. Pygame was utilized for texture loading, sound design, and pushing frames to the screen. All 3d calculations were done solely through python.

Raycasting is a technique to render a 3D space. Put simply, rays are cast from the player's view, and at each sample along the ray's path, the ray is checked for intersections. Once an intersection is found, that object is rendered at that pixel. This implementation uses one ray per pixel on the screen, and can draw walls, floors and ceilings, and sprites. Game data is stored in a 2D array, and rays are sent through the arrays. After each frame, the information gathered is rendered in 3D.

## Installation

Two options: download the script and assets and it's dependencies, or download the .exe and assets from [Google Drive](https://drive.google.com/drive/folders/18-rA0l1d8kWjZCXsZs8lKWJoxZjno4Fm?usp=sharing)

### Executable

This one is easy. Simply download the contents of the [Google Drive](https://drive.google.com/drive/folders/18-rA0l1d8kWjZCXsZs8lKWJoxZjno4Fm?usp=sharing) folder, and run the executable. This Google Drive folder also contains a demo video of the project. 

### Script & Dependencies

If you'd like to run the script in an IDE or in your command line, or if the link to the executable goes down, download the script and assets from this GitHub repo. Make sure the Assets folder and the ARENA.py script are in the same directory. Your file structure should look like this:

•

├── Assets                   
├── ARENA.py

Make sure you have [Python](https://www.python.org/downloads/) installed, as well as pip (it should be included). Then, install your dependencies:

Pygame:
```bash
pip install pygame
```

Numpy:
```bash
pip install numpy
```

Numba:
```bash
pip install numba
```

Navigate to the directory containing the script, and (assuming you're using Python 3), run the script:

```bash
python3 ARENA.py
```

## Usage

The gameplay elements are very barebones. W and S move you forwards and backwards, and A and D rotate you left and right. Clicking anywhere in the game view will swing your sword. IF an enemy is within range and you click directly on them, you'll attack them. Stand too close for too long, and you'll take damage, represented with a health bar on the left side of the UI. Once your health runs out, you die. Close the game and restart!
