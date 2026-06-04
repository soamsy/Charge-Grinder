from source.utils.utils import *
from source.shop.browse_shop import *
from itertools import combinations_with_replacement
from source_app.params import CACHE
from source.teams import TEAMS

TWO_ITEM_COMBOS = list(combinations_with_replacement(range(1, 5), 2))

item_points = {1: 3, 2: 6, 3: 10, 4: 15}

fusion_ranges = {
    1: (9, 10),
    2: (11, 16),
    3: (17, 24),
    4: (25, 45)
}

super_ranges = {
    1: (9, 9),
    2: (10, 14),
    3: (15, 21),
    4: (22, 75)
}

COMBOS = list(combinations_with_replacement(range(1, 5), 3))
get_tier3 = [((1, 1, 4), 21), ((1, 2, 3), 19), ((1, 2, 4), 24), ((1, 3, 3), 23), ((2, 2, 2), 18), ((2, 2, 3), 22)]

EXTRA = []
for i in range(3, 6):
    EXTRA += list(combinations_with_replacement(range(1, 5), i))

def init_fuse():
    if not now.button(p.SUPER): return
    chain_actions(shop_click, [
        Action(p.SUPER, click=(405, 580), ver="fuse"),
        lambda: win_moveTo(469, 602, duration=0.1),
        ClickAction((469, 602), ver="keywordSel")
    ])
    win_moveTo(605, 612)
    for i, team in enumerate(p.GIFTS):
        if has_fusions_for(team):
            continue
        p.IDX = i
        break
    confirm_affinity()

def fuse():
    init_fuse()

    if handle_available_fusion():
        hook_x = find_hook_x()
        while not_at_bottom():
            print("scroll down for inventory scan alignment")
            browse_fast(hook_x)
            time.sleep(0.3)

    order = [
        fuse_one_uptie2,
        fuse_one_extra,
        fuse_one_by_type,
    ]

    first_missing = None
    for i, _ in enumerate(p.GIFTS):
        for action in order:
            missing = action(i)
            if missing and not first_missing:
                first_missing = missing

    return first_missing or fuse_lunar()

def get_fuse_list():
    gift_list = p.GIFTS[0]["goal"]

    for i in range(2, 5, 2):
        if not p.GIFTS[0].get(f"fuse{i}", False):
            continue
        gift_list += [name for name, tier in p.GIFTS[0][f"fuse{i}"].items() if tier is None]
    return gift_list    

def handle_available_fusion():
    print("checking available fusion...")
    hook_x = find_hook_x()
    while not_at_top():
        print("scroll up for alignment")
        browse_fast(hook_x, up=True)
        time.sleep(0.3)

    if not now_rgb.button("fusion_available"):
        return now_rgb.button("scroll", "scroll_full")
    
    gift_list = get_fuse_list()
    print(f"gifts to fuse: {gift_list}")
    if not gift_list: return now_rgb.button("scroll", "scroll_full")
    
    if click_gifts_for_fusion(gift_list, REG["fuse_shelf_top"], chain=fuse_selected, is_fuse=True):
        return now_rgb.button("scroll", "scroll_full")
    
    if now_rgb.button("scroll", "scroll_full"):
        h = 1
        adj = 0
        hook_x = find_hook_x()
        while not_at_bottom():
            print("scroll down for available fusions tab")
            browse(hook_x, adj=adj)
            if click_gifts_for_fusion(gift_list, REG["fuse_shelf_top"], chain=fuse_selected, is_fuse=True):
                return now_rgb.button("scroll", "scroll_full")
            ck = LocateRGB.locate(PTH["height_ck"], region=REG["fuse_shelf_top"])
            adj = 625 - gui.center(ck)[1] if ck else 0
            h += 1
    return False

def fuse_one_extra(i):
    init_fuse()
    team = p.GIFTS[i]
    for name, tier in team["fuse_ex"].items():
        while not name in get_inventory()["have"].keys():
            set_affinity(i)
            missing = actual_fuse(tier, get_inventory()["coords"])
            return missing
    return None

def fuse_lunar(_ignored_index):
    init_fuse()
    if p.EXTREME and "lunarmemory" in get_inventory()["have"].keys():
        return None
    for _ in range(5):
        missing = fuse_one_lunar()
        if missing:
            return missing
    return None

def fuse_one_lunar():
    inventory = get_inventory()
    coords = inventory["coords"]
    have = inventory["have"]
    teams = list(TEAMS.values())
    to_click = []
    for i in range(7, 10):
        if not list(teams[i]["uptie2"].keys())[0] in have.keys():
            set_affinity(i, teams=teams)
            missing = actual_fuse(4, coords)
            return missing
        to_click.append(have[list(teams[i]["uptie2"].keys())[0]])
    stones_have = list(set([f"stone{i}" for i in range(7)]) & set(have.keys()))
    if len(stones_have) < 2:
        for i in range(7):
            if not f"stone{i}" in have.keys():
                set_affinity(i, teams=teams)
                missing = actual_fuse(4, coords)
                return missing
    for i in range(2):
        to_click.append(have[stones_have[i]])
    if p.SUPER == "supershop":
        perform_clicks(to_click)
    return None

def fuse_one_by_type():
    init_fuse()
    to_click = []
    inventory = get_inventory()
    have = inventory["have"]
    coords = inventory["coords"]
    sub_goal = sub_goal_search(have)
    if not sub_goal:
        return None
    i, _, fuse_type = sub_goal[0]
    for name, tier in p.GIFTS[p.IDX][f"fuse{fuse_type+1}"].items():
        if not name in have.keys():
            if tier != None:
                return actual_fuse(tier, coords)
            else: # need to fuse
                for name, tier in p.GIFTS[p.IDX][f"fuse{fuse_type}"].items():
                    if not name in have.keys():
                        return actual_fuse(tier, coords)
                    to_click.append(have[name])
                set_affinity(i)
                perform_clicks(to_click)
                return None
        to_click.append(have[name])
    set_affinity(i)
    perform_clicks(to_click)
    return None

def fuse_one_uptie2(i):
    init_fuse()
    inventory = get_inventory()
    coords = inventory["coords"] if p.EXTREME else inventory["coords_agg"]
    team = p.GIFTS[i]
    for item in team["uptie2"].keys():
        if item in inventory["have"]:
            continue
        set_affinity(i)
        return actual_fuse(4, coords)
    return None

def has_fusions_for(config):
    needed = []
    needed.extend(config["uptie2"].keys())
    needed.extend(config["goal"])
    needed.extend(config.get("fuse1", {}).keys())
    needed.extend(config.get("fuse2", {}).keys())
    needed.extend(config.get("fuse3", {}).keys())
    needed.extend(config.get("fuse4", {}).keys())
    needed.extend(config.get("fuse_ex", {}).keys())
    return all([item in p.INVENTORY["have"] for item in needed])

def has_all_fusions():
    for config in p.GIFTS:
        if not has_fusions_for(config):
            return False

    if p.EXTREME and "lunarmemory" not in p.INVENTORY["have"]:
        return False
    return True

def sub_goal_search(have):
    sub_goal = []
    if not p.GIFTS[0]["goal"]:
        return []
    if p.GIFTS[0]["sin"] and p.GIFTS[0]["goal"] and not p.GIFTS[0]["goal"][0] in have.keys():
        sub_goal.append((0, search_have(have, 1, 0), 1))
    if p.is_on_hard() and p.GIFTS[0]["sin"] and p.GIFTS[0]["goal"] and len(p.GIFTS[0]["goal"]) > 1 and not p.GIFTS[0]["goal"][1] in have.keys():
        sub_goal.append((0, search_have(have, 3, 0), 3))
    sub_goal.sort(key=lambda item: (item[1], item[0]))
    return sub_goal

def search_have(have, fuse_type, idx):
    missing = 0
    iterations = 0
    names = []
    if name := next((key for key, value in p.GIFTS[idx][f"fuse{fuse_type + 1}"].items() if value is None), None):
        if name in have:
            iterations += 2
        else:
            names += list(p.GIFTS[idx][f"fuse{fuse_type}"].keys())

    names += [key for key, value in p.GIFTS[idx][f"fuse{fuse_type + 1}"].items() if value is not None]
    for name in names:
        if name not in have.keys():
                missing += 1
        iterations += 1
    return missing/iterations

def set_affinity(i, teams=None):
    if teams is None: teams = p.GIFTS
    if p.IDX == i: return
    p.IDX = i
    ClickAction((469, 602), ver="keywordSel").execute(shop_click)
    win_moveTo(605, 612)
    confirm_affinity(teams=teams)
    time.sleep(0.2)

def click_gifts_for_fusion(gifts, reg, chain=None):
    if LocateGray.check(PTH["gifts_owned"], region=REG["gifts_owned"], wait=False):
        return True
    
    gift_searcher = find_gifts_for_fusion(gifts, reg)
    for (x, y, gift) in gift_searcher:
        ignore = LocateRGB.locate_all(PTH["cannot_fuse"], region=reg, threshold=80)
        if any(abs(gui.center(res)[0] - x) < 50 for res in ignore):
            continue

        win_click((x, y))
        time.sleep(0.1)
        if LocateGray.check(PTH["gifts_owned"], region=REG["gifts_owned"], wait=False):
            print("all fused!")
            return True
    return False

def find_gifts_for_fusion(gifts, reg):
    for gift in gifts:
        fuse_shelf = screenshot(region=reg)
        image = amplify(fuse_shelf)
        try:
            if gift in CACHE: template = CACHE[gift]
            else: template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
            yield (x, y, gift)
        except gui.ImageNotFoundException:
            continue

def actual_fuse(tier, coords, depth=0):
    to_click = []
    combo, missing = decide_fusion(tier, coords, depth)
    print("fusing", combo, "and missing", missing)
    if not missing:
        for tier in combo:
            to_click.append(coords[tier][-1])
            coords[tier].pop(-1)
        perform_clicks(to_click)
        p.NEED_INVENTORY_CHECK = True
        get_inventory()
        return None
    else: return missing

def fuse_selected(gift=None):
    wait_while_condition(lambda: not now.button("Confirm.2"), lambda: win_click(1197, 876) if now.button("fuse") else None, timer=1.5)
    wait_while_condition(lambda: not now.button("Confirm"), lambda: gui.press("space") if now.button("Confirm.2") else None, timer=1.5)
    connection()
    wait_while_condition(
        lambda: loc.button("Confirm", wait=0.5), 
        lambda: gui.press("space"), 
        interval=0.1
    )
    p.NEED_INVENTORY_CHECK = True

def perform_clicks(to_click):
    if p.WISHMAKING and not now_rgb.button("wishmaking"):
        time.sleep(0.1)
        wait_while_condition(lambda: not now.button("Confirm.0"), lambda: win_click(410, 755), interval=0.1, timer=0.2)
        wait_while_condition(lambda: now_click.button("Confirm.0"))
        win_moveTo(1194, 841)
        time.sleep(0.2)

    hook_x = find_hook_x()
    while not_at_bottom():
        print("scroll down for inventory click alignment")
        browse_fast(hook_x)
        time.sleep(0.5)

    to_click = sorted(to_click, key=lambda x: x[2])
    h = 0
    adj = 0
    for pos in to_click:
        if pos[2] - h > 0:
            print("iterating items for fuse")
            for _ in range(pos[2] - h):
                browse(hook_x, step=-135, adj=adj)
                ck = LocateRGB.locate(PTH["height_ck"], region=REG["fuse_shelf_low"])
                adj = 625 - gui.center(ck)[1] if ck else 0
            h = pos[2]
            time.sleep(0.2)
        ClickAction(pos[:2], ver="forecast!").execute(click_rgb)
        print("pos", pos)
    
    fuse_selected()
    to_click.clear()

    hook_x = find_hook_x()
    while not_at_top():
        print("scroll up for alignment")
        browse_fast(hook_x, up=True)
        time.sleep(0.3)

def decide_fusion(target_tier, inventory, depth=0):
    if target_tier not in fusion_ranges: raise ValueError("Invalid target fusion tier")

    if p.SUPER == "shop":
        combos = COMBOS
        ranges = fusion_ranges
    else:
        combos = EXTRA
        ranges = super_ranges

    if p.WISHMAKING:
        combos += TWO_ITEM_COMBOS

    low, high = ranges[target_tier]
    valid_combos = [
        (combo, sum(item_points[t] for t in combo))
        for combo in combos
        if low <= sum(item_points[t] for t in combo) <= high
        and (depth == 0 or all([t < target_tier for t in combo]))
    ]
    
    best_choice = None
    best_missing = None
    best_missing_cost = None
    best_total_cost = None

    for combo, total in valid_combos:
        needed = combo_counter(combo)
        missing = {}
        missing_cost = 0
        for tier, count_needed in needed.items():
            have = len(inventory[tier])
            if have < count_needed:
                deficit = count_needed - have
                missing[tier] = deficit
                missing_cost += deficit * item_points[tier]
        
        if missing.get(4, 0) > 0: # we are not buying tier 4 for fusion, no way
            continue
        
        if p.SUPER == "shop" and not depth and missing.get(3, 0) == 1 and \
           sum([missing.get(i, 0) for i in range(1, 2)]) == 0:
            new_have = {tier: len(items) for tier, items in inventory.items()}
            skip_missing = True
            for i in range(1, 5): # update inventory
                if i in needed.keys():
                    for _ in range(needed[i]):
                        if i == 3 and skip_missing:
                            skip_missing = False
                            continue
                        if new_have[i] > 0:
                            new_have[i] -= 1
            new_combo = None
            best_price = None
            for tier3_combo, price in get_tier3: # I don't want to do a recursion
                need = combo_counter(tier3_combo)
                for tier, count_needed in need.items():
                    if new_have[tier] < count_needed:
                        break
                else:
                    if best_price is None or price < best_price:
                        new_combo = tier3_combo
                        best_price = price
            # new_combo, new_missing = decide_fusion(3, new_inventory, 1)
            if new_combo:
                combo = new_combo
                missing = {}
                missing_cost = 0
                total = total - item_points[3] + best_price

        if best_missing_cost is None        or \
           missing_cost < best_missing_cost or \
          (missing_cost == best_missing_cost and 
           total < best_total_cost):

            best_choice = combo
            best_missing = missing
            best_missing_cost = missing_cost
            best_total_cost = total

    return best_choice, best_missing

def combo_counter(combo):
    counter = {}
    for tier in combo:
        if tier in counter:
            counter[tier] += 1
        else:
            counter[tier] = 1
    return counter