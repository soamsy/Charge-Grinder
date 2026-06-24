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
    if p.NUM_PURCHASED >= 4:
        return gained, missing
    keywordless = [{"buy": [name for name, state in p.KEYWORDLESS.items() if state > 1], "sin": True}]

    ts = time.time()
    def _debug_shelf(suffix, annotations):
        if p.SHOP_SHELF is None:
            return
        comp = p.WINDOW[2] / 1920
        dbg = p.SHOP_SHELF.copy()
        for (x, y, w, h), color, label in annotations:
            ax, ay = round(x * comp), round(y * comp)
            aw, ah = round(w * comp), round(h * comp)
            cv2.rectangle(dbg, (ax, ay), (ax + aw, ay + ah), color, 2)
            cv2.putText(dbg, label, (ax, max(ay - 4, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
        cv2.imwrite(f"testing/shop_buy_{suffix}_{ts}.png", dbg)

    print(f"\n=== buy() budget={budget} missing={missing} affinity_junk={buy_affinity_junk} ===")
    print(f"  SHOP_TIERS_AVAILABLE: { {t: len(pts) for t, pts in p.SHOP_TIERS_AVAILABLE.items()} }")

    def click_and_purchase(tier, point, tsize=(5, 5)):
        nonlocal budget
        print(f"  → purchasing tier {tier} cost={buy_cost[tier]} at {point}  remaining_budget={budget - buy_cost[tier]}")
        if budget < buy_cost[tier] or p.NUM_PURCHASED >= 4:
            return
        win_click(point, tsize=tsize)
        conf_gift()
        update_shelf()
        p.NEED_INVENTORY_CHECK = True
        p.NEED_BALANCE_CHECK = True
        budget -= buy_cost[tier]
        p.NUM_PURCHASED += 1
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
        print(f"  ✗ want tier {tier} (cost={buy_cost[tier]}) but budget={budget} is too low")
        unmet_needs.append(buy_cost[tier])

    # --- named gifts ---
    teams = keywordless + p.GIFTS
    all_gifts_to_buy = [gift for team in teams for gift in team["buy"] if team["sin"]]
    if p.INVENTORY["have"]:
        known_to_have = [item["name"] for loc, item in p.INVENTORY["have"].items() if "name" in item]
        all_gifts_to_buy = [gift for gift in all_gifts_to_buy if gift not in known_to_have]
    print(f"  named gifts to look for: {all_gifts_to_buy}")
    named_annotations = []
    for team in teams:
        if not team["sin"]:
            continue
        for gift in all_gifts_to_buy:
            try:
                box = LocateRGB.try_locate(PTH[gift], image=p.SHOP_SHELF, comp=0.75, conf=0.83)
                x, y = gui.center(box)
                bx, by, bw, bh = box
                tier = find_tier(x, y)
                if tier is None:
                    print(f"  ? found {gift} at ({x},{y}) but couldn't determine tier")
                    named_annotations.append(((bx, by, bw, bh), (0, 165, 255), f"{gift}:no-tier"))
                    continue
                cost = buy_cost[tier]
                if budget < cost:
                    print(f"  ✗ {gift} tier={tier} cost={cost} budget={budget} — too expensive")
                    named_annotations.append(((bx, by, bw, bh), (0, 0, 255), f"{gift} t{tier} ${cost} NO$$"))
                    want_but_cannot_buy(tier)
                    continue
                print(f"  ✓ buying {gift} tier={tier} cost={cost} at ({x},{y})")
                named_annotations.append(((bx, by, bw, bh), (0, 255, 0), f"{gift} t{tier} ${cost}"))
                _debug_shelf(f"before_{gift}", named_annotations)
                click_and_purchase(tier, (x+809, y+300))
                schedule_for_uptie(gift)
            except gui.ImageNotFoundException:
                print(f"  - {gift} not found on shelf")
    _debug_shelf("named_gifts", named_annotations)

    # --- affinity junk ---
    if buy_affinity_junk:
        print(f"  affinity junk pass")
        for team in p.GIFTS:
            check_key = team["checks"][0]
            locs = LocateRGB.locate_all(PTH[check_key], image=p.SHOP_SHELF, method=cv2.TM_SQDIFF_NORMED, comp=0.88, conf=0.9)
            locs = [gui.center(loc) for loc in locs]
            print(f"  affinity '{check_key}' matched at {locs}")
            affinity_annotations = [((x-5, y-5, 10, 10), (255, 255, 0), check_key) for x, y in locs]
            for tier in [3, 2, 1, 4]:
                if budget < buy_cost[tier]:
                    print(f"  ✗ affinity junk tier {tier}: budget={budget} < cost={buy_cost[tier]}")
                    continue
                points = p.SHOP_TIERS_AVAILABLE.get(tier, [])
                for x, y in points:
                    has_affinity = any(x <= x2 <= x+100 and y <= y2 <= y+100 for x2, y2 in locs)
                    if not has_affinity:
                        print(f"    skip tier {tier} slot ({x},{y}) — doesn't match affinity")
                        affinity_annotations.append(((x, y, 100, 100), (0, 165, 255), f"t{tier} skip"))
                        continue
                    print(f"    buying affinity junk tier {tier} at ({x},{y})")
                    affinity_annotations.append(((x, y, 100, 100), (0, 255, 0), f"t{tier} buy"))
                    _debug_shelf(f"affinity_before_t{tier}", affinity_annotations)
                    click_and_purchase(tier, (x+809, y+300))
            _debug_shelf(f"affinity_{check_key}", affinity_annotations)

    # --- fill missing tiers ---
    if missing:
        print(f"  filling missing tiers: {missing}")
    for tier in sorted(missing.keys(), reverse=True):
        count_needed = missing[tier]
        avail = p.SHOP_TIERS_AVAILABLE.get(tier, [])
        print(f"  tier {tier}: need {count_needed}, available slots={len(avail)}")
        tier_annotations = []
        for i, (sx, sy) in enumerate(avail):
            tier_annotations.append(((sx, sy, 100, 100), (200, 200, 200), f"t{tier} slot{i}"))
        for _ in range(count_needed):
            if not p.SHOP_TIERS_AVAILABLE[tier]:
                print(f"    no slots left for tier {tier}")
                break
            if budget < buy_cost[tier]:
                want_but_cannot_buy(tier)
                break
            x, y = p.SHOP_TIERS_AVAILABLE[tier][-1]
            print(f"    buying tier {tier} from slot ({x},{y})")
            tier_annotations.append(((x, y, 100, 100), (0, 255, 0), f"t{tier} BUY"))
            _debug_shelf(f"missing_t{tier}", tier_annotations)
            click_and_purchase(tier, (x+809, y+300))

    print(f"=== buy() done: gained={gained} remaining_budget={budget} unmet={unmet_needs} ===\n")
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
    tiers_owned, tiers_missing = simulate_all_tiered_fusions(include_lower_tiers=False)
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
        print("not missing anything??")
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

    for i in range(4):
        print(f"fusing for {i}-th time")
        should_continue = fuse_with_buys()
        if not should_continue:
            print("won't continue fusing")
            break
        if has_all_fusions():
            break
    close_panel()

def leave():
    p.EXPECT_ACTION = "move"
    p.EXPECT_REWARD = True
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
    p.NUM_PURCHASED = 0
    p.NUM_PURCHASED_SKILL3 = 0

def should_skip():
    if p.FINISHED_ALL_FUSIONS and p.FINISHED_ALL_UPTIES:
        return True
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

    invalidate_inventory()
    skip = should_skip()
    if skip:
        update_skill3(current_budget())
        win_moveTo(1705, 837)
    else:
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
            buy_extra()
            print("apply upties")
            if balance() < sum(all_uptie_costs()):
                sell_unnecessary()
            apply_upties()
        except Exception as e:
            import traceback
            print("wtf")
            traceback.print_exc()
            if not now.button(p.SUPER):
                gui.press("esc")
            raise e

    leave()
    return True