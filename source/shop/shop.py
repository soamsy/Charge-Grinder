from source.utils.utils import *
import source.utils.params as p
from source.shop.browse_shop import *
from source.shop.fuse import *
from source.shop.sell import *
from source.shop.uptie import *
from source.shop.heal import *
from source.shop.skill3 import *
from source.shop.refresh import *

def conf_gift():
    try:
        Action("purchase", ver="connecting").execute(click)
        connection()
    except RuntimeError:
        pass

    time.sleep(0.16)
    gui.press("space")
    wait_while_condition(lambda: now.button("purchase"), lambda: now_click.button("purchase"), timer=1.0)
    wait_while_condition(lambda: now.button("Confirm"), lambda: now_click.button("Confirm"), timer=1.0)
    time.sleep(0.25)

def buy(already_gained, missing, budget, buy_affinity_junk=False):
    gained = {1: 0, 2: 0, 3: 0, 4: 0}
    missing = missing.copy()
    keywordless = [{"buy": [name for name, state in p.KEYWORDLESS.items() if state > 1], "sin": True}]
    def click_and_purchase(tier, point, tsize=(5, 5)):
        print(f"buy {tier} at {point}", time.time())
        nonlocal budget
        if budget < buy_cost[tier]:
            return
        # debug_points(screenshot(region=(0, 0, 1920, 1080)), [point], f"testing/shelf_click_{time.time()}_{gift}.png")
        win_click(point, tsize=tsize)
        conf_gift()
        update_shelf()
        p.NEED_INVENTORY_CHECK = True
        p.NEED_BALANCE_CHECK = True
        budget -= buy_cost[tier]
        gained[tier] += 1
        need = missing.get(tier, 0)
        missing[tier] = need - 1
        if missing[tier] <= 0:
            del missing[tier]

    def find_tier(x, y):
        for tier, points in p.SHOP_TIERS_AVAILABLE.items():
            for tier_x, tier_y in points:
                if (tier_x, tier_y) <= (x, y) <= (tier_x + 150, tier_y + 150):
                    return tier
        return None
    
    unmet_needs = []
    def want_but_cannot_buy(tier):
        print("want but cannot buy", tier)
        unmet_needs.append(buy_cost[tier])
        pass

    teams = keywordless + p.GIFTS
    for team in teams:
        if not team["sin"]:
            continue
        all_gifts_to_buy = [gift for team in teams for gift in team["buy"]]
        for gift in all_gifts_to_buy:
            try:
                x, y = gui.center(LocateRGB.try_locate(PTH[gift], image=p.SHOP_SHELF, comp=0.75, conf=0.83))
                tier = find_tier(x, y)
                if tier is None:
                    print(f"Error, could not find tier of gift {gift} despite it being at {(x, y)}")
                    continue

                if budget < buy_cost[tier]:
                    want_but_cannot_buy(tier)
                    continue

                print(f"buying named item", gift)
                click_and_purchase(tier, (x+809, y+300))
                schedule_for_uptie(gift)
            except gui.ImageNotFoundException:
                continue

    if buy_affinity_junk:
        for team in p.GIFTS:
            locs = LocateRGB.locate_all(PTH[team["checks"][0]], image=p.SHOP_SHELF, method=cv2.TM_SQDIFF_NORMED, comp=0.88, conf=0.9)
            locs = [gui.center(loc) for loc in locs]
            print("locs affinity", locs)
            debug_points(p.SHOP_SHELF, locs, f"testing/affinity_junkers_{time.time()}.png")
            for tier in [3, 2, 1, 4]:
                if budget < buy_cost[tier]:
                    continue
                points = p.SHOP_TIERS_AVAILABLE.get(tier, [])
                for x, y in points:
                    target = None
                    for x2, y2 in locs:
                        if x <= x2 <= x+100 and y <= y2 <= y + 100:
                            target = (x, y)
                            break
                    if target is not None:
                        continue
                    print(f"buying affinity junk", tier, (x, y))
                    cv2.imwrite(f"testing/affinity_junk_{time.time()}.png", screenshot((x+809, y+300, 120, 120)))
                    click_and_purchase(tier, (x+809, y+300))

    for tier in sorted(missing.keys(), reverse=True):
        count_needed = missing[tier]
        for _ in range(count_needed):
            if not p.SHOP_TIERS_AVAILABLE[tier]:
                break
            if budget < buy_cost[tier]:
                want_but_cannot_buy(tier)
                break
            print(f"buying tier {tier} and this is available: {p.SHOP_TIERS_AVAILABLE}", time.time())
            x, y = p.SHOP_TIERS_AVAILABLE[tier][-1]
            click_and_purchase(tier, (x+809, y+300))

    for tier, count in already_gained.items():
        gained[tier] += count
    return gained, missing, budget, unmet_needs

def current_budget():
    bal = balance()
    budget = bal
    def eval_cost(cost):
        nonlocal budget
        if cost < budget:
            budget -= cost
            return True
        return False

    needed_costs = all_uptie_costs()
    for cost in needed_costs:
        eval_cost(cost)

    print("budget", budget, "needed", bal - budget)
    return budget

def buy_fusion_materials():
    tiers_owned, tiers_missing = simulate_all_tiered_fusions()
    print("buy_fusion_materials: tiers_to_keep", tiers_owned, "tiers_missing", tiers_missing)
    if not tiers_missing:
        return
    tier_counts = Counter(tiers_missing)
    buy_needed(tier_counts)

def buy_needed(missing):
    gained = {1: 0, 2: 0, 3: 0, 4: 0}
    budget = current_budget()
    def should_stop():
        return budget < 80 or not missing
    if should_stop(): return gained, missing

    gained, missing, budget, unmet_needs = buy(gained, missing, budget)
    if should_stop(): return gained, missing

    print("please refresh!!!")
    did_refresh, budget = try_refresh(budget)
    if not did_refresh: return gained, missing
    if should_stop(): return gained, missing

    gained, missing, budget, unmet_needs = buy(gained, missing, budget)
    if should_stop(): return gained, missing

    did_refresh, budget = try_refresh(budget)
    if not did_refresh: return gained, missing
    if should_stop(): return gained, missing

    did_refresh, budget = try_refresh(budget)
    if not did_refresh: return gained, missing
    if should_stop(): return gained, missing

    did_refresh, budget = try_refresh(budget)
    if not did_refresh: return gained, missing
    if should_stop(): return gained, missing
    
    gained, missing, budget, unmet_needs = buy(gained, missing, budget)
    return gained, missing

def buy_extra():
    budget = current_budget()
    def should_stop():
        return budget < 80
    if should_stop(): return
    _, _, budget, _ = buy({}, {}, budget, buy_affinity_junk=True)
    if should_stop(): return

    did_refresh, budget = try_keyword_refresh(budget)
    if not did_refresh: return
    if should_skip(): return

    _, _, budget, _ = buy({}, {}, budget, buy_affinity_junk=True)
    if should_stop(): return

    did_refresh, budget = try_keyword_refresh(budget)
    if not did_refresh: return
    if should_stop(): return

    _, _, budget, _ = buy({}, {}, budget, buy_affinity_junk=True)
    return

def fuse_with_buys():
    print("fuse_with_buys")
    missing = fuse()
    if not missing:
        return True
    print("missing in fuse_with_buys", missing)
    close_panel()
    print(f"want to buy {missing} but don't have it")
    gained, missing = buy_needed(missing)
    if missing:
        return False

    fuse()
    return True

def fuse_loop():
    if has_all_fusions():
        return

    for i in range(3):
        should_continue = fuse_with_buys()
        if not should_continue:
            break
        if has_all_fusions():
            break
    close_panel()

def leave():
    p.EXPECT_ACTION = "move"
    ClickAction((1705, 967), ver="ConfirmInvert").execute(click)
    wait_while_condition(lambda: loc.button("ConfirmInvert", wait=0.3), lambda: gui.press("space"), interval=0.2, timer=5)
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
    p.REFRESH_COUNT = 0

def should_skip():
    last_level = 5 + p.EXTREME*11
    return p.SKIP and p.LVL >= last_level

from pprint import pprint
def enter_shop():
    if now_click.button("return"): time.sleep(0.3)
    if now.button("shop"): p.SUPER = "shop"
    elif not now.button("supershop"): return False
    else: p.SUPER = "supershop"
    print("shop check")
    if stuck_in_menu():
        return False

    from pprint import pprint
    print("GIFTS on shop enter:")
    pprint(p.GIFTS)
    invalidate_inventory()
    skip = should_skip()
    if not skip:
        try:
            update_shelf()
            print("sell unnecessary")
            sell_unnecessary()
            print("heal sinners")
            heal_sinners()
            print("update skill3")
            update_skill3(current_budget())
            print("buy fusion materials")
            buy_fusion_materials()
            print("fuse loop")
            fuse_loop()
            print("buy extra")
            if not p.is_saikai():
                buy_extra()
            print("apply upties")
            if balance() < sum(all_uptie_costs()):
                sell_unnecessary()
            apply_upties()
        except Exception as e:
            import traceback
            print("wtf")
            traceback.print_exc()
            raise e

    leave()
    p.EXPECT_ACTION = "move"
    return True