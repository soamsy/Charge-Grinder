import threading, time

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
MODS = {}

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
NEED_INVENTORY_CHECK = True
REFRESH_COUNT = 0
REFRESH_COUNT = 0
INVENTORY = { "have": {} }
UPTIE_QUEUE = []
UPTIE_INCOMPLETE_QUEUE = []
UPTIE_SCHEDULED = set()

SHOP_SHELF = None
SHOP_TIERS_AVAILABLE = {}
NEED_SHELF_CHECK = {}

MOVE_ANIMATION = False
BUS_COUNT = 0

BALANCE = 0
NEED_BALANCE_CHECK = True
NUM_PURCHASED = 0
NUM_PURCHASED_SKILL3 = 0
FINISHED_ALL_FUSIONS = False
FINISHED_ALL_UPTIES = False

EXPECT_CHAIN = False
EXPECT_FOCUSED = False
EXPECT_REWARD = False
EXPECT_ACTION = None

# Macro behavior configuration.
MACRO_PROFILE = "SAFE"
MACRO_RHYTHM = True
KEY_ERRORS = 0

START_TIME = 0

def time_elapsed():
    elapsed_seconds = time.perf_counter() - START_TIME
    minutes, seconds = divmod(int(elapsed_seconds), 60)
    print(f"Elapsed time: {minutes:02d}:{seconds:02d}")

def is_on_hard(level=None):
    lvl = level if level is not None else LVL
    if HARD_STATE == "normal4hard1":
        return lvl >= (4 if is_saikai() else 5)
    return HARD_STATE == "hard"

def did_normal_then_hard():
    if not is_on_hard():
        return False
    if HARD_STATE == "normal4hard1":
        return LVL >= 5
    return False
    
def is_saikai():
    return "saikai" in MODS