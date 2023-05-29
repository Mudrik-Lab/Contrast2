def cast_as_boolean(val: bool | str | int):
    if isinstance(val, str):
        if val in ["true", "True"]:
            return True
        else:
            return False
    return bool(val)