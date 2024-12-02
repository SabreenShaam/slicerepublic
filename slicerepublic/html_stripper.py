from html.parser import HTMLParser


class MLStripper(HTMLParser):
    linebreak_tags = ['br', 'p', 'div']

    def __init__(self):
        super(MLStripper, self).__init__()
        self.output = []

    def handle_starttag(self, tag, attrs):
        if tag in self.linebreak_tags:
            self.output.append('\n')

    def handle_data(self, data):
        self.output.append(data)

    def get_data(self):
        return ''.join(self.output).strip()


def strip_tags(html):
    s = MLStripper()
    s.feed(str(html))
    return str(s.get_data())