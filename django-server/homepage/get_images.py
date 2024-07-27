from django.template.base import logging
import re
import json
import requests
import pathlib
import torch
import base64
from super_image import EdsrModel, ImageLoader
import io
from PIL import Image
import time
import urllib.request
import os
import glob
import random

from .params import Params as p


class Page:
    def __init__(self, card_width):
        self.card_width = card_width
        self.card_height = int(p.card_ratio * card_width)

        self.page_width = int(p.card_to_page_width_ratio * card_width)
        self.page_height = int(p.page_ratio * self.page_width)

        self.margin_w = int(p.margin_w_ratio * self.page_width)
        self.margin_top = int(p.margin_top_ratio * self.page_height)

        self.clear_page()

    def add_image_to_page(self, image):
        x = self.margin_w + self.current_col * (self.card_width + p.spacing)
        y = self.margin_top + self.current_row * (self.card_height + p.spacing)
        self.page.paste(image, (x, y))
        self.is_empty = False
        self.current_col += 1

        if self.current_col >= p.columns:
            self.current_col = 0
            self.current_row += 1

        if self.current_row >= p.rows:
            self.is_full = True

    def save_page(self, filename):
        self.page.save(filename)

    def clear_page(self):
        self.page = Image.new(
            "RGBA", (self.page_width, self.page_height), (255, 255, 255, 255)
        )
        self.is_empty = True
        self.is_full = False
        self.has_back = False
        self.current_row = 0
        self.current_col = 0


BASIC_LANDS = ["island", "mountain", "forest", "plains", "swamp", "wastes"]
CARD_WIDTHS = {"png": 745, "large": 672, "normal": 488, "small": 146}
SCRYFALL_REQUEST_SIZE_LIMIT = 75


"""
def main():
    clear_image_folder()
    cards = get_cards()
    create_pages(cards)
"""


# Helper function to clear images from a previous run
def clear_image_folder():
    files = glob.glob("../images/*")
    for f in files:
        os.remove(f)


# Returns list of json objects containing card information for each card
# in the deck. If random_basic_land_art is enabled, the basic lands will
# go through a seperate process.
def get_cards(deck, params):
    reqs = []
    identifiers = []
    basic_lands = []
    for card in deck:
        # Instead of using the set code and collecter number from the deck,
        # basic lands will be randomised.

        if params.random_basic_land_art:
            if card.name.lower() in BASIC_LANDS:
                basic_lands.append(get_basic_lands(card.name, card.quantity, params))
                continue

        for _ in range(card.quantity):
            identifiers.append(
                {"set": card.set_code, "collector_number": card.collector_number}
            )

            if len(identifiers) == SCRYFALL_REQUEST_SIZE_LIMIT:
                reqs.append({"identifiers": identifiers})
                identifiers = []

    if identifiers != []:
        reqs.append({"identifiers": identifiers})

    url = "https://api.scryfall.com/cards/collection"
    responses = []

    for req in reqs:
        try:
            responses.append(requests.post(url, json=req).json()["data"])
        except KeyError:
            raise Exception(req)

        time.sleep(0.1)

    if p.random_basic_land_art:
        responses.append(flatten_list(basic_lands))

    return flatten_list(responses)


def flatten_list(nested_list):
    return [i for j in nested_list for i in j]


# If random_basic_land_art is True then instead of fetching a specific land
# this fetches all versions of the land and randomly chooses from them
def get_basic_lands(land, quantity, params):
    basic_lands = []
    url = f"https://api.scryfall.com/cards/search?q=!%22{land}%22+unique%3Aprints"

    response = requests.get(url).json()

    land_uris = search_basic_land_pages(response, [], params)
    if quantity > len(land_uris):
        print(
            f"Not enough different land arts for {land}! Duplicate lands will be enabled."
        )
        allow_dup = True
    else:
        allow_dup = params.allow_duplicate_basic_lands

    for _ in range(quantity):
        basic_lands.append(random.choice(land_uris))
        try:
            if not allow_dup:
                land_uris.remove(basic_lands[-1])
        except IndexError:
            print(
                f"Not enough different land arts for {land}! Consider allowing duplicate lands or allowing non-full card art"
            )

    return basic_lands


# basic lands tend to be pagified since there are so many of them.
# This recursive function goes through each page.
def search_basic_land_pages(response, land_uris, params):
    if response["has_more"]:
        time.sleep(0.1)
        land_uris = search_basic_land_pages(
            requests.get(response["next_page"]).json(), land_uris, params
        )

    for card in response["data"]:
        if not p.allow_foils and card["nonfoil"] is False:
            continue
        if card["lang"] != p.card_lang:
            continue
        if params.only_full_art_basic_lands:
            if card["full_art"]:
                land_uris.append(card)
        else:
            land_uris.append(card)

    return land_uris


def get_card_images(cards, quality):
    images = []
    for card in cards:
        if card["layout"] == "normal" or card["layout"] == "adventure":
            images.append(card["image_uris"][quality])
        else:
            images.append(card["card_faces"][0]["image_uris"][quality])
            images.append(card["card_faces"][1]["image_uris"][quality])
    return images


# Place card images in a page for printing. Page ratios are set so that
# printing onto a a4 page will result in realistic size cards.
def create_pages(cards):
    if p.upscale_images:
        scale = 2
    else:
        scale = 1
    page = Page(CARD_WIDTHS[p.card_quality] * scale)
    back = Page(CARD_WIDTHS[p.card_quality] * scale)

    page_count = 0

    for card in cards:
        start = time.time()

        add_card(card, page, back)
        if page.is_full:
            page_count += 1
            save_pages(page, back, page_count)

        print(time.time() - start)

    if not page.is_empty:
        save_pages(page, back, page_count + 1)


def save_pages(page, back, name):
    page.save_page(f"../images/{name}.png")

    if page.has_back:
        back.save_page(f"../images/{name}_back.png")

    back.clear_page()
    page.clear_page()


# Add card to page, also adds the backside of the card to a seperate
# page if applicable, for double sided cards for example.
def add_card(card_object, page, back):
    if card_object["layout"] == "normal":
        image_uri = card_object["image_uris"][p.card_quality]
        image = requests.get(image_uri, stream=True)
        image.raw.decode_content = True

        if p.upscale_images:
            image = upscale_image(Image.open(image.raw))
        else:
            image = Image.open(image.raw)

        page.add_image_to_page(image)

    else:
        image_uri = card_object["card_faces"][0]["image_uris"][p.card_quality]
        image = urllib.request.urlopen(image_uri).read()

        if p.upscale_images:
            image = upscale_image(Image.open(io.BytesIO(image)))
        else:
            image = Image.open(io.BytesIO(image))

        image_uri = card_object["card_faces"][1]["image_uris"][p.card_quality]
        image_back = urllib.request.urlopen(image_uri).read()

        if p.upscale_images:
            image_back = upscale_image(Image.open(io.BytesIO(image_back)))
        else:
            image_back = Image.open(io.BytesIO(image_back))

        back.current_row = page.current_row
        back.current_col = p.columns - 1 - page.current_col

        page.add_image_to_page(image)
        back.add_image_to_page(image_back)

        page.has_back = True


# Doubles the resolution of the card for extra detail.
def upscale_image(image):
    model = EdsrModel.from_pretrained("eugenesiow/edsr-base", scale=2)
    inputs = ImageLoader.load_image(image)

    torch.cuda.empty_cache()

    scaled = model(inputs)

    ImageLoader.save_image(scaled, "../images/tmp.png")
    image = Image.open("../images/tmp.png")
    pathlib.Path("../images/tmp.png").unlink()

    return image
