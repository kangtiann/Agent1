import xml.etree.ElementTree as ET
from io import StringIO
import re

with open('data/13F.xml', 'r') as f:
    content = str(f.read())
content = re.sub(' xmlns="[^"]+"', '', content, count=1)
root = ET.parse(StringIO(content))

for item in root.getroot():
    print(item)
    print(item.findtext("nameOfIssuer"))
    # for i in item:
    #     print(i.text)

print(1)