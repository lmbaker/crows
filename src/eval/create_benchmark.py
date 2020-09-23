import os
import json

def convert_txt_to_squad_json(documents_dir, filename):
    '''Read an article given as a .txt file, and create a SQuAD json file,
    with no questions added yet. A .json file is created in the same
    directory as the .txt file, with the same filename.

    documents_dir: str The path to the directory with the .txt file.
    filename: str The name of the .txt file (with the extension).
    '''
    with open(os.path.join(documents_dir, filename)) as f:
        file = f.read()

    file_paragraphs = file.split('\n')
    file_paragraphs = [f for f in file_paragraphs if len(f) > 30]

    title = filename.split('.')[0]

    squad_paragraphs = [{'context': p, 'qas': []} for p in file_paragraphs]

    squad_data = {'data': [{'title': title, 'paragraphs': squad_paragraphs}]}

    with open(os.path.join(documents_dir, title + '.json'), 'w') as f:
        json.dump(squad_data, f)

def convert_articles_json_to_squad_json(documents_dir, filename):
    '''Read a dict of (title, text) pairs and create a SQuAD json file,
    with no questions added yet. The SQuAD file is created in the same
    directory as the first .json file, with '_squad' appended to the
    file name.

    documents_dir: str The path to the directory with the file of articles.
    filename: str The name of the .json file (with the extension).
    '''
    with open(os.path.join(documents_dir, filename)) as f:
        articles_dict = json.load(f)

    squad_data = {'data': []}

    file_title = filename.split('.')[0]

    for title, text in articles_dict.items():
        file_paragraphs = text.split('\n')
        file_paragraphs = [f for f in file_paragraphs if len(f) > 30]

        squad_paragraphs = [{'context': p, 'qas': []} for p in file_paragraphs]
        squad_data['data'].append({'title': title,
                                   'paragraphs': squad_paragraphs})

    with open(os.path.join(documents_dir,
                           file_title + '_squad.json'), 'w') as f:
        json.dump(squad_data, f)


def fix_filename(file_dir, filename):
    '''Make the given filename unique in the directory by adding a suffix if
    needed. Made to avoid overwriting files.

    file_dir: str
    filename: str, should end with a file extension.
    return: str
    '''
    if '.' not in filename:
        msg = ("Expected the filename to contain a '.' to show a file"
               "extension, got '{}'.")
        raise ValueError(msg.format(filename))
    filename_parts = filename.split('.')
    filename_no_extension = '.'.join(filename_parts[:-1])
    file_extension = '.' + filename_parts[-1]
    if not os.path.exists(os.path.join(file_dir, filename)):
        return filename
    unique_suffix = 1
    while os.path.exists(os.path.join(file_dir,
                                      (filename_no_extension +
                                       str(unique_suffix) +
                                       file_extension))):
        unique_suffix += 1
    return filename_no_extension + str(unique_suffix) + file_extension

def find_sentence(sentence, squad_data, article_title=''):
    '''Find the given sentence in a squad data file.

    sentence: str A sentence to identify.
    squad_data: Dict A squad dataset.
    article_title: Optional[str] An article to look in; ignore other articles.
    return: Optional[Dict], Optional[str] Returns a paragraph dict and the
        article title matching the paragraph, or None if sentence not found.
    '''

    #TODO verify the squad_data dict follows the right structure.
    article_titles = [article['title'] for article in squad_data['data']]

    # Raise a ValueError if the given article title is not in the SQuAD data.
    if article_title and article_title not in article_titles:
        raise ValueError("Unknown article title '{}'".format(article_title))

    # Run a filter over the articles, if a title is given, to find matching
    # article(s). Otherwise, just use a dummy filter.
    if article_title:
        filter_fn = lambda x: x['title'] == article_title
    else:
        filter_fn = lambda x: x
    articles_matching_title = filter(filter_fn, squad_data['data'])

    paragraphs_matching_sentence = []
    paragraph_article_titles = []
    for article in articles_matching_title:
        for paragraph in article['paragraphs']:
            if sentence in paragraph['context']:
                paragraphs_matching_sentence.append(paragraph)
                paragraph_article_titles.append(article['title'])

    if len(paragraphs_matching_sentence) > 1:
        raise ValueError('More than one matching paragraph found.')

    if len(paragraphs_matching_sentence) == 0:
        raise ValueError('No matching paragraph found.')

    return paragraphs_matching_sentence[0], paragraph_article_titles[0]

def add_question(question, answers, paragraph_dict, article_title):
    '''Add a question to the given paragraph.

    Make sure this question is unique, and verify that the 'answer_text' and
    'answer_start' match the contents of the paragraph for each answer. This
    function creates a hashed ID using the question and article title.

    question: str The question to answer.
    answers: List[Dict[str, str]] The answers, as written in the SQuAD format.
    paragraph_dict: Dict A dictionary, in the SQuAD format.
    article_title: str The article title, used for hashing to create the
        question ID.
    '''
    # Check that the question is unique.
    existing_questions = [q['question'] for q in paragraph_dict['qas']]
    if question in existing_questions:
        msg = "Question '{}' not unique in paragraph."
        raise ValueError(msg.format(question))

    # Check that the paragraph text at answer_start matches answer_text
    # for each answer.
    for answer_dict in answers:
        answer_start = answer_dict['answer_start']
        answer_text = answer_dict['answer_text']
        para_text = paragraph_dict['context']

        if len(para_text) < answer_start + len(answer_text):
            msg = "Answer '{}' starting at {} can't fit in paragraph."
            raise ValueError(msg.format(answer_text, answer_start))

        answer_in_para = paragraph_dict['context'][
            answer_start : answer_start + len(answer_text)]

        if answer_text != answer_in_para:
            msg = ("Answer '{}' doesn't match '{}' in paragraph"
                   "using answer_start '{}'")
            raise ValueError(msg.format(answer_text,
                                        answer_in_para,
                                        answer_start))

    question_dict = {'answers': answers,
                     'id': str(hash(question + article_title)),
                     'question': question,
                     'is_impossible': False}

    paragraph_dict['qas'].append(question_dict)

def json_from_filename(documents_dir, file_title):
    '''Read in json data from a json file.
    documents_dir: str The path to the directory containing the file.

    file_title: str The filename without the .json suffix.
    return: Dict The contents of the json file.
    '''
    filename = '{}.json'.format(file_title)

    with open(os.path.join(documents_dir, filename)) as f:
        starting_squad_data = json.load(f)
    return starting_squad_data

def combine_squad_files(file1, file2):
    '''Add the articles in file2 to file1. Both files are in SQuAD format.

    file1: Dict SQuAD file, which file2 will be merged into.
    file2: Dict SQuAD file to merge in.
    '''
    #articles_in_file2 = [article['title'] for article in file2['data']]
    articles_in_file1 = [article['title'] for article in file1['data']]
    for article in file2['data']:
        if article['title'] in articles_in_file1:
            msg = "Warning - article title '{}' in two files."
            print(msg.format(article['title']))
        else:
            file1['data'].append(article)

documents_dir = '../../data/documents-dd2e8b2'

'''
for filename in ['races.txt', 'barbarian.txt', 'bard.txt', 'cleric.txt']:
    convert_txt_to_squad_json(documents_dir, filename)

file_title = 'races'
starting_squad_data = json_from_filename(documents_dir, file_title)
other_squad_data = json_from_filename(documents_dir, 'barbarian')
combine_squad_files(starting_squad_data, other_squad_data)
other_squad_data = json_from_filename(documents_dir, 'bard')
combine_squad_files(starting_squad_data, other_squad_data)
other_squad_data = json_from_filename(documents_dir, 'cleric')
combine_squad_files(starting_squad_data, other_squad_data)
'''

# template:
'''
para, article_title = find_sentence("", starting_squad_data, article_title=)
add_question("", [{'answer_start': , 'answer_text': ""}], para, article_title)
'''

convert_articles_json_to_squad_json(documents_dir, 'srd_articles.json')
starting_squad_data = json_from_filename(documents_dir, 'srd_articles_squad')

file_title = 'Races'
para, article_title = find_sentence('Dwarven Resilience. You have advantage on saving throws against poison, and you have resistance against poison damage', starting_squad_data, article_title=file_title)
add_question('What weapons can dwarves use?', [{'answer_start': 1181, 'answer_text': 'battleaxe, handaxe, light hammer, and warhammer'}], para, article_title)
add_question('At what age are dwarves thought of as adults?', [{'answer_start': 264, 'answer_text': '50'}], para, article_title)
add_question('How long do dwarves live?', [{'answer_start': 296, 'answer_text': '350 years'}], para, article_title)

para, article_title = find_sentence('Your draconic ancestry determines the size, shape, and damage type of the exhalation.', starting_squad_data, article_title=file_title)
add_question("What is the DC for the saving throw on a dragonborn's breath weapon?", [{'answer_start': 559, 'answer_text': '8 + your Constitution modifier + your proficiency bonus'}], para, article_title)

para, article_title = find_sentence('Gnomes are between 3 and 4 feet tall and average about 40 pounds.', starting_squad_data, article_title=file_title)
add_question("How tall is a gnome?", [{'answer_start': 641, 'answer_text': 'between 3 and 4 feet'}], para, article_title)

para, article_title = find_sentence('Your Strength score increases by 2, and your Constitution score increases by 1.', starting_squad_data, article_title=file_title)
add_question("Which character race has increased Strength and Constitution?", [{'answer_start': 5, 'answer_text': 'half-orc'}], para, article_title)
add_question("Which skill are half-orcs proficient in?", [{'answer_start': 1018, 'answer_text': 'Intimidation'}], para, article_title)

file_title = 'Barbarian'
para, article_title = find_sentence('Hit Dice: 1d12 per barbarian level Hit Points at 1st Level: 12 + your Constitution modifier', starting_squad_data, article_title=file_title)
add_question('How many hit points does a barbarian have at first level?', [{'answer_start': 60, 'answer_text': '12 + your Constitution modifier'}], para, article_title)

file_title = 'Bard'
para, article_title = find_sentence('Once within the next 10 minutes, the creature can roll the die and add the number rolled to one ability check, attack roll, or saving throw it makes.', starting_squad_data, article_title=file_title)
add_question('What dice rolls can bardic inspiration be used on?', [{'answer_start': 335, 'answer_text': 'ability check, attack roll, or saving throw'}], para, article_title)

file_title = 'Cleric'
para, article_title = find_sentence('When you choose this domain at 1st level, you gain proficiency with heavy armor.', starting_squad_data, article_title=file_title)
add_question('How do clerics gain proficiency with heavy armor?', [{'answer_start': 9, 'answer_text': 'choose this domain at 1st level'}], para, article_title)

para, article_title = find_sentence('When you do so, choose a number of cleric spells equal to your Wisdom modifier + your cleric level (minimum of one spell).', starting_squad_data, article_title='Cleric')
add_question('How many spells can a cleric prepare?', [{'answer_start': 421, 'answer_text': 'Wisdom modifier + your cleric level'},
                                                      {'answer_start': 421, 'answer_text': 'Wisdom modifier + your cleric level (minimum of one spell)'}], para, article_title)

para, article_title = find_sentence('Whenever you use a spell of 1st level or higher to restore hit points to a creature, the creature regains additional hit points equal to', starting_squad_data, article_title='Cleric')
add_question("How many extra hit points are restored by a life domain cleric's healing spells?", [{'answer_start': 205, 'answer_text': "2 + the spell’s level"}], para, article_title)

para, article_title = find_sentence("Weapons: Clubs, daggers, darts, javelins, maces, quarterstaffs, scimitars, sickles, slings, spears Tools: Herbalism kit Saving Throws: Intelligence, Wisdom", starting_squad_data, article_title='Druid')
add_question("Which saving throws are druids proficient in?", [{'answer_start': 235, 'answer_text': "Intelligence, Wisdom"}], para, article_title)

para, article_title = find_sentence("Example 2nd 1/4 No flying or swimming speed", starting_squad_data, article_title='Druid')
add_question("What level can a druid turn into a beast with a flying speed?", [{'answer_start': 109, 'answer_text': "8th"},
                                                                              {'answer_start': 109, 'answer_text': "8"}], para, article_title)

para, article_title = find_sentence("Beginning at 1st level, while you are wearing no armor and not wielding a shield, your AC equals 10 + your Dexterity modifier + your Wisdom modifier.", starting_squad_data, article_title='Monk')
add_question("What is a monk's AC while unarmored?", [{'answer_start': 97, 'answer_text': "10 + your Dexterity modifier + your Wisdom modifier"}], para, article_title)

para, article_title = find_sentence("At 1st level, your practice of martial arts gives you mastery of combat styles that use unarmed strikes and monk weapons, which are ", starting_squad_data, article_title='Monk')
add_question("Which weapons are monk weapons?", [{'answer_start': 132, 'answer_text': "shortswords and any simple melee weapons that don’t have the two-handed or heavy property"}], para, article_title)

para, article_title = find_sentence("Starting at 2nd level, when you hit a creature with a melee weapon attack, you can expend one spell slot to deal radiant damage to the target, in addition to the weapon’s damage.", starting_squad_data, article_title='Paladin')
add_question("What is the damage type of divine smite?", [{'answer_start': 113, 'answer_text': "radiant"}], para, article_title)

para, article_title = find_sentence("You must then finish a short or long rest to use your Channel Divinity again.", starting_squad_data, article_title='Paladin')
add_question("When do paladins regain the use of their Channel Divinity?", [{'answer_start': 237, 'answer_text': "short or long rest"}], para, article_title)

para, article_title = find_sentence("You can transform unexpended sorcery points into one spell slot as a bonus action on your turn.", starting_squad_data, article_title='Sorcerer')
add_question("What type of action is required for sorcerers to turn sorcery points into a spell slot?", [{'answer_start': 291, 'answer_text': "bonus"}], para, article_title)

para, article_title = find_sentence("A standard coin weighs about a third of an ounce, so fifty coins weigh a pound.", starting_squad_data, article_title='Equipment')
add_question("How much does a gold coin weigh?", [{'answer_start': 1539, 'answer_text': "a third of an ounce"}], para, article_title)

para, article_title = find_sentence("If the Armor table shows “Str 13” or “Str 15” in the Strength column for an armor type, the armor reduces the wearer’s speed by 10 feet unless the wearer has a Strength score equal to or higher than the listed score.", starting_squad_data, article_title='Equipment')
add_question("What is the effect of wearing armor without meeting the strength score in the armor table?", [{'answer_start': 1379, 'answer_text': "reduces the wearer’s speed by 10 feet"}], para, article_title)

para, article_title = find_sentence("This kit is a leather pouch containing bandages, salves, and splints. The kit has ten uses.", starting_squad_data, article_title='Equipment')
add_question("How many uses does a healer's kit have?", [{'answer_start': 4209, 'answer_text': "ten"}], para, article_title)

para, article_title = find_sentence("A torch burns for 1 hour, providing bright light in a 20-foot radius and dim light for an additional 20 feet.", starting_squad_data, article_title='Equipment')
add_question("What radius of bright light is provided by a torch?", [{'answer_start': 10798, 'answer_text': "20-foot"}], para, article_title)

para, article_title = find_sentence("A creature moving across the covered area must succeed on a DC 10 Dexterity saving throw or fall prone.", starting_squad_data, article_title='Equipment')
add_question("What is the effect of walking on ball bearings?", [{'answer_start': 1473, 'answer_text': "succeed on a DC 10 Dexterity saving throw or fall prone"}], para, article_title)

para, article_title = find_sentence(" You can push, drag, or lift a weight in pounds up to twice your carrying capacity (or 30 times your Strength score).", starting_squad_data, article_title='Using Ability Scores')
add_question("How much weight can a character lift?", [{'answer_start': 386, 'answer_text': "weight in pounds up to twice your carrying capacity"},
                                                      {'answer_start': 386, 'answer_text': "weight in pounds up to twice your carrying capacity (or 30 times your Strength score)"}], para, article_title)

para, article_title = find_sentence("In a lightly obscuredarea, such as dim light, patchy fog, or moderate foliage, creatures have disadvantage on Wisdom (Perception) checks that rely on sight.", starting_squad_data, article_title='Using Ability Scores')
add_question("What is the effect of lightly obscured terrain?", [{'answer_start': 430, 'answer_text': "disadvantage on Wisdom (Perception) checks that rely on sight"}], para, article_title)

para, article_title = find_sentence("A character can’t benefit from more than one long rest in a 24-hour period, and a character must have at least 1 hit point at the start of the rest to gain its benefits.", starting_squad_data, article_title='')
add_question("Can a character take two long rests in one day?", [{'answer_start': 759, 'answer_text': "can’t benefit from more than one long rest in a 24-hour period"}], para, article_title)

para, article_title = find_sentence("You can take a bonus action only when a special ability, spell, or other feature of the game states that you can do something as a bonus action.", starting_squad_data, article_title='')
add_question("When does a character get a bonus action?", [{'answer_start': 240, 'answer_text': "a special ability, spell, or other feature of the game states that you can do something"}], para, article_title)

para, article_title = find_sentence("Some magic items and other special objects always require an action to use, as stated in their descriptions.", starting_squad_data, article_title='')
add_question("Does it require an action to use a magic item?", [{'answer_start': 552, 'answer_text': "magic items and other special objects always require an action to use"}], para, article_title)

para, article_title = find_sentence("In either case, if the mount provokes an opportunity attack while you’re on it, the attacker can target you or the mount.", starting_squad_data, article_title='')
add_question("Can you be targeted if your mount provokes an opportunity attack?", [{'answer_start': 940, 'answer_text': "attacker can target you or the mount"}], para, article_title)

para, article_title = find_sentence("1st-level abjuration (ritual) Casting Time: 1 minute Range: 30 feet Components: V, S, M (a tiny bell and a piece of fine silver wire)", starting_squad_data, article_title='')
add_question("What is the range of Alarm?", [{'answer_start': 60, 'answer_text': "30 feet"}], para, article_title)

para, article_title = find_sentence("2nd-level enchantment (ritual) Casting Time: 1 action Range: 30 feet Components: V, S, M (a morsel of food)", starting_squad_data, article_title='')
add_question("What is the casting time of Animal Messenger?", [{'answer_start': 45, 'answer_text': "1 action"}], para, article_title)

para, article_title = find_sentence("The creature is under your control for 24 hours, after which it stops obeying any command you’ve given it.", starting_squad_data, article_title='')
add_question("How long are creatures controlled by Animate Dead?", [{'answer_start': 1167, 'answer_text': "24 hours"}], para, article_title)

para, article_title = find_sentence("Each target must succeed on a Wisdom saving throw or be affected by this spell for the duration. An affected target’s speed is halved, it takes a −2 penalty to AC and Dexterity saving throws, and it can’t use reactions.", starting_squad_data, article_title='')
add_question("Which saving throw is required for the Slow spell?", [{'answer_start': 263, 'answer_text': "Wisdom saving throw"},
                                                                   {'answer_start': 263, 'answer_text': "Wisdom"}], para, article_title)

para, article_title = find_sentence("2nd-level transmutation Casting Time: 1 action Range: 150 feet Components: V, S, M (seven sharp thorns or seven small twigs, each sharpened to a point)", starting_squad_data, article_title='')
add_question("What is the range of Spike Growth?", [{'answer_start': 54, 'answer_text': "150 feet"}], para, article_title)

para, article_title = find_sentence("Any character can attempt an Intelligence (Arcana) check to detect or disarm a magic trap, in addition to any other checks noted in the trap’s description.", starting_squad_data, article_title='')
add_question("How can a magic trap be disarmed?", [{'answer_start': 1044, 'answer_text': "Intelligence (Arcana) check"},
                                                  {'answer_start': 1121, 'answer_text': "any other checks noted in the trap’s description"}], para, article_title)

para, article_title = find_sentence("Your Constitution score is 19 while you wear this amulet.", starting_squad_data, article_title='')
add_question("What is the effect of an amulet of health?", [{'answer_start': 47, 'answer_text': "Constitution score is 19"}], para, article_title)

para, article_title = find_sentence("A legendary creature can take a certain number of special actions — called legendary actions — outside its turn. Only one legendary action option can be used at a time and only at the end of another creature’s turn.", starting_squad_data, article_title='')
add_question("When can legendary actions be used?", [{'answer_start': 177, 'answer_text': "at the end of another creature’s turn"}], para, article_title)

para, article_title = find_sentence("Huge dragon, chaotic evil Armor Class 18 (natural armor) Hit Points 200 (16d12 + 96)", starting_squad_data, article_title='')
add_question("How big is an adult white dragon?", [{'answer_start': 0, 'answer_text': "Huge"}], para, article_title)

para, article_title = find_sentence("Gargantuan dragon, chaotic good Armor Class 20 (natural armor) Hit Points 297 (17d20 + 119)", starting_squad_data, article_title='')
add_question("What is the armor class of an ancient brass dragon?", [{'answer_start': 44, 'answer_text': "20"},
                                                                    {'answer_start': 44, 'answer_text': "20 (natural armor)"}], para, article_title)

para, article_title = find_sentence("A frightened creature has disadvantage on ability checks and attack rolls while the source of its fear is within line of sight.", starting_squad_data, article_title='')
add_question("What are the effects of the Frightened condition on a creature?", [{'answer_start': 28, 'answer_text': "disadvantage on ability checks and attack rolls"},
                                                                                {'answer_start': 28, 'answer_text': "disadvantage on ability checks and attack rolls while the source of its fear is within line of sight."},
                                                                                {'answer_start': 28, 'answer_text': "disadvantage on ability checks and attack rolls while the source of its fear is within line of sight. • The creature can’t willingly move closer to the source of its fear."}], para, article_title)

para, article_title = find_sentence("• An unconscious creature is incapacitated (see the condition), can’t move or speak, and is unaware of its surroundings", starting_squad_data, article_title='')
add_question("Do you have advantage on attacks if the target is unconscious?", [{'answer_start': 255, 'answer_text': "Attack rolls against the creature have advantage"}], para, article_title)

non_overwrite_filename = fix_filename(documents_dir, 'benchmark.json')
with open(os.path.join(documents_dir, non_overwrite_filename), 'w') as f:
    json.dump(starting_squad_data, f)
