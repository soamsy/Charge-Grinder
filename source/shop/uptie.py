from source.utils.utils import *
from itertools import combinations_with_replacement
import source.utils.params as p
from source.teams import TEAMS
from source_app.params import CACHE
from source.shop.browse_shop import *

enhance_cost_first = { 1: 50, 2: 60, 3: 75, 4: 100, }
enhance_cost_second = { tier: cost*2 for tier, cost in enhance_cost_first.items() }
enhance_cost = { tier: cost*3 for tier, cost in enhance_cost_first.items() }

def open_enhance():
    ClickAction((250, 581), ver="power").execute(click)

def find_gifts_in_queue():
    to_uptie_half1 = []
    to_uptie_half2 = []
    to_uptie_full = []

    bal = balance()
    for item, tier in p.UPTIE_INCOMPLETE_QUEUE:
        cost = enhance_cost_second[tier]
        if cost < bal:
            to_uptie_half2.append((item, tier))
            bal -= cost

    for item, tier in p.UPTIE_QUEUE:
        cost = enhance_cost[tier]
        halfway_cost = enhance_cost_first[tier]
        if cost < bal:
            to_uptie_full.append((item, tier))
            bal -= cost
        elif halfway_cost < bal:
            to_uptie_half1.append((item, tier))
            bal -= cost

    return to_uptie_half1, to_uptie_half2, to_uptie_full

def apply_upties():
    to_uptie_half1, to_uptie_half2, to_uptie_full = find_gifts_in_queue()
    if not (to_uptie_half2 or to_uptie_half1 or to_uptie_full):
        return
    print("to_uptie_half1", to_uptie_half1)
    print("to_uptie_half2", to_uptie_half2)
    print("to_uptie_full", to_uptie_full)

    open_enhance()
    for gift in uptie_inventory_gifts(to_uptie_half2, 1):
        p.UPTIE_INCOMPLETE_QUEUE.remove(gift)
    for gift in uptie_inventory_gifts(to_uptie_half1, 1):
        p.UPTIE_QUEUE.remove(gift)
        p.UPTIE_INCOMPLETE_QUEUE.append(gift)
    for gift in uptie_inventory_gifts(to_uptie_full, 2):
        p.UPTIE_QUEUE.remove(gift)
    if are_upties_done():
        p.FINISHED_ALL_UPTIES = True
    close_panel()

def uptie_inventory_gifts(gift_list, times):
    if not gift_list:
        return []
    uptied = []
    def click_visible_upties(scrolls_from_bottom, reg, row_height):
        uptied.extend(click_gifts_for_uptie(gift_list, reg, times))
        return get_usable_rows(reg, row_height)

    scan_entire_inventory_while_parsing(click_visible_upties, location="uptie")
    return uptied

def power_up(gift):
    print(f"uptying {gift}")
    wait_while_condition(lambda: not now.button("Confirm.2"), lambda: gui.press("space"), timer=1.5)
    wait_while_condition(lambda: not now.button("power"), lambda: gui.press("space"), timer=1.5)

def click_gifts_for_uptie(gifts, reg, times):
    print("Am i actually uptying", gifts, reg, times)
    uptied = []
    found_gifts = find_gifts_for_uptie(gifts, reg)
    for (x, y, gift, tier) in found_gifts:
        ignore = LocateRGB.locate_all(PTH["cannot_fuse"], region=reg, threshold=80)
        if any(abs(gui.center(res)[0] - x) < 50 for res in ignore):
            continue

        win_click((x, y))
        for _ in range(times):
            power_up(gift)
        uptied.append((gift, tier))
    return uptied

def find_gifts_for_uptie(gifts, reg):
    fuse_shelf = screenshot(region=reg)
    image = amplify(fuse_shelf)

    for gift, tier in gifts:
        try:
            if gift in CACHE: template = CACHE[gift]
            else: template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
            print(f"can actually click on {gift}")
            yield (x, y, gift, tier)
        except gui.ImageNotFoundException:
            continue

def all_uptie_costs():
    costs = []
    for (item, tier) in all_uptie_items():
        if (item, tier) in p.UPTIE_QUEUE:
            costs.append(enhance_cost_first[tier])
            costs.append(enhance_cost_second[tier])
        elif (item, tier) in p.UPTIE_INCOMPLETE_QUEUE:
            costs.append(enhance_cost_second[tier])
    print("uptie_costs", costs, "uptie_queue", p.UPTIE_QUEUE, "uptie_half_queue", p.UPTIE_INCOMPLETE_QUEUE)
    return costs

def are_upties_done():
    all_uptie_names = []
    for team in p.GIFTS:
        for uptie in team["upties"]:
            for name, tier in uptie.items():
                all_uptie_names.append(name)
    owned_names = [gift["name"] for gift in p.INVENTORY["have"].values() if "name" in gift]
    for name in all_uptie_names:
        if name in p.UPTIE_SCHEDULED and not name in p.UPTIE_QUEUE and name not in p.UPTIE_INCOMPLETE_QUEUE:
            continue
        if name in owned_names and not name in p.UPTIE_SCHEDULED:
            print(f"Unexpected! {name} never got uptied")
            p.UPTIE_SCHEDULED.add(name)
            if name not in p.UPTIE_QUEUE:
                p.UPTIE_QUEUE.append(name)

        return False
    return True
