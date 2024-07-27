import re


def card_generator(deck_list):
    prevnl = -1
    while True:
        nextnl = deck_list.find("\n", prevnl + 1)
        if nextnl < 0:
            yield deck_list[prevnl + 1 : nextnl]
            break
        yield deck_list[prevnl + 1 : nextnl]
        prevnl = nextnl


def get_quantity(card_info):
    return re.findall(r"[0-9]+", card_info)[0]


def get_name(card_info):
    return re.findall(r"(?<=[0-9]\s)(.+)(?=\s\()", card_info)[0]


def get_set_code(card_info):
    return re.findall(r"(?<=\()(.+?)(?=\))", card_info)[0]


def get_collecter_number(card_info):
    return re.findall(r"(?<=\)\s)(.+)", card_info)[0]
