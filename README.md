# TasksBoot

A lightweight, stay-on-top desktop widget which helps you set a direction for each working session.
<img width="406" height="214" alt="Screenshot 2026-07-24 150401" src="https://github.com/user-attachments/assets/ef8db34e-f8d1-41ec-bb16-d103bd0686c0" />

## Features
* **Stay-on-Top Boot Sequence**: On startup, the widget positions itself in the top-right corner of the screen and stays on top of all other windows until the session task is decided.
* **Animations**:
  * **Ladder Animation**: A custom step-by-step sorting animation that moves the focused task up to the top.
  * **Shuffle Animation**: A sequence that chooses a random task for you if none were designated.
* **Task Editor**: Add, delete, edit, or focus tasks.
 <img width="568" height="497" alt="image" src="https://github.com/user-attachments/assets/4cc2d395-73e9-4a17-80e7-0e62a752ea88" />
 
* **Hotkeys**:
  * `Alt + T`: Toggle/Show TasksBoot main window.
  * `Alt + E`: Open the Task Editor.

---

## Animations Demonstration

Below are the visual walkthroughs demonstrating how the boot sequence, animations, and editor function:

### Shuffle Selection Animation
When the application starts and no task is focused, a random shuffling sequence executes to designate a task:

![Shuffle Selection Animation](<img width="131" height="153" alt="axdcug" src="https://github.com/user-attachments/assets/d3a17e72-48f2-4b21-a3e9-7596a9b52786" />) 


###  Ladder Animation
When a task is selected or pre-focused, it lights up green and steps through the list until it sits at the top:

![Ladder Animation](<img width="120" height="151" alt="axdcl2" src="https://github.com/user-attachments/assets/ea7f58d1-a502-44c1-a04c-e4fe1f6e21a4" />)


---

## Setup & Run

### Method 1: Run the Precompiled Program (Easiest)
1. Go to the `dist/` directory in this project.
2. Locate [main.exe](file:///c:/Users/Arnav/Documents/project/dist/main.exe).
3. Double-click it to launch TasksBoot instantly! (You can move or copy this file to your Desktop or anywhere else).

### Method 2: Run from Python Source
1. Make sure PySide6 and keyboard library are installed in your environment:
   ```bash
   pip install PySide6 keyboard
   ```
2. Start the program:
   ```bash
   python main.py
   ```

### Method 3: Re-compiling the Executable Yourself
If you modify the source files and want to rebuild the `.exe`:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets;assets" --add-data "tasks.json;." main.py
```
The compiled output will update inside the `dist/` folder.
