from source.utils.utils import *
from source.shop.browse_shop import *

def revive_idiots():
    if p.is_saikai(): return
    revivals = min(p.DEAD, balance()//100)
    if revivals < 1: return
    
    ClickAction((293, 705), ver="return").execute(click)
    for _ in range(revivals):
        if not wait_while_condition(lambda: now.button("return"), lambda: win_click(1545, 690), timer=3):
            Action("return", ver=p.SUPER).execute(click)
            return
        Action("no_hp", ver="select").execute(click_rgb) # 1700 970
        Action("select", ver="connecting").execute(click)
        connection()
        ClickAction((1545, 500), ver="return").execute(click)
        time.sleep(0.2)
    Action("return", ver=p.SUPER).execute(click)
    time.sleep(0.2)

def heal_all():
    if balance() < 100: return

    ClickAction((293, 705), ver="return").execute(click)
    try:
        ClickAction((1645, 500), ver="connecting").execute(click)
        connection()
        time.sleep(0.2)
    except RuntimeError as e:
        print("couldn't heal:", e)
        return
    finally:
        ClickAction((1645, 500), ver="return").execute(click)
        Action("return", ver=p.SUPER).execute(click)
        time.sleep(0.2)

def heal_more_for_extreme():
    if p.LVL > 11:
        for _ in range(min(p.LVL - 11, 3)):
            heal_all()

def heal_for_hard():
    if p.DEAD > 0 and p.is_on_hard():
        revive_idiots()
        heal_all()

def heal_sinners():
    heal_for_hard()
    heal_more_for_extreme()