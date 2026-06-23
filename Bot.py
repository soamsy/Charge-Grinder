from source.utils.utils import *
from source_app.utils import *
from itertools import cycle

from source.battle import fight, select_team
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm, get_adversity
from source.shop import shop
from source.lux import grind_lux, check_enkephalin
from source.teams import TEAMS, HARD, CUSTOM_TEAMS, DEFAULT_TEAM_MODS
import source.utils.params as p


# Action          -> next action is verifier
# Action with ver -> don't need next action
# default ver     -> verification by button image in corresponding region
# if ver has !    -> verification by screenshot region change (image correlation)

# INIT RUN

start_locations = {
    "Drive": 0, 
    "MD": 1, 
    "Start": 2, 
    "enterInvert": 5, 
    "ConfirmTeam": 6, 
    "enterBonus": 12, 
    "Confirm.0": 15, 
    "refuse": 17, 
    "Confirm": 23
}

def select_grace():
    for i in range(len(p.BUFF)):
        if p.BUFF[i]:
            x = int(335 + 297*(i % 5))
            y = int(375 + 357*(i // 5))
            ClickAction((x, y), ver="money!").execute(try_click)
            if p.BUFF[i] > 1:
                ClickAction((x + 60*(1 - 2*(p.BUFF[i] < 3)), y + 155), ver="money!").execute(try_click)

def ignore_gift_search():
    searchOn = now.button("giftSearch")
    if p.is_saikai():
        if not searchOn:
            win_click(1720, 240)
        return
    elif searchOn:
        now_click.button("giftSearch")

def get_out():
    gui.press("space")
    win_click()

def has_keywordless():
    return now.button("keywordless", timeout=0.2)

def navigate_gift_search():
    if not p.is_saikai():
        return

    chain_actions(try_click, [
        lambda: wait_while_condition(lambda: not has_keywordless(), action=lambda: get_out(), timer=4, interval=0.1),
        Action("keywordless", region=(951, 251, 25, 25)),
        lambda: time.sleep(0.2),
        lambda: wait_while_condition(lambda: not LocateRGB.locate(PTH["spiderwebentangled"], region=(115, 334, 1020, 600)), timer=4),
        lambda: win_click(gui.center(LocateRGB.locate(PTH["spiderwebentangled"]))),
        Action("selectgiftsearch"),
        Action("ConfirmInvert", ver="Confirm.0"),
        confirm_items,
    ])

def confirm_items():
    return wait_while_condition(lambda: not now.button("loading"), lambda: gui.press("space") if now.button("Confirm") else None, timer=4)

def dungeon_start():
    ACTIONS = [
        Action("Drive"),
        Action("MD", ver="Start"),
        lambda: time.sleep(1.4),
        lambda: win_click(1588, 567) if p.EXTREME and now_rgb.button("infinite_off") else None,
        Action("Start"),
        lambda: win_moveTo(1150, 730),
        lambda: time.sleep(0.1),
        Action("enterInvert", ver="ConfirmTeam", click=(1150, 730)),
        select_team,
        lambda: try_click.button("ConfirmTeam"),
        lambda: time.sleep(0.5),
        lambda: now_click.button("ConfirmInvert"),
        lambda: wait_while_condition(lambda: not now.button("enterBonus")),
        lambda: time.sleep(0.2),

        select_grace,

        Action("enterBonus", ver="Confirm.0"),
        lambda: now_click.button("starlight"),
        Action("Confirm.0", ver="refuse"),

        lambda: time.sleep(0.2),
        ignore_gift_search,
        ClickAction(p.GIFTS[0]["checks"][2], ver="gifts!"),
        lambda: ClickAction((1239, 395), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 0) else None,
        lambda: ClickAction((1239, 549), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 1) else None,
        lambda: ClickAction((1239, 703), ver="selected!").execute(try_click) if p.BUFF[9] else None,
        ClickAction((1624, 882)),

        navigate_gift_search if p.is_saikai() else confirm_items,
        loading_halt
    ]
    
    failed = 0
    while True:
        try:
            now_click.button("resume")
            for key in start_locations.keys():
                if now.button(key):
                    i = start_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, ACTIONS[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1509, 978)
        except gui.PauseException as e:
            pause(e.window)
        if failed > 5:
            print("Initialization error")
            logging.error("Initialization error")
            break
    print("Entering MD!")


# END RUN
def collect_rewards():
    wait_while_condition(
        condition=lambda: not now.button("loading"),
        action=lambda: gui.press("space") if now.button("Confirm.0") else None,
        interval=0.1
    )

def click_bonus():
    if p.is_on_hard():
        now_rgb.button("bonus", "hardbonus", click=True)
    else:
        now_rgb.button("bonus", click=True)
    x, y = random.randint(770, 1080), random.randint(428, 500)
    win_moveTo(x, y)

def bonus_gone():
    if p.is_on_hard():
        if not loc_rgb.button("bonus", "hardbonus", wait=1):
            return now_rgb.button("bonus_off", "hardbonus", conf=0.8)
        else: return False
    elif not loc_rgb.button("bonus", wait=1):
        return now_rgb.button("bonus_off", conf=0.8)
    else: return False

def handle_bonus():
    time.sleep(0.5)
    if p.BONUS or bonus_gone(): return

    if not wait_while_condition(lambda: not bonus_gone(), click_bonus):
        raise RuntimeError

TERMIN = [
    Action("victory", click=(1693, 841)),
    lambda: win_moveTo(1710, 982),
    Action("Claim", ver="ClaimInvert"),
    handle_bonus,
    Action("ClaimInvert"),
    Action("ConfirmInvert", ver="Confirm.0"),
    collect_rewards,
    loading_halt,
    lambda: try_loc.button("Drive")
]

end_locations = {
    "victory": 0,
    "Claim": 2,
    "ClaimInvert": 4,
    "ConfirmInvert": 5,
    "Confirm.0": 6,
}

def dungeon_end():
    failed = 0
    while True:
        try:
            for key in end_locations.keys():
                if now.button(key):
                    i = end_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, TERMIN[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1710, 982)
        except gui.PauseException as e:
            pause(e.window)
        if now.button("out_of_fuel"):
            logging.error("We are out of enkephalin!")
            if p.ALTF4: close_limbus()
            if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
            raise StopExecution
        if failed > 5:
            print("Termination error")
            logging.error("Termination error")
            break
    print("MD Finished!")
    p.time_elapsed()

# FAIL RUN
FAIL = [
    Action("defeat", click=(1693, 841)),
    lambda: win_moveTo(1710, 982),
    Action("Claim"),
    Action("GiveUp"),
    Action("ConfirmInvert", ver="loading"),
    loading_halt,
    lambda: try_loc.button("Drive")
]

fail_locations = {
    "defeat": 0,
    "Claim": 2,
    "GiveUp": 3,
    "ConfirmInvert": 4,
    "loading": 5,
}

def dungeon_fail():
    failed = 0
    while True:
        try:
            for key in fail_locations.keys():
                if now.button(key):
                    i = fail_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, FAIL[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1710, 982)
        except gui.PauseException as e:
            pause(e.window)
        if failed > 5:
            print("Termination error")
            logging.error("Termination error")
            break
    print("MD Failed!")


# MAIN LOOP
def main_loop():
    dungeon_start()
    error = 0
    last_error = 0
    ck = False
    p.MOVE_ANIMATION = False
    p.LVL = 1
    while True:
        if now.button("ServerError"):
            for _ in range(3):
                time.sleep(6)
                win_click(1100, 700)
                time.sleep(1)
                if not now.button("ServerError"): break

            time.sleep(10)
            if now_click.button("ServerError"):
                logging.error('Server error happened')

        if now.button("EventEffect"):
            win_click(773, 521)
            time.sleep(0.2)
            win_click(967, 774)

        if p.LIMBUS_NAME not in (win := gui.getActiveWindowTitle()): pause(win)

        if p.is_on_hard() and now.button("suicide"):
            if not p.EXTREME:
                win_click(815, 700)
            else:
                win_click(1117, 700)
            connection()
        
        if now.button("victory"):
            logging.info('Run Completed')
            dungeon_end()
            return True

        if now.button("defeat"):
            logging.info('Run Failed')
            dungeon_fail()
            return False
        
        actions = {
            "pack": pack,
            "move": move,
            "fight": fight,
            "event": event,
            "grab_EGO": grab_EGO,
            "confirm": confirm,
            "get_adversity": get_adversity,
            "grab_card": grab_card,
            "shop": shop.enter_shop,
        }

        def steps():
            return [actions[action] for action in actions.keys() if action != "get_adversity" or p.EXTREME]

        ck = False
        try:
            ring = steps()
            for action in ring:
                ck += action()
                while p.EXPECT_ACTION:
                    sidequest = p.EXPECT_ACTION
                    p.EXPECT_ACTION = None
                    print("got sidequest!", sidequest)
                    time.sleep(0.3)
                    ck += actions[sidequest]()
        except RuntimeError:
            handle_fuckup()
            error += 1
        except gui.PauseException as e:
            pause(e.window)

        if ck == False:
            # check if start
            for key in start_locations.keys():
                if now.button(key):
                    dungeon_start()
                    error = 0
                    last_error = 0
                    p.LVL = 1
                    break
            else: 
                # check if end
                for key in end_locations.keys():
                    if now.button(key):
                        logging.info('Run Completed')
                        dungeon_end()
                        return True
                
                if last_error != 0:
                    if time.time() - last_error > 30:
                        handle_fuckup()
                        error += 1
                else:
                    last_error = time.time()
        else:
            last_error = 0

        if error > 20:
            logging.error('We are stuck')
            if p.ALTF4: close_limbus()
            if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
            raise StopExecution # change maybe

        time.sleep(0.2)

def handle_mods(teams, team, keywordless):
    if "mods" not in teams[team]:
        return
    if "saikai" in teams[team]["mods"]:
        p.TEAM = p.TEAM[:1]
        p.GIFTS = CUSTOM_TEAMS["SAIKAI"]
        keywordless["spiderwebentangledred"] = 1

# when App is run:
def set_team(team, teams, keywordless):
    if p.is_on_hard(): team_list = HARD
    else: team_list = TEAMS

    p.TEAM = [list(team_list.keys())[aff] for aff in list(teams[team]["affinity"])]
    p.NAME_ORDER = teams[team]["affinity_idx"]
    p.DUPLICATES = teams[team]["duplicates"]
    p.GIFTS = [team_list[keyword] for keyword in p.TEAM]
    p.MODS = teams[team]["mods"] if teams[team] else {}
    handle_mods(teams, team, keywordless)

    p.SELECTED = [list(SINNERS.keys())[i] for i in list(teams[team]["sinners"])]
    p.PICK_NORMAL = generate_packs_pr(teams[team]["priority_normal"])
    p.IGNORE_NORMAL = generate_packs_av(teams[team]["avoid_normal"])
    p.PICK_ALL_NORMAL = generate_packs_all(teams[team]["priority_normal"])
    p.PICK_HARD = generate_packs_pr(teams[team]["priority_hard"])
    p.IGNORE_HARD = generate_packs_av(teams[team]["avoid_hard"])
    p.PICK_ALL_HARD = generate_packs_all(teams[team]["priority_hard"])

    logging.info(f'Team: {p.TEAM[0]}')
    
    difficulty = "HARD" if p.is_on_hard() else "NORMAL"
    if p.EXTREME: 
        difficulty = "EXTREME"
        lunar_comp = list(set(["slashmemory", "piercememory", "bluntmemory"]) - set([f"{name.lower()}memory" for name in p.TEAM]))
        stones = [f"stone{i}" for i in range(7)] + lunar_comp
        p.KEYWORDLESS = keywordless | {"lunarmemory": 2} | {gift: 2 for gift in stones}
    else:
        p.KEYWORDLESS = keywordless
    logging.info(f'Difficulty: {difficulty}')


def execute_me(count, count_exp, count_thd, teams, settings, hard_state, app, warning):
    p.HARD_STATE = hard_state
    p.BONUS = settings['bonus']
    p.RESTART = settings['restart']
    p.ALTF4, p.ALTF4_lux = settings['altf4']
    p.NETZACH = settings['enkephalin']
    p.SKIP = settings['skip']
    p.BUFF = settings['buff']
    p.CARD = settings['card']
    p.WISHMAKING = settings['wishmaking']
    p.WINRATE = settings['winrate']
    p.EXTREME = settings['infinity']
    p.APP = app
    p.WARNING = warning
    p.START_TIME = time.perf_counter()
    lux_keys = [key for key in teams.keys() if key >= 7]
    team_keys = [key for key in teams.keys() if key < 7]
    p.MODS = teams[team_keys[0]]["mods"] if team_keys else teams[lux_keys[0]]["mods"]

    if count == -1: count = 9999
    print("Switch to Limbus Window")
    countdown(5)
    logging.info('Script started')
    try:
        gui.set_window()
        if lux_keys:
            print("Entering Lux!")
            grind_lux(count_exp, count_thd, teams)
            if team_keys and p.APP: QMetaObject.invokeMethod(p.APP, "lux_hide", Qt.ConnectionType.QueuedConnection)
            elif p.ALTF4_lux:
                close_limbus()
            
        if team_keys:
            print("Entering MD!")
            rotator = cycle(team_keys)
            keywordless = settings['keywordless']

            for i in range(count):
                team = next(rotator)

                logging.info(f'Iteration {i}')
                completed = False
                while not completed:
                    set_team(team, teams, keywordless)
                    completed = main_loop()
                    if p.NETZACH: check_enkephalin()

            if p.ALTF4:
                close_limbus()
    except StopExecution:
        return
    except ZeroDivisionError: # gotta launch the game
        raise RuntimeError("Launch Limbus Company!")

    QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
    return

