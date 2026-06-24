from source.utils.utils import *
from source.dungeon_graph import next_direction

def move():
    enter(wait=False)
    is_move = now.button("Move")

    if is_move and p.MOVE_ANIMATION:
        wait_while_condition(condition=lambda: now.button("Move"), interval=0.1)
        p.MOVE_ANIMATION = False
        is_move = loc.button("Move", wait=2)
    
    if not is_move:
        return False
    
    if now.button("Confirm"):
        gui.press("space")
        return False

    if p.is_on_hard():
        time.sleep(1.4) # node reveal animation

    if p.is_on_hard() and now.button("suicide"):
        return False
    
    print("move check")
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

    if not now_rgb.button("Danteh"):
        print("Case 0: Bus is out of view")
        p.BUS_COUNT += 1
        if p.BUS_COUNT == 1:
            time.sleep(0.25)
            return False
        
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
    p.BUS_COUNT = 0
    
    direction_key, node_type = next_direction()
    print(f"Entering {node_type}")
    use_node_type(node_type)
    gui.press(direction_key)
    gui.press("space")
    time.sleep(0.3)
    return enter(wait=0.3)

def use_node_type(name):
    p.EXPECT_CHAIN = False
    p.EXPECT_FOCUSED = False
    p.EXPECT_REWARD = False
    if name == 'Normal':
        p.EXPECT_CHAIN = True
    elif name == 'Focused':
        p.EXPECT_FOCUSED = True
    elif name in ['Risky', 'Miniboss', 'Boss']:
        p.EXPECT_REWARD = True

def enter(wait=0.6):
    if now.button("enter", wait=wait):
        gui.press("space")
        connection()
        time.sleep(0.25)
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