from source.utils.utils import *
from itertools import combinations_with_replacement
import source.utils.params as p
from source.teams import TEAMS
from source_app.params import CACHE
from source.shop.browse_shop import *

enhance_cost_first = {
    1: 50,
    2: 60,
    3: 75,
    4: 100,
}

enhance_cost_second = { cost*2 for cost in enhance_cost_first }
enhance_cost = { cost*3 for cost in enhance_cost_first }

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
        p.UPTIE_INCOMPLETE_QUEUE.add(gift)
    for gift in uptie_inventory_gifts(to_uptie_full, 2):
        p.UPTIE_QUEUE.remove(gift)
    close_panel()

def uptie_inventory_gifts(gift_list):
    click_gifts_for_uptie(gift_list, REG["fuse_shelf"])
    if now_rgb.button("scroll", "scroll_full"):
        h = 1
        adj = 0
        hook_x = find_hook_x()
        while not_at_bottom():
            print("scroll down for uptie click")
            browse(hook_x, adj=adj)
            click_gifts_for_uptie(gift_list, REG["fuse_shelf_low"])
            ck = LocateRGB.locate(PTH["height_ck"], region=REG["fuse_shelf_low"])
            adj = 625 - gui.center(ck)[1] if ck else 0
            h += 1

def power_up(gift):
    print(f"uptying {gift}")
    wait_while_condition(lambda: not now.button("Confirm.2"), lambda: gui.press("space"), timer=1.5)
    wait_while_condition(lambda: not now.button("power"), lambda: gui.press("space"), timer=1.5)

def click_gifts_for_uptie(gifts, reg, times):
    found_gifts = find_gifts_for_uptie(gifts, reg)
    for (x, y, gift) in found_gifts:
        ignore = LocateRGB.locate_all(PTH["cannot_fuse"], region=reg, threshold=80)
        if any(abs(gui.center(res)[0] - x) < 50 for res in ignore):
            continue

        win_click((x, y))
        for _ in range(times):
            power_up(gift)
    return False

def find_gifts_for_uptie(gifts, reg):
    fuse_shelf = screenshot(region=reg)
    image = amplify(fuse_shelf)

    for gift in gifts:
        try:
            if gift in CACHE: template = CACHE[gift]
            else: template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
            print(f"can actually click on {gift}")
            yield (x, y, gift)
        except gui.ImageNotFoundException:
            continue

def total_uptie_cost():
    cost = 0
    for _, tier in p.UPTIE_INCOMPLETE_QUEUE:
        cost += enhance_cost_second[tier]
    for _, tier in p.UPTIE_QUEUE:
        cost += enhance_cost[tier]
    return cost

def all_uptie_items():
    return [g["uptie1"] | g["uptie2"] | g["uptie3"] for g in p.GIFTS]

def schedule_for_uptie(gift):
    for uptie in all_uptie_items():
        if gift in uptie and not gift in p.UPTIE_SCHEDULED:
            p.UPTIE_QUEUE.append((gift, uptie[gift]))
            p.UPTIE_SCHEDULED.add(gift)