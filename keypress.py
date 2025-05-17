import sys, tty, termios, select, time

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setcbreak(fd)

try:
    print("press keys (press q to quit):")
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            print(f"you pressed: {key}")
            if key == 'q':
                break
        time.sleep(0.01)
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
