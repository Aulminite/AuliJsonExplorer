# Auli JSON Explorer (v1.1)

Auli JSON Explorer is a terminal-based JSON navigation tool built with Python and curses. It provides an interactive, keyboard-driven interface for exploring JSON files quickly and comfortably.

---

## Features

### Interactive JSON navigation
- Arrow keys to move, enter, and exit nodes 
- Full-screen viewer for long primitive values 
- Breadcrumb-style path display 

### Color-coded JSON types
- Objects → yellow 
- Arrays → cyan 
- Strings → green 
- Numbers → magenta 
- Null → gray 

### Command console
- `open "filepath"` — load a JSON file 
- `set arrayWidth N` — control how many array elements appear per row
- `set searchMode MODE` — choose what elements are searched (`all`,`keys`,`values`)
- `help` — show built-in help
- `quit` — exit the program 

### Search System
AJsonE includes a simple search system:
#### Local Search (`/`)
- Searches within the current object or array
- Respects searchMode

#### Global Search (`?`)
- Searches the entire JSON tree
- Respects searchMode
- Automatically jumps to each match
- `n` goes to the next match
- `N` goes to the previous match

### Array grid layout
- Arrays are displayed in rows for easier scanning 
- Width is user-configurable 

### QoL Features
- TAB completion for file paths in the console
- Command history using up and down arrow keys

## Navigation Inside the JSON explorer: 
| Key | Action | 
|-----|--------| 
| ↑ / ↓ | Move selection | 
| → | Enter object/array OR view primitive value | 
| ← | Go back to parent OR exit value viewer | 
| q | Return to command console | 

Primitive values (strings, numbers, null) open in a full-screen viewer when selected with →. The arrayWidth settings affects arrays in this view only.

---