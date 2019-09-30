import re

#Classes
class JaClass:
    className = ""
    variables = []
    methods = []

    def __init__(self, className, variables, methods):
        self.className = className
        self.variables = variables
        self.methods = methods

class Package:
    classes = []
    packageName = ""
    height = 0
    width = 0
    xCoordinate = 0
    yCoordinate = 0

    def __init__(self, packageName, height, width, xCoordinate, yCoordinate):
        self.height = height
        self.width = width
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate


#Methods
def getAttributeFromGeometry(tag, string):
    return re.findall("(?<=" + tag + "=\")(\d*.\d)", string)

#Running Code
f = open('neu0.graphml', 'r')
xmlFile = f.read()
f.close()

xmlFile = re.sub("(\n| {2,})", "", xmlFile)

groupNodes = re.findall("\<y\:GenericGroupNode[^>]*>.*?\<\/y\:GenericGroupNode\>", xmlFile)
print(len(groupNodes))

packages = []
for x in groupNodes:
    geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
    height = getAttributeFromGeometry("height", geometryTag)[0]
    width = getAttributeFromGeometry("width", geometryTag)[0]
    if not height == '80.0' and not width == '100.0':
        xCoordinate = getAttributeFromGeometry("x", geometryTag)[0]
        yCoordinate = getAttributeFromGeometry("y", geometryTag)[0]
        nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", x)[0]
        name = re.findall("(?<=>)[^']*", nodeLabel)[0]

        packages.append(Package("name",height,width,xCoordinate,yCoordinate))

classNodes = re.findall("\<y\:UMLClassNode[^>]*>.*?\<\/y\:UMLClassNode\>", xmlFile)

for x in classNodes:
    nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", x)[0]
    className = re.findall("(?<=>)[^']*", nodeLabel)[0];
    attributeLabel = re.findall("<y\:AttributeLabel[^>]*>[^<]+", x)[0];
    attributeString = re.findall("(?<=>).*", attributeLabel)[0];
    print(attributeString)

