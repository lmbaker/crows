import os
import re
import xml.etree.ElementTree as ET

xml_namespace = {'svg': '{http://www.w3.org/2000/svg}'}
svg_directory = '/home/lauren/svg'


def parse_svg_tag(element):
    '''Elements from SVG files have tags that look like
    {http://www.w3.org/2000/svg}path, this method removes the curly braces and
    their contents.'''
    return re.sub('{.*}', '', element.tag)


def traverse_element_tree(root_element):
    '''For preorder traversal.

    element: Element
    '''
    yield root_element
    for child in root_element:
        yield from traverse_element_tree(child)


def svg_to_text(filename):
    '''Given an SVG filename representing a page of the 5e SRD, return a list
    of objects with text from the file.

    filename: str
    return: List[FormattedText]
    '''
    tree = ET.parse(os.path.join(svg_directory, filename))
    root = tree.getroot()
    top_g = root.find(xml_namespace['svg'] + 'g')

    gen = traverse_element_tree(top_g)
    text_list = []
    for element in gen:
        if parse_svg_tag(element) == 'text':
            # The method to create a FormattedText object returns None if there
            # is no text.
            text_object = FormattedText.from_text_element(element)
            if text_object:
                text_list.append(text_object)

    merged_text_list = []
    merge_text = text_list[0]
    for text in text_list[1:]:
        if merge_text.should_merge(text):
            merge_text = merge_text.merge(text)
        else:
            merged_text_list.append(merge_text)
            merge_text = text
    merged_text_list.append(merge_text)

    # Strip the footer and page number
    if ('Permission granted' in merged_text_list[0].text and
            'System Reference Document' in merged_text_list[2].text):
        if len(merged_text_list) == 2:
            # In case there is a blank page
            merged_text_list = []
        merged_text_list = merged_text_list[3:]

    # else:
    #    raise ValueError('Page found with no footer, this is unexpected.')
    return merged_text_list


def merge_pages(page_1, page_2):
    '''Combine two lists of FormattedText items. Check if the last element of
    the first list should be combined with the first element of the second
    list.

    page_1: List[FormattedText]
    page_2: List[FormattedText]
    return: List[FormattedText]
    '''
    if not page_1 or not page_2:
        merged = page_1 + page_2

    elif page_1[-1].should_merge(page_2[0]):
        # Protection if page 2 is a list with only one FormattedText item.
        if len(page_2) == 1:
            rest_of_page_2 = []
        else:
            rest_of_page_2 = page_2[1:]
        merged = page_1[:-1] + [page_1[-1].merge(page_2[0])] + rest_of_page_2

    else:
        merged = page_1 + page_2

    return merged


class FormattedText:

    def __init__(self, text, color, size, bold=False, italic=False):
        '''Constructor

        text: str
        color: str representing a hex color
        size: int font size
        '''

        self.text = text
        self.color = color
        self.size = size
        self.bold = bold
        self.italic = italic

    @classmethod
    def from_text_element(cls, element):
        '''Turn an Element into a FormattedText object, which has the text and
        various attributes for formatting details.

        element: Element
        return: FormattedText
        '''
        # Text style attributes look like:
        # "font-variant:normal;font-weight:600;font-size:75px"
        # font-weight can be bold or normal, font-style can be italic
        if parse_svg_tag(element) != 'text':
            raise ValueError(
                "from_text_element received an element with tag" +
                "'{}', should be 'text'".format(element.parse_svg_tag))

        # Check children for a tspan element
        child_element_tags = [parse_svg_tag(child) for child in element]
        tspan_instances = child_element_tags.count('tspan')
        if tspan_instances == 0:
            return None
        elif tspan_instances > 1:
            print(('Unexpected parsing condition - text grouping has multiple '
                   'tspan children.'))

        tspan_element = list(element)[child_element_tags.index('tspan')]

        # Harvest text style
        style_dict = {}
        for style_key_value in element.get('style').split(';'):
            style_key, style_value = style_key_value.split(':')
            style_dict[style_key] = style_value

        clean_text = cls.fix_text(tspan_element.text)
        text_color = style_dict['fill']  # a hex string preceeded by a '#'
        font_size = int(style_dict['font-size'][:-2])  # an integer
        text_bold = style_dict.get('font-weight') == 'bold'
        text_italic = style_dict.get('font-style') == 'italic'

        formatted_text = cls(clean_text,
                             text_color,
                             font_size,
                             text_bold,
                             text_italic)

        return formatted_text

    def should_merge(self, other_element):
        '''Determine if these two text objects should be combined.

        This method checks the font size and color and returns True if they
        match.

        other_element: Element
        return: bool
        '''
        if (self.size == other_element.size and
                self.color == other_element.color):
            return True
        else:
            return False

    def merge(self, other_element):
        '''Return a new FormattedText instance with the text from self and
        other_element.

        Note: bold and italic formatting will be lost with the current
        implementation of this method.

        other_element: Element
        return: FormattedText
        '''

        if (self.size != other_element.size or
                self.color != other_element.color):
            raise ValueError(
                ("Cannot merge provided text '{}' and '{}', different font "
                 "size or color.").format(self.text, other_element.text))

        # Sometimes one piece of text ends with a word, and the next piece
        # starts the next word, and there is no space in between. Other times,
        # one piece of text ends midway through a word, and the next one
        # finishes the word.
        # Add a space between the two pieces to join if the first ends with a
        # lowercase letter (and no newline) and the next starts with an
        # uppercase letter.
        if self.text == '' or other_element.text == '':
            # If a bold/italic phrase is merged with an empty text string, then
            # the bold/italic formatting should be kept, so that space will be
            # added before the following word.
            return FormattedText(self.text + other_element.text,
                                 self.color,
                                 self.size,
                                 (self.bold or other_element.bold),
                                 (self.italic or other_element.italic))

        use_space = False

        first_tail = self.text[-1]
        second_head = other_element.text[0]
        use_bold = False
        use_italic = False

        either_side_false = [' ', '-', '\n', '\t']

        if (first_tail in either_side_false + ['('] or
                second_head in either_side_false + [')', '.']):
            use_space = False

        elif (self.bold != other_element.bold or
                self.italic != other_element.italic):
            # When a non-bold phrase has a bold phrase merged onto the end, the
            # merged phrase needs to be marked as bold so that the subsequent
            # phrase will get a space before it.
            use_space = True
            use_bold = other_element.bold
            use_italic = other_element.italic

        elif first_tail.isalpha() and second_head.isalpha():
            if first_tail.islower() and second_head.isupper():
                use_space = True
            elif (len(self.text) >= 2 and self.text[-2].isupper() and
                    first_tail.isupper()):
                use_space = True
            else:
                use_space = False

        elif first_tail in ['.', ':']:
            use_space = True

        else:
            use_space = True

        if use_space:
            new_text = self.text + ' ' + other_element.text
        else:
            new_text = self.text + other_element.text

        return FormattedText(new_text,
                             self.color,
                             self.size,
                             use_bold,
                             use_italic)

    @staticmethod
    def fix_text(text):
        '''Apply hard-coded rules to clean up text (address tabs and newlines)

        text: str
        return: str'''

        if text == '\t':
            return ''
        else:
            return text.replace('\t', ' ')

    def __repr__(self):

        return '<{}> <{}> {}'.format(self.color, self.size, repr(self.text))
