import os

from blessed import Terminal


def input_no_return(prompt):
    flush_input()
    print(prompt)
    term = Terminal()
    with term.cbreak():
        key = term.inkey()
    flush_input()
    if key == 'q':
        print("\n\nQ key pressed. Aborting game.")
        exit()
    return key


def flush_input():
    try:
        import sys
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def clear_screen():
    """Clear the screen."""
    # For IDEs
    print('\n' * 100)
    # For OS terminals
    os.system('cls' if os.name == 'nt' else 'clear')
