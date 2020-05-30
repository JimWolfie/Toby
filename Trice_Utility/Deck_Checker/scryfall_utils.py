import time

import json
import requests
from word2number import w2n


class ScryfallCache:
    def __init__(self, cache_location="scryfall_cache.json"):
        self.last_query_time = 0
        self.cache_location = cache_location

        try:
            with open(cache_location, "r", encoding="utf-8") as cache_file:
                self.cache = json.load(cache_file)
        except IOError:
            self.cache = dict()
            print("cache file doesn't exist, initializing...")
            with open(cache_location, "w", encoding="utf-8") as cache_file:
                json.dump(self.cache, cache_file)

    def get_card_data(self, card_name):
        """
        Returns the card_data dictionary associated with card_name.

        If the card_name is not in the cache, we query Scryfall.
        """
        if card_name in self.cache:
            return self.cache[card_name]
        else:
            while time.time() - self.last_query_time < 0.05:
                time.sleep(0.05)

            response = requests.get(
                "https://api.scryfall.com/cards/named?exact="
                + card_name.replace(" ", "+").replace("û", "u")
            ).json()

            if not response["object"] == "card":
                raise ValueError(
                    "Could not find {} in Scryfall database".format(card_name)
                )

            self.last_query_time = time.time()
            self.cache[card_name] = response

            with open(self.cache_location, "w", encoding="utf-8") as cache_file:
                json.dump(self.cache, cache_file)

            return response


scryfall_cache = ScryfallCache()


##
# helper functions to parse the scryfall json:


def get_oracle_text(card_data):
    try:
        return card_data["oracle_text"]
    except KeyError:
        faces = card_data["card_faces"]
        oracle_text = ""
        for face in faces:
            oracle_text = " // ".join([oracle_text, face["oracle_text"]])
        return oracle_text


def can_be_commander(card_data):
    """checks whether a card can be a commander"""
    type_line = card_data["type_line"].lower()
    oracle_text = get_oracle_text(card_data).lower()
    if "legendary" in type_line and "creature" in type_line:
        return True
    if "can be your commander" in oracle_text:
        return True
    return False


def get_color_id(card_data):
    """Retrieves color identity info from Scryfall's card json"""
    return set(card_data["color_identity"])


def is_legal(card_data, tourney_format="commander"):
    """
    Checks if the card is legal in any number of copies to play in FORMAT
    (this includes restricted cards.)
    """
    return card_data["legalities"][tourney_format] in {"legal", "restricted"}


def is_in_unset(card_data):
    """Returns true if the card represented by card_data is in an unset """
    return card_data["set_type"] == "funny"


def legal_number(card_data, tourney_format="commander", is_singleton=True):
    """
    finds the maximum number of copies the given card is legal to play in format
    """
    try:
        oracle_text = get_oracle_text(card_data)
        if "A deck can have" in oracle_text:
            number = (
                oracle_text.split("A deck can have")[1].strip().split(" ")[0]
            )
            if number == "any":
                return float("inf")
            try:
                number = (
                    oracle_text.split("A deck can have up to")[1]
                    .strip()
                    .split(" ")[0]
                )
                return w2n.word_to_num(number)
            except ValueError:
                print(
                    "Could not parse maximum legal number of copies in deck"
                    + "on {} assuming default number".format(card_data["name"])
                )
    except KeyError:
        print(card_data["name"])

    if "basic" in card_data["type_line"].lower():
        return float("inf")
    if is_singleton:
        return 1
    if (
        format == "vintage"
        and card_data["legalities"][tourney_format] == "restricted"
    ):
        return 1
    return 4


def legal_in_color_id(card_data, color_id):
    """
    Returns true if the card represented by card_data is legal inside of
    color_id.
    """
    card_id = get_color_id(card_data)
    return card_id.issubset(color_id)


def card_ok(
    card_data,
    count,
    tourney_format="commander",
    has_color_id=True,
    color_id=None,
):
    """
    checks if the card and number it's played in is legal
    """
    if color_id is None:
        color_id = set("WUBRG")

    if has_color_id:  # format has color id rules
        if not legal_in_color_id(card_data, color_id):
            raise ValueError(
                "Color Identity Issue: {} has color identity of {}"
                "and can thus not be played in a {} {} deck".format(
                    card_data["name"],
                    get_color_id(card_data),
                    color_id,
                    tourney_format,
                )
            )
    max_count = legal_number(card_data)
    if count > max_count:
        raise ValueError(
            "Deck Issue: {} copies of {}"
            "is more than the allowed {} in {}".format(
                count, card_data["name"], max_count, tourney_format
            )
        )
    if not is_legal(card_data, tourney_format):
        raise ValueError(
            "Deck Issue: {} is not legal (or restricted) in {}".format(
                card_data["name"], tourney_format
            )
        )

    return True
