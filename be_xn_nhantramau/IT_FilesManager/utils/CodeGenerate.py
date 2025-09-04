import random
import string
from datetime import datetime


def GenerateCodeRoom():
    code = (
        datetime.now().strftime("%Y%m%d%H%M%S") + f"{random.randint(1, 99)}"
    ) + f"{random.choice(string.ascii_lowercase)}"
    return code


def GenerateCodeThanhVien(id):
    code = "TV/" + datetime.now().strftime("%Y") + f"/{id}"
    return code
