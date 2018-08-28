import curses

# un-insane-ify the screen so we can debug
def debug(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

