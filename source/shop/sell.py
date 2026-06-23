from collections import Counter

from source.shop.browse_shop import *
from source.utils.utils import *
from source.shop.fuse import simulate_all_tiered_fusions

def sell_unnecessary():
    open_sell_menu()
    get_inventory(location="sell")
    if not has_all_tier_fusions():
        sell_junk()
    # sacrifice_fusion_material_for_uptie()
    close_panel()

# Function for later, it's not necessary right now
# def sacrifice_fusion_material_for_uptie():
#     pass

def sell_junk():
    bottom_up_coord_list = allowed_coords()
    if bottom_up_coord_list:
        sell([bottom_up_coord_list[0]])
        get_inventory(location="sell")
        # bottom_up_coord_list = allowed_coords()

def sell(bottom_up_coord_list):
    def sell_from_region(starting_row, reg, row_height):
        return search_sell(bottom_up_coord_list, starting_row, reg, row_height)

    scan_up_entire_inventory_while_parsing(sell_from_region, location="sell")
    p.NEED_INVENTORY_CHECK = True
    p.NEED_BALANCE_CHECK = True

def search_sell(bottom_up_coord_list, starting_row, reg, row_height):
    all_locs = list(get_inventory(location="sell")["have"].keys())
    dangling_items = len(all_locs) % 5
    usable_rows = get_usable_rows(reg, row_height)
    j_low = 0
    j_high = max([j for i, j in all_locs])
    j_high = max(1, j_high)
    j_high -= starting_row
    j_low = j_high - usable_rows + 1
    print("j_low", j_low, "j_high", j_high)
    print(bottom_up_coord_list)

    for (i, j), gift in bottom_up_coord_list:
        if j_low <= j <= j_high:
            x, y = to_coords_upsidedown(i, j_high - j, reg, row_height)
            debug_points(screenshot(reg), [(x - reg[0], y - reg[1])], f"testing/search_sell_{time.time()}_{gift["tier"] if "tier" in gift else ""}.png")
            win_click(x, y)
            wait_while_condition(lambda: not now.button("Confirm_retry.0"), lambda: gui.press("space"), timer=1.5)
            wait_while_condition(lambda: not now.button("connecting"), lambda: gui.press("space"), timer=1.5)
            connection()
            print(f"sold {gift}")
            dangling_items -= 1
            if dangling_items <= 0:
                p.NEED_INVENTORY_CHECK = True
                p.NEED_BALANCE_CHECK = True
                return -1
            time.sleep(0.2)
    return usable_rows

def allowed_coords():
    tiers_to_keep, tiers_missing = simulate_all_tiered_fusions()
    print("sell: tiers_to_keep", tiers_to_keep, "tiers_missing", tiers_missing)
    tiers_to_keep.append(4)
    tier_counts = Counter(tiers_to_keep)
    for tier in [1, 2, 3, 4]:
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    print("selling with tier_counts", tier_counts)
    have = get_inventory(location="sell")["have"]
    coords = [(loc, item) for loc, item in have.items() if not item["keep"]]
    print("coords that can sell", coords)
    coords.sort(reverse=True)
    allowed_coords = []
    for loc, item in coords:
        tier = item.get("tier")
        if tier and tier_counts.get(tier, 0) > 0:
            tier_counts[tier] -= 1
            continue
        allowed_coords.append((loc, item))

    print("coords that I WILL sell", allowed_coords)
    return allowed_coords