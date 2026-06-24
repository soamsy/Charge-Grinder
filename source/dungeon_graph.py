from collections import defaultdict

from source.utils.utils import *

priority        = {"Event": 0, "Normal": 52, "Miniboss": 67, "Risky": 87, "Focused": 77, "Unknown": 53}
saikai_priority = {"Event": 0, "Normal": 52, "Miniboss": 47, "Risky": 66, "Focused": 63, "Unknown": 53}

def _binary_locate_all(template_path, crop, rx, ry, bin_thresh=100, conf=0.8, dedup_px=30):
    tmpl = cv2.imread(template_path)
    tmpl_gray = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
    _, tmpl_bin = cv2.threshold(tmpl_gray, bin_thresh, 255, cv2.THRESH_BINARY)
    crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, crop_bin = cv2.threshold(crop_gray, bin_thresh, 255, cv2.THRESH_BINARY)
    th, tw = tmpl_bin.shape[:2]
    if th > crop_bin.shape[0] or tw > crop_bin.shape[1]:
        return []
    result = cv2.matchTemplate(crop_bin, tmpl_bin, cv2.TM_CCORR_NORMED)
    locs = list(zip(*np.where(result >= conf)[::-1]))
    hits = []
    for (lx, ly) in locs:
        score = float(result[ly, lx])
        if any(abs(lx - hx) <= dedup_px and abs(ly - hy) <= dedup_px for hx, hy, *_ in hits):
            continue
        hits.append((lx + rx, ly + ry, tw, th, score))
    return hits


def print_graph(graph, types):
    LABEL_W = 4
    NODE_W  = 9
    CONN_W  = 4
    levels  = [1, 0, -1]
    steps   = [0, 1, 2, 3]

    step_x  = [LABEL_W + i * (NODE_W + CONN_W) for i in range(len(steps))]
    total_w = step_x[-1] + NODE_W
    gap_x   = [step_x[i] + NODE_W + CONN_W // 2 for i in range(len(steps) - 1)]

    def blank():
        return [' '] * total_w

    def put(r, x, s):
        for i, c in enumerate(s):
            if x + i < total_w:
                r[x + i] = c

    def node_str(step, level):
        if step == 0:
            return 'Bus' if level == 0 else None
        return types.get((step, level))

    def has_edge(s, l, ds, dl):
        return (ds, dl) in graph[(s, l)]

    r = blank()
    for i, s in enumerate(steps):
        put(r, step_x[i], (f'step {s}' if s else '  Bus').center(NODE_W))
    lines = [''.join(r)]

    for ri, level in enumerate(levels):
        r = blank()
        put(r, 0, f'{level:2d}: ')
        for i, s in enumerate(steps):
            name = node_str(s, level)
            if name:
                put(r, step_x[i], name.center(NODE_W))
            if i < len(steps) - 1 and has_edge(s, level, s + 1, level):
                put(r, step_x[i] + NODE_W, '─' * CONN_W)
        lines.append(''.join(r))

        if ri < len(levels) - 1:
            next_level = levels[ri + 1]
            r = blank()
            for i in range(len(steps) - 1):
                s = steps[i]
                down = has_edge(s, level,      s + 1, next_level)
                up   = has_edge(s, next_level, s + 1, level)
                ch = '╳' if down and up else '╲' if down else '╱' if up else None
                if ch:
                    put(r, gap_x[i], ch)
            lines.append(''.join(r))

    print('\n'.join(lines))


def map_out_next_3_steps():
    image = screenshot((0, 0, 1920, 1080))
    graph = defaultdict(list)
    types = {}

    ts = time.time()
    # cv2.imwrite(f"testing/map3_full_{ts}.png", image)

    # Step 0→1 connections (bus is always at level 0)
    STEP0_CONF = 0.78
    for pth_key, (rx, ry, rw, rh), level in [
        ("_up",      (830, 225, 125, 115), 1),
        ("_forward", (830, 387, 125, 95), 0),
        ("_down",    (830, 530, 125, 115), -1),
    ]:
        crop = image[ry:ry+rh, rx:rx+rw]
        # cv2.imwrite(f"testing/map3_step0_{pth_key}_{ts}.png", crop)
        conf = Locate.get_conf(PTH[pth_key], image=crop)
        found = conf >= STEP0_CONF
        print(f"step0 {pth_key}: conf={conf:.3f} threshold={STEP0_CONF} found={found}")
        if found:
            graph[(0, 0)].append((1, level))
            types[(1, level)] = "Event"

    # Diagonal and horizontal connections for steps 1→2 and 2→3.
    CONN_CONF = 0.83
    step_x_mids = {(1, 2): 1280, (2, 3): 1665}

    diag_w, diag_h = 60, 40
    level_y_mids = {(1, 0): 275, (0, -1): 590}

    for (src_step, dst_step), x_mid in step_x_mids.items():
        rx = x_mid - diag_w // 2
        for (lvl_hi, lvl_lo), y_mid in level_y_mids.items():
            ry = y_mid - diag_h // 2
            crop = image[ry:ry+diag_h, rx:rx+diag_w]
            up_conf   = LocateGray.get_conf(PTH["up"],   image=crop)
            down_conf = LocateGray.get_conf(PTH["down"], image=crop)
            # cv2.imwrite(f"testing/map3_diag_{src_step}to{dst_step}_hi{lvl_hi}lo{lvl_lo}_{ts}.png", crop)
            print(f"diag {src_step}→{dst_step} lvl {lvl_hi}/{lvl_lo}: up={up_conf:.2f} down={down_conf:.2f}")
            if down_conf >= CONN_CONF and down_conf >= up_conf:
                graph[(src_step, lvl_hi)].append((dst_step, lvl_lo))
                types.setdefault((dst_step, lvl_lo), "Event")
            elif up_conf >= CONN_CONF:
                graph[(src_step, lvl_lo)].append((dst_step, lvl_hi))
                types.setdefault((dst_step, lvl_hi), "Event")

    # Horizontal (forward) connections — same level across consecutive steps.
    fwd_w, fwd_h = 56, 36
    level_y_fwd = {1: 115, 0: 435, -1: 755}

    for (src_step, dst_step), x_mid in step_x_mids.items():
        rx = x_mid - fwd_w // 2
        for level, y_center in level_y_fwd.items():
            ry = y_center - fwd_h // 2
            crop = image[ry:ry+fwd_h, rx:rx+fwd_w]
            conf = LocateGray.get_conf(PTH["forward"], image=crop)
            # cv2.imwrite(f"testing/map3_fwd_{src_step}to{dst_step}_lvl{level}_{ts}.png", crop)
            print(f"fwd {src_step}→{dst_step} lvl {level}: conf={conf:.2f}")
            if conf >= CONN_CONF:
                graph[(src_step, level)].append((dst_step, level))
                types.setdefault((src_step, level), "Event")
                types.setdefault((dst_step, level), "Event")

    # Centered coin = Fight, off-center coin = Risky.
    x_regions    = {1: (990, 1190), 2: (1370, 1570), 3: (1760, 1920)}
    x_centers    = {s: (lo + hi) // 2 for s, (lo, hi) in x_regions.items()}
    CENTER_TOL   = 25
    COIN_CONF    = 0.9
    COIN_BIN_THRESH = 80

    for pth_key, (rx, ry, rw, rh), level in [
        ("TopCost",    (990,   5, 930, 20), 1),
        ("BrightCost", (990, 325, 930, 50), 0),
        ("BrightCost", (990, 640, 930, 50), -1),
    ]:
        crop = image[ry:ry+rh, rx:rx+rw]
        # debug_img = crop.copy()
        for x, y, w, h, score in _binary_locate_all(PTH[pth_key], crop, rx, ry,
                                                     bin_thresh=COIN_BIN_THRESH,
                                                     conf=COIN_CONF):
            lx, ly = x - rx, y - ry
            step_label = next((s for s, (lo, hi) in x_regions.items() if lo <= x < hi), None)
            if step_label is None:
                continue
            coin_cx = x + w // 2
            offset = abs(coin_cx - x_centers[step_label])
            centered = offset <= CENTER_TOL
            node_type = "Fight" if centered else "Risky"
            print(f"  coin lvl {level} step {step_label} @ ({x},{y}) cx={coin_cx} offset={offset}: conf={score:.3f} → {node_type}")
            color = (0, 255, 0) if centered else (0, 165, 255)
            # cv2.rectangle(debug_img, (lx, ly), (lx + w, ly + h), color, 1)
            # cv2.putText(debug_img, f"{score:.2f}", (lx, max(ly - 2, 8)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
            types[(step_label, level)] = node_type
        # cv2.imwrite(f"testing/map3_coins_lvl{level}_{ts}.png", debug_img)

    # Step 3, level 0: UI occludes the top of the coin — use corner template instead.
    if types.get((3, 0)) == "Event":
        rx, ry, rw, rh = 1790, 360, 130, 38
        crop = image[ry:ry+rh, rx:rx+rw]
        hits = _binary_locate_all(PTH["CoinLeftCorner"], crop, rx, ry,
                                  bin_thresh=COIN_BIN_THRESH, conf=COIN_CONF)
        # debug_img = crop.copy()
        print(f"found hits {hits}")
        for x, y, w, h, score in hits:
            lx, ly = x - rx, y - ry
            coin_cx = x + w // 2 + 5
            offset = abs(coin_cx - x_centers[3])
            centered = offset <= CENTER_TOL
            node_type = "Fight" if centered else "Risky"
            print(f"  corner coin step 3 lvl 0 @ ({x},{y}) cx={coin_cx} offset={offset}: conf={score:.3f} → {node_type}")
            color = (0, 255, 0) if centered else (0, 165, 255)
            # cv2.rectangle(debug_img, (lx, ly), (lx + w, ly + h), color, 1)
            # cv2.putText(debug_img, f"{score:.2f}", (lx, max(ly - 2, 8)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
            types[(3, 0)] = node_type
        # cv2.imwrite(f"testing/map3_coins_corner_s3l0_{ts}.png", debug_img)

    if types.get((3, 1)) == "Event":
        rx, ry, rw, rh = 1760, 5, 160, 20
        crop = image[ry:ry+rh, rx:rx+rw]
        hits = _binary_locate_all(PTH["DarkLeftTopCost"], crop, rx, ry,
                                  bin_thresh=COIN_BIN_THRESH, conf=COIN_CONF)
        # debug_img = crop.copy()
        for x, y, w, h, score in hits:
            lx, ly = x - rx, y - ry
            coin_cx = x + w // 2 + 5
            offset = abs(coin_cx - x_centers[3])
            centered = offset <= CENTER_TOL
            node_type = "Fight" if centered else "Risky"
            print(f"  corner coin step 3 lvl 1 @ ({x},{y}) cx={coin_cx} offset={offset}: conf={score:.3f} → {node_type}")
            color = (0, 255, 0) if centered else (0, 165, 255)
            # cv2.rectangle(debug_img, (lx, ly), (lx + w, ly + h), color, 1)
            # cv2.putText(debug_img, f"{score:.2f}", (lx, max(ly - 2, 8)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
            types[(3, 1)] = node_type
        # cv2.imwrite(f"testing/map3_coins_corner_s3l1_{ts}.png", debug_img)

    if types.get((3, -1)) == "Event":
        rx, ry, rw, rh = 1760, 640, 160, 50
        crop = image[ry:ry+rh, rx:rx+rw]
        hits = _binary_locate_all(PTH["DarkLeftCornerCoin"], crop, rx, ry,
                                  bin_thresh=COIN_BIN_THRESH, conf=COIN_CONF)
        # debug_img = crop.copy()
        for x, y, w, h, score in hits:
            lx, ly = x - rx, y - ry
            coin_cx = x + w // 2 + 5
            offset = abs(coin_cx - x_centers[3])
            centered = offset <= CENTER_TOL
            node_type = "Fight" if centered else "Risky"
            print(f"  corner coin step 3 lvl -1 @ ({x},{y}) cx={coin_cx} offset={offset}: conf={score:.3f} → {node_type}")
            color = (0, 255, 0) if centered else (0, 165, 255)
            # cv2.rectangle(debug_img, (lx, ly), (lx + w, ly + h), color, 1)
            # cv2.putText(debug_img, f"{score:.2f}", (lx, max(ly - 2, 8)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
            types[(3, -1)] = node_type
        # cv2.imwrite(f"testing/map3_coins_corner_s3l-1_{ts}.png", debug_img)

    print_graph(graph, types)
    return graph, types


def rank_paths(graph, types):
    pri = saikai_priority if p.is_saikai() else priority
    step_bonus = {1: -3, 2: -2, 3: -1}

    all_paths = []

    def dfs(node, path, cost):
        step, level = node
        if step > 0:
            node_type = types.get(node, "Unknown")
            node_cost  = pri.get(node_type, pri["Unknown"])
            node_cost += step
            node_cost += step_bonus[step] * len(graph[node])
            cost += node_cost
        path = path + [node]
        neighbors = graph[node]
        if not neighbors:
            all_paths.append((cost, path))
            return
        for neighbor in neighbors:
            dfs(neighbor, path, cost)

    dfs((0, 0), [], 0)
    all_paths.sort(key=lambda x: x[0])
    return all_paths


def next_direction():
    graph, types = map_out_next_3_steps()
    paths = rank_paths(graph, types)
    if not paths:
        return "d", "Unknown"

    for cost, path in paths:
        labels = " → ".join(f"{types.get(n, 'Bus')}@{n}" for n in path)
        print(f"  cost={cost:>6.1f}  {labels}")

    _, best = paths[0]
    step1 = best[1]
    _, level = step1
    return {1: "w", 0: "d", -1: "s"}[level], types.get(step1, "Unknown")
