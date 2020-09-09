from FormattedText import merge_pages, svg_to_text
from TableNames import tables_to_remove

# A script to parse the rules from SVG files (one per page).

merged_content = []
for page_number in range(1, 404):
    current_page = svg_to_text('{}.svg'.format(page_number))
    merged_content = merge_pages(merged_content, current_page)

indices_to_remove = []

for i in range(1, len(merged_content)):
    if merged_content[i].size == 37:
        if merged_content[i-1].text in tables_to_remove:
            indices_to_remove += [i-1, i]

for index in sorted(indices_to_remove, reverse=True):
    del merged_content[index]

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

for title, text in articles.items():
    print(title)
    print('------------')
    print(text)
    print()
    print('============================================')
    print()
