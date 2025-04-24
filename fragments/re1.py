import regex as re

if __name__ == '__main__':
    r = re.match("^\\d+.html", "e1234.html")
    print(r)