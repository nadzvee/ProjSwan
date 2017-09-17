import re
linkTitle = 'Befikre (2016)'
parsed = re.compile('(.+?) \((\d{4})\)').findall(linkTitle)
print parsed