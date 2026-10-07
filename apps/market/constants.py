"""Shared constants: units + month names."""
UNITS = [
    ("KG", "KG"),
    ("GRAM", "Gram"),
    ("LITRE", "Litre"),
    ("ML", "ML"),
    ("PACKET", "Packet"),
    ("PIECE", "Piece"),
    ("DOZEN", "Dozen"),
    ("BAG", "Bag"),
    ("BOTTLE", "Bottle"),
    ("BOX", "Box"),
    ("OTHER", "Other"),
]
UNIT_VALUES = [u[0] for u in UNITS]

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
