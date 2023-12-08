
def get_value_To_string(logValue):
    if type(logValue) is float \
       or type(logValue) is int \
       or type(logValue) is complex:
        return str(logValue)

    elif type(logValue) is str:
        return f'''"{logValue}"'''


def remove_case_append(string):
    return string.replace("case:", "")


def check_if_string_is_not_None(string):
    return string != "nan" and string is not None
