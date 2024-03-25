def read_file(filename:str = 'My Clippings.txt') -> str:
    """
    Reads the contents of a text file and returns the text.

    Args:
        filename (str, optional): The name of the file to read. Should be in the same directory. Defaults to 'My Clippings.txt'.

    Returns:
        str: The text contained in the file.

    """

    with open(filename, 'r') as file:

        text = file.read()
        
    return text

file_content = read_file()

raw_highlights =  file_content.split('==========')

unique_titles = []

for highlight in raw_highlights:
    try:
        title = highlight.splitlines()[1]
    except IndexError:
        print('Unable to parse:', highlight)
        continue
        

    unique_titles.append(title.strip())

print('{')
for title in set(unique_titles):
    print(f"\t '{title}': '',")
print('}')

updated_titles = {
         'Do It Today Overcome Procrastination, Improve Productivity Achieve More Meaningful Things by Darius foroux (z-lib.org)': 'Do It Today Overcome Procrastination, Improve Productivity Achieve More Meaningful Things by Darius foroux',
         'How to Build Self-Discipline (Martin Meadows) (z-lib.org) 2': 'How to Build Self-Discipline by Martin Meadows',
         'The McKinsey Way  Us... by Ethan Rasiel (z-lib.org)': 'The McKinsey Way by Ethan Rasiel',
         'The Lean Startup How Todays Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses by Eric Ries (z-lib.org).epub': 'The Lean Startup by Eric Ries',
         'Influence - The Psychology of Persuas... (Z-Library)': 'Influence by Robert B. Cialdini',
         'Atomic Habits An Easy Proven Way to Build Good Habits Break Bad Ones (James Clear) (z-lib.org)': 'Atomic Habits by James Clear',
         'Tools of Titans (Timothy Ferriss) (z-lib.org)': 'Tools of Titans by Timothy Ferriss',
         'Surrounded By Idiots (Thomas Erikson) (z-lib.org)': 'Surrounded By Idiots by Thomas Erikson',
         'The-Great-Mental-Models-General-Think...-_Z-Library_': 'The Great Mental Models by Shane Parrish',
         'Deep Work Rules for Focused Success in a Distracted World by Cal Newport (z-lib.org)': 'Deep Work by Cal Newport',
         'Give and Take (Grant Adam M, D Ph) (Z-Library) 2': 'Give and Tak by Adam Grant',
         'Timothy Ferriss - The 4-Hour Workweek [EnglishOnlineClub.com]': 'The 4 hour week by Timothy Ferris',
         'The Dip A Little Book That Teaches You When to Quit (and When to Stick) (Seth Godin) (z-lib.org)': 'The Dip by Seth Godin',
         'Le génocide des Amériques (Marcel Gro... (Z-Library)': 'Le génocide des Amériques by Marcel Grondin et. Moema Viezzer',
         'The Art of Impossible (Steven Kotler) (Z-Library)': 'The Art of Impossible by Steven Kotler',
         'La-grande-histoire-du-monde-_François...-_Z-Library_': 'La grande histoire du monde by François Reynaert',
         'The Case Against the Sexual Revolution (Louise Perry) (Z-Library)': 'The Case Against the Sexual Revolution by Louise Perry',
         'Healthy Brain, Happy Life (Wendy Suzuki) (Z-Library)-2': 'Healthy Brain, Happy Life by Wendy Suzuki',
         'Mindset - Updated Edition Changing The Way You think To Fulfil Your Potential - PDFDrive.com by Carol Dweck (z-lib.org)': 'Mindset by Carol Dweck',
         'Dumas_Le_comte_de_Monte_Cristo_1': 'Le compte de Monte Cristo by Alexandre Dumas',
         'El Alquimista (Paulo Cohelo) (Z-Library)': 'El Alquimista by Paulo Cohelo',
         'The 100 Startup (Chris Guillebeau [Gu... (Z-Library)-2': 'The 100 Startup by Chris Guillebeau',
         'Bored and brilliant how time spent doing nothing changes everything by Manoush Zomorodi': 'Bored and brilliant by Manoush Zomorodi',
         'The Hidden Habits of Genius': 'The Hidden Habits of Genius by Craig M. Wright',
         'Take Your Shot by Robin Waite (z-lib.org)': 'Take Your Shot by Robin Waite',
         'The Inner Game of Te... by W. Timothy Gallwey (z-lib.org)': 'The Inner Game of Tennis by Timothy Gallwey',
         'Corruptible-Who-Gets-Power-and-How-It-Changes-Us-_Brian-Klaas_-_Z-Library_': 'Corruptible by Brian Klaas',
         'How the World Really Works (Vaclav Smil) (z-lib.org)': 'How the World Really Works by Vaclav Smil',
         'Beginners The Joy and Transformative... (z-lib.org)_12249766': 'Beginners by Tom Vanderbilt',
         'Never Split the Difference Negotiating as if Your Life Depended on It by Chris Voss [Voss, Chris] (z-lib.org)': 'Never Split the Difference by Chris Voss',
         'Can’t Hurt Me Master Your Mind and Defy the Odds by David Goggins': 'Can’t Hurt Me by David Goggins',
         'The Rare Metals War (Guillaume Pitron)': 'The Rare Metals War by Guillaume Pitron',
         'How Not to Be Wrong The Power of Mathematical Thinking by Jordan Ellenberg': 'How Not to Be Wrong by Jordan Ellenberg',
         'The Mamba Mentality by Kobe Bryant (z-lib.org)': 'The Mamba Mentality by Kobe Bryant',
         'Start With Why (Simon Sinek) (Z-Library)': 'Start With Why by Simon Sinek',
         'On Writing Well (Zinsser, William Knowlton) (Z-Library)': 'On Writing Well by Zinsser, William Knowlton',
         'How to Become a Straight-A Student The Unconventional Strategies Real College Students Use to Score High While Studying Less (Cal Newport) (z-lib.org)': 'How to Become a Straight-A Student by Cal Newport',
         'Thinking, Fast and Slow by Daniel Kahneman (z-lib.org).epub (Unknown)': 'Thinking, Fast and Slow by Daniel Kahneman',
         'Flow The Psychology of Optimal Experience by Mihaly Csikszentmihalyi (z-lib.org).epub': 'Flow The Psychology of Optimal Experience by Mihaly Csikszentmihalyi',
         'Why-Grow-Up-Subversive-Thoughts-for-a...-_Z-Library_': 'Why Grow Up by Susan Neiman',
         'The Man from the Future (Ananyo Bhattacharya) (Z-Library)': 'The Man from the Future by Ananyo Bhattacharya',
         'The Judgment of Paris The Revolutiona... (Z-Library)': 'The Judgment of Paris by Ross King',
         'Thinking, Fast and Slow by Daniel Kahneman (z-lib.org)': 'Thinking, Fast and Slow by Daniel Kahneman',
         'Glucose Revolution (Jessie Inchauspe) (z-lib.org)': 'Glucose Revolution by Jessie Inchauspe',
         'Magic Words (Jonah Berger) (Z-Library)': 'Magic Word by Jonah Berger',
         'The Defining Decade Why Your Twenties... (Z-Library)': 'The Defining Decade by Meg May',
         'Spark The Revolutionary New Science of Exercise and the Brain by John J. Ratey': 'Spark by John J. Ratey',
         'Parisians An Adventure History of Paris (Robb Graham) (Z-Library)': 'Parisians by Robb Graham',
         'Dopamine Nation Finding Balance in th... (Z-Library)': 'Dopamine Nation by Anna Lembke',
         'Effortless Make It Easier to Do What Matters Most (Greg McKeown) (z-lib.org)': 'Effortless by Greg McKeown',
         'Artificial-Intelligence-_Melanie-Mitchell_-_z-lib.org_': 'Artificial Intelligence: A Guide for Thinking Humans by Melanie Mitchell',
         'The Harvard Business Review Entrepreneur’s Handbook by Harvard Business Review (z-lib.org)': 'The Harvard Business Review Entrepreneur’s Handbook by Harvard Business Review',
         'Competing In The Age Of AI (Marco Iansiti, Karim R. Lakhani) (z-lib.org)': 'Competing In The Age Of AI by Marco Iansiti, Karim R. Lakhani',
         'The Organized Mind Thinking Straight in the Age of Information Overload by Daniel J. Levitin': 'The Organized Mind by Daniel J. Levitin',
         'The Hidden Habits of Genius': 'The Hidden Habits of Genius by Craig Wright',
}

original_file_content = read_file()

new_file_content = original_file_content

for old_title, updated_title in updated_titles.items():

    new_file_content = new_file_content.replace(old_title, updated_title)


with open('My Clippings updated.txt', 'w') as file:
    file.write(new_file_content)