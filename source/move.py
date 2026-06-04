from source.utils.utils import *

# Weights are the average battle time in seconds
priority = {"Event": 0, "Normal": 52, "Miniboss": 67, "Risky": 87, "Focused": 77}
saikai_priority = {"Event": 0, "Normal": 52, "Miniboss": 47, "Risky": 63, "Focused": 63}
v_list = [0.8, 0.9, 1]
d_list = [None, -0.1, -0.19]
keys_map = {0: "w", 1: "d", 2: "s"}


def is_boss(region=(624, 376, 282, 275)):
    image = screenshot(region=region)
    red_mask = cv2.inRange(image, np.array([0, 0, 180]), np.array([50, 50, 255]))
    
    if any(now.button(f"boss{i}", region, image=red_mask, conf=0.6) for i in range(2)):
        return True
    return False

def is_risky(_loc, region):
    if _loc.button("risk0", region) or \
   any(_loc.button("risk1", region, comp=(1 - 0.14*j)) for j in range(2)) or \
   any(_loc.button("risk2", region, comp=(1 - 0.14*j), v_comp=None, distort=None) for j in range(2)):
        return True
    return False

def is_focused(_loc, region):
    if any(_loc.button(f"focus{j}", region, conf=0.85) for j in range(2)) or \
       any(_loc.button(f"focus{j+2}", region, conf=0.85, v_comp=None, distort=None) for j in range(2)):
        return True
    return False

def is_event(_loc, region):
    if any(_loc.button(f"event{j}", region, conf=0.85) for j in range(2)) or \
           _loc.button("event2", region, conf=0.9, v_comp=None, distort=None):
        return True
    return False

def is_shop(_loc, region):
    if _loc.button("shop0", region) or \
       _loc.button("shop1", region, v_comp=None, distort=None) or \
       (p.is_on_hard() and (_loc.button("super0", region) or _loc.button("super1", region, v_comp=None, distort=None))):
        return True
    return False

def get_node_name(_loc, region):
    if is_boss(region):
        p.EXPECT_ACTION = "fight"
        return "Boss"
    
    if now_rgb.button("coin", region, conf=0.9):
        p.EXPECT_ACTION = "fight"
        if now_rgb.button("gift", region, conf=0.9):
            if is_risky(_loc, region):
                return "Risky"
            elif is_focused(_loc, region):
                return "Focused"
            else:
                return "Miniboss"
        else:
            return "Normal"
    elif is_event(_loc, region):
        p.EXPECT_ACTION = "event"
        return "Event"
    elif is_shop(_loc, region):
        p.EXPECT_ACTION = "shop"
        return "Shop"
    else:
        # cv2.imwrite(f"debug{time.time()}.png", screenshot(region=region))
        return "Unknown"
    

def position(shift=0):
    x, y = random.randint(1500, 1700), random.randint(300, 500)
    time.sleep(0.1)
    win_moveTo(x, y, tsize=(1, 1))
    win_dragTo(x - 295, y + 100 + shift*320, duration=1.5, hook=True, tsize=(1, 1))

def directions(is_aligned=True):
    options = {
        0: "_up",
        1: "_forward",
        2: "_down"
    }
    regions = dict()
    dir_reg = "directions_init" if not is_aligned else "directions"
    reg_xy = (634, 80) if is_aligned else (914, 0)
    # cv2.imwrite(f"testing/directions{time.time()}.png", screenshot(region=REG[dir_reg]))
    for i, suffix in options.items():
        if now.button(suffix, dir_reg, conf=0.85):
            regions[i] = (reg_xy[0], reg_xy[1] + i * 310, 282, 275)
    return regions


def get_connections(region=(850, 340, 610, 370)):
    image = screenshot(region=region)
    h, w = image.shape[:2]
    crop_h = int(0.216 * h)
    crop_w = int(0.492 * w)

    images = [
        image[0:crop_h, 0:crop_w],
        image[0:crop_h, w - crop_w:w],
        image[h - crop_h:h, 0:crop_w],
        image[h - crop_h:h, w - crop_w:w]
    ]
    connections = []
    for i, image in enumerate(images):
        paths = dict()
        for j, direction in enumerate(["up", "down"]):
            paths[j] = LocateGray.get_conf(PTH[direction], image=image)
        j = max(paths, key=paths.get)
        if paths[j] >= 0.87:
            direction = ["up", "down"][j]
            # cv2.imwrite(f"data/{direction}/{time.time()}_{direction}.png", image)
            connections.append(((i % 2, (i//2) + 1 - j), (i % 2 + 1, (i//2) + j)))
        # else:
            # cv2.imwrite(f"data/none/{time.time()}_none.png", image)
    return connections

def check_connections(connections):
    levels = [y for pair in connections for (_, y) in pair]
    
    has_zero = 0 in levels
    has_two = 2 in levels
    
    if (has_zero and has_two) or (not has_zero and not has_two): return 0
    elif has_zero: return 1
    else: return -1

def next_step(nodes, extra_connections):
    print("nodes", nodes, "extra_connections", extra_connections)
    L = len(nodes)
    adj = {}
    for i in range(L):
        for j in range(len(nodes[i])):
            if nodes[i][j] is not None:
                adj[(i,j)] = []
    for i in range(L-1):
        for j in range(len(nodes[i])):
            if nodes[i][j] is not None and nodes[i+1][j] is not None:
                adj[(i,j)].append((i+1, j))
    for (a,b),(c,d) in extra_connections:
        if 0 <= a < L and 0 <= b < len(nodes[a]) and 0 <= c < L and 0 <= d < len(nodes[c]):
            if nodes[a][b] is None or nodes[c][d] is None:
                continue
            if a + 1 == c:
                adj.setdefault((a,b), []).append((c,d))
            elif c + 1 == a:
                adj.setdefault((c,d), []).append((a,b))

    def dfs(i, j, mult=1.02):
        base = (priority if not p.is_saikai() else saikai_priority)[nodes[i][j]]
        base *= mult
        if i == L - 1:
            return base, True
        best = float('inf')
        connections = adj.get((i,j), [])
        can_go_fast = len(connections) <= 1
        for (ni, nj) in connections:
            if ni != i + 1:
                continue
            sub, _ = dfs(ni, nj, mult*1.02)
            total = base + sub + (0 if j == nj else 1)
            if total < best:
                best = total
                can_go_fast = j == nj or len(connections) == 1
        return best, can_go_fast

    best_idx = None
    best_cost = float('inf')
    fast = False
    for j0 in range(len(nodes[0])):
        if nodes[0][j0] is None:
            continue
        cost0, can_fast = dfs(0, j0)
        if cost0 <= best_cost:
            best_cost = cost0
            best_idx = j0
            fast = can_fast
            # print("connect", nodes[0][j0], "via", adj.get((0, j0), []), "fast?", fast) 
    if best_idx is None:
        return None, None, False
    return best_idx, nodes[0][best_idx], fast


def enter(wait=1.2):
    if now.button("enter", wait=wait):
        gui.press("space")
        connection()
        return True
    elif p.EXTREME and now.button("secretEncounter", wait=wait):
        if p.SKIP: button = "skipEncounter"
        else: button = "secretEncounter"
        wait_while_condition(
            condition= lambda: now.button(button),
            action=lambda: click.button(button)
        )
        win_moveTo(1721, 999)
        connection()
        return True
    return False


def move():
    enter(wait=False)
    is_move = now.button("Move")

    if is_move and p.MOVE_ANIMATION:
        wait_while_condition(condition=lambda: now.button("Move"), interval=0.1)
        p.MOVE_ANIMATION = False
        is_move = loc.button("Move", wait=2)
    
    if not is_move or \
           now.button("Confirm"): return False
    
    if p.is_on_hard():
        time.sleep(1.4) # node reveal animation
    else:
        time.sleep(0.15)

    if p.is_on_hard() and now.button("suicide"):
        return False
    
    print("move check")
    # run fail detection
    p.DEAD = len([gui.center(box) for box in LocateRGB.locate_all(PTH["0"], region=REG["alldead"], conf=0.9, threshold=40)])
    print(f"{p.DEAD} dead sinners")
    if p.DEAD >= len(p.SELECTED):
        gui.press("esc")
        time.sleep(0.5)
        chain_actions(click, [
            Action("forfeit"),
            Action("ConfirmInvert", ver="connecting"),
        ])
        connection()
        return False
    # fail detection end
    # if now.button("victory") or not now.button("Move"): return False
    
    if p.MOVE_FAST_NEXT_TIME:
        p.MOVE_FAST_NEXT_TIME = False
        print("Moving quickly...")
        for key in ["d", "space"]:
            gui.press(key)
        return enter(wait=0.5)

    if not now_rgb.button("Danteh"):
        print("Case 0: Bus is out of view")
        gui.press("d")
        gui.press("a")

        wait_while_condition(
            condition=lambda: not now_rgb.button("Danteh"),
            action=lambda: gui.press("a"),
            timer=2)
        if not now_rgb.button("Danteh"):
            gui.press("space")
            if enter():
                logging.info("Entering unknown node")
                return True
            return False
    
    regions = directions(is_aligned=False)
    print(f"Visible directions: {list(regions.keys())}")

    adjust = 0
    if len(regions) == 0:
        print("Case 2: No directions are visible")
        if input_with_fallback("space", lambda: win_click(705, 411), enter) or move_fallback():
            logging.info("Entering unknown node")
            return True
        return False
    elif len(regions) == 1:
        print("Case 3: No node search, only one direction")
        region_idx = next(iter(regions.keys()))
        region = regions[region_idx]
        _loc = LocatePreset(image=screenshot(region=region), v_comp=v_list[region_idx], conf=0.8, wait=False)
        name = get_node_name(_loc, region)
        key_name = keys_map.get(region_idx, "d")

        if input_with_fallback(key_name, lambda: win_click(gui.center(region)), enter):
            logging.info(f"Entering {name} {'fight'*(name!='Event' and name!='Shop')}")
            use_node_name(name)
            return True
        return False
    elif all(k in regions for k in (0, 2)):
        print("Case 4: No major adjustment needed for node search")
        position()
    else:
        print("Case 5: Adjusting position for node search")
        inter_connect = get_connections(region=(1140, 230, 610, 370))
        adjust = check_connections(inter_connect)
        position(shift=adjust)

    regions = directions()
    if adjust:
        keys = [i + adjust for i in regions.keys() if 0 <= i + adjust <= 2]
        regions = {key: (634, 80 + key * 310, 282, 275) for key in keys}
    
    inter_connect = get_connections()
    # print(inter_connect)
    nodes = [[None, None, None] for _ in range(3)]

    for depth in range(3):
        if depth == 0: srch_regions = regions.copy()
        else: srch_regions = {i: (634 + 380 * depth, 80 + i * 310, 282, 275) for i in range(3)}

        for level, region in srch_regions.items():
            _loc = LocatePreset(image=screenshot(region=region), v_comp=v_list[level], distort=d_list[depth], conf=0.8, wait=False)
            # cv2.imwrite(f"testing/region{depth}{level}.png", screenshot(region=region))

            if now_rgb.button("coin", region, conf=0.9):
                if now_rgb.button("gift", region, conf=0.9):
                    if is_risky(_loc, region):
                        nodes[depth][level] = "Risky"
                        continue
                    elif is_focused(_loc, region):
                        nodes[depth][level] = "Focused"
                        continue
                    else:
                        nodes[depth][level] = "Miniboss"
                        continue
                else:
                    nodes[depth][level] = "Normal"
                    continue

            elif is_event(_loc, region):
                nodes[depth][level] = "Event"
                continue

        if not any(nodes[depth]):
            if depth != 0: nodes = nodes[:depth]
            break
    if any(nodes[0]):
        # print(nodes)
        id, name, can_go_fast = next_step(nodes, inter_connect)
        if not id is None:
            p.MOVE_FAST_NEXT_TIME = can_go_fast
            if can_go_fast:
                print("go fast next time!!!")
            key_name = keys_map.get(int(id-adjust), "d")
            region = regions[id]
            if input_with_fallback(key_name, lambda: win_click(gui.center(region)), enter):
                logging.info(f"Entering {name} {'fight'*(name!='Event')}")
                use_node_name(name)
                return True
    elif move_fallback():
        logging.info("Entering unknown node")
        print("nodes is nothing, inter-connect is ", inter_connect)
        return True
    return False

def use_node_name(name):
    p.EXPECT_CHAIN = False
    p.EXPECT_FOCUSED = False
    p.EXPECT_REWARD = False
    if name == 'Normal':
        p.EXPECT_CHAIN = True
    elif name == 'Focused':
        p.EXPECT_FOCUSED = True
    elif name in ['Risky', 'Miniboss', 'Boss', 'Shop']:
        p.EXPECT_REWARD = True

def move_fallback():
    for key in ["d", "space"]:
        gui.press(key)
        if enter():
            return True
    
    Danteh = LocateRGB.locate(PTH["Danteh"])
    if Danteh is None: return False

    Danteh = gui.center(Danteh)
    win_click(Danteh)
    if enter(): return True

    for i in range(3):
        x_click = int(Danteh[0] + 336)
        y_click = int(Danteh[1] - 241 + i * 275)
        if 57 <= x_click <= 1809 and 110 <= y_click <= 934:
            win_moveTo(x_click, y_click)
            gui.click()
            if enter(): return True
    return False