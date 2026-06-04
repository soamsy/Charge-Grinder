from source.utils.utils import *
import source.utils.params as p
from source.shop.browse_shop import *
from source.shop.fuse import *
from source.shop.sell import *
from source.shop.uptie import *
from source.shop.heal import *
from source.shop.skill3 import *

def apply_inflation(value):
    if 13 > p.LVL > 10:
        value = value // 2
    elif p.LVL >= 13:
        value = value // 3
    return value

def conf_gift():
    try:
        Action("purchase", ver="connecting").execute(click)
        connection()
        p.NEED_BALANCE_CHECK = True
    except RuntimeError:
        pass

    time.sleep(0.2)
    input_with_fallback(
        "space", 
        lambda: now_click.button("Confirm"),
        lambda: wait_while_condition(
            lambda: loc.button("Confirm", wait=0.1),
            timer=2
        )
    )

def update_shelf():
    shop_shelf = screenshot(region=REG["buy_shelf"]) # ( 809,  300,  942,  402),
    shop_shelf = rectangle(shop_shelf, (52, 33), (224, 195), (0, 0, 0), -1)
    for ignore in ["purchased", "cost"]:
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(ignore)], region=REG["buy_shelf"], image=shop_shelf, threshold=20)]
        for res in found:
            shop_shelf = rectangle(shop_shelf, (int(res[0] - 70 - 809), int(res[1] - 25 - 300)), (int(res[0] + 70 - 809), int(res[1] + 150 - 300)), (0, 0, 0), -1)
    return shop_shelf

def filter_x_distance(points, x_tol=2, y_tol=25):
    points = sorted(points, key=lambda p: p[0])
    result = []
    for p in points:
        if all(abs(p[0] - q[0]) >= x_tol or abs(p[1] - q[1]) > y_tol for q in result):
            result.append(p)
    return result

def get_shop(shop_shelf):
    tier1 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy1"], region=REG["buy_shelf"], image=shop_shelf, threshold=3.5, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
    tier4 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy4"], region=REG["buy_shelf"], image=shop_shelf, threshold=10, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
    tier1 = filter_x_distance(tier1)
    tiers_available = {1: [], 2: [], 3: [], 4: []}
    visited = set()
    for i, pt_i in enumerate(tier1):
        if i in visited: continue
        count = 1
        for j in range(i + 1, len(tier1)):
            pt_j = tier1[j]
            if all(abs(pt_i[k] - pt_j[k]) <= 25 for k in range(2)):
                visited.add(j)
                count += 1
        tiers_available[min(count, 3)].append(pt_i)
    tiers_available[1] = [
        (fx, fy) for (fx, fy) in tiers_available[1]
        if not any(abs(fx - x) <= 25 and abs(fy - y) <= 25 for (x, y) in tier4)
    ]
    tiers_available[4] = tier4
    return tiers_available

def buy_known(aff):
    shop_shelf = update_shelf()
    for gift in aff["buy"]:
        try:
            res = gui.center(LocateRGB.try_locate(PTH[gift], image=shop_shelf, region=REG["buy_shelf"], comp=0.75, conf=0.83))
            print(f"bought {gift}")
            win_click(res, tsize=(90, 90))
            conf_gift()
            time.sleep(0.1)
            schedule_for_uptie(gift)
            shop_shelf = update_shelf()
            p.NEED_INVENTORY_CHECK = True
            p.NEED_BALANCE_CHECK = True
        except gui.ImageNotFoundException:
            continue
    return shop_shelf

def buy_affinity(aff):
    gained = {1: 0, 2: 0, 3: 0, 4: 0}
    box = True
    shop_shelf = update_shelf()
    tiers_available = get_shop(shop_shelf)
    print("buy affinity", tiers_available)
    cv2.imwrite(f"testing/shelf_shelf_{datetime.now().second}", shop_shelf)
    for tier, points in tiers_available.items():
        debug_points(shop_shelf, points + [(x+240, y+240) for x, y in points], f"testing/shelf_{datetime.now().second}_{tier}")
        for x, y in points:
            box = LocateRGB.locate(PTH[aff["checks"][0]], region=(x, y, 240, 240), image=shop_shelf, method=cv2.TM_SQDIFF_NORMED, comp=0.88, conf=0.8)
            if not box:
                continue
            res = gui.center(box)
            win_click(res)
            conf_gift()
            shop_shelf = update_shelf()
            p.NEED_INVENTORY_CHECK = True
            p.NEED_BALANCE_CHECK = True
            gained[tier] += 1
    return shop_shelf, gained

def buy(already_gained, missing, buy_anyway=False):
    gained = {1: 0, 2: 0, 3: 0, 4: 0}
    missing = missing.copy()
    keywordless = [{"buy": [name for name, state in p.KEYWORDLESS.items() if state > 1], "sin": True}]
    def got_tier(tier, count):
        gained[tier] += count
        need = missing.get(tier, 0)
        missing[tier] = need - count
        if missing[tier] <= 0:
            del missing[tier]

    for team in keywordless + p.GIFTS:
        if team["sin"]:
            shop_shelf = buy_known(team)
        elif buy_anyway:
            shop_shelf, bought = buy_affinity(team)
            for tier, count in bought.items():
                got_tier(tier, count)

    for tier in sorted(missing.keys(), reverse=True):
        if balance() < enhance_cost[tier]:
            break
        for _ in range(missing[tier]):
            tiers_available = get_shop(shop_shelf)
            if not tiers_available[tier]:
                break
            win_click(tiers_available[tier][0])
            conf_gift()
            shop_shelf = update_shelf()
            p.NEED_INVENTORY_CHECK = True
            p.NEED_BALANCE_CHECK = True
            got_tier(tier, 1)

    for tier, count in already_gained.items():
        gained[tier] += count
    return gained, missing

def try_keyword_refresh():
    costs = {
        0: 0 if p.BUFF[5] > 0 else 90,
        1: 90 if p.BUFF[5] > 0 else 135,
    }
    if not p.REFRESH_KEYWORD_COUNT in costs:
        return False
    refresh_cost = costs[p.REFRESH_KEYWORD_COUNT]
    if balance() - refresh_cost < 120:
        return False
    
    Action(p.SUPER, click=(1715, 176), ver="keywordRef").execute(shop_click)
    wait_while_condition(
        condition=lambda: now.button("keywordRef") and not now.button("connecting"), 
        action=confirm_affinity
    )
    connection()
    p.REFRESH_KEYWORD_COUNT += 1
    p.NEED_BALANCE_CHECK = True
    return True

def try_refresh():
    costs = {
        0: 0 if p.BUFF[0] > 0 else 30,
        1: 30 if p.BUFF[0] > 0 else 60,
    }
    if p.REFRESH_COUNT not in costs:
        return False
    refresh_cost = costs[p.REFRESH_COUNT]
    if balance() - refresh_cost < 120:
        return False
    win_click(1489, 177, tsize=(180, 53))
    connection()
    time.sleep(0.1)
    p.REFRESH_COUNT += 1
    p.NEED_BALANCE_CHECK = True
    return True

def buy_a_lot(missing, buy_anyway=False):
    gained = {1: 0, 2: 0, 3: 0, 4: 0}
    def should_stop():
        have_everything = not missing and not buy_anyway
        ans = balance() < 120 or p.UPTIE_QUEUE or p.UPTIE_INCOMPLETE_QUEUE or have_everything
        print("ans", ans, "balance", balance(), "uptie", p.UPTIE_QUEUE + p.UPTIE_INCOMPLETE_QUEUE, "missing", missing, "buy_anyway", buy_anyway)
        return ans
    if should_stop(): return gained, missing

    gained, missing = buy(gained, missing, buy_anyway)
    if should_stop(): return gained, missing

    if try_refresh():
        update_skill3()
        if should_stop(): return gained, missing

        gained, missing = buy(gained, missing, buy_anyway)
        if should_stop(): return gained, missing

    if try_keyword_refresh():
        update_skill3()
        if should_stop(): return gained, missing
        gained, missing = buy(gained, missing, buy_anyway)

    return buy(gained, missing)

def fuse_buy_loop():
    if has_all_fusions():
        return
    for i in range(3):
        try:
            missing = fuse() or {}
            p.NEED_FOR_FUSION = missing
        except Exception as error:
            print("oops", error)
            break

        print("missing", missing)
        if missing:
            close_panel()
            if len(LocateRGB.locate_all(PTH["purchased"], region=REG["buy_shelf"], threshold=100)) == 8: return
            _, missing = buy_a_lot(missing)
        if missing or has_all_fusions():
            break
        
    close_panel()

def leave():
    p.MOVE_FAST_NEXT_TIME = True
    ClickAction((1705, 967), ver="ConfirmInvert").execute(click)
    wait_while_condition(lambda: loc.button("ConfirmInvert", wait=0.5), lambda: gui.press("space"), interval=0.2, timer=5)
    wait_while_condition(lambda: now.button(p.SUPER), timer=5)

def stuck_in_menu():
    if now.button("Confirm"):
        menu_disappeared = input_with_fallback("space", lambda: now_click.button("Confirm"), lambda: wait_while_condition(lambda: now.button("Confirm"), timer=2))
        if not menu_disappeared:
            return True
    return False

def invalidate_inventory():
    p.NEED_INVENTORY_CHECK = True
    p.NEED_BALANCE_CHECK = True
    p.REFRESH_COUNT = 0
    p.REFRESH_KEYWORD_COUNT = 0

def enter_shop():
    if now_click.button("return"): time.sleep(0.3)
    if now.button("shop"): p.SUPER = "shop"
    elif not now.button("supershop"): return False
    else: p.SUPER = "supershop"
    print("shop check")
    if stuck_in_menu():
        return False

    sell_unnecessary()
    heal_sinners()
    update_skill3()

    last_level = 5 + p.EXTREME*11
    should_skip = p.SKIP and p.LVL >= last_level
    if not should_skip:
        fuse_buy_loop()
        apply_upties()
        buy_a_lot({}, buy_anyway=True)

    leave()
    p.EXPECT_ACTION = "move"
    return True