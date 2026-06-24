from collections import defaultdict

from source.utils.utils import *
from source.shop.browse_shop import *
from itertools import combinations_with_replacement
from source_app.params import CACHE
from source.teams import TEAMS
from itertools import groupby

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

def fuse():
    for i, team in enumerate(p.GIFTS):
        if fusions_complete_for(team):
            continue
        fuse_any_strict_fusions(i)
        missing_tiers = fuse_one_tiered_fusion(i)
        if missing_tiers:
            fuse_one_tiered_fusion(i, skips=1)
            return missing_tiers

    return fuse_lunar()

def get_strict_fusion_list():
    gift_list = []
    for team in p.GIFTS:
        for fusion in team["strict_fusions"]:
            for name, _ in fusion.items():
                gift_list.append(name)
    return gift_list

def handle_available_fusion():
    go_to_top_fast()
    if not now_rgb.button("fusion_available"):
        return False
    
    gift_list = get_strict_fusion_list()
    if not gift_list:
        return False

    if click_gifts_for_available_fusion(gift_list, REG["fuse_shelf_top"]):
        return True

    return False

def fuse_lunar():
    if 1 == 1:
        return None # TODO: refactor
    if p.EXTREME and "lunarmemory" in get_inventory()["have"].keys():
        return None
    for _ in range(5):
        missing = fuse_one_lunar()
        if missing:
            return missing
    return None

# TODO: refactor to reflect new team configs!!!
def fuse_one_lunar():
    inventory = get_inventory()
    have = inventory["have"]
    teams = list(TEAMS.values())
    to_click = []
    for i in range(7, 10):
        if not list(teams[i]["uptie2"].keys())[0] in have.keys():
            set_affinity(i, teams=teams)
            missing = execute_tier_fuse(4)
            return missing
        to_click.append(have[list(teams[i]["uptie2"].keys())[0]])
    stones_have = list(set([f"stone{i}" for i in range(7)]) & set(have.keys()))
    if len(stones_have) < 2:
        for i in range(7):
            if not f"stone{i}" in have.keys():
                set_affinity(i, teams=teams)
                missing = execute_tier_fuse(4)
                return missing
    for i in range(2):
        to_click.append(have[stones_have[i]])
    if p.SUPER == "supershop":
        perform_clicks(to_click)
    return None

def fuse_one_tiered_fusion(i, skips=0):
    named_locs = get_named_locs()
    team = p.GIFTS[i]
    print("fuse_one_tiered_fusion", i, named_locs)
    for fusion in team["tiered_fusions"]:
        for item, tier in fusion.items():
            if item in named_locs:
                continue
            if skips > 0:
                skips -= 1
                continue
            print("want to fuse ", fusion, " and I own ", named_locs)
            combo, missing = decide_fusion(tier)
            if missing:
                lower_tiers = [t for t in missing.keys() if t < tier]
                lower_tiers.sort()
                if lower_tiers:
                    nested_combo, nested_missing = decide_fusion(lower_tiers[0], exclude_tiers=missing)
                    if not nested_missing:
                        execute_tier_fuse(lower_tiers[0], i, exclude_tiers=missing)
                        return execute_tier_fuse(tier, i)
                return missing
            else:
                return execute_tier_fuse(tier, i)
    return None

def simulate_all_tiered_fusions(include_lower_tiers=True):
    named_locs = get_named_locs()
    tiers_for_combos = []
    tiers_missing = []
    for i, team in enumerate(p.GIFTS):
        for fusion in team["tiered_fusions"]:
            for item, tier in fusion.items():
                if item in named_locs:
                    continue
                combo, missing = decide_fusion(tier)
                print("simulate:", "combo", combo, "missing", missing)
                tiers_for_combos.extend(combo or [])
                tiers_missing.extend(missing or [])
                if missing and include_lower_tiers:
                    lower_tiers = [t for t in missing.keys() if t < tier]
                    print("lower_tiers", lower_tiers)
                    if lower_tiers:
                        nested_combo, nested_missing = decide_fusion(lower_tiers[0])
                        print("nested", nested_combo, nested_missing)
                        tiers_for_combos.extend(nested_combo or [])
                        tiers_missing.extend(nested_missing or [])
    return tiers_for_combos, tiers_missing

def fuse_any_strict_fusions(i):
    named_locs = get_named_locs()
    team = p.GIFTS[i]
    for fusion in team["strict_fusions"]:
        for name, ingredients in fusion.items():
            missing = {}
            for ingredient, tier in ingredients.items():
                if ingredient not in named_locs:
                    missing[ingredient] = tier
            if missing:
                print(f"Missing items for fusing. {name} still needs {missing}")
                return missing
            set_affinity(i)
            if handle_available_fusion():
                return None
            locs = [named_locs[name] for name in ingredients.keys()]
            click_locs(locs)
            
    return None

def set_affinity(i, teams=None):
    if init_fuse(i):
        return
    if teams is None:
        teams = p.GIFTS
    if p.IDX == i:
        return
    p.IDX = i
    ClickAction((469, 602), ver="keywordSel").execute(shop_click)
    win_moveTo(605, 612)
    confirm_affinity(teams=teams)
    time.sleep(0.2)

def click_gifts_for_available_fusion(gifts, reg):
    fused_some = False
    for (x, y, gift) in find_gifts_for_fusion(gifts, reg):
        ignore = LocateRGB.locate_all(PTH["cannot_fuse"], region=reg, threshold=80)
        if any(abs(gui.center(res)[0] - x) < 50 for res in ignore):
            continue
        win_click((x, y))
        fuse_selected()
        fused_some = True
        time.sleep(0.1)
        if LocateGray.check(PTH["gifts_owned"], region=REG["gifts_owned"], wait=False):
            break
    return fused_some

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

def find_locs_for_fusion(combo, coords):
    coords.sort(key=lambda coord: (coord[1]["keep"], coord[0]))
    print("wtf coords", coords)
    groups = defaultdict(list)
    for loc, item in coords:
        if "tier" in item:
            groups[item["tier"]].append((loc, item))
    locs = []
    print("combo for fusion", combo)
    print("groups", groups)
    for tier in combo:
        if tier in groups and groups[tier]:
            loc, item = groups[tier].pop()
            print("fusion: loc", loc, "item", item)
            locs.append(loc)
    if len(locs) < len(combo):
        print("Error: don't have enough items for combo fusion")
        return []
    return locs

def execute_tier_fuse(tier, affinity, exclude_tiers={}):
    to_click = []
    combo, missing = decide_fusion(tier, exclude_tiers=exclude_tiers)
    if missing:
        return missing
    
    if not combo:
        return None

    have = get_inventory()["have"]
    coords = [(loc, item) for loc, item in have.items() if item["fuse"]]
    locs = find_locs_for_fusion(combo, coords)
    for loc in locs:
        to_click.append(loc)

    if not locs:
        return
    set_affinity(affinity)
    click_locs(locs)
    p.NEED_INVENTORY_CHECK = True
    get_inventory()
    return None

def fuse_selected():
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
    pass

def click_locs(locs):
    if p.WISHMAKING and not now_rgb.button("wishmaking"):
        time.sleep(0.1)
        wait_while_condition(lambda: not now.button("Confirm.0"), lambda: win_click(410, 755), interval=0.1, timer=0.2)
        wait_while_condition(lambda: now_click.button("Confirm.0"))
        win_moveTo(1194, 841)
        time.sleep(0.2)

    clicks_left = len(locs)
    def scan(starting_row, reg, row_height):
        nonlocal clicks_left
        usable_rows = get_usable_rows(reg, row_height)
        max_j = starting_row + usable_rows
        for i, j in locs:
            if starting_row <= j < max_j:
                x, y = to_coords(i, j, reg, row_height)
                win_click(x, y)
                clicks_left -= 1
                time.sleep(0.1)
        return get_usable_rows(reg, row_height) if clicks_left > 0 else -1
    # ClickAction((x, y) , ver="forecast!").execute(click_rgb)

    scan_entire_inventory_while_parsing(scan, location="fuse")
    fuse_selected()    

def decide_fusion(target_tier, exclude_tiers={}):
    have = get_inventory()["have"]
    all_available = [(loc, gift) for loc, gift in have.items() if gift["fuse"]]
    by_tier = {key: list(group) for key, group in groupby(all_available, lambda pair: pair[1].get("tier", -1))}
    for tier, count in exclude_tiers.items():
        if tier in by_tier:
            new_len = max(0, len(by_tier[tier]) - count)
            by_tier[tier] = by_tier[tier][0:new_len]

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
        and ((target_tier <= 2 and not exclude_tiers) or all([t < target_tier for t in combo]))
    ]
    print("valid_combos", valid_combos)
    
    best_choice = None
    best_missing = None
    best_missing_cost = None
    best_total_cost = None

    for combo, total in valid_combos:
        needed = combo_counter(combo)
        missing = {}
        missing_cost = 0
        for tier, count_needed in needed.items():
            num_owned = len(by_tier[tier]) if tier in by_tier else 0
            if num_owned < count_needed:
                deficit = count_needed - num_owned
                missing[tier] = deficit
                missing_cost += deficit * item_points[tier]
        
        if missing.get(4, 0) > 0: # we are not buying tier 4 for fusion, no way
            continue
        
        if p.SUPER == "shop" and missing.get(3, 0) == 1 and \
           sum([missing.get(i, 0) for i in range(1, 2)]) == 0:
            owned_counts = {tier: len(gifts) for gifts in by_tier.items()}
            skip_missing = True
            for i in range(1, 5): # update inventory
                if i in needed.keys():
                    for _ in range(needed[i]):
                        if i == 3 and skip_missing:
                            skip_missing = False
                            continue
                        if i in owned_counts and owned_counts[i] > 0:
                            owned_counts[i] -= 1
            new_combo = None
            best_price = None
            for tier3_combo, price in get_tier3: # I don't want to do a recursion
                need = combo_counter(tier3_combo)
                for tier, count_needed in need.items():
                    if tier not in owned_counts or owned_counts[tier] < count_needed:
                        break
                else:
                    if best_price is None or price < best_price:
                        new_combo = tier3_combo
                        best_price = price
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

    return best_choice, best_missing # TODO: sometimes both are None, this is bad

def expected_combo_for(tier):
    expected = {
        1: (1, 1),
        2: (1, 2),
        3: (2, 2, 1),
        4: (3, 2, 2),
    }
    return expected.get(tier, ())

def combo_counter(combo):
    counter = {}
    for tier in combo:
        if tier in counter:
            counter[tier] += 1
        else:
            counter[tier] = 1
    return counter