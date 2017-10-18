class RTF:
    def __init__(self, path):
        self.path = path
        self.head = "{\\rtf1\\ansi\\deff0\n"
        self.tail = "}"
        self.contents = []

    def append(self, s):
        s = s.replace("\n", "\\line\n")
        self.contents.append(s + "\\line\n")

    def bold(self, s):
        return "\\b {}\\b0 ".format(s)

    def italic(self, s):
        return "\\i {}\\i0 ".format(s)

    def underline(self, s):
        return "\\ul {}\\ul0 ".format(s)

    def write(self):
        output = "{}{}{}".format(self.head, ''.join(self.contents), self.tail)
        with open(self.path, 'w') as f:
            f.write(output)


def test():
    r = RTF('/var/tmp/hooligan.rtf')
    r.append("Line 1 is normal")
    r.append(r.bold("Line 2 is bold"))
    r.append(r.italic("Line 3 is italic"))
    r.append(r.underline("Line 4 is underlined"))
    r.append('multi\nline\nsyntax!')
    r.write()
