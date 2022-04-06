from typing import Dict


def safe_chained_dict_get(d_obj: Dict, *args):
    """
    Return None if any link is missing on the chain, otherwise the final val
    """
    i = 0
    while i < len(args):
        d_obj = d_obj.get(args[i])
        if d_obj is None:
            return None
        i += 1
    return d_obj
