from source.utils.utils import *

loc_shop = loc_rgb(conf=0.83, wait=False, method=cv2.TM_SQDIFF_NORMED)
shop_click = loc_shop(click=True, wait=5)

SCROLLABLE_X_LOCS = [1083, 1228, 1370, 1515]

def find_hook_x(shifted=False):
    shift = -8 if shifted else 0
    return random.choice([x+shift for x in SCROLLABLE_X_LOCS])

def not_at_bottom():
    return not now_rgb.button("scroll.0") and now_rgb.button("scroll", "scroll_full")

def not_at_top():
    return not now_rgb.button("scroll") and now_rgb.button("scroll", "scroll_full")

def browse(hook_x, step=140, adj=0, dur=0.5):
    win_moveTo(hook_x, 480, tsize=(1, 1))
    win_dragTo(hook_x, 480 - step + adj, duration=dur, hook=True, tsize=(1, 1))

def browse_fast(hook_x, up=False):
    dy = -300 if not up else 300
    x_noise = random.randint(-10, 10)
    win_moveTo(hook_x + x_noise, 480)
    win_dragTo(hook_x, 480 + dy, duration=0.25)

def close_panel():
    if now.button(p.SUPER): return
    gui.press("esc")
    if not wait_while_condition(lambda: not now.button(p.SUPER), timer=1.5):
        gui.press("esc")
    time.sleep(0.1)
    x, y = win_get_position()
    if x > 750 and y < 830:
        win_moveTo(x, 841)

def get_inventory(shifted=False):
    if not p.NEED_INVENTORY_CHECK:
        return p.INVENTORY
    hook_x = find_hook_x(shifted)
    while not_at_bottom():
        print("scroll down for inventory alignment")
        browse_fast(hook_x)
        time.sleep(0.5)

    def get_box_region(box):
        _, y = gui.center(box)
        y = clip(295, y, 777)
        return (920, y, 790, 777 - y)
    
    def inventory_check_ignore_banner():
        box = LocateGray.locate(PTH["gifts_owned"], region=REG["fuse_shelf"])
        region = REG["fuse_shelf"]
        if box:
            region = get_box_region(box)
        return box, *inventory_check(region, 0)

    banner_box, coords, coords_agg, have = inventory_check_ignore_banner()
    if now_rgb.button("scroll.0") and not banner_box:
        h = 1
        adj = 0
        hook_x = find_hook_x(shifted)
        while not_at_top():
            browse(hook_x, step=-140, adj=adj)

            if LocateGray.check(PTH["gifts_owned"], region=REG["fuse_shelf"], wait=False):
                break
            
            new_coords, new_coords_agg, new_have = inventory_check(REG["fuse_shelf_peak"], h)
            coords = concat(coords, new_coords)
            coords_agg = concat(coords_agg, new_coords_agg)
            have.update(new_have)

            ck = LocateRGB.locate(PTH["height_ck"], region=(920, 585, 790, 165), method=1)
            adj = 625 - gui.center(ck)[1] if ck else 0
            h += 1

    p.INVENTORY = { 
        "coords": coords,
        "coords_agg": coords_agg, 
        "have": have,
    }
    p.NEED_INVENTORY_CHECK = False
    return p.INVENTORY

def inventory_check(reg, h):
    coords_agg = {1: [], 2: [], 3: [], 4: []}
    coords     = {1: [], 2: [], 3: [], 4: []}
    have = {}
    comp = p.WINDOW[2] / 1920

    fuse_shelf = screenshot(region=reg)
    image = amplify(fuse_shelf)

    uptie_items = all_uptie_items()
    for i, team in enumerate(p.GIFTS):
        uptie_ego = uptie_items[i]
        for gift in team["all"]:
            try:
                if gift in CACHE: template = CACHE[gift]
                else: template = amplify(cv2.imread(PTH[gift]))
                x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
                have[gift] = (x, y, h)

                if gift in uptie_ego.keys():
                    uptie_region = fuse_shelf[int((y-66-reg[1])*comp):int((y-22-reg[1])*comp), int((x-14-reg[0])*comp):int((x+55-reg[0])*comp)]
                    try:
                        if not LocateRGB.check(PTH["+"], image=uptie_region, wait=False):
                            schedule_for_uptie(gift)
                    except cv2.error:
                        print("Uptie detection failed", gift)
                
                fuse_shelf = rectangle(fuse_shelf, (int(x - 62 - reg[0]), int(y - 72 - reg[1])), (int(x + 60 - reg[0]), int(y + 60 - reg[1])), (0, 0, 0), -1)
                image = rectangle(image, (int(x - 62 - reg[0]), int(y - 72 - reg[1])), (int(x + 60 - reg[0]), int(y + 60 - reg[1])), (0, 0, 0), -1)
            except gui.ImageNotFoundException:
                continue
    
    for gift in list(p.KEYWORDLESS.keys()):
        try:
            if gift in CACHE: template = CACHE[gift]
            else: template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.84))
            have[gift] = (x, y, h)

            if p.KEYWORDLESS[gift] > 2:
                uptie_region = fuse_shelf[int((y-66-reg[1])*comp):int((y-22-reg[1])*comp), int((x-14-reg[0])*comp):int((x+55-reg[0])*comp)]
                try:
                    if not LocateRGB.check(PTH["+"], image=uptie_region, wait=False):
                        schedule_for_uptie(gift)
                except cv2.error:
                    print("Uptie detection failed", gift)

            fuse_shelf = rectangle(fuse_shelf, (int(x - 62 - reg[0]), int(y - 72 - reg[1])), (int(x + 60 - reg[0]), int(y + 60 - reg[1])), (0, 0, 0), -1)
            image = rectangle(image, (int(x - 62 - reg[0]), int(y - 72 - reg[1])), (int(x + 60 - reg[0]), int(y + 60 - reg[1])), (0, 0, 0), -1)
        except gui.ImageNotFoundException:
            print("didn't find keywordless gift", gift)
            continue

    found_aff = []
    for aff in p.GIFTS:
        found_aff += [gui.center(box) for box in LocateRGB.locate_all(PTH[aff["checks"][4]], region=reg, image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]

    for i in range(4, 0, -1):
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(i)], region=reg, image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]

        for res in found:
            fuse_shelf = rectangle(fuse_shelf, (int(res[0] - 20 - reg[0]), int(res[1] - 22 - reg[1])), (int(res[0] + 102 - reg[0]), int(res[1] + 100 - reg[1])), (0, 0, 0), -1)
            x, y = res
            coords_agg[i].append((x, y, h))
            coords[i].append((x, y, h))

    for res in found_aff:
        for i in range(1, 5):
            match = next((coord for coord in coords[i] if is_in_range(res, coord)), None)
            if match:
                coords[i].remove(match)
                break

    return coords, coords_agg, have

def confirm_affinity(teams=None):
    if teams is None: teams = p.GIFTS
    if not (0 <= p.IDX < len(teams)): p.IDX = 0
    is_not_seleted = True
    while is_not_seleted:
        click_rgb.button(teams[p.IDX]["checks"][3], "affinity!")
        win_click(1194, 841, tsize=(100, 30))
        time.sleep(0.1)
        if not now.button("notSelected"):
            is_not_seleted = False
        else:
            ClickAction((469, 602), ver="keywordSel").execute(shop_click)
            # win_moveTo(605, 612)

def balance():
    if not p.NEED_BALANCE_CHECK:
        return p.BALANCE
    close_panel()
    answer_me = True
    bal = -1
    start_time = time.time()
    # gui.screenshot(f"cost{time.time()}.png", region=(857, 175, 99, 57)) # debugging
    while bal == -1:
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
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

def extra_items_needed_for_fusion():
    return { 1: 0, 2: 0, 3: 0, 4: 0 } # TODO: actually check inventory

def concat(dict1, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key].extend(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

def is_in_range(res, coord):
    return res[0] - 103 < coord[0] < res[0] + 19 and res[1] - 105 < coord[1] < res[1] + 17

import datetime
def debug_points(image, points, filename):
    comp = p.WINDOW[2] / 1920
    for x, y in points:
        cv2.circle(image, (int(x*comp), int(y*comp)), radius=5, color=(0, 255, 0), thickness=1)
    cv2.imwrite(filename, image)