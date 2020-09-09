from functools import partial
import pytest

from svgParsing.formatted_text import FormattedText

no_space_cases = [('T', 'winned'),
                  ('Half', '-'),
                  ('-', 'Orc'),
                  ('-', 'orc'),
                  ('abc ', 'Abc'),
                  ('abc', ' Abc'),
                  ('Ins', 'ight'),
                  ('10', '-'),
                  ('G', 'M'),
                  ('', 'x'),
                  ('x', ''),
                  ('x', '.'),
                  ]

space_cases = [('Story', 'Work'),
               ('abc.', 'Abc'),
               ('dice:', '1d8'),
               ('1', 'word'),
               ('word', '1'),
               ]

bold_word = FormattedText('bold', color='#000000', size=42, bold=True)
bold_upper_word = FormattedText('Bold', color='#000000', size=42, bold=True)
bold_word_sp = FormattedText('bold ', color='#000000', size=42, bold=True)
italic_word = FormattedText('italic', color='#000000', size=42, italic=True)
plain_word = FormattedText('plain', color='#000000', size=42)

special_no_space_cases = [(bold_word_sp, plain_word),
                          (bold_word_sp, bold_word)]

special_space_cases = [(bold_word, plain_word),
                       (bold_word, italic_word),
                       (bold_word, bold_upper_word),
                       (plain_word, bold_word),
                       (italic_word, plain_word),
                       ]

# Helper function, in case the arguments to FormattedText change. Generates a
# FormattedText instance where the only changing input is the text.
formatted_text_fn = partial(FormattedText, color='#000000', size=42)


@pytest.mark.parametrize("text_1, text_2", no_space_cases)
def test_merge_no_space(text_1, text_2):
    formatted_text_1 = formatted_text_fn(text_1)
    formatted_text_2 = formatted_text_fn(text_2)
    expected = text_1 + text_2
    assert formatted_text_1.merge(formatted_text_2).text == expected


@pytest.mark.parametrize("text_1, text_2", space_cases)
def test_merge_add_space(text_1, text_2):
    formatted_text_1 = formatted_text_fn(text_1)
    formatted_text_2 = formatted_text_fn(text_2)
    expected = text_1 + ' ' + text_2
    assert formatted_text_1.merge(formatted_text_2).text == expected


@pytest.mark.parametrize("form_text_1, form_text_2", special_no_space_cases)
def test_merge_special_no_space(form_text_1, form_text_2):
    expected = form_text_1.text + form_text_2.text
    assert form_text_1.merge(form_text_2).text == expected


@pytest.mark.parametrize("form_text_1, form_text_2", special_space_cases)
def test_merge_special_space(form_text_1, form_text_2):
    expected = form_text_1.text + ' ' + form_text_2.text
    assert form_text_1.merge(form_text_2).text == expected
