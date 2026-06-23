from source.shop.browse_shop import *
from source.shop.sell import *

def update_skill3(budget):
    if budget < 120:
        return
    if p.EXTREME or p.is_saikai():
        for _ in range(1 + int(p.SUPER == "supershop")):
            if buy_skill3():
                budget -= 120
    return budget

def skill3_ranges():
    purchased_ranges = []
    buffer = 80
    sold1 = LocateGray.locate(PTH["purchased"], region=REG["purchased"])
    if sold1:
        center = gui.center(sold1)
        purchased_ranges.append([center[0]-buffer,center[0]+buffer])

    if p.SUPER == "supershop":
        sold2 = LocateGray.locate(PTH["purchased"], region=REG["purchased_sup!"])
        if sold2:
            center = gui.center(sold2)
            purchased_ranges.append([center[0]-buffer,center[0]+buffer])
    return purchased_ranges

def find_sinner(sinner, ranges):
    box = LocateGray.locate(PTH[f"{sinner.lower()}_s3"], region=REG["buy_s3"], conf=0.85)
    if box:
        coord = gui.center(box)
        for low, high in ranges:
            if low < coord[0] < high:
                return None
        return coord
    return None

def buy_skill3():
    purchased = skill3_ranges()
    if len(purchased) >= (2 if p.SUPER == "supershop" else 1):
        return False

    coord = None
    for sinner in p.SELECTED[:7]:
        if p.is_saikai() and sinner != "RYOSHU":
            continue
        coord = find_sinner(sinner, purchased)
        if coord:
            break

    if coord == None or coord[1] - 120 < 0:
        return False

    print("Getting skill 3")
    ClickAction((coord[0], coord[1] - 120), ver="replace").execute(click)
    win_click(1442, 497)
    win_click(1187, 798)
    p.NEED_BALANCE_CHECK = True
    if not wait_while_condition(lambda: not now.button(p.SUPER), lambda: win_click(1187, 798), timer=1):
        win_click(953, 497)
        win_click(1187, 798)
        if not wait_while_condition(lambda: not now.button(p.SUPER), lambda: win_click(1187, 798), timer=1):
            win_click(772, 800)
            return True
    connection()
    return True