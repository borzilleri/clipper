from colorama import Fore, Style, init

__initialized = False

__color_table = str.maketrans({
    'x': Style.RESET_ALL+Fore.RESET,
    'b': Style.BRIGHT,
    'd': Style.DIM,

    'w': Fore.WHITE,
    'r': Fore.RED,
    'g': Fore.GREEN,
    'y': Fore.YELLOW,
    'c': Fore.CYAN
})

def c(color: str) -> str:
    return color.translate(__color_table)

def init_colors():
    global __initialized
    if not __initialized:
        init()
        __initialized = True
