
import re
import os
import wx
import ctypes.wintypes
import ntpath


# Classes
class JaClass:
    nodeId = ""
    className = ""
    variables = []
    methods = []

    def __init__(self, nodeId, className, variables, methods):
        self.nodeId = nodeId
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

class Connection:
    fromNode = ""
    toNode = ""

    def __init__(self, fromNode, toNode):
        self.fromNode = fromNode
        self.toNode = toNode


class DnDPanel(wx.Panel):
    """"""

    # Methods / Get attribute
    def getAttributeFromGeometry(self, tag, string):
        result = re.findall("(?<=" + tag + "=\")(-*\d*.\d)", string)
        return result

    def printMessage(self, message):
        self.logTextCtrl.AppendText(message + '\n')

    # Parser
    def parse(self, filePath):
        try:
            f = open(str(filePath), 'r')
        except:
            self.printMessage("File not found")
        try:
            xmlFile = f.read()
            f.close()
            self.printMessage("File successfully read")
        except:
            self.printMessage("Currupt File")

        xmlFile = re.sub("(\n| {2,})", "", xmlFile)

        groupNodes = re.findall("\<y\:GenericGroupNode[^>]*>.*?\<\/y\:GenericGroupNode\>", xmlFile)

        packages = []
        use = True
        for x in groupNodes:
            geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
            height = self.getAttributeFromGeometry("height", geometryTag)[0]
            width = self.getAttributeFromGeometry("width", geometryTag)[0]
            if use:
                xCoordinate = self.getAttributeFromGeometry("x", geometryTag)[0]
                yCoordinate = self.getAttributeFromGeometry("y", geometryTag)[0]
                nodeLabel = re.findall("<y\:NodeLabel[^>]*>[^<]+", x)[0]
                name = re.findall("(?<=>)[^']*", nodeLabel)[0]

                packages.append(Package(name, height, width, xCoordinate, yCoordinate))

                use = False
            else:
                use = True


        connections = []
        connectionTags = re.findall("<edge[^>]*>", xmlFile)

        for connection in connectionTags:
            fromNode = re.findall('(?<=source=")[^"]*', connection)[0]
            toNode = re.findall('(?<=target=")[^"]*', connection)[0]
            connections.append(Connection(fromNode, toNode))

        nodes = re.findall('<node id="n\d::n\d">.*?<\/node>',xmlFile) #Error in regex doess't select <node> Tag

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
                self.printMessage("Error with attribute definition: Layout probably wrong in" + x.className)

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
                            self.printMessage(str(e))
                else:
                    methods = []
                    self.printMessage("No Methods in class")
            except:
                self.printMessage("Error with attribute definition: Layout probably wrong in" + x.className)

            geometryTag = str(re.findall("\<y\:Geometry[^>]*\/\>", x))
            xCoordinate = float(self.getAttributeFromGeometry("x", geometryTag)[0])
            yCoordinate = float(self.getAttributeFromGeometry("y", geometryTag)[0])

            for p in packages:
                packageH = p.height
                packageW = p.width
                packageX = p.xCoordinate  # Did't work without calling the variables like that
                packageY = p.yCoordinate
                xMax = packageW + packageX
                yMax = packageY + packageH

                if packageX <= xCoordinate and xCoordinate <= xMax and packageY <= yCoordinate and yCoordinate <= yMax:
                    newClasses = p.classes
                    newClasses.append(JaClass(classId, className, attributes, methods))
                    p.classes = newClasses
                    break
        # Compiler
        baselocation = self.projectPathText.GetValue() + "\\" + self.editname.GetValue() + "\\"
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
                    self.printMessage("File has been overwritten")
                    print("File exists")

                f.write("package " + p.packageName + ";\n")

                f.write("public class " + c.className + "{\n")

                for v in c.variables:
                    f.write("\t" + str(v) + ";\n")

                for m in c.methods:
                    f.write("\t" + str(m) + "{}\n")
                f.write("}")
                f.close()

        self.printMessage("File successfully exported to " + baselocation)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        self.panel = wx.Panel(self)
        file_drop_target = MyFileDropTarget(self)
        self.lbl = wx.StaticText(self.panel, label="Drag some files here:")
        self.fileTextCtrl = wx.TextCtrl(self.panel,
                                        style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY, size=(180, 70))
        self.fileTextCtrl.SetDropTarget(file_drop_target)
        self.logLabel = wx.StaticText(self.panel, label="Log Console:")
        self.logTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY, size=(250, 150))
        self.button = wx.Button(self.panel, label="Convert")
        self.lblname = wx.StaticText(self.panel, label="Projektname:")
        self.editname = wx.TextCtrl(self.panel, size=(230, -1))
        self.projectPathLabel = wx.StaticText(self.panel, label="Projektpfad:")
        self.projectPathText = wx.TextCtrl(self.panel, size=(230, -1))

        self.fileTextCtrl.AppendText("Double Click to select File")

        # Get MyDocuments Folder
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        self.projectPathText.AppendText(buf.value)

        # Set sizer for the frame, so we can change frame size to match widgets
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.lblname, (0, 0))
        self.sizer.Add(self.editname, (0, 1))
        self.sizer.Add(self.projectPathLabel, (1, 0))
        self.sizer.Add(self.projectPathText, (1, 1))
        self.sizer.Add(self.button, (2, 0), (1, 2), flag=wx.EXPAND)
        self.sizer.Add(self.lbl, (3, 0))
        self.sizer.Add(self.fileTextCtrl, (4, 0))
        self.sizer.Add(self.logLabel, (5, 0))
        self.sizer.Add(self.logTextCtrl, (6, 0), (6, 2), flag=wx.EXPAND)

        # Set simple sizer for a nice border
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        # Use the sizers
        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.button.Bind(wx.EVT_BUTTON, self.convert)
        self.fileTextCtrl.Bind(wx.EVT_LEFT_DCLICK, self.openFileChooser)
        self.path = ''

    def convert(self, e):
        if len(self.editname.GetValue()) < 1:
            self.printMessage("Error: Field 'Project name' is empty")
            return
        path = self.path
        self.parse(path)

    def openFileChooser(self, event):
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open .graphml file",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.setFilePath(fileDialog.GetPath())

    def setFilePath(self, filePath):
        self.path = filePath
        self.fileTextCtrl.SetValue("Double Click to select File\n\nSelected File: " + ntpath.basename(filePath))


class MyFileDropTarget(wx.FileDropTarget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, window):
        """Constructor"""
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ----------------------------------------------------------------------
    def OnDropFiles(self, x, y, filenames):
        """
        When files are dropped, write where they were dropped and then
        the file paths themselves
        self.window.SetInsertionPointEnd()
        self.window.updateText("\n%d file(s) dropped at %d,%d:\n" %
                              (len(filenames), x, y))
                              """
        print(filenames)
        print("\n%d file(s) dropped at %d,%d:\n" %
              (len(filenames), x, y))
        filepath = filenames[0]
        if not ntpath.basename(filepath).endswith(".graphml"):
            self.window.printMessage("Error: File extension must be: .graphml")
            return False
        self.window.setFilePath(filepath)

        return True


class DnDFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="UMLJA", size=wx.Size(440, 400))
        panel = DnDPanel(self)
        self.Show()


# Running Code

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DnDFrame()
    app.MainLoop()
