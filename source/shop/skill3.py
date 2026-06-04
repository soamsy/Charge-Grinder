from source.shop.browse_shop import *
from source.shop.sell import *

def update_skill3():
    if p.EXTREME or p.is_saikai():
        for _ in range(1 + int(p.SUPER == "supershop")):
            buy_skill3()

def skill3_available():
    sold = LocateGray.locate_all(PTH["purchased"], region=REG["purchased_s3"])
    if p.SUPER == "shop" and len(sold) < 1:
        return True
    if p.SUPER == "supershop" and len(sold) < 2:
        return True
    return False

def buy_skill3():
    if not skill3_available():
        return
    print("Trying to skill 3")

    sold = []
    coord = None
    for sinner in p.SELECTED[:7]:
        if p.is_saikai() and sinner != "RYOSHU":
            continue
        box = LocateGray.locate(PTH[f"{sinner.lower()}_s3"], region=REG["buy_s3"], conf=0.85)
        if box:
            coord = gui.center(box)
            if len(sold) > 0:
                sold_coord = gui.center(sold[0])
                if abs(coord[0] - sold_coord[0]) < 100:
                    continue
            break
    else:
        return
    
    if coord == None or coord[1] - 120 < 0:
        return

    print("Getting skill 3")
    ClickAction((coord[0], coord[1] - 120), ver="replace").execute(click)
    win_click(1442, 497)
    win_click(1187, 798)
    p.NEED_BALANCE_CHECK = True
    if not wait_while_condition(lambda: not loc.button(p.SUPER, wait=0.5), lambda: win_click(1187, 798), timer=1):
        win_click(953, 497)
        win_click(1187, 798)
        if not wait_while_condition(lambda: not loc.button(p.SUPER, wait=0.5), lambda: win_click(1187, 798), timer=1):
            win_click(772, 800)
            return
    connection()