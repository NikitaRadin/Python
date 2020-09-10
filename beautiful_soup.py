import bs4
import re
import itertools
import unittest


def parse(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as file:
        html = file.read()
    body_tag = bs4.BeautifulSoup(html, 'html.parser').find('div', id='bodyContent')

    images = len([tag for tag in body_tag.find_all('img', width=re.compile(r'.*')) if int(tag['width']) >= 200])

    headers = len([tag for tag in body_tag.find_all(name=re.compile(r'h\d+')) if
                   str(tag.text)[:2].replace('\n', '')[0] in ['C', 'E', 'T']])

    def find_length(contents):
        tags = [element for element in contents if isinstance(element, bs4.element.Tag)]
        if not len(tags):
            return 0
        lengths = [len(list(group)) for key, group in itertools.groupby(tags, key=lambda tag: tag.name) if key == 'a']
        if len(lengths):
            first = max(lengths)
        else:
            first = 0
        second = max([find_length(tag.contents) for tag in tags])
        return max(first, second)
    links = find_length(body_tag.contents)

    def find_number(contents):
        first = len(
            [element for element in contents if isinstance(element, bs4.element.Tag) and element.name in ['ol', 'ul']])
        second = sum([find_number(element) for element in contents if
                      isinstance(element, bs4.element.Tag) and element.name not in ['ol', 'ul']])
        return first + second
    lists = find_number(body_tag.contents)

    return [images, headers, links, lists]


class TestParse(unittest.TestCase):
    def test_parse(self):
        test_cases = (
            ('wiki/Stone_Age', [13, 10, 12, 40]),
            ('wiki/Brain', [19, 5, 25, 11]),
            ('wiki/Artificial_intelligence', [8, 19, 13, 198]),
            ('wiki/Python_(programming_language)', [2, 5, 17, 41]),
            ('wiki/Spectrogram', [1, 2, 4, 7]),)
        for path, expected in test_cases:
            with self.subTest(path=path, expected=expected):
                self.assertEqual(parse(path), expected)


if __name__ == '__main__':
    unittest.main()
