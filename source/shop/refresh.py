from source.utils.utils import *
from source.shop.skill3 import *

def keyword_refresh_costs():
    return {
        0: 50,
        1: 50,
        2: 50,
        3: 60,
        4: 75,
        5: 90,
    }

def normal_refresh_costs():
    return {
        0: 100,
        1: 105,
        2: 120,
    }

def try_refresh(budget):
    costs = normal_refresh_costs()
    print("costs for refresh", costs, "budget", budget)
    if not can_refresh(budget, costs, p.REFRESH_COUNT):
        return False, budget

    if now.button("CannotRefresh") or now.button("NotEnoughCost"):
        return False, budget
    print("trying to refresh")
    click_normal_refresh()
    budget -= costs[p.REFRESH_COUNT]
    p.REFRESH_COUNT += 1
    update_shelf()
    budget = update_skill3(budget)
    return True, budget

def try_keyword_refresh(budget):
    costs = keyword_refresh_costs()
    print("costs for keyword refresh", costs, "budget", budget)
    if not can_refresh(budget, costs, p.REFRESH_COUNT):
        return False, budget

    if now.button("CannotKeywordRefresh") or now.button("NotEnoughKeywordCost"):
        return False, budget
    click_keyword_refresh()
    budget -= costs[p.REFRESH_COUNT]
    p.REFRESH_COUNT += 1
    update_shelf()
    budget = update_skill3(budget)
    return True, budget

def click_keyword_refresh():
    Action(p.SUPER, click=(1715, 176), ver="keywordRef").execute(shop_click)
    wait_while_condition(
        condition=lambda: now.button("keywordRef") and not now.button("connecting"), 
        action=confirm_affinity
    )
    connection()

def click_normal_refresh():
    win_click(1489, 177, tsize=(180, 53))
    connection()

def can_refresh(budget, costs, times_refreshed):
    if not times_refreshed in costs:
        return False
    return budget > costs[times_refreshed] + 120