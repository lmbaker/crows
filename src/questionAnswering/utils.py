def make_substring_bold(full_string, substring):
    '''Given a string and a substring from this string, return the string with
    bold formatting (by HTML tags) applied to the substring.

    Throws a ValueError if the substring is not found.

    full_string: str
    substring: str
    return: str
    '''

    substring_start_idx = str.find(full_string, substring)

    if substring_start_idx == -1:
        error_msg = "Expected string '{}' to occur in '{}', but not found."
        raise ValueError(error_msg.format(substring, full_string))

    string_beginning = full_string[:substring_start_idx]
    string_end = full_string[substring_start_idx + len(substring):]

    return string_beginning + '<b>' + substring + '</b>' + string_end
