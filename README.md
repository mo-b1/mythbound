# MYTHBOUND ⚔️

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Framework](https://img.shields.io/badge/pygame-2.0%2B-green)

**MYTHBOUND** is a robust 2D multiplayer platform fighter featuring dynamic combat, custom physics, and real-time LAN matchmaking. Developed as the official codebase for my H046 Computer Science NEA Project, with a final score of 68/70.

This repository contains the complete source code, object-oriented engine, and assets developed alongside the technical documentation.


## Features

* **Real-Time LAN Multiplayer:** Custom server/client architecture built from scratch using TCP for reliable game-state syncing and UDP broadcasting for automatic local network game discovery. Handled concurrently via `threading`
* **Advanced Combat Mechanics:** Pixel-perfect collision detection using Pygame masks, combined with a robust animation system handling I-frames (invincibility), animation locking, attack recoveries, and knockbacks.
* **Dynamic Scene Management:** A scalable state-machine architecture (`SceneManager`) seamlessly routing between threaded loading screens, fully interactive menus, character/stage selections, and live gameplay loops.
* **Custom Physics Engine:** Precise horizontal/vertical collision handling with platforms, integrated with vector-based gravity, jumping mechanics, and variable movement states.
* **Responsive UI & Accessibility:** Fully remappable controls via an in-game widget system, dynamically scaling assets to support any screen resolution, and real-time interactive health/timer HUDs.

## Tech Stack

* **Language:** Python 3
* **Libaries:** pygame-ce, socket, json, threading


## Installation & Play

To run MYTHBOUND locally on your machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mo-b1/mythbound.git](https://github.com/mo-b1/mythbound.git)
   cd mythbound
   ```

2. **Create a virtual environment:**
```bash
   python -m venv venv
```

3. **Install pygame-ce:**
```bash
    ./venv/bin/pip install pygame-ce
```

4. **Run main.py:**
```bash
    ./venv/bin/python main.py
```