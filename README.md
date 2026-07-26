# TasksBoot

A lightweight, stay-on-top desktop widget which helps you set a direction for each working session. Working on integrating it with other productivity features.

<img width="406" height="214" alt="Screenshot 2026-07-24 150401" src="https://github.com/user-attachments/assets/ef8db34e-f8d1-41ec-bb16-d103bd0686c0" />

## Features
* On startup, the widget positions itself in the top-right corner of the screen and stays on top of all other windows until the session task is decided.
* Animations:
  * Ladder Animation: A custom step-by-step sorting animation that moves the focused task up to the top.
  * Shuffle Animation: A sequence that chooses a random task for you if none were designated.
* Task Editor: Add, delete, edit, or focus tasks.
  
<img width="564" height="486" alt="Screenshot 2026-07-25 193730" src="https://github.com/user-attachments/assets/365516de-539f-4f70-8e93-3ccf507b2ea8" />
 
* Within the editor, you can choose to have TasksBoot load on startup.
* **Hotkeys**:
  * `Alt + T`: Toggle/Show TasksBoot main window.
  * `Alt + E`: Open the Task Editor.

---

## Animations Demonstration

Below are the visual high-quality walkthroughs demonstrating how the boot sequence, animations, and editor function. 

### Shuffle Selection Animation
When the application starts and no task is focused, a random shuffling sequence executes to designate a task:

<img src="https://github.com/user-attachments/assets/d3a17e72-48f2-4b21-a3e9-7596a9b52786" width="300" alt="Shuffle Selection Animation" />

### Ladder Animation
When a task is selected or pre-focused, it lights up green and steps through the list until it sits at the top:

<img src="https://github.com/user-attachments/assets/ea7f58d1-a502-44c1-a04c-e4fe1f6e21a4" width="300" alt="Ladder Animation" />

### Editor Function
GIF still in progress


---

## Setup & Run
1. Go to the `dist/` directory in this project.
2. Locate [main.exe](file:///c:/Users/Arnav/Documents/project/dist/main.exe).
3. Double-click it to launch TasksBoot  (You can move or copy this file to your Desktop or anywhere else).


I don't know why you'd want to run it through the python source but if you do:

1. Make sure PySide6 and keyboard library are installed in your environment:
   ```bash
   pip install PySide6 keyboard
   ```
2. Start the program:
   ```bash
   python main.py
   ```


If you modify the source files and want to rebuild the `.exe`:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets;assets" --add-data "tasks.json;." main.py
```
The compiled output will update inside the `dist/` folder.
