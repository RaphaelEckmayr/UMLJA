import re


f = open('neu0.graphml', 'r')
xmlFile = f.read()
f.close()

xmlFile = re.sub("(\n| +)", "", xmlFile)

print(xmlFile)

print(re.findall("\<y\:UMLClassNode[^>]*>.*\<\/y\:UMLClassNode\>", xmlFile))

