from source.utils.utils import *
from source_app.params import CACHE

loc_shop = loc_rgb(conf=0.83, wait=False, method=cv2.TM_SQDIFF_NORMED)
shop_click = loc_shop(click=True, wait=5)

SCROLLABLE_X_LOCS = [1083, 1228, 1370, 1515]
SCROLLABLE_X_LOCS_SELL = [1086, 1232, 1369, 1507]

buy_cost = {
    1: 160,
    2: 215,
    3: 265,
    4: 360,
}

inventory_regions = {
    "fuse": { "region": (942, 320, 723, 436), "row_height": 145, "first_down_scroll": 145, "first_up_scroll": 145, "scrollable_x_gaps": [1083, 1228, 1370, 1515] },
    "sell": { "region": (945, 320, 720, 436), "row_height": 167, "first_down_scroll": 58, "first_up_scroll": 58, "scrollable_x_gaps": [1089, 1232, 1368, 1507] },
    "uptie": { "region": (942, 320, 723, 436), "row_height": 145, "first_down_scroll": 145, "first_up_scroll": 145, "scrollable_x_gaps": [1083, 1228, 1370, 1515] },
}

def bottom_row_region(region, row_height):
    x, y, xlen, ylen = region
    return (x, y + ylen - row_height, xlen, row_height)

def top_row_region(region, row_height):
    x, y, xlen, ylen = region
    return (x, y, xlen, row_height)

def find_hook_x(location="fuse"):
    gaps = inventory_regions[location]["scrollable_x_gaps"]
    return random.choice(gaps)  

def has_scrollbar():
    return now_rgb.button("scroll", "scroll_full")

def not_at_bottom():
    return not now_rgb.button("scroll.0") and has_scrollbar()

def not_at_top():
    return not now_rgb.button("scroll") and has_scrollbar()

def browse(hook_x, step=140, adj=0, dur=1.6):
    print(f"browse by step {step} and adj {adj}")
    win_moveTo(hook_x, 480, tsize=(1, 1))
    time.sleep(0.2)
    win_dragTo(hook_x, 480 - step + adj, duration=dur, hook=True, tsize=(1, 1))

def browse_fast(hook_x, up=False, mult=1.0):
    dy = -300 if not up else 300
    x_noise = random.randint(-2, 2)
    win_moveTo(hook_x + x_noise, 480)
    time.sleep(0.1)
    win_dragTo(hook_x, 480 + int(dy * mult), duration=0.3)
    time.sleep(0.5 * mult)

def go_to_top_fast(location="fuse"):
    if not has_scrollbar():
        return
    hook_x = find_hook_x(location)
    browse_fast(hook_x, up=True, mult=0.25)
    while not_at_top():
        browse_fast(hook_x, up=True)

def go_to_bottom_fast(location="fuse"):
    if not has_scrollbar():
        return
    hook_x = find_hook_x(location)
    browse_fast(hook_x, mult=0.25)
    while not_at_bottom():
        browse_fast(hook_x)

def go_to_bottom_while_parsing(parse_row, location="fuse"):
    hook_x = find_hook_x(location)
    region = inventory_regions[location]["region"]
    row_height = inventory_regions[location]["row_height"]
    has_first_scroll = "first_down_scroll" in inventory_regions[location]
    first_down_scroll = inventory_regions[location]["first_down_scroll"] if has_first_scroll else row_height
    starting_region = list(region)
    if location == "fuse":
        banner_box = LocateGray.locate(PTH["gifts_owned"], region=REG["fuse_shelf"])
        tries = 0
        while has_scrollbar() and banner_box and tries < 2:
            boost_scroll = banner_box[1] + 20 - starting_region[1]
            browse(1228, step=boost_scroll, adj=0)
            banner_box = LocateGray.locate(PTH["gifts_owned"], region=REG["fuse_shelf"])
            tries += 1
        if banner_box:
            start_y = region[1]
            new_start_y = banner_box[1] + 20
            starting_region[1] = new_start_y
            starting_region[3] = starting_region[3] - (new_start_y - start_y)

    bottom_row = bottom_row_region(region, row_height)

    undershoot = 0
    starting_row = 0
    rows_consumed = parse_row(starting_row, starting_region, row_height)
    if rows_consumed <= 0:
        return
    while not_at_bottom():
        scroll = first_down_scroll if starting_row == 0 else row_height
        browse(hook_x, step=scroll, adj=undershoot)
        last_item_coords = LocateRGB.locate(PTH["height_ck"], region=bottom_row)
        # if last_item_coords:
        #     updated_bottom_row_y = last_item_coords[1] - 17
        #     undershoot = updated_bottom_row_y - bottom_row[1]
        #     bottom_row = (bottom_row[0], updated_bottom_row_y, bottom_row[2], bottom_row[3])
        #     print("last_item_coords", last_item_coords, "undershoot", undershoot)
        # else:
        #     undershoot = 0
        #     bottom_row = (bottom_row[0], region[1], bottom_row[2], bottom_row[3])
        #     print("couldn't find anything with I")
        # if abs(undershoot / row_height) > 0.8:
        #     print("undershoot is weird", undershoot)
        #     undershoot = 0
            
        starting_row += rows_consumed
        rows_consumed = parse_row(starting_row, bottom_row, row_height)
        if rows_consumed <= 0:
            return
        
def go_to_top_while_parsing(parse_row, location="fuse"):
    hook_x = find_hook_x(location)
    region = inventory_regions[location]["region"]
    row_height = inventory_regions[location]["row_height"]
    has_first_scroll = "first_down_scroll" in inventory_regions[location]
    first_down_scroll = inventory_regions[location]["first_down_scroll"] if has_first_scroll else row_height

    starting_region = list(region)
    if not has_scrollbar():
        starting_region[3] = row_height * 2

    top_row = top_row_region(region, row_height)
    undershoot = 0
    starting_row = 0
    rows_consumed = parse_row(starting_row, starting_region, row_height)
    if rows_consumed <= 0:
        return
    while not_at_top():
        scroll = first_down_scroll if starting_row == 0 else row_height
        browse(hook_x, step=-scroll, adj=-undershoot)
        banner_box = LocateGray.locate(PTH["gifts_owned"], region=REG["fuse_shelf"])
        if banner_box:
            break
        first_item_coords = LocateRGB.locate(PTH["height_ck"], region=top_row)
        if first_item_coords:
            updated_bottom_row_y = first_item_coords[1] - 17
            undershoot = updated_bottom_row_y - top_row[1]
            top_row = (top_row[0], updated_bottom_row_y, top_row[2], top_row[3])
        else:
            undershoot = 0
            top_row = (top_row[0], region[1], top_row[2], top_row[3])
        if abs(undershoot / row_height) > 0.8:
            undershoot = 0
            
        starting_row += rows_consumed
        rows_consumed = parse_row(starting_row, top_row, row_height)
        if rows_consumed <= 0:
            return

def scan_entire_inventory_while_parsing(parse_area, location="fuse"):
    go_to_top_fast(location)
    go_to_bottom_while_parsing(parse_area, location)

def scan_up_entire_inventory_while_parsing(parse_area, location="fuse"):
    go_to_bottom_fast(location)
    go_to_top_while_parsing(parse_area, location)

def close_panel():
    if now.button(p.SUPER): return
    gui.press("esc")
    if not wait_while_condition(lambda: not now.button(p.SUPER), timer=1.0):
        gui.press("esc")
    x, y = win_get_position()
    if x > 750 and y < 830:
        win_moveTo(x, 841)

def get_inventory(location="fuse"):
    if not p.NEED_INVENTORY_CHECK:
        return p.INVENTORY
    
    if location == "fuse":
        init_fuse()
    else:
        open_sell_menu()
    have = {}
    def read_row(starting_row, reg, row_height):
        new_have = inventory_check(reg, starting_row, row_height)
        have.update(new_have)
        return get_usable_rows(reg, row_height)

    scan_entire_inventory_while_parsing(read_row, location)
    p.INVENTORY = { "have": have }
    p.NEED_INVENTORY_CHECK = False
    print_inventory()
    return p.INVENTORY

def get_named_locs(location="fuse"):
    have = get_inventory(location)["have"]
    return {gift["name"]: loc for loc, gift in have.items() if "name" in gift}

def update_shelf():
    wait_while_condition(lambda: not now.button("shopcorner"), timer=1.0)
    time.sleep(0.1)
    p.SHOP_SHELF = screenshot(region=REG["buy_shelf"])
    p.SHOP_SHELF = rectangle(p.SHOP_SHELF, (52, 33), (650 if p.SUPER == "supershop" else 224, 195), (0, 0, 0), -1)
    for ignore in ["purchased", "cost"]:
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(ignore)], region=REG["buy_shelf"], image=p.SHOP_SHELF, threshold=20)]
        for res in found:
            p.SHOP_SHELF = rectangle(p.SHOP_SHELF, (int(res[0] - 70 - 809), int(res[1] - 25 - 300)), (int(res[0] + 70 - 809), int(res[1] + 150 - 300)), (0, 0, 0), -1)
    cv2.imwrite(f"testing/update_shelf_{time.time()}_d.png", p.SHOP_SHELF)
    p.SHOP_TIERS_AVAILABLE = get_shop()
    print("SHOP_TIERS_AVAILABLE", p.SHOP_TIERS_AVAILABLE)
    _tier_colors = {1: (255, 80, 80), 2: (80, 255, 80), 3: (80, 80, 255), 4: (80, 255, 255)}
    dbg = p.SHOP_SHELF.copy()
    for tier, pts in p.SHOP_TIERS_AVAILABLE.items():
        color = _tier_colors.get(tier, (200, 200, 200))
        for (x, y) in pts:
            cv2.rectangle(dbg, (x - 50, y - 50), (x + 50, y + 50), color, 2)
            cv2.putText(dbg, f"t{tier}", (x - 14, y + 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    cv2.imwrite(f"testing/shelf_tiers_{time.time()}.png", dbg)

def get_shop():
    tier1 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy1"], image=p.SHOP_SHELF, threshold=4, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
    tier4 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy4"], image=p.SHOP_SHELF, threshold=10, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
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

def filter_x_distance(points, x_tol=2, y_tol=25):
    points = sorted(points, key=lambda p: p[0])
    result = []
    for p in points:
        if all(abs(p[0] - q[0]) >= x_tol or abs(p[1] - q[1]) > y_tol for q in result):
            result.append(p)
    return result

def print_inventory():
    print(f"{' inventory listing ':—^58}")    
    have = p.INVENTORY["have"]
    if not have:
        print(f"{' NO INVENTORY ':—^58}")
        return

    max_i = max(i for i, j in have.keys())
    max_j = max(j for i, j in have.keys())

    grid_strings = {
        (i, j): ", ".join(str(v) for v in entry.values()) 
        for (i, j), entry in have.items()
    }

    col_widths = {}
    for i in range(max_i + 1):
        col_widths[i] = max(
            len(grid_strings.get((i, j), "")) 
            for j in range(max_j + 1)
        )

    for j in range(max_j + 1):
        row_cells = []
        for i in range(max_i + 1):
            cell_text = grid_strings.get((i, j), "")
            # Pad the cell based on its specific column's maximum width
            row_cells.append(cell_text.ljust(col_widths[i]))
        
        print(" | ".join(row_cells))


def get_usable_rows(reg, row_height):
    len_y = reg[3]
    est_rows = len_y / row_height
    number = int(est_rows)
    fractional_part = est_rows - number

    return (number + 1) if fractional_part > 0.8 else number

def to_indices(x, y, reg, row_height):
    low_x, low_y, len_x, len_y = reg
    usable_rows = get_usable_rows(reg, row_height)

    i = int(5 * (x - low_x) / len_x)
    rows_from_start = (y - low_y) / row_height
    if rows_from_start >= usable_rows:
        return (-1, -1)
    j = int(rows_from_start)
    return (i, j)

def to_coords(i, j, reg, row_height):
    start_x, start_y, len_x, len_y = reg
    column_width = len_x / 5
    x = start_x + i * column_width + (column_width / 2)
    y = start_y + j * row_height + row_height / 2
    return x, y

def to_coords_upsidedown(i, j, reg, row_height):
    start_x, start_y, len_x, len_y = reg
    end_y = start_y + len_y
    column_width = len_x / 5
    x = start_x + i * column_width + (column_width / 2)
    y = end_y - (j * row_height + row_height / 2)
    return x, y

def inventory_check(reg, starting_row, row_height):
    have = {} # { (i, j, h): { name: "superneedle", tier: 2, aff: "BURN", keep: True }}
    comp = p.WINDOW[2] / 1920

    cv2.imwrite(f"testing/work_with_{time.time()}.png", screenshot(region=reg))
    other = list(reg)
    other[3] = int(reg[3] / row_height) * row_height
    cv2.imwrite(f"testing/slice_I_see_{time.time()}.png", screenshot(region=other))

    fuse_shelf = screenshot(region=reg)
    image = amplify(fuse_shelf)

    all_gifts = [gift for team in p.GIFTS for gift in team["all"]]
    all_gifts.extend(p.KEYWORDLESS.keys())
    all_upties = {item: tier for team in p.GIFTS for uptie in team["upties"] for item, tier in uptie.items()}
    all_upties.update(p.KEYWORDLESS)

    def update_with(i, j, new_props):
        if i < 0 or j < 0:
            return
        loc = (i, starting_row + j)
        props = have.get(loc, { "tier": 0, "keep": False, "fuse": True })
        props.update(new_props)
        have[loc] = props

    for tier in [1, 2, 3, 4]:
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(tier)], region=reg, image=fuse_shelf, threshold=20, conf=0.9, method=cv2.TM_SQDIFF_NORMED)]
        indices = [to_indices(x, y, reg, row_height) for x, y in found]
        for i, j in indices:
            update_with(i, j, { "tier": tier })

    found_aff = []
    for aff in p.GIFTS:
        found_aff = [to_indices(*gui.center(box), reg, row_height) for box in LocateRGB.locate_all(PTH[aff["checks"][4]], region=reg, image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]
        for i, j in found_aff:
            update_with(i, j, { "team": aff["checks"][0], "keep": True })

    for gift in all_gifts:
        try:
            if gift in CACHE: template = CACHE[gift]
            else: template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
            i, j = to_indices(x, y, reg, row_height)
            update_with(i, j, { "keep": True, "fuse": False, "name": gift })
            if gift in all_upties:
                uptie_region = fuse_shelf[int((y-66-reg[1])*comp):int((y-22-reg[1])*comp), int((x-14-reg[0])*comp):int((x+55-reg[0])*comp)]
                try:
                    uptie_count = LocateRGB.locate_all(PTH["+"], image=uptie_region, wait=False)
                    print(f"uptie level {len(uptie_count)} for {gift}")
                    if len(uptie_count) < 2:
                        schedule_for_uptie(gift)
                except cv2.error:
                    print("Uptie detection failed", gift)
        except gui.ImageNotFoundException:
            continue

    return have

def all_uptie_items():
    return [(item, tier) for team in p.GIFTS for upties in team["upties"] for item, tier in upties.items()]

def schedule_for_uptie(gift):
    for item, tier in all_uptie_items():
        if gift == item and not gift in p.UPTIE_SCHEDULED:
            p.UPTIE_QUEUE.append((gift, tier))
            p.UPTIE_SCHEDULED.add(gift)

def init_fuse(affinity=None):
    if not now.button(p.SUPER):
        return False
    if affinity is not None:
        p.IDX = affinity
    elif p.NEED_INVENTORY_CHECK:
            p.IDX = 0
    else:
        affinities_with_fusions = [i for i, team in enumerate(p.GIFTS) if fusions_complete_for(team)]
        if affinities_with_fusions:
            p.IDX = affinities_with_fusions[i]
        else:
            p.IDX = 0
    chain_actions(shop_click, [
        Action(p.SUPER, click=(405, 580), ver="fuse"),
        lambda: win_moveTo(469, 602, duration=0.3),
        ClickAction((469, 602), ver="keywordSel")
    ])
    confirm_affinity()
    return True

def activate_affinity(teams):
    click.button(teams[p.IDX]["checks"][3], "affinity!")
    win_click(1194, 841, tsize=(30, 20))

def confirm_affinity(teams=None):
    if teams is None: teams = p.GIFTS
    if not (0 <= p.IDX < len(teams)): p.IDX = 0

    def open_and_activate():
        ClickAction((469, 602), ver="keywordSel")
        activate_affinity(teams)

    activate_affinity(teams)
    wait_while_condition(lambda: now.button("notSelected"), open_and_activate, timer=4.0)

def fusions_complete_for(config):
    named_locs = get_named_locs()
    for fusion in config["tiered_fusions"]:
        for name, tier in fusion.items():
            if name not in named_locs:
                return False
    for fusion in config["strict_fusions"]:
        for name, materials in fusion.items():
            if name not in named_locs:
                if all([m in named_locs for m in materials.keys()]):
                    return False
    return True

def has_all_fusions():
    for config in p.GIFTS:
        if not fusions_complete_for(config):
            return False

    if p.EXTREME and "lunarmemory" not in get_named_locs():
        return False
    p.FINISHED_ALL_FUSIONS = True
    return True

def tier_fusion_count():
    count = 0
    named_locs = get_named_locs()
    for config in p.GIFTS:
        for fusion in config["tiered_fusions"]:
            for name, tier in fusion.items():
                if name not in named_locs:
                    count += 1
    return count

def has_all_tier_fusions():
    return tier_fusion_count() == 0

def balance():
    if not p.NEED_BALANCE_CHECK:
        return p.BALANCE
    close_panel()
    answer_me = True
    bal = -1
    start_time = time.time()
    # gui.screenshot(f"cost{time.time()}.png", region=(857, 175, 99, 57)) # debugging
    while bal == -1:
        if time.time() - start_time > 10: raise RuntimeError("Infinite loop exited")
        digits = []
        for i in range(9, -1, -1):
            pos = [gui.center(box) for box in LocateRGB.locate_all(PTH[f"cost{i}"], region=(837, 175, 119, 57), threshold=7, conf=0.9, method=cv2.TM_SQDIFF_NORMED)]
            for coord in pos:
                if all(abs(coord[0] - existing_coord) > 7 for _, existing_coord in digits):
                    digits.append((i, coord[0]))
        digits = sorted(digits, key=lambda x: x[1])

        bal = ""
        for i in digits: bal += str(i[0])
        bal = int(bal or -1)
        if bal != -1 and bal < 300 and answer_me: 
            time.sleep(0.2)
            answer_me = False # you game me an answer, but not your own
            bal = -1 # I will ask again
    print("money", bal)
    if p.LVL > 10:
        bal = apply_inflation(bal)
    p.BALANCE = bal
    p.NEED_BALANCE_CHECK = False
    return bal

def open_sell_menu():
    if now.button(p.SUPER):
        Action(p.SUPER, click=(600, 585), ver="sell").execute(click)
        time.sleep(0.1)

def apply_inflation(value):
    if 13 > p.LVL > 10:
        value = value // 2
    elif p.LVL >= 13:
        value = value // 3
    return value

def concat(dict1, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key].extend(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

def is_in_range(res, coord):
    return res[0] - 103 < coord[0] < res[0] + 19 and res[1] - 105 < coord[1] < res[1] + 17

from datetime import datetime
def debug_points(image, points, filename):
    comp = p.WINDOW[2] / 1920
    print(points)
    for x, y in points:
        cv2.circle(image, (int(x*comp), int(y*comp)), radius=5, color=(0, 255, 0), thickness=1)
    cv2.imwrite(filename, image)
