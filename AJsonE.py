#!/usr/bin/env python3
import curses
import json
import os
import textwrap
import readline
import glob

# GLOBAL SETTINGS
ARRAY_WIDTH = 5
SEARCH_MODE = "all"   # "all", "keys", or "values"

# COLOR SETUP
def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW, -1)   # object
    curses.init_pair(2, curses.COLOR_CYAN, -1)     # array
    curses.init_pair(3, curses.COLOR_GREEN, -1)    # string
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # number
    curses.init_pair(5, curses.COLOR_WHITE, -1)    # null

def color_for_value(v):
    if isinstance(v, dict):
        return curses.color_pair(1)
    if isinstance(v, list):
        return curses.color_pair(2)
    if isinstance(v, str):
        return curses.color_pair(3)
    if isinstance(v, (int, float)):
        return curses.color_pair(4)
    if v is None:
        return curses.color_pair(5)
    return curses.A_NORMAL

# VALUE VIEWER (full screen)
def view_value(stdscr, value):
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    wrapped = textwrap.wrap(str(value), width=w - 2)
    for i, line in enumerate(wrapped[:h - 2]):
        stdscr.addstr(i + 1, 1, line)
    stdscr.addstr(h - 1, 1, "Press ← to return")
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch == curses.KEY_LEFT:
            return

# NODE FORMATTER
def format_node(node):
    if isinstance(node, dict):
        return "{...}"
    if isinstance(node, list):
        return "[...]"
    if isinstance(node, str):
        return f"\"{node[:20]}...\"" if len(node) > 20 else f"\"{node}\""
    if node is None:
        return "null"
    return repr(node)

def jump_to_path(root, stack, index_stack, path, key):
    # Reset stack
    stack[:] = [(None, root)]
    index_stack[:] = [0]
    current = root
    for p in path:
        if isinstance(current, dict):
            keys = list(current.keys())
            idx = keys.index(p)
            stack.append((p, current[p]))
            index_stack.append(idx)
            current = current[p]
        elif isinstance(current, list):
            stack.append((p, current[p]))
            index_stack.append(p)
            current = current[p]
    # Finally select the key/index inside the final node
    if isinstance(current, dict):
        index_stack[-1] = list(current.keys()).index(key)
    else:
        index_stack[-1] = key


def find_local_matches(node, term):
    matches = []
    term = term.lower()
    # Search keys
    if isinstance(node, dict):
        for i, (k, v) in enumerate(node.items()):
            if SEARCH_MODE in ("all", "keys") and term in str(k).lower():
                matches.append(i)
            if SEARCH_MODE in ("all", "values"):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    if term in str(v).lower():
                        matches.append(i)
    # Search array indices + values
    elif isinstance(node, list):
        for i, (k, v) in enumerate(enumerate(node)):
            if SEARCH_MODE in ("all", "keys") and term in str(k).lower():
                matches.append(i)
            if SEARCH_MODE in ("all", "values"):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    if term in str(v).lower():
                        matches.append(i)
    return matches

def find_global_matches(node, term, path=None, results=None):
    if path is None:
        path = []
    if results is None:
        results = []
    term = term.lower()
    if isinstance(node, dict):
        for k, v in node.items():
            # Key match
            if SEARCH_MODE in ("all", "keys") and term in str(k).lower():
                results.append((path.copy(), k))
            # Value match
            if SEARCH_MODE in ("all", "values"):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    if term in str(v).lower():
                        results.append((path.copy(), k))
            # Recurse
            find_global_matches(v, term, path + [k], results)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            # Index match
            if SEARCH_MODE in ("all", "keys") and term in str(i).lower():
                results.append((path.copy(), i))
            # Value match
            if SEARCH_MODE in ("all", "values"):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    if term in str(v).lower():
                        results.append((path.copy(), i))
            # Recurse
            find_global_matches(v, term, path + [i], results)
    return results

# JSON EXPLORER
def explore_json(stdscr, root):
    curses.curs_set(0)
    init_colors()
    stack = [(None, root)]
    index_stack = [0]
    search_term = ""
    search_results = []
    search_index = 0
    search_mode = None
    while True:
        stdscr.clear()
        key, node = stack[-1]
        idx = index_stack[-1]
        # Title path
        title = "Path: " + "/".join(str(k) for k, _ in stack if k is not None)
        stdscr.addstr(0, 0, title)
        # Determine children
        if isinstance(node, dict):
            items = list(node.items())
        elif isinstance(node, list):
            items = list(enumerate(node))
        else:
            items = []
        # Display children
        if isinstance(node, list):
            # ARRAY GRID LAYOUT
            for i, (k, v) in enumerate(items):
                row = i // ARRAY_WIDTH
                col = i % ARRAY_WIDTH
                y = row + 2
                x = col * 20
                prefix = "→ " if i == idx else "  "
                stdscr.addstr(y, x, prefix)
                stdscr.addstr(format_node(v), color_for_value(v))
        elif isinstance(node, dict):
            # OBJECT VERTICAL LAYOUT
            for i, (k, v) in enumerate(items):
                prefix = "→ " if i == idx else "  "
                stdscr.addstr(i + 2, 0, prefix + str(k) + ": ")
                stdscr.addstr(format_node(v), color_for_value(v))
        else:
            # PRIMITIVE NODE (no children)
            stdscr.addstr(2, 0, "(value) ")
            stdscr.addstr(format_node(node), color_for_value(node))
        # Primitive display
        if not items:
            stdscr.addstr(2, 0, "(value) ")
            stdscr.addstr(format_node(node), color_for_value(node))
        stdscr.refresh()
        # Input handling
        ch = stdscr.getch()
        if ch == curses.KEY_UP:
            if items:
                index_stack[-1] = max(0, idx - 1)
        elif ch == curses.KEY_DOWN:
            if items:
                index_stack[-1] = min(len(items) - 1, idx + 1)
        elif ch == curses.KEY_RIGHT:
            if items:
                k, v = items[idx]
                if isinstance(v, (dict, list)):
                    stack.append((k, v))
                    index_stack.append(0)
                else:
                    # Full-screen value viewer
                    view_value(stdscr, v)
        elif ch == curses.KEY_LEFT:
            if len(stack) > 1:
                stack.pop()
                index_stack.pop()
        elif ch == ord('/'):
            curses.echo()
            stdscr.addstr(curses.LINES - 1, 0, "/")
            term = stdscr.getstr(curses.LINES - 1, 1).decode("utf-8")
            curses.noecho()
            search_term = term
            search_mode = "local"
            search_results = find_local_matches(node, term)
            search_index = 0
            if search_results:
                index_stack[-1] = search_results[0]
        elif ch == ord('?'):
            curses.echo()
            stdscr.addstr(curses.LINES - 1, 0, "?")
            term = stdscr.getstr(curses.LINES - 1, 1).decode("utf-8")
            curses.noecho()
            search_term = term
            search_mode = "global"
            search_results = find_global_matches(root, term)
            search_index = 0
            if search_results:
                path, key = search_results[0]
                # rebuild stack
                stack[:] = [(None, root)]
                index_stack[:] = [0]
                # walk down the path
                current = root
                for p in path:
                    if isinstance(current, dict):
                        items = list(current.items())
                        idx = list(current.keys()).index(p)
                        stack.append((p, current[p]))
                        index_stack.append(idx)
                        current = current[p]
                    elif isinstance(current, list):
                        stack.append((p, current[p]))
                        index_stack.append(p)
                        current = current[p]
                # finally select the key/index
                if isinstance(current, dict):
                    index_stack[-1] = list(current.keys()).index(key)
                else:
                    index_stack[-1] = key
        elif ch == ord('n'):
            if search_results:
                search_index = (search_index + 1) % len(search_results)
                if search_mode == "local":
                    index_stack[-1] = search_results[search_index]
                elif search_mode == "global":
                    path, key = search_results[search_index]
                    jump_to_path(root, stack, index_stack, path, key)
        elif ch == ord('N'):
            if search_results:
                search_index = (search_index - 1) % len(search_results)
                if search_mode == "local":
                    index_stack[-1] = search_results[search_index]
                elif search_mode == "global":
                    path, key = search_results[search_index]
                    jump_to_path(root, stack, index_stack, path, key)
        elif ch == ord('q'):
            return

def path_completer(text, state):
    # Expand ~
    if text.startswith("~"):
        text = os.path.expanduser(text)
    matches = glob.glob(text + "*")
    try:
        return matches[state]
    except IndexError:
        return None

# COMMAND CONSOLE
def command_console():
    print("Welcome to the Auli JSON Explorer! (v1.1)")
    print("----------------------------------------")
    readline.set_completer(path_completer)
    readline.parse_and_bind("tab: complete")
    while True:
        cmd = input("\n> ").strip()
        if cmd.lower() == "quit":
            print("Goodbye.")
            return
        if cmd.startswith("set arrayWidth"):
            try:
                global ARRAY_WIDTH
                ARRAY_WIDTH = int(cmd.split()[2])
                print(f"arrayWidth set to {ARRAY_WIDTH}")
            except:
                print("Usage: set arrayWidth N")
            continue
        if cmd.startswith("set searchMode"):
            try:
                global SEARCH_MODE
                mode = cmd.split()[2].lower()
                if mode in ("all", "keys", "values"):
                    SEARCH_MODE = mode
                    print(f"searchMode set to {SEARCH_MODE}")
                else:
                    print("Valid options: all, keys, values")
            except:
                print("Usage: set searchMode [all|keys|values]")
            continue
        if cmd.startswith("open "):
            # Extract quoted path
            if "\"" in cmd:
                path = cmd.split("\"")[1]
            else:
                print("Usage: open \"filepath\"")
                continue
            if not os.path.exists(path):
                print("File not found.")
                continue
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print("Error loading JSON:", e)
                continue
            curses.wrapper(explore_json, data)
            continue
        if cmd == "help":
            print("\nAuli JSON Explorer — Help")
            print("-------------------------")
            print("\nCommands:")
            print("  open \"filepath\"       - open a JSON file")
            print("  set arrayWidth N        - set how many array elements appear per row")
            print("  set searchMode MODE     - set search mode: all | keys | values")
            print("  help                    - show this help message")
            print("  quit                    - exit the program")
            print("\nSearch Modes:")
            print("  all    - search keys AND primitive values (default)")
            print("  keys   - search only keys / array indices")
            print("  values - search only primitive values")
            print("\nExplorer Controls:")
            print("  ↑ / ↓                  - move selection")
            print("  →                      - enter object/array OR view primitive value")
            print("  ←                      - go back OR exit value viewer")
            print("  q                      - return to command console")
            print("\nSearching:")
            print("  /                      - local search (recursive inside current node)")
            print("  ?                      - global search (entire JSON tree)")
            print("  n                      - jump to next search result")
            print("  N                      - jump to previous search result")
            print("\nConsole Features:")
            print("  TAB                    - file path auto-completion")
            print("  ↑ / ↓                  - command history navigation")
            print("\nNotes:")
            print("  - Arrays are displayed in a grid using arrayWidth.")
            print("  - Objects are always displayed as a vertical list.")
            print("  - Primitive values open in a full-screen viewer; press ← to exit.")
            continue
        print("Unknown command. Available commands:")
        print("  open \"filepath\"")
        print("  set arrayWidth N")
        print("  quit")

# MAIN
if __name__ == "__main__":
    command_console()
