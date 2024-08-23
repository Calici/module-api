from datetime import datetime
import pytz

def get_current_time():
    return datetime.now(tz=pytz.timezone('Asia/Seoul'))

def get_original_time():
    return datetime(1970,1,1,tzinfo=pytz.timezone('Asia/Seoul'))

def random_string(
    length: int, b_upper: bool = True, b_lower: bool = True, b_number: bool = True, b_special_characters: bool = False
):
    """Generate random string

    Args:
        length (int):
        b_upper (bool, optional): Defaults to True.
        b_lower (bool, optional): Defaults to True.
        b_number (bool, optional): Defaults to True.
        b_special_characters (bool, optional): Defaults to False.

    Raises:
        ValueError:

    Returns:
        str:
    """
    import random
    import string
    letters = ""
    if b_upper:
        letters += string.ascii_uppercase
    if b_lower:
        letters += string.ascii_lowercase
    if b_number:
        letters += string.digits
    if b_special_characters:
        letters += string.punctuation

    if not letters:
        raise ValueError("Must be select one type character")

    return ''.join(random.choice(letters) for _ in range(length))
