from collections import defaultdict, namedtuple
import glob
import hashlib
import itertools
import os
import xml.etree.ElementTree as ET
from .math_utils import number_to_base, conv_dict
import scryfall_utils
scryfall_cache = scryfall_utils.ScryfallCache()

# CHANGE TO THE FORMAT BEING PLAYED
tourney_format = "commander"

# CHANGE THESE TO THE CORRECT ONES
output_file = "output.txt"
cod_folder = "Trice Tourney Utitility\decks"  # folder containing player folders containing cod files

Deck = namedtuple("Deck", "Maindeck Sideboard")


def get_new_deck():
    main, side = defaultdict(lambda: 0), defaultdict(lambda: 0)
    return Deck(main, side)


def combine_main_side(main, side):
    combined = main.copy()
    for card in side:
        combined[card] += side[card]
    return combined


def convert_deck_to_deck_str(deck: Deck):
    """Converts a Deck namedtuple into semicolon-delineated deck string."""
    main, side = deck
    deck_str = []

    for card_name in main:
        for _ in range(main[card_name]):
            deck_str.append(card_name.lower().split("(")[0].strip())
    for card_name in side:
        for _ in range(side[card_name]):
            deck_str.append("SB:" + card_name.lower().split("(")[0].strip())

    deck_str.sort()
    return ";".join(deck_str)


def trice_hash(deck_str: str):
    """Converts a semicolon-delineated deck string into a hash."""
    m = hashlib.sha1()
    m.update(deck_str.encode("utf-8"))
    hashed_deck = m.digest()
    hashed_deck = (
        (hashed_deck[0] << 32)
        + (hashed_deck[1] << 24)
        + (hashed_deck[2] << 16)
        + (hashed_deck[3] << 8)
        + (hashed_deck[4])
    )
    processed_hash = number_to_base(hashed_deck, 32)
    return "".join([conv_dict[i] for i in processed_hash])


def convert_to_deck(cod_file) -> Deck:
    """
    Converts an .cod xml file object into a Deck namedtuple.
    """
    tree = ET.parse(cod_file)
    deck = get_new_deck()
    main, side = deck
    for zone in tree.findall("zone"):
        in_sideboard = zone.attrib["name"] == "side"

        for card in zone:
            count = int(card.attrib["number"])
            card_name = card.attrib["name"].split("(")[0].strip()

            if in_sideboard:
                side[card_name] += count
            else:
                main[card_name] += count

    return deck


##

"""
Methods for checking the legality of decks.
"""


def get_max_color_id(deck: Deck):
    """
    Returns a largest possible color_id for a commander deck - we search through
    the main deck and sideboard to find the legendary creature(s) with the
    largest color identity.

    Unfortunately, we don't handle "partner with"s correctly - we are treating
    them as if they said "partner".
    """
    partners = set()
    largest_id = set()

    main, side = deck
    for card_name in main:
        card_data = scryfall_cache.get_card_data(card_name.split("(")[0].strip())
        if scryfall_utils.can_be_commander(card_data):
            color_id = scryfall_utils.get_color_id(card_data)
            if len(color_id) > len(largest_id):
                largest_id = color_id

            if "partner" in scryfall_utils.get_oracle_text(card_data):
                partners.add(card_name.split("(")[0].strip())

    for card_name in side:
        card_data = scryfall_cache.get_card_data(card_name.split("(")[0].strip())
        if scryfall_utils.can_be_commander(card_data):
            color_id = scryfall_utils.get_color_id(card_data)
            if len(color_id) > len(largest_id):
                largest_id = color_id

            if "partner" in scryfall_utils.get_oracle_text(card_data):
                partners.add(card_name.split("(")[0].strip())

    for c1, c2 in itertools.combinations(partners, r=2):
        c1_data = scryfall_cache.get_card_data(c1)
        c2_data = scryfall_cache.get_card_data(c2)
        c1_colors = scryfall_utils.get_color_id(c1_data)
        c2_colors = scryfall_utils.get_color_id(c2_data)
        color_id = c1_colors.union(c2_colors)
        if len(color_id) > len(largest_id):
            largest_id = color_id

    return largest_id

def count_dict(to_count: dict):
    count = 0
    for item in to_count:
        count += to_count[item]
    return count

def check_deck_legality(deck: Deck, tourney_format: str = tourney_format):
    """
    In the Marchesa cEDH tournament, a deck is legal if
    - It has 100-101 cards, of which 98-100 are in main deck and 0-3 in sideboard
    - It has <= 1 cards illegal in commander, and that card is an unset card in the
        sideboard
    - It has no duplicates outside of Basic Lands, Rats, and Seven Dwarves
    """
    if tourney_format == "commander":
        main, side = deck
        main_count = count_dict(main)
        side_count = count_dict(side)

        # Check count
        if not (98 <= main_count <= 100):
            raise ValueError(
                "Number of cards in main ({}) is illegal".format(main_count)
            )
        if not (0 <= side_count <= 3):
            raise ValueError(
                "Number of cards in side ({}) is illegal".format(side_count)
            )
        if not (100 <= main_count + side_count <= 101):
            raise ValueError(
                "Total number of cards ({}) is illegal".format(
                    main_count + side_count
                )
            )

        max_color_id = get_max_color_id(deck)

        # check legality of cards
        combined = combine_main_side(main, side)

        has_uncard = False
        for card_name in combined:
            card_data = scryfall_cache.get_card_data(card_name.split("(")[0].strip())
            count = combined[card_name.split("(")[0].strip()]
            try:
                scryfall_utils.card_ok(
                    card_data,
                    count,
                    tourney_format=tourney_format,
                    has_color_id=True,
                    color_id=max_color_id,
                )
            except ValueError as err:
                if (
                    scryfall_utils.is_in_unset(card_data)
                    and not has_uncard
                    and count == 1
                    and card_name in side
                ):
                    # we allow one
                    has_uncard = True
                else:
                    raise err

    else:
        raise NotImplementedError(
            "Format {} is not supported".format(tourney_format)
        )

    return True


def getHash(file_location):
    try:
        with open(file_location) as deck_file:
            deck = convert_to_deck(file_location)
            check_deck_legality(deck, tourney_format=tourney_format)
            deck_str = convert_deck_to_deck_str(deck)
            return True, trice_hash(deck_str)
    except ValueError as err:
        return False, "Error: {}".format(err)


##
def process_decks():
    with open(output_file, "w+") as output:
        _, player_dirs, _ = next(os.walk(cod_folder))
        player_dirs.sort()

        for player_dir in player_dirs:
            print("Processing player {}...".format(player_dir))

            dir_path = os.path.join(cod_folder, player_dir)
            cod_files = glob.glob(os.path.join(dir_path, "*.cod"))

            output.write("@"+player_dir + "\n")

            for file_path in cod_files:
                with open(file_path) as cod_file:
                    try:
                        deck = convert_to_deck(file_path)
                        check_deck_legality(deck, tourney_format=tourney_format)
                        deck_str = convert_deck_to_deck_str(deck)
                        output.write("\t{}\n".format(trice_hash(deck_str)))
                    except ValueError as err:
                        output.write("\t{}\n".format(err))
                        print("Deck '{}' has error '{}'".format(file_path, err))