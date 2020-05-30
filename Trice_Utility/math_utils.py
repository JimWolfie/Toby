import string

conv_dict = {
    int(c, 32): c for c in (string.digits + string.ascii_lowercase)[:32]
}  # convert from integer to base32hex symbols


def number_to_base(n, b):
    """Converts a number in base 10 to base b"""
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def count_dict(to_count: dict):
    count = 0
    for item in to_count:
        count += to_count[item]

    return count
