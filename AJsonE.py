#!/usr/bin/env python3
import curses
import json
import os
import textwrap

# -----------------------------
# GLOBAL SETTINGS
# -----------------------------
ARRAY_WIDTH = 5


# -----------------------------
# COLOR SETUP
# -----------------------------
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


# -----------------------------
# VALUE VIEWER (full screen)
# -----------------------------
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


# -----------------------------
# NODE FORMATTER
# -----------------------------
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


# -----------------------------
# JSON EXPLORER
# -----------------------------
def explore_json(stdscr, root):
    curses.curs_set(0)
    init_colors()

    stack = [(None, root)]
    index_stack = [0]

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
            # Row-based array layout
            for i, (k, v) in enumerate(items):
                row = i // ARRAY_WIDTH
                col = i % ARRAY_WIDTH
                y = row + 2
                x = col * 20
                prefix = "→ " if i == idx else "  "
                stdscr.addstr(y, x, prefix)
                stdscr.addstr(format_node(v), color_for_value(v))
        else:
            # Normal vertical layout
            for i, (k, v) in enumerate(items):
                prefix = "→ " if i == idx else "  "
                stdscr.addstr(i + 2, 0, prefix + str(k) + ": ")
                stdscr.addstr(format_node(v), color_for_value(v))

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

        elif ch == ord('q'):
            return


# -----------------------------
# COMMAND CONSOLE
# -----------------------------
def command_console():
    print("Welcome to the Auli JSON Explorer! (v1.0)")
    print("----------------------------------------")

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

        print("Unknown command. Available commands:")
        print("  open \"filepath\"")
        print("  set arrayWidth N")
        print("  quit")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    command_console()
