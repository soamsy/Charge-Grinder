import threading

LIMBUS_NAME = "LimbusCompany"

SELECTED = ["YISANG", "DONQUIXOTE" , "ISHMAEL", "RODION", "SINCLAIR", "GREGOR"]
GIFTS = []
TEAM = ["BURN"]
NAME_ORDER = 0
DUPLICATES = False

LOG = True
BONUS = False
RESTART = True
ALTF4 = False
ALTF4_lux = False
NETZACH = False
SKIP = True
WINRATE = False
WISHMAKING = False
BUFF = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
CARD = [1, 0, 2, 3, 4]
KEYWORDLESS = {}
HARD_STATE = 'normal4hard1'
EXTREME = False
APP = None

PICK_NORMAL = {}
IGNORE_NORMAL = {}
PICK_ALL_NORMAL = {}
PICK_HARD = {}
IGNORE_HARD = {}
PICK_ALL_HARD = {}

WARNING = None
WINDOW = (0, 0, 1920, 1080)
SCREEN = None

pause_event = threading.Event()
stop_event = threading.Event()

LVL = 1
SUPER = "shop" # for Hard MD
DEAD = 0
IDX = 0
TO_UPTIE = {}
MOVE_ANIMATION = False

# Macro behavior configuration.
MACRO_PROFILE = "SAFE"
MACRO_RHYTHM = True
KEY_ERRORS = 0

def is_on_hard(level=None):
    if HARD_STATE == "normal4hard1_canceled":
        return False
    lvl = level if level is not None else LVL
    if HARD_STATE == "normal4hard1":
        return lvl >= 5
    return HARD_STATE == "hard"

def did_normal_then_hard():
    return HARD_STATE == "normal4hard1" and LVL >= 5

def cancel_normal_then_hard():
    global HARD_STATE
    HARD_STATE = "normal4hard1_canceled"