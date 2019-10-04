import re

baselocation = "./TestDir"

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
    packageName = ""
    height = 0
    width = 0
    xCoordinate = 0
    yCoordinate = 0
    classes = []

    def __init__(self, packageName, height, width, xCoordinate, yCoordinate):
        self.packageName = packageName
        self.height = float(height)
        self.width = float(width)
        self.xCoordinate = float(xCoordinate)
        self.yCoordinate = float(yCoordinate)
        self.classes = []




#Methods
def getAttributeFromGeometry(tag, string):
    return re.findall("(?<=" + tag + "=\")(\d*.\d)", string)

#Running Code
f = open('neu0.graphml', 'r')
xmlFile = f.read()
f.close()

xmlFile = re.sub("(\n| {2,})", "", xmlFile)

groupNodes = re.findall("\<y\:GenericGroupNode[^>]*>.*?\<\/y\:GenericGroupNode\>", xmlFile)

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

        packages.append(Package(name,height,width,xCoordinate,yCoordinate))



classNodes = re.findall("\<y\:UMLClassNode[^>]*>.*?\<\/y\:UMLClassNode\>", xmlFile)

for x in classNodes:
    nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", x)[0]
    className = re.findall("(?<=>)[^']*", nodeLabel)[0];
    attributeLabel = re.findall("<y\:AttributeLabel[^>]*>[^<]+", x)[0];
    attributeString = re.findall("(?<=>).*", attributeLabel)[0];

    attributeString = re.sub("\+", "\npublic ", attributeString)
    attributeString = re.sub("-", "\nprivate ", attributeString)
    attributeString = re.sub("#", "\nprotected ", attributeString)

    attributes = re.split("\n", attributeString)


    methodLabel = re.findall("<y\:MethodLabel[^>]*>[^<]+", x)[0]; #only if not null [0]
    methodString = re.findall("(?<=>).*", methodLabel);

    methodString = re.sub("\+", "\npublic ", methodString)
    methodString = re.sub("-", "\nprivate ", methodString)
    methodString = re.sub("#", "\nprotected ", methodString)

    methods = re.split("\n", methodString)



    del attributes[0]
    del methods[0]

    geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
    xCoordinate = float(getAttributeFromGeometry("x", geometryTag)[0])
    yCoordinate = float(getAttributeFromGeometry("y", geometryTag)[0])

    for p in packages:
        packageH = p.height
        packageW = p.width
        packageX = p.xCoordinate #Did't work without calling the variables like that
        packageY = p.yCoordinate
        xMax = packageW + packageX
        yMax = packageY + packageH

        if packageX < xCoordinate and xCoordinate < xMax and packageY < yCoordinate and yCoordinate < yMax:
            newClasses = p.classes
            newClasses.append(JaClass(className,attributes,[]))
            p.classes = newClasses
            break;


print("yeet")

