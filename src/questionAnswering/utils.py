import os


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


def create_absolute_path(script_dir, other_path):
    """
    script_dir is the result of os.dirname(__file__) in the script using the
    file.
    other_path should be a path relative to the root directory of this
    repository.
    """
    relative_path = os.path.join(script_dir,
                                 '..{}..'.format(os.sep),
                                 other_path)
    return os.path.abspath(relative_path)
