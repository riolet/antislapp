# based on http://www.pindari.com/rtf1.html


class RTF:
    def __init__(self, path):
        """
        :param path: The output file name
        :type path: basestring
        """
        self.path = path
        self.head = "{\\rtf1\\ansi\\deff0\n"
        self.tail = "}"
        self.contents = []
        self.written = False

    def append(self, s):
        """
        :param s: The next string to write to the document.
        :type s: str
        :return: None
        :rtype: None
        """
        if self.written:
            raise IOError("File already written and closed.")
        s = s.replace("\n", "\\line\n")
        self.contents.append(s + "\\line\n")

    def set_path(self, path):
        self.path = path
        self.written = False

    @staticmethod
    def bold(s):
        """
        Returns the given string with bold formatting. Chain this with .append()

        :param s: The string to make bold
        :type s: str
        :return: A bold string for use with .append()
        :rtype: str
        """
        return "\\b {}\\b0 ".format(s)

    @staticmethod
    def italic(s):
        """
        Returns the given string with italic formatting. Chain this with .append()

        :param s: The string to make italic
        :type s: str
        :return: An italic string for use with .append()
        :rtype: str
        """
        return "\\i {}\\i0 ".format(s)

    @staticmethod
    def underline(s):
        """
        Returns the given string with underline formatting. Chain this with .append()

        :param s: The string to make underlined
        :type s: str
        :return: An underlined string for use with .append()
        :rtype: str
        """
        return "\\ul {}\\ul0 ".format(s)

    def write(self):
        """
        Writes the string buffer to the file
        :return:
        """
        output = "{}{}{}".format(self.head, ''.join(self.contents), self.tail)
        with open(self.path, 'w') as f:
            f.write(output)
        self.written = True


def test():
    r = RTF('/var/tmp/hooligan.rtf')
    r.append("Line 1 is normal")
    r.append(r.bold("Line 2 is bold"))
    r.append(r.italic("Line 3 is italic"))
    r.append(r.underline("Line 4 is underlined"))
    r.append('multi\nline\nsyntax!')
    r.write()
