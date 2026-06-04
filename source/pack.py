from source.utils.utils import *
from source_app.utils import *

def within_region(x, regions):
    for i, region in enumerate(regions):
        x1, _, w, _ = region
        if x1 < x < x1 + w:
            return i
    else:
        print("wtf", x, "is not in regions", regions)
        return None


def remove_pack(level, name):
    for l in range(level, 6 + p.EXTREME*10):
        if name in p.PICK_NORMAL[f"floor{l}"]:
            p.PICK_NORMAL[f"floor{l}"].remove(name)
        if name in p.PICK_NORMAL[f"floor{l}"]:
            p.PICK_HARD[f"floor{l}"].remove(name)

def pack_sifter():
    return SIFTMatcher(region=(161, 630, 1632, 140), nfeatures=1500, contrastThreshold=0.00, edgeThreshold=12)

def pack_eval(regions, skip, skips):
    # best packs
    priority = p.PICK_HARD[f"floor{p.LVL}"] if p.is_on_hard() else p.PICK_NORMAL[f"floor{p.LVL}"]
    logging.info(f"Pick: {priority}")

    backup = p.PICK_ALL_HARD[f"floor{p.LVL}"] if p.is_on_hard() else p.PICK_ALL_NORMAL[f"floor{p.LVL}"]
    backup = [p for p in backup if p not in priority]
    logging.info(f"Backup: {backup}")

    # worst packs (suboptimal time)
    banned = p.IGNORE_HARD[f"floor{p.LVL}"] if p.is_on_hard() else p.IGNORE_NORMAL[f"floor{p.LVL}"]
    logging.info(f"Ignore: {banned}")

    pack_list = HARD_FLOORS[format_lvl(p.LVL)] if p.is_on_hard() else FLOORS[format_lvl(p.LVL)]

    first = [p for p in pack_list if p in priority]
    second = [p for p in pack_list if p in backup]
    third = [p for p in pack_list if p not in priority and p not in backup]

    # for i, region in enumerate(regions):
    #     cv2.imwrite(f"testing/region_{time.time()}_{i}.png", screenshot(region))

    def locate_packs(packs, tries=1):
        for _ in range(tries):
            sift = pack_sifter()
            # cv2.imwrite(f"testing/sift{time.time()}.png", sift.base_image)
            for pack in packs:
                box = sift.locate(PTH[pack])
                if box:
                    x, _ = gui.center(box)
                    region_id = within_region(x, regions)
                    if region_id is not None:
                        return pack, region_id
            time.sleep(0.10)
        return None, None
    
    first_pack, region_id = locate_packs(first, 2)
    if first_pack:
        remove_pack(p.LVL, first_pack)
        logging.info(f"Pack: {first_pack}")
        print(f"Pack: {first_pack}")
        return region_id
    if skip != skips and priority:
        return None
    second_pack, region_id = locate_packs(second, 2)
    if second_pack:
        remove_pack(p.LVL, second_pack)
        logging.info(f"Pack: {second_pack}")
        print(f"Pack: {second_pack}")
        return region_id
    if skip != skips and backup:
        return None

    sift = pack_sifter()
    packs = dict()
    for pack in third:
        if len(packs.keys()) >= len(regions): break
        box = sift.locate(PTH[pack])
        if box:
            x, _ = gui.center(box)
            if (region_id := within_region(x, regions)) is not None \
                and region_id not in packs.values():
                    packs[pack] = region_id
    
    logging.info(packs)
    ordered_packs = list(sorted([(i, pack) for pack, i in packs.items()]))
    in_order = [pack for _, pack in ordered_packs]
    print(in_order)
    filtered = {pack: i for pack, i in packs.items() if pack not in banned}

    if not filtered and skip != skips: 
        return None
    elif not filtered:
        print("Pick bad pack")
        if p.did_normal_then_hard():
            return 'CANCEL_NORMAL4HARD1' # Try switching back to normal for last floor
        if packs:
            name = random.choice(list(packs.keys()))
            remove_pack(p.LVL, name)
            logging.info(f"Pack: {name}")
            return packs[name]
        return 0

    # locating relevant ego gifts in floor rewards
    ego_coords = [gui.center(box) for box in LocateRGB.locate_all(PTH[p.GIFTS[0]["checks"][1]])]
    owned_x = [x + w for x, _, w, _ in LocateRGB.locate_all(PTH["OwnedSmall"])]

    # excluding owned ego gifts from evaluation
    ego_coords = [
        coord for coord in ego_coords
        if all(abs(coord[0] - x) >= 25 for x in owned_x)
    ]

    ids = sorted(filtered.values())
    new_regions = [regions[i] for i in ids]
    weight = {i: 0 for i in ids} # evaluating each floor based on ego gifts
    for coord in ego_coords:
        index = within_region(coord[0], new_regions)
        if index is not None:
            weight[ids[index]] += 1

    id = max(weight, key=weight.get)
    name = next((pack for pack, i in filtered.items() if i == id), None)

    remove_pack(p.LVL, name)
    print(f"Entering {name}")
    logging.info(f"Pack: {name}")
    return id


def update_lvl(level):
    floor_range = list(range(1, 6))
    if p.EXTREME: floor_range = list(range(1, 10)) + [0]

    assumed_lvl = 0
    digit_conf = 0
    for i in floor_range:
        det = len(LocateGray.locate_all(PTH[f"lvl{i}"], region=REG["lvl"], threshold=5, conf=0.95))
        if det == 1:
            if i != 1:
                conf = LocateGray.get_conf(PTH[f"lvl{i}"], region=REG["lvl"])
                if conf < digit_conf: continue
                else: 
                    digit_conf = conf
                    if assumed_lvl != 1:
                        assumed_lvl //= 10
            assumed_lvl = assumed_lvl*10 + i
        elif det == 2:
            assumed_lvl = 11
            break

    if (assumed_lvl in range(1, 6)) or (p.EXTREME and assumed_lvl in range(1, 16)):
        return assumed_lvl
    elif (level + 1 in range(1, 6)) or (p.EXTREME and level + 1 in range(1, 16)):
        return level + 1
    else:
        return level


def pack():
    if not now.button("PackChoice"):
        return False
    p.time_elapsed()
    print("pack check")
    p.LVL = update_lvl(p.LVL)

    win_moveTo(1617, 62, tsize=(240, 60))
    if p.LVL <= 5:
        if p.is_on_hard():
            if not now.button("hardDifficulty"):
                win_click(1349, 64)
        else:
            now.button("hardDifficulty", click=(1349, 64))

    time.sleep(1.0)
    print(f"Entering Floor {p.LVL}")
    logging.info(f"Floor {p.LVL}")

    start_time = time.time()
    box = None
    while p.LVL > 5 and box is None:
        box = LocateGray.locate(PTH["PackPull"], region=REG["PackPull"])
        if time.time() - start_time > 4:
            break
        time.sleep(0.2)

    card_count = 5
    if box:
        card_count = 5 - min((max((gui.center(box)[0] - 21), 1) // 157), 2)
    
    offset = (5 - card_count)*161
    regions = [(170 + offset + 321 * i, 280, 270, 624) for i in range(card_count)]
    skips = 1 + p.BUFF[2] + int(p.BUFF[2] > 0)

    print(f"{card_count} Packs")

    for skip in range(skips + 1):
        id = pack_eval(regions, skip, skips)
        # cv2.imwrite(f"choices/pack{int(time.time())}.png", screenshot()) # debugging
        if not id is None:
            if id == 'CANCEL_NORMAL4HARD1':
                print('Cancel normal4->hard1')
                p.cancel_normal_then_hard()
                if now.button("hardDifficulty"):
                    win_click(1349, 64, delay=0.5)
                time.sleep(1.3)
                id = pack_eval(regions, skip, skips)
                if id is None:
                    continue

            region = regions[id]
            x, y = (region[0] + (region[2] // 2), region[1] + (region[3] // 2))
            x += random.randint(-40, 40)
            y += random.randint(-100, 100)
            win_moveTo(x, y)
            win_dragTo(x, y + 300, duration=0.61)
            break
        if skip != skips:
            win_click(1617, 62, tsize=(240, 60))
            time.sleep(1.3)
    
    wait_while_condition(lambda: now.button("PackChoice"), interval=0.1)
    if p.LVL != 1: p.MOVE_ANIMATION = True
    else: time.sleep(0.1)
    p.EXPECT_ACTION = "move"
    return True
