import sys
import traceback
import tkinter as tk
from config import *
from game import Game

if __name__ == '__main__':
    try:
        print('starting Survival Grounds')
        root = tk.Tk()
        root.title('Survival Grounds 3D')
        root.attributes('-fullscreen', True)
        root.focus_force()
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        Game(root)
        print('game initialized, entering mainloop')
        root.mainloop()
        print('mainloop exited')
    except Exception:
        print('startup error')
        traceback.print_exc()
        sys.exit(1)
