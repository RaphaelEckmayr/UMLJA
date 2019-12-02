import os
import re

# Classes


class JaClass:
    nodeId = ""
    className = ""
    variables = []
    methods = []
    packagePath = ""

    def __init__(self, nodeId, className, variables, methods, packagePath):
        self.nodeId = nodeId
        self.className = className
        self.variables = variables
        self.methods = methods
        self.packagePath = packagePath


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


class Connection:
    fromNode = ""
    toNode = ""

    def __init__(self, fromNode, toNode):
        self.fromNode = fromNode
        self.toNode = toNode


def getAttributeFromGeometry(tag, string):
    result = re.findall("(?<=" + tag + "=\")(-*\d*.\d)", string)
    return result

# Parser
def parse(filePath, baselocation):
    try:
        f = open(str(filePath), 'r')
    except:
        print("File not found")
    try:
        xmlFile = f.read()
        f.close()
        print("File successfully read")
    except:
        print("Currupt File")

    xmlFile = re.sub("(\n| {2,})", "", xmlFile)

    groupNodes = re.findall("\<y\:GenericGroupNode[^>]*>.*?\<\/y\:GenericGroupNode\>", xmlFile)

    packages = []
    use = True
    for x in groupNodes:
        geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
        height = getAttributeFromGeometry("height", geometryTag)[0]
        width = getAttributeFromGeometry("width", geometryTag)[0]
        if use:
            xCoordinate = getAttributeFromGeometry("x", geometryTag)[0]
            yCoordinate = getAttributeFromGeometry("y", geometryTag)[0]
            nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", x)[0]
            name = re.findall("(?<=>)[^']*", nodeLabel)[0]

            packages.append(Package(name, height, width, xCoordinate, yCoordinate))

            use = False
        else:
            use = True


    nodes = re.findall('<node id="n\d::n\d">.*?<\/node>',xmlFile)

    for x in nodes:
        try:
            classId = re.findall('(?<=<node id=")[^"]+',x)[0]
            if re.match("n\d::n\d", classId):
                classNode = re.findall("\<y\:UMLClassNode[^>]*>.*?\<\/y\:UMLClassNode\>", x)[0]
                nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", classNode)[0]
                className = re.findall("(?<=>)[^']*", nodeLabel)[0];
                attributeLabelArray = re.findall("<y\:AttributeLabel[^>]*>[^<]+", x);

                if len(attributeLabelArray) == 1:
                    attributeString = re.findall("(?<=>).*", attributeLabelArray[0])[0];

                    attributeString = re.sub("\+", "\npublic ", attributeString)
                    attributeString = re.sub("-", "\nprivate ", attributeString)
                    attributeString = re.sub("#", "\nprotected ", attributeString)

                    attributeString = re.sub("&lt;u&gt;", "static ", attributeString)
                    attributeString = re.sub("&lt;[^&]*&gt;", "", attributeString)

                    attributes = re.split("\n", attributeString)

                    del attributes[0]

                    for i, a in enumerate(attributes):
                        a = re.sub(":", "", a)
                        temp = re.split(" ", a)
                        for tempVar in temp:
                            if tempVar == "":
                                temp.remove(tempVar)

                        isFinal = True
                        for c in temp[1]:
                            if c.islower():
                                isFinal = False
                                break
                        if isFinal:
                            temp[0] += " final"

                        if temp[1] == "static":
                            a = temp[0] + " " + temp[1] + " " + temp[3] + " " + temp[2]
                        else:
                            a = temp[0] + " " + temp[2] + " " + temp[1]
                        attributes[i] = a
                else:
                    attributes = []
        except:
            print("Error with attribute definition: Layout probably wrong in" + x.className)

        try:
            methodLabelArray = re.findall("<y\:MethodLabel[^>]*>[^<]+", x);
            if len(methodLabelArray) == 1:
                methodLabel = methodLabelArray[0]
                methodString = re.findall("(?<=>).*", methodLabel)[0];
                methodString = re.sub("\+", "\npublic ", methodString)
                methodString = re.sub("-", "\nprivate ", methodString)
                methodString = re.sub("#", "\nprotected ", methodString)

                methodString = re.sub("&lt;u&gt;", "static ", methodString)
                methodString = re.sub("&lt;[^&]*&gt;", "", methodString)

                methods = re.split("\n", methodString)

                del methods[0]

                for i, a in enumerate(methods):
                    a = re.sub(":", "", a)
                    temp = re.split(" ", a)
                    for tempVar in temp:
                        if tempVar == "":
                            temp.remove(tempVar)
                    try: #Handle if Constructor
                        if not temp[1][0].islower() and temp[1][1].islower():
                            constructor = True
                        else:
                            constructor = False

                        if temp[1] == "static":
                            a = temp[0] + " " + temp[1] + " " + temp[len(temp)-1]+ " "
                            for index in range(2,len(temp)-1):
                                a += temp[index] + " "
                        elif constructor:
                            a = ""
                            for index in range(0,len(temp)):
                                a += temp[index] + " "
                        else:
                            a = temp[0] + " " + temp[len(temp)-1] + " " + temp[1] + " "
                            for index in range(2,len(temp)-1):
                                a += temp[index] + " "

                        attributePart = re.findall("(?<=\()[^\)]*", a)[0]
                        attributesInMethod = re.split(",", attributePart)
                        fullattributes = ""

                        for cntr, attribute in enumerate(attributesInMethod):
                            tempParts = re.split(" ", attribute)
                            if len(tempParts) > 1:
                                if cntr == 0:
                                    fullattributes = tempParts[1] + " " + tempParts[0]
                                else:
                                    fullattributes += ", " + tempParts[2] + " " + tempParts[1] #Higher Index because of empty String

                        a = re.sub("(?<=\()[^\)]*", fullattributes, a)

                        methods[i] = a
                    except Exception as e:
                        print(str(e))
            else:
                methods = []
                print("No Methods in class")
        except:
            print("Error with attribute definition: Layout probably wrong in" + x.className)

        geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
        xCoordinate = float(getAttributeFromGeometry("x", geometryTag)[0])
        yCoordinate = float(getAttributeFromGeometry("y", geometryTag)[0])

        for p in packages:
            packageH = p.height
            packageW = p.width
            packageX = p.xCoordinate  # Did't work without calling the variables like that
            packageY = p.yCoordinate
            xMax = packageW + packageX
            yMax = packageY + packageH

            if packageX <= xCoordinate and xCoordinate <= xMax and packageY <= yCoordinate and yCoordinate <= yMax:
                newClasses = p.classes
                newClasses.append(JaClass(classId, className, attributes, methods, p.packageName+"."))
                p.classes = newClasses
                break

    connections = []
    connectionTags = re.findall("<edge[^>]*>", xmlFile)

    for connection in connectionTags:
        fromNodeId = re.findall('(?<=source=")[^"]*', connection)[0]
        toNodeId = re.findall('(?<=target=")[^"]*', connection)[0]

        for package in packages:
            for packageClass in package.classes:
                if packageClass.nodeId == fromNodeId:
                    fromNode = packageClass
                if packageClass.nodeId == toNodeId:
                    toNode = packageClass

        connections.append(Connection(fromNode, toNode))

    # Compiler
    if not os.path.isdir(baselocation):
        os.mkdir(baselocation)
    for p in packages:
        dirs = re.split("\.", p.packageName)
        filepath = ""
        for dir in dirs:
            filepath = filepath + dir + "/"
            if not os.path.isdir(baselocation + filepath):
                os.mkdir(baselocation + filepath)

        for c in p.classes:
            directory = baselocation + filepath + c.className + ".java"

            if not os.path.isfile(directory):
                f = open(directory, "w")
            else:
                f = open(directory, "w+")
                print("File has been overwritten")
                print("File exists")

            f.write("package " + p.packageName + ";\n")
            for connection in connections: #Turn from and to Node if you want to execute the test file
                if c.nodeId == connection.fromNode.nodeId:
                    f.write("import " + connection.toNode.packagePath + connection.toNode.className + ";\n")
            f.write("public class " + c.className + "{\n")

            for v in c.variables:
                f.write("\t" + str(v) + ";\n")

            for m in c.methods:
                f.write("\t" + str(m) + "{}\n")
            f.write("}")
            f.close()

    print("File successfully exported to " + baselocation)


parse('./test01.graphml', './TestResults1/')
parse('./test02.graphml', './TestResults2/')
parse('./test03.graphml', './TestResults3/')
