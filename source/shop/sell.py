from source.shop.browse_shop import *

def search_sell(sellables, reg):
    coords, _, _, _ = inventory_check(reg, 0)
    for i in len(sellables):
        tier = sellables[i]
        if coords[tier] != []:
            win_click(coords[tier][0][:2])
            time.sleep(0.2)
            wait_while_condition(lambda: not now.button("Confirm_retry.0"), lambda: gui.press("space"), timer=1.5)
            wait_while_condition(lambda: not now.button("connecting"), lambda: gui.press("space"), timer=1.5)
            connection()
            close_panel()
            del sellables[i]
            p.NEED_INVENTORY_CHECK = True
            p.NEED_BALANCE_CHECK = True
            return True
    return False

def open_sell_menu():
    if now.button(p.SUPER):
        Action(p.SUPER, click=(600, 585), ver="sell").execute(click)

def all_sellables():
    coords = p.INVENTORY["coords"]
    need_for_fusion = extra_items_needed_for_fusion()
    can_sell = {}
    for tier in [1, 2, 3, 4]:
        can_sell[tier] = min(0, len(coords[tier]) - need_for_fusion.get(tier, 0))
    return can_sell

def get_sellables():
    if p.NEED_INVENTORY_CHECK:
        open_sell_menu()
    print("getting sellable inventory")
    get_inventory(shifted=True)
    tiers = []
    for tier, count in all_sellables().items():
        for _ in range(count):
            tiers.append(tier)
    tiers.sort(reverse=True)
    print("sellables", tiers)
    return tiers

def sell(needed_cost):
    if balance() >= needed_cost:
        return True
    sellables = get_sellables()
    if not sellables:
        return False

    while balance() < needed_cost and sellables:
        if search_sell(sellables, (920, 295, 790, 345)):
            continue
        elif now_rgb.button("scroll", "scroll_full"):
            hook_x = find_hook_x(shifted=True)
            while not_at_bottom():
                print("scroll down for sell scan")
                browse_fast(hook_x)
                time.sleep(0.3)
            adj = 0
            hook_x = find_hook_x(shifted=True)
            while not_at_top():
                if search_sell(sellables, (920, 585, 790, 165)):
                    break
                print("scroll up for sell click")
                browse(hook_x, step=-165, adj=adj)
                ck = LocateRGB.locate(PTH["height_ck"], region=(920, 585, 790, 165))
                adj = 618 - gui.center(ck)[1] if ck else 0

    if p.NEED_INVENTORY_CHECK:
        get_inventory()
    return balance() >= needed_cost

def sell_unnecessary():
    open_sell_menu()

    close_panel()
    pass