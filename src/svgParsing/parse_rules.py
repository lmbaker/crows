import re

from svgParsing.formatted_text import merge_pages, svg_to_text, FormattedText
from svgParsing.table_names import tables_to_remove

# A function to parse the rules from SVG files (one per page).

def generate_srd_articles():
    ''' Parse the svg files created from the SRD, into a dictionary of
    articles. Each article has a title and its corresponding text.

    return: Dict[str, str]
    '''

    # Read the svg file for each page, and generate a list of FormattedText objects
    # representing all text in the SRD. This loop handles 'smoothing out' the page
    # breaks.
    merged_content = []
    for page_number in range(1, 404):
        current_page = svg_to_text('{}.svg'.format(page_number))
        merged_content = merge_pages(merged_content, current_page)

    # Identify tables using their font size. Treat the title of the table as the
    # previous FormattedText object in the list. Remove tables if the title is in
    # the tables_to_remove list.

    indices_to_remove = []

    for i in range(1, len(merged_content)):
        if merged_content[i].size == 37:
            if merged_content[i-1].text in tables_to_remove:
                indices_to_remove += [i-1, i]

    for index in sorted(indices_to_remove, reverse=True):
        del merged_content[index]

    # Split the list of FormattedText objects up, using text at size 108 as the
    # start of a 'new article.' Extract the text from the FormattedText objects.

    # [ [<list of conditions for higher-font titles>, <list of lower-font headers to split on> ]
    rules = [
        [["^Races$", 108], [[".*", 75]]],
        [["^Beyond 1st Level$", 108], [[".*", 75]]],
        [["^Using Ability Scores$", 108], [[".*", 75]]],
        [["^Spellcasting$", 108], [[".*", 75]]],
        [["^Spell Descriptions$", 75], [[".*", 50]]],
        [["^Magic Items A-Z$", 75], [[".*", 50]]],
        [["^Monsters$", 108], [["^Monsters \(.*", 75]]],
        [["^Monsters \(.*", 75], [[".*", 58], [".*", 50]]],
    ]

    # one absolute of this system - no text will be added to an article if the text font size is larger than the article title font size.

    def check_text_matches_rule(formText, rule):
        '''Check a FormattedText object against a rule for starting a new article.

        formText: FormattedText The text to match against the rule.
        rule: List[str, int] A pattern and a font size to match text against.
        '''
        #import pdb;pdb.set_trace()
        if formText.size != rule[1]:
            return False
        if re.match(rule[0], formText.text):
            return True
        else:
            return False

    articles = {}
    cur_larger_font_titles = [['Introduction', 108]]
    current_title = 'Introduction'
    current_article = ''

    for formatted_text in merged_content:
        #if formatted_text.text == "Spell Descriptions":
        #    import pdb;pdb.set_trace()
        if formatted_text.size == 108:
            cur_larger_font_titles = [[formatted_text.text, 108]]

            # make new article
            articles[current_title] = current_article
            current_title = formatted_text.text
            current_article = ''
            continue

        # if text size any 'larger font title', then remove larger title(s), and make the current piece of text a new article title.
        # I believe with this code, the list of cur_larger_font_titles will be sorted by font size in descending order.
        create_new_article_by_font_size = False

        while len(cur_larger_font_titles) and formatted_text.size >= cur_larger_font_titles[-1][1]:
            create_new_article_by_font_size = True
            cur_larger_font_titles = cur_larger_font_titles[:-1]

        if create_new_article_by_font_size:
            articles[current_title] = current_article
            current_title = formatted_text.text
            current_article = ''
            cur_larger_font_titles.append([current_title, formatted_text.size])
            continue

        # If text matches a rule for the smallest 'larger font title', then make a new article.
        create_new_article_by_formatting_rules = False
        if formatted_text.size >= 50: # Don't do these looping checks for pieces of text that are too small for any of the rules to turn into a header.
            for title in cur_larger_font_titles:
                for condition_rule_pair in rules:
                    #print(condition_rule_pair, title)
                    if check_text_matches_rule(FormattedText(title[0], '#000000', title[1]), condition_rule_pair[0]):
                        for rule in condition_rule_pair[1]:
                            if check_text_matches_rule(formatted_text, rule):
                                create_new_article_by_formatting_rules = True
        if create_new_article_by_formatting_rules:
            cur_larger_font_titles.append([formatted_text.text, formatted_text.size])
            articles[current_title] = current_article
            current_title = formatted_text.text
            current_article = ''
            continue

        current_article += formatted_text.text + '\n'

    articles[current_title] = current_article

    return articles
