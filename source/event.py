from source.utils.utils import *

PROBS = ["VeryHigh", "High", "Normal", "Low", "VeryLow"]

favorites = ["chicken", "factory"]

def is_choice_made():
    connection()
    return wait_while_condition(lambda: now.button("choices"), interval=0.1, timer=1.5)

def event():
    if not now.button("event"): return False
    print("event check")
    start_time = time.time()
    while True:
        if time.time() - start_time > 100:
            return False
        if p.LIMBUS_NAME not in (win := gui.getActiveWindowTitle()): pause(win)

        now_click.button("skip")
        gui.press("space")
        
        if now.button("choices"):
            time.sleep(0.05)
            if now_click.button("textNew", "textEGO") and is_choice_made(): continue
            if now_click.button("textLvl", "textEGO") and is_choice_made(): continue
            if any(now_click.button(f"choice_{favorite}", "textEGO") for favorite in favorites) and is_choice_made(): continue

            egos = LocateGray.locate_all(PTH["textEGO"], region=REG["textEGO"], conf=0.85)

            if egos:
                affinity = []
                for aff in p.TEAM:
                    affinity += LocateGray.locate_all(PTH[f"{aff.lower()}_choice"], region=REG["textEGO"], conf=0.85)
                win = LocateGray.locate(PTH["textWIN"], region=REG["textEGO"], conf=0.85)

                filtered = []
                priority = []
                for box in egos:
                    if not win or abs(box[1] - win[1]) > 80:
                        filtered.append(box)

                        for aff in affinity:
                            if abs(box[1] - aff[1]) < 80:
                                priority.append(box)
                
                if priority:
                    sorted(priority, key=lambda x: x[1])            
                    win_click(gui.center(priority[0]), delay=0)
                    if is_choice_made(): continue
                
                if filtered:
                    sorted(priority, key=lambda x: x[1])            
                    win_click(gui.center(filtered[0]), delay=0)
                    if is_choice_made(): continue
                else:
                    win_click(1356, 498, delay=0)
                    if is_choice_made(): continue
            
            for choice in [316, 520, 730]:
                win_click(1348, choice, delay=0)
                if is_choice_made(): break
            else:
                if not is_choice_made():
                    raise RuntimeError


        now_click.button("Proceed")
        now_click.button("CommenceBattle")

        if now.button("check"):
            time.sleep(0.4)
            for prob in PROBS:
                if now_click.button(prob, "probs", search_from_right=True):
                    if now.button("skip"):
                        wait_while_condition(lambda: now.button("skip"), lambda: gui.press("space"), timer=2.0)
                    if click.button("Commence"):
                        wait_while_condition(lambda: not now.button("skip"), interval=0.1, timer=4.5)
                        if now_click.button("skip"):
                            wait_while_condition(lambda: not now.button("Continue"), lambda: gui.press("space"), interval=0.2, timer=8.0)
        
        if now_click.button("Continue"):
            print("Leaving event")
            connection()
            p.EXPECT_ACTION = "move"
            return True