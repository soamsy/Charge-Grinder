from source.utils.utils import *
from source.event import event
import source.utils.params as p
from itertools import product


exit_if = ["loading", "Move", "EGObin", "encounterreward", "victory", "defeat", "PackChoice", "Confirm"]

# HARD MD
comps = [0.71, 0.77, 0.89, 1]
low = {"struggle": (0, 199, 252), "hopeless": (2, 245, 214)}
ego = ["zayin", "teth", "he", "waw"]
best1 = ["FluidSac"]
best2 = [
    "DimensionShredder", "Sunshower", "MagicBullet", "Holiday", "EffervescentCorrosion", "EbonyStem", "Binds", "YaSunyataTadRupam", 
    "GardenofThorns", "AEDD", "Lantern", "CavernousWailing", "Capote", "Pursuance", "Regret", "RimeShank", "WishingCairn", 
    "ElectricScreaming", "4thMatchFlame", "RedEyesOpen", "ArdorBlossomStar", "BlindObsession", "FluidSac", "HexNail"
]

def get_saikai_ryoshu():
    image = screenshot(region=(0, 900, 1920, 180))
    ryoshu = LocateRGB.locate(PTH["ryoshu"], image)
    if ryoshu is None: return
    x, _ = gui.center(ryoshu)
    return x

def get_lowskill():
    image = screenshot(region=(0, 820, 1920, 100))
    boxes = []
    for name in low.keys():
        target_color = low[name]
        mask = create_mask(image, target_color, 20)
        for comp in comps:
            boxes += LocateGray.locate_all(PTH[name], image=mask, region=(0, 820, 1920, 100), threshold=20, comp=comp, conf=0.8)
    coords_x = []
    for box in boxes:
        x, y = gui.center(box)
        if y > 870: # lower skill
            x += int(0.061*x - 93)
        else: # upper skill
            x += int(0.206*x - 224)
        if any(abs(x - px) <= 20 for px in coords_x): continue
        coords_x.append(int(x))
    return sorted(coords_x)

def ego_click(best_ego):
    gui.mouseDown()
    time.sleep(1.5)
    gui.mouseUp()
    image_all = screenshot(region=(0, 200, 1920, 50))
    _, image_best = cv2.threshold(cv2.cvtColor(screenshot(region=(0, 495, 1920, 50)), cv2.COLOR_BGR2GRAY), 100, 255, cv2.THRESH_TOZERO)
    for i, h_comp in product(best_ego, [0.95, 0.98, 1, 1.02, 1.05]):
        box = LocateGray.locate(PTH[i], image=image_best, region=(0, 495, 1920, 50), method=1, h_comp=h_comp, conf=0.6)
        if box:
            res = gui.center(box)
            win_click(res)
            win_click(res)
            break
    else:
        for i in ego:
            res = LocateRGB.locate(PTH[i], image=image_all, region=(0, 200, 1920, 50), method=1, conf=0.8)
            print(i, res)
            if res:
                c0, c1 = gui.center(res)
                win_click(c0, int(c1 + 200))
                win_click(c0, int(c1 + 200))
                break
        else:
            win_click(1850, 1000)
    if not loc.button("winrate", wait=2):
        win_click(1888, 901)
    time.sleep(0.2)


def check_selection(button="winrate_on", st_clicks=3):
    gui.press("p", st_clicks, 0.5)
    time.sleep(0.5)
    wait_while_condition(lambda: not loc.button(button, "winrate", wait=0.5, method=cv2.TM_SQDIFF_NORMED), lambda: gui.press("p"))

def select_ego():
    loc.button("winrate_on", "winrate", wait=1, method=cv2.TM_SQDIFF_NORMED)
    coords_x = get_lowskill()
    if not coords_x: return

    # try using zayin
    for x in coords_x: 
        win_moveTo(x, 990)
        ego_click(best1)
    check_selection()
    coords_x = get_lowskill()
    if len(coords_x) < 3: 
        # zayin kinda worked
        for x in coords_x: win_click(x, 990)
        return
    
    for x in coords_x: # zayin didn't work, so let's use something more deadly
        win_click(x, 990, clicks=2)
        time.sleep(0.1)
        ego_click(best2)
    check_selection()
    coords_x = get_lowskill()
    if len(coords_x) < 3: 
        # we winrate with this
        for x in coords_x: win_click(x, 990)
        return
    
    # even that didn't work, so let's go for damage
    check_selection("damage_on", st_clicks=1)
    coords_x = get_lowskill()
    for x in coords_x: win_click(x, 990)


def is_ego():
    background = screenshot(region=REG["ego_usage"])
    hsv = cv2.cvtColor(background, cv2.COLOR_BGR2HSV)
    for hue, _, hue_threshold, _, _ in sins.values():
        lo_h = hue - hue_threshold
        hi_h = hue + hue_threshold
        if lo_h < 0:
            mask = cv2.bitwise_or(
                cv2.inRange(hsv, np.array([lo_h + 179, 50, 50]), np.array([179, 255, 255])),
                cv2.inRange(hsv, np.array([0,          50, 50]), np.array([hi_h, 255, 255])),
            )
        else:
            mask = cv2.inRange(hsv, np.array([lo_h, 50, 50]), np.array([hi_h, 255, 255]))
        if now.button("ego_usage", image=mask, conf=0.8):
            return background
    return None

def _blended_sat_val_bounds(hue, opacity, bg_samples):
    """Minimum HSV sat/val for a pure hue at given opacity composited over the given BGR background samples."""
    fg_bgr = cv2.cvtColor(np.uint8([[[hue % 180, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0].astype(float)
    min_sat, min_val = 255, 255
    for bg in bg_samples:
        blended = np.clip(opacity * fg_bgr + (1 - opacity) * bg.astype(float), 0, 255).astype(np.uint8)
        hsv_px = cv2.cvtColor(np.uint8([[blended]]), cv2.COLOR_BGR2HSV)[0][0]
        min_sat = min(min_sat, int(hsv_px[1]))
        min_val = min(min_val, int(hsv_px[2]))
    return max(0, min_sat - 10), max(0, min_val - 10)

def get_centroids_by_hue(image, hue, hue_threshold=3, opacity=0.8,
                         lower_sat=None, upper_sat=255, lower_val=None, upper_val=255,
                         area_min=26, area_max=4000):
    comp = p.WINDOW[2] / 1920
    area_min *= comp
    area_max *= comp

    if lower_sat is None or lower_val is None:
        h, w = image.shape[:2]
        cs = max(1, min(8, h // 4, w // 4))
        corners = [
            image[0:cs,   0:cs  ],
            image[0:cs,   w-cs:w],
            image[h-cs:h, 0:cs  ],
            image[h-cs:h, w-cs:w],
        ]
        bg_samples = [np.median(c.reshape(-1, 3), axis=0) for c in corners]
        # Always include white — it gives the lowest possible blended saturation
        # for any hue and sets the permissive floor for the threshold.
        bg_samples.append(np.array([255.0, 255.0, 255.0]))
        calc_sat, calc_val = _blended_sat_val_bounds(hue, opacity, bg_samples)
        if lower_sat is None:
            lower_sat = calc_sat
        if lower_val is None:
            lower_val = calc_val

    lower_hue = hue - hue_threshold
    upper_hue = hue + hue_threshold
    ranges = []
    if lower_hue < 0:
        ranges.append(([lower_hue + 179, lower_sat, lower_val], [179, upper_sat, upper_val]))
        ranges.append(([0, lower_sat, lower_val], [upper_hue, upper_sat, upper_val]))
    else:
        ranges.append(([lower_hue, lower_sat, lower_val], [upper_hue, upper_sat, upper_val]))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    print(f"[hue_debug] hue={hue} thresh={hue_threshold} opacity={opacity} lower_sat={lower_sat} lower_val={lower_val}")
    for lo, hi in ranges:
        print(f"  range: H[{lo[0]}–{hi[0]}] S[{lo[1]}–{hi[1]}] V[{lo[2]}–{hi[2]}]")

    masks = [cv2.inRange(hsv, np.array(lo), np.array(hi)) for lo, hi in ranges]
    mask = masks[0]
    if len(masks) > 1:
        mask = cv2.bitwise_or(masks[0], masks[1])
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    ts = time.time()
    cv2.imwrite(f"testing/hue_debug_input_{hue}_{ts}.png", image)
    cv2.imwrite(f"testing/hue_debug_mask_{hue}_{ts}.png", mask)
    hsv_vis = hsv.copy()
    hsv_vis[:, :, 1] = np.maximum(hsv_vis[:, :, 1], 255)
    hsv_vis[:, :, 2] = np.maximum(hsv_vis[:, :, 2], 255)
    cv2.imwrite(f"testing/hue_debug_hsvmap_{hue}_{ts}.png", cv2.cvtColor(hsv_vis, cv2.COLOR_HSV2BGR))
    print(f"  mask nonzero pixels: {cv2.countNonZero(mask)}")

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask, connectivity=8, ltype=cv2.CV_32S
    )

    points = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        x, y = centroids[i]
        if area > area_min and area <= area_max:
            status = "KEPT"
        elif area <= area_min:
            status = f"dropped (min={area_min:.1f})"
        else:
            status = f"dropped (max={area_max:.1f})"
        print(f"  component {i}: area={area} centroid=({x:.1f},{y:.1f}) {status}")
        if area > area_min and area <= area_max:
            points.append((int(x/comp), int(y/comp)))

    print(f"  → {len(points)} centroids returned")
    return points

def is_solo(gear_start, gear_end):
    return count_sinners(gear_start, gear_end) == 1
    
def count_sinners(gear_start, gear_end):
    start_x = round(gear_start[0] + 75)
    end_x = round(gear_end[0] - 57)
    start_y = 1026
    end_y = 1050
    width = end_x - start_x
    height = end_y - start_y
    num_actions = round(width / 123)
    hp_numbers_image = screenshot(region=(start_x, start_y, width, height))
    centroids = get_centroids_by_hue(hp_numbers_image, 8, opacity=1.0, lower_sat=200, lower_val=180)
    # debug_points([(x+start_x, y+start_y) for x, y in centroids], "debug_count_sinners.png")
    bins = []
    bin_size = width / num_actions
    bins = [(round(i*bin_size), round((i+1)*bin_size)) for i in range(num_actions)]
    is_bin_filled = [0] * num_actions
    for x, _ in centroids:
        for i, (left, right) in enumerate(bins):
            if left <= x < right:
                is_bin_filled[i] = 1
                break

    count = sum(is_bin_filled)
    return count

sins = {
    "wrath"   : (0, 0.52, 4, 12, 250),
    "gloom"   : (96, 0.5, 5, 12, 250),
    "sloth"   : (23, 0.5, 5, 12, 250),
    "lust"    : (13, 0.4, 5, 12, 250),
    "pride"   : (110, 0.5, 5, 13, 250),
    "gluttony": (41, 0.5, 5, 12, 250),
    "envy"    : (140, 0.40, 6, 12, 250),
}

def find_skill3(background, sin="envy"):
    hue, opacity, hue_threshold, min_pixels, max_pixels = sins[sin]
    points = get_centroids_by_hue(background, hue, hue_threshold=hue_threshold, opacity=opacity, area_min=min_pixels, area_max=max_pixels)

    # merge nearby centroids that belong to the same skill icon
    centers = [np.array(pt, dtype=float) for pt in points]
    merged = []
    while centers:
        current = centers.pop()
        group = [c for c in centers if np.linalg.norm(current - c) <= 50]
        centers = [c for c in centers if np.linalg.norm(current - c) > 50]
        merged.append(np.mean([current] + group, axis=0))

    filtered = [int(c[0]) for c in merged]
    if filtered:
        print(sin, "found at", filtered)
    return filtered

def select_team():
    time.sleep(0.3)

    affinity = p.TEAM[0].lower()
    idx = p.NAME_ORDER
    if not p.DUPLICATES and LocateGray.check(PTH[f"{affinity}_current"], region=REG["current_team"], conf=0.92, method=cv2.TM_SQDIFF_NORMED, wait=False):
        return
    
    if now_rgb.button("arrow", conf=0.7):
        win_moveTo(191, 475)
        win_dragTo(289, 984, duration=1.0)
        time.sleep(1)

    for i in range(4):
        coords = [gui.center(box) for box in LocateGray.locate_all(PTH[f"{affinity}_team"], region=REG["teams"], threshold=15, conf=0.85)]
        sorted(coords, key=lambda coord: coord[1])

        if len(coords) > idx:
            if i != 0 and i != 3: gui.mouseUp()
            win_click(coords[idx])
            break
        elif i != 3:
            idx -= len(coords)
            if i != 0: gui.mouseUp()
            win_moveTo(196, 670)
            gui.mouseDown()
            win_moveTo(193, 400)
            if i == 2: gui.mouseUp()
            time.sleep(0.3)
    else:
        logging.info("Team selecton failed!")
        return
    logging.info(f"Selected {p.TEAM[0]}")
    time.sleep(1)

def select(sinners):
    selected = [gui.center(box) for box in LocateGray.locate_all(PTH["selected"])]
    backup = [gui.center(box) for box in LocateGray.locate_all(PTH["backup"])]
    correct = 0
    correct_back = 0
    to_click = []
    regions = [SINNERS[name] for name in sinners]
    death_offset = 0
    for i, region in enumerate(regions):
        if any(
            region[0] < point[0] < region[0]+region[2] and  
            region[1] < point[1] < region[1]+region[3] 
            for point in selected) and i < 7 + death_offset:
            correct += 1
            continue
        if i > 5 + death_offset and any(
            region[0] < point[0] < region[0]+region[2] and  
            region[1] < point[1] < region[1]+region[3] 
            for point in backup):
            correct_back += 1
            continue
        if is_grayscale(screenshot(region=region)): # dead
            death_offset += 1
            continue
        to_click.append(gui.center(region))
    if len(selected) > correct or len(backup) > correct_back:
        ClickAction((1713, 712), ver="Confirm_alt").execute(click)
        time.sleep(0.21)
        click.button("Confirm_alt")
        time.sleep(0.5)
        for region in regions:
            win_click(gui.center(region))
            time.sleep(0.1)
    elif to_click:
        for i in to_click:
            win_click(i)
            time.sleep(0.1)

    input_with_fallback(
        "space", 
        lambda: win_click(1728, 884, tsize=(200,  50)), 
        lambda: loc.button("loading", wait=3)
    )
    loading_halt()
    return death_offset

def chain(gear_start, gear_end, check_lowskill=False):
    # Finding skill3 positions
    x, y = gear_start
    skill_start_x = x + 73
    skill_end_x = gear_end[0] - 58
    skill_middle_y = y + 89
    length = skill_end_x - skill_start_x
    # overshoots for low skill count, but undershoots for high skill count due to how the skill tray is resized.
    # this is fine regardless, since rounding will get us the correct bin length later
    est_bin_length = 121

    skill_num = int(round(length/est_bin_length))
    bin_length = length / skill_num
    half_bin = bin_length / 2
    
    top_padding = 28 + skill_num * 4
    top_start_x = skill_start_x + top_padding
    top_end_x = skill_end_x - top_padding
    top_length = top_end_x - top_start_x
    skill3_tip_background = screenshot(region=(top_start_x, 775, top_length, 10))
    skill3 = []
    for sin in sins.keys():
        skill3 += find_skill3(skill3_tip_background, sin=sin)
    moves = [False]*skill_num
    for coord in skill3:
        moves[int(skill_num * coord / top_length)] = True

    def sin_search(hue, y_loc, padding=0, opacity=1.0, area_min=30, hue_threshold=3, area_max=1000):
        comp = p.WINDOW[2] / 1920
        padding *= comp
        left = skill_start_x + padding
        width = length - padding * 2
        row = screenshot(region=(left, y_loc, width, 20))
        points = get_centroids_by_hue(row, hue, opacity=opacity, area_min=area_min, area_max=area_max)
        # if filename:
            # debug_points([(x+left, y+y_loc) for x, y in points], filename)
        indexes = {int(skill_num * x / width) for x, _ in points}
        return indexes

    ryoshu_x = -1
    if p.is_saikai():
        if is_solo(gear_start, gear_end):
            wrath_top = sin_search(-3, 795, padding=30, opacity=0.27, area_min=35)
            wrath_bottom = sin_search(0, 885, padding=10, opacity=0.18, area_min=25, hue_threshold=1)
            pride_top = sin_search(109, 795, padding=30, opacity=0.4, area_min=35)
            pride_bottom = sin_search(109, 885, padding=10, opacity=0.4, area_min=35)
            wraths = set()
            prides = set()
            for i in range(skill_num):
                if i in (wrath_top | wrath_bottom):
                    wraths.add(i)
                elif i in (pride_top | pride_bottom):
                    prides.add(i)
            lusts = [i for i in range(skill_num) if i not in wraths and i not in prides]
            dodges = set()
            dodges_wanted = skill_num - len(wraths)
            if len(wraths) == 0:
                dodges_wanted = 0
            elif len(wraths) == 1 and skill_num >= 4:
                dodges_wanted -= 1

            possible_dodges = list(sorted(lusts)) + list(sorted(list(prides)))
            for possible in possible_dodges:
                if len(dodges) < dodges_wanted:
                    dodges.add(possible)
                else:
                    break
            print("wraths_top", wrath_top)
            print("wraths_bottom", wrath_bottom)
            print("prides", prides)
            print("dodges", dodges)
            for i in range(skill_num):
                if i in wraths:
                    moves[i] = i in wrath_bottom and i not in wrath_top
                elif i in dodges:
                    moves[i] = True
                    win_click(skill_start_x + bin_length * i + half_bin, 990)
                else:
                    moves[i] = i in pride_bottom and i not in pride_top
        else:
            ryoshu_x = get_saikai_ryoshu()
            if ryoshu_x and 0 <= ryoshu_x:
                win_click(ryoshu_x, 990)
                move_index = int(skill_num * (ryoshu_x-skill_start_x) / length)
                moves[move_index] = True
    print("moves", ["Down" if m else "Up" for m in moves])

    skill_targets = []
    curr_x = skill_start_x
    curr_y = skill_middle_y
    for i in range(skill_num):
        next_y = curr_y + (88 if moves[i] else -88)
        last_y = (curr_y + (88 if moves[i-1] else 88)) if i > 0 else next_y
        if last_y != next_y:
            sub_target_x = curr_x + half_bin * 0.5
            perspective_offset = -(sub_target_x - 960) / 30
            diff_y = next_y - last_y
            sub_target_y = last_y + diff_y * 0.66
            skill_targets.append((int(sub_target_x), int(sub_target_y), 4))

        target_x = curr_x + half_bin
        perspective_offset = -(target_x - 960) / 30
        skill_targets.append((int(target_x + perspective_offset), next_y, 4))
        curr_x += bin_length
    final_x = gear_end[0] + 44
    final_y = skill_middle_y + 4
    if skill_targets[-1][1] > skill_middle_y:
        final_y = skill_middle_y - 4

    win_moveTo(gear_start)
    gui.mouseDown()

    # debug_points([(x, y) for x, y, _ in skill_targets] + [(final_x, final_y)], "debug_skill_chain.png")
    for x, y, size in skill_targets:
        dur = 0.2
        curve = 0.1
        win_moveTo(x, y, duration=dur, tsize=(size, size), inertia=True, curve=curve)

    if check_lowskill:
        gui.mouseUp()
        time.sleep(0.3)
        lowskill = get_lowskill()
        if len(lowskill) >= 2:
            raise ValueError("Battle is too hard for chaining")
        else:
            if moves[i]:
                win_moveTo(int(curr_x - half_bin), curr_y - 80, duration=0.2, tsize=(20, 20), inertia=True)
                gui.mouseDown()
                win_moveTo(int(curr_x - half_bin), curr_y + 80, duration=0.2, tsize=(20, 20), inertia=True)
            else:
                win_moveTo(int(curr_x - half_bin), curr_y - 80, duration=0.2, tsize=(20, 20), inertia=True)
                gui.mouseDown()

    win_moveTo(final_x, final_y, duration=0.43, tsize=(2, 2), inertia=True)
    gui.mouseUp()

def debug_points(points, filename):
    image = screenshot(region=(0, 0, 1920, 1080))
    comp = p.WINDOW[2] / 1920
    for x, y in points:
        cv2.circle(image, (int(x*comp), int(y*comp)), radius=10, color=(0, 255, 0), thickness=2)
    cv2.imwrite(filename, image)

def fight(lux=False):
    is_tobattle = now.button("TOBATTLE")
    is_battle   = now_rgb.button("winrate") or now.button("pause")
    if not is_tobattle and not is_battle: return False
    print("battle check")
    if is_tobattle:
        if lux: 
            win_moveTo(880, 880)
            select_team()
        else:
            x, y = win_get_position()
            if x < 1560 and y < 820:
                win_moveTo(random.randint(1560, 1730), random.randint(250, 620))
                time.sleep(0.1)
        select(p.SELECTED)

        # for lux with 6 sinners max
        if lux and now.button("TOBATTLE"): 
            select(p.SELECTED[:6])

    print("Entered Battle")
    win_moveTo(1700, 750)
    p.time_elapsed()
    last_error = 0
    attempts = 0
    should_winrate = (lux and not p.is_saikai()) or p.WINRATE
    check_lowskill = p.is_on_hard()
    first_turn = True
    while True:
        ck = False
        gear_start = None
        if loc.button("winrate", wait=0.8):
            time.sleep(0.2)
            ck = True
            is_focused = True
            try:
                gear_start = gui.center(LocateEdges.try_locate(PTH["gear"], region=(0, 761, 900, 179), conf=0.7))
                gear_end = gui.center(LocateEdges.try_locate(PTH["gear2"], region=(350, 730, 1570, 232), conf=0.7))
                is_focused = False
                if should_winrate:
                    raise ValueError("Battle isn't focused but we want to winrate anyway")
                if first_turn == True:
                    time.sleep(0.3) # ego gift text pops up at battle start, making it hard to detect slotted skills
                    first_turn = False
                chain(gear_start, gear_end, check_lowskill)
                p.EXPECT_CHAIN = True
                check_lowskill = False

                # success check
                time.sleep(0.6)
                if now.button("winrate"):
                    gui.press("p", 1, 0.1)
                    time.sleep(0.3)
                    gui.press("enter", 1, 0.1)
                    time.sleep(0.6)
            except (gui.ImageNotFoundException, ValueError) as error:
                if isinstance(error, ValueError):
                    print(error)
                if check_lowskill:
                    should_winrate = True
                gui.press("p", 1, 0.1)
                time.sleep(0.2)
                
                if is_focused and not loc.button("winrate_on", "winrate", wait=1, method=cv2.TM_SQDIFF_NORMED):
                    win_click(1400, 930)

                if not lux and p.is_on_hard():
                    select_ego()
                if lux and p.is_saikai() and not is_solo((100, 990), (1820, 990)):
                    ryoshu_x = get_saikai_ryoshu()
                    if ryoshu_x and 0 <= ryoshu_x:
                        win_click(ryoshu_x, 990)
                        win_moveTo(200, 990)

                gui.press("enter", 1, 0.1)
                time.sleep(0.5)

        if p.EXPECT_CHAIN:
            if gear_start:
                gx, gy = gear_start
                win_moveTo(max(10, gx-150), gy+120)
            else:
                win_moveTo(300, 960)
            p.EXPECT_CHAIN = False

        if now_rgb.button("event"):
            ck = True
            event()

        if now.button("ego_warning"): # skip corrosion
            ck = True
            gui.mouseDown()
            wait_while_condition(lambda: loc.button("ego_warning", wait=1), interval=0)
            gui.mouseUp()

        if (ego_image := is_ego()) is not None: # skip EGO animation
            ck = True
            gui.mouseDown()
            wait_while_condition(lambda: LocateRGB.check(ego_image, region=REG["ego_usage"], wait=1), interval=0)
            gui.mouseUp()

        if now.button("RetryStage"):
            attempts += 1
            if attempts >= 5:
                logging.info("Got stuck in hard battle")
                if not p.RESTART:
                    wait_while_condition(lambda: not now.button("Confirm_retry", method=cv2.TM_SQDIFF_NORMED), lambda: win_click(1200, 400), interval=1, timer=3)
                    gui.press("space")
                    loading_halt()
                    logging.info("Run stopped")
                    err = StopIteration("Dante, we failed... If you want to end run here, enable 'End stuck runs'")
                    if p.ALTF4: close_limbus(error=err)
                    raise err
                else:
                    wait_while_condition(lambda: not now.button("Confirm_retry", method=cv2.TM_SQDIFF_NORMED), lambda: win_click(1200, 670), interval=1, timer=3)
                    gui.press("space")
                    loading_halt()
                    print("Battle is over")
                    logging.info("Battle is over")
                    p.time_elapsed()
                    return True
            else:
                wait_while_condition(lambda: not now.button("Confirm_retry", method=cv2.TM_SQDIFF_NORMED), lambda: win_click(1200, 530), interval=1, timer=3)
                gui.press("space")
                loading_halt()
                logging.info(f"Re-attempting the battle (attempt {attempts + 1})")

        for i in exit_if:
            if now.button(i):
                if i == "loading":
                    if not lux:
                        if p.EXPECT_REWARD:
                            win_moveTo(1000, 950)
                        else:
                            win_moveTo(300, 600)
                        p.EXPECT_REWARD = False
                    loading_halt()
                print("Battle is over")
                logging.info("Battle is over")
                p.time_elapsed()
                p.EXPECT_ACTION = "grab_card" if p.EXPECT_REWARD else "move"
                return True
            
        # for i in range(3):
        #     if now_rgb.button(f"end_{i}", "skip_yap"):
        #         gui.press("space")
        
        if p.LIMBUS_NAME not in (win := gui.getActiveWindowTitle()):
            ck = True
            pause(win)
        
        if now.button("pause"):
            ck = True
            time.sleep(0.5)
        else:
            time.sleep(0.2)
        
        # stuck check
        if ck == False:
            if last_error != 0:
                if time.time() - last_error > 100:
                    raise RuntimeError('Stuck in battle')
            else:
                last_error = time.time()
        else:
            last_error = 0