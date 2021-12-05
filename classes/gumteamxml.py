import xml.etree.ElementTree as xml
import xml.etree as etree


class GunTeamXML:
    fileName: str

    def __init__(self, fileName='default'):
        self.fileName = f'{fileName}.xml'
        self.openFile()

    def openFile(self):
        try:
            file = open(self.fileName, "r")
            file.close()
        except:
            self.createFile()
        self.tree = xml.ElementTree(file=self.fileName)

    def createFile(self, type="Эксперимент"):
        rootXML = xml.Element(type)

        file = open(self.fileName, "w")
        file.close()
        self.tree = xml.ElementTree(rootXML)
        self.tree.write(self.fileName, encoding="UTF-8")

    def editFile(self, element, value):
        rootXML = self.tree.getroot()
        for elem in rootXML.iter(element):
            elem.text = str(value)

        self.tree = xml.ElementTree(rootXML)
        self.tree.write(self.fileName, encoding="UTF-8")

    def parsingFile(self, elements, text=True):
        rootXML = self.tree.getroot()

        for element in rootXML.iter(elements):
            if (text):
                return element.text
            return element

    def addElement(self, parentname, childname, text=None):
        parent = self.parsingFile(parentname, False)
        child = xml.Element(childname)
        if child in parent.items():
            return
        if text is not None:
            child.text = text
        parent.append(child)
        self.updatafile()

    def updatafile(self):

        self.tree.write(self.fileName, encoding="UTF-8")

        # file = open(self.fileName, 'r')
        # text = file.read()
        # file.close()
        # new_text = re.sub(r'(</.+?>)', r'\1\n', text)
        # file = open(self.fileName, 'w')
        # file.write(new_text)
        # file.close()

    def temptelement(self, name):
        return xml.Element(name)
