import re
import os

baselocation = "C:/Schule/4/AUD/Test/"

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
    attributeLabelArray = re.findall("<y\:AttributeLabel[^>]*>[^<]+", x);

    if(len(attributeLabelArray) == 1):
        attributeString = re.findall("(?<=>).*", attributeLabelArray[0])[0];

        attributeString = re.sub("\+", "\npublic ", attributeString)
        attributeString = re.sub("-", "\nprivate ", attributeString)
        attributeString = re.sub("#", "\nprotected ", attributeString)

        attributes = re.split("\n", attributeString)

        del attributes[0]

    else:
        attributes = []


    methodLabelArray = re.findall("<y\:MethodLabel[^>]*>[^<]+", x); #only if not null [0] missing

    if len(methodLabelArray) == 1:
        methodLabel = methodLabelArray[0]
        methodString = re.findall("(?<=>).*", methodLabel)[0];
        methodString = re.sub("\+", "\npublic ", methodString)
        methodString = re.sub("-", "\nprivate ", methodString)
        methodString = re.sub("#", "\nprotected ", methodString)

        methods = re.split("\n", methodString)

        del methods[0]
    else:
        methods=[]


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
            newClasses.append(JaClass(className,attributes,methods))
            p.classes = newClasses
            break;

for p in packages:
    os.mkdir(baselocation + p.packageName);
    for c in p.classes:
        f = open(baselocation+p.packageName + "/" + c.className + ".java", "w+")
        f.write("package " + p.packageName + ";\n")
        f.write("public class " + c.className + "{\n")
        for v in c.variables:
            f.write("\t"+str(v)+";\n")

        f.write("}")
        f.close()
print("yeet")

