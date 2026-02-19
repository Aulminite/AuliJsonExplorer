# Auli JSON Explorer (v1.0)

Auli JSON Explorer is a terminal-based JSON navigation tool built with Python and curses. It provides an interactive, keyboard-driven interface for exploring JSON files quickly and comfortably.

---

## Features

- **Interactive JSON navigation** 
- Arrow keys to move, enter, and exit nodes 
- Full-screen viewer for long primitive values 
- Breadcrumb-style path display 

- **Color-coded JSON types** 
- Objects → yellow 
- Arrays → cyan 
- Strings → green 
- Numbers → magenta 
- Null → gray 

- **Command console** 
- `open "filepath"` — load a JSON file 
- `set arrayWidth N` — control how many array elements appear per row 
- `quit` — exit the program 

- **Array grid layout** 
- Arrays are displayed in rows for easier scanning 
- Width is user-configurable 

- **Executable-friendly** 
- Can be packaged into a standalone Linux binary using PyInstaller 

## 🧭 Navigation Inside the JSON explorer: 
| Key | Action | 
|-----|--------| 
| ↑ / ↓ | Move selection | 
| → | Enter object/array OR view primitive value | 
| ← | Go back to parent OR exit value viewer | 
| q | Return to command console | 

Primitive values (strings, numbers, null) open in a full-screen viewer when selected with →. The arrayWidth settings affects arrays in this view only.

---