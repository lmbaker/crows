from svgParsing.formatted_text import merge_pages, svg_to_text
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

    articles = {}

    current_title = 'Introduction'
    current_article = ''

    for formatted_text in merged_content:
        if formatted_text.size == 108:
            articles[current_title] = current_article
            current_title = formatted_text.text
            current_article = ''
        else:
            current_article += formatted_text.text + '\n'

    articles[current_title] = current_article

    return articles
