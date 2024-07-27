from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.conf import settings
from django.forms import formset_factory

import logging
import re

from .models import Deck, Params, Cards
from .forms import DeckForm, ParamsForm

from .get_images import get_cards, get_card_images

lvl = getattr(settings, "LOG_LEVEL", logging.DEBUG)
logging.basicConfig(level=lvl)


@ensure_csrf_cookie
def homepage(request):
    context = {}
    if request.method == "POST":
        Deck.objects.all().delete()
        Params.objects.all().delete()
        Cards.objects.all().delete()

        params = ParamsForm(request.POST).save()

        for i in card_generator(request.POST["deck"]):
            if i == "":
                continue

            Deck.objects.create(
                quantity=get_quantity(i),
                name=get_name(i),
                set_code=get_set_code(i),
                collector_number=get_collector_number(i),
            )

        cards = get_cards(Deck.objects.all(), params)

        for card in cards:
            Cards.objects.create(card=card)

        card_images = get_card_images(cards, "normal")
        context = {
            "deck_form": DeckForm(),
            "params_form": ParamsForm(),
            "card_images": card_images,
        }
    else:
        context = {"deck_form": DeckForm(), "params_form": ParamsForm()}

    return render(request, "homepage.html", context=context)


def preparing_images(request):
    create_pages(Deck.objects.all())
    response = HttpResponse()


def card_generator(deck_list):
    prevnl = -1
    while True:
        nextnl = deck_list.find("\n", prevnl + 1)
        if nextnl < 0:
            yield deck_list[prevnl + 1 :]
            break
        yield deck_list[prevnl + 1 : nextnl].replace("\r", "")
        prevnl = nextnl


def get_quantity(card_info):
    return re.findall(r"[0-9]+", card_info)[0]


def get_name(card_info):
    return re.findall(r"(?<=[0-9]\s)(.+)(?=\s\()", card_info)[0]


def get_set_code(card_info):
    return re.findall(r"(?<=\()(.+?)(?=\))", card_info)[0]


def get_collector_number(card_info):
    return re.findall(r"(?<=\)\s)(.*)", card_info)[0]
