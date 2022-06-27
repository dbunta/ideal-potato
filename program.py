from audioop import add
from enum import Enum
from asyncore import write
from collections import OrderedDict
from ctypes.wintypes import tagMSG
from doctest import testfile
from functools import reduce
from itertools import groupby
import itertools
from xml.dom.minidom import Element
import xml.etree.ElementTree as et
import csv
import os

# group by div type to get total count per div type
# put in dict with type and count
# loop through divtypeenum
# if divtypeenum.type in dict
# print that count
# otherwise print 0
# loop through divtypeenum twice
# counts of divs per type
# counts of notes per div type
# finally,
# loop through non-grouped list of divs
# track occurrences of each type
# print type name + occurrence and note count
# possibility for tracking occurrences:
# add col name as looping
# if col name already in collection
# then append value
# get # of times name appears in collection
# if 0 - append 1
# if 1 - append 2
# etc
#


class DivTypeEnum(Enum):
    none = 17
    masthead = 0
    issue = 1
    section = 2
    subsection = 3
    article = 4
    item = 5
    advert = 6
    nameplate = 7
    feature = 8
    frontMatter = 9
    backMatter = 10
    supplement = 11
    index = 12
    bulletin = 13
    appendix = 14
    observations = 15
    tableOfContents = 16


class DivElement:
    Element: et.Element = None
    Type: DivTypeEnum = None
    NoteCount: int = None
    Instance: int = None
    Name: str = None
    # Name = "<div type='" + DivType.name + "'>_" + str(Instance)
    def __init__(self, element) -> None:
        self.Element = element
        if self.getType() is None:
            self.Type = DivTypeEnum.none
        else:
            self.Type = DivTypeEnum[self.getType()]
        self.NoteCount = self.getNoteCount()

    def getType(self):
        type = self.Element.get("type")
        if type is None:
            return "none"
        else:
            return self.Element.get("type")

    def getNoteCount(self):
        count = 0
        for element in self.Element.iter():
            if element.tag == "note":
                count += 1
        return count

    def getName(self):
        return "DivNoteCount_" + self.Type.name.capitalize() + "_" + str(self.Instance)

class XmlCounts:
    Headers: list = None
    DivElementObjects: list = None
    Counts: list = None
    
    def __init__(self, divElementObjects, totalNoteCount) -> None:
        self.DivElementObjects = divElementObjects
        self.TotalDivCount = len(divElementObjects)
        self.TotalNoteCount = totalNoteCount
        self.setCounts()
        self.setHeaders()

    def getCounts(self):
        divAndNoteCountsByType = getDivAndNoteCountsByType(self.DivElementObjects)
        divNoteCountsByTypeInstance = getDivNoteCountsByTypeInstance(self.DivElementObjects)
        retval = {**divAndNoteCountsByType, **divNoteCountsByTypeInstance}
        return retval
        
    def setHeaders(self):
        headers = getHeaders()
        self.Headers = getHeaders2(headers, self.DivElementObjects)

    
def getDivCountColumnNameFromType(type):
    return "DivCount_" + type.name.capitalize()

def getNoteCountColumnNameFromType(type):
    return "NoteCount_" + type.name.capitalize()

def getDivAndNoteCountsByType(divElementObjects):
    noteTypesAndCounts = []
    divTypesAndCounts = []
    sortedDivElementObjects = sorted(divElementObjects, key=lambda div: div.Type.name)
    groups = groupby(sortedDivElementObjects, lambda div: div.Type)
    for key, group in groups:
        colName = getDivCountColumnNameFromType(key)
        listOfGroupedDivs = list(group)
        divTypesAndCounts.append((getDivCountColumnNameFromType(key), len(listOfGroupedDivs)))
        noteCount = sum(div.NoteCount for div in listOfGroupedDivs)
        divTypesAndCounts.append((getNoteCountColumnNameFromType(key), noteCount))
    return OrderedDict(divTypesAndCounts)

def getDivNoteCountsByTypeInstance(divElementObjects):
    retval = []
    for divElementObject in divElementObjects:
        if divElementObject.NoteCount > 0:
            retval.append((divElementObject.getName(), divElementObject.getNoteCount()))
    return OrderedDict(retval)

def addDivNoteCounts(x, y):
    return x.NoteCount + y.NoteCount

def getXmlFilePathsFromCurrentDirectory():
    xmlFilePaths = []
    currentDirectory = os.getcwd()
    allFileNamesInWorkingDirectory = os.listdir(currentDirectory)
    for fileName in allFileNamesInWorkingDirectory:
        if fileName.endswith(".xml"):
            filePath = os.path.join(currentDirectory, fileName)
            xmlFilePaths.append(filePath)
    return xmlFilePaths

def parseXmlFiles(xmlFilePaths):
    xmlTrees = []
    for xmlFilePath in xmlFilePaths:
        xmlTree = et.parse(xmlFilePath)
        xmlTrees.append(xmlTree)
        removeNamespaceFromTagNames(xmlTree)
    return xmlTrees

def removeNamespaceFromTagNames(xmlTree):
    for element in xmlTree.iter():
        prefix, has_namespace, postfix = element.tag.partition("}")
        if has_namespace:
            element.tag = postfix

def getAllDivsFromXmlTree(xmlTree):
    return getElementsFromXmlTreeWithGivenTagName(xmlTree, "div")

def getAllNotesFromXmlTree(xmlTree):
    return getElementsFromXmlTreeWithGivenTagName(xmlTree, "note")

def getElementsFromXmlTreeWithGivenTagName(xmlTree, tagName):
    tags = []
    for element in xmlTree.iter(tagName):
        tags.append(element)
    return tags



def groupList(lst):
    res = [(el, lst.count(el)) for el in lst]
    return OrderedDict(res)

def getNotesInDivs(divs):
    noteList = []
    for div in divs: 
        for element in div.iter():
            if element.tag == "note":
                noteList.append(element)
    return noteList
        


def transformDivsToDivElementObjects(divs):
    divElementObjects = []
    for div in divs:
        divElement = DivElement(div)
        if divElement.NoteCount > 0:
            numDivsOfType = len([x for x in divElementObjects if x.Type == divElement.Type and x.NoteCount > 0])
            divElement.Instance = numDivsOfType + 1
        divElementObjects.append(divElement)
    return divElementObjects

def getAllDivElementObjectsFromXmlTree(xmlTree):
    divs = getAllDivsFromXmlTree(xmlTree)
    divElementObjects = transformDivsToDivElementObjects(divs)
    return divElementObjects

def getDivAndNoteCounts(xmlTrees):
    xmlCountsList = []
    for xmlTree in xmlTrees:
        divs = getAllDivElementObjectsFromXmlTree(xmlTree)
        notes = getAllNotesFromXmlTree(xmlTree)
        totalNotesCount = len(notes)

        xmlCounts = XmlCounts(divs, totalNotesCount)
        xmlCountsList.append(xmlCounts)

    return xmlCountsList


def writeCsvTest(xmlCountsList):
    headers = getHeaders()
    xmlCountsHeaders = [xmlCounts.Headers for xmlCounts in xmlCountsList]
    xmlCountsHeaders2 = list(itertools.chain.from_iterable(xmlCountsHeaders))
    headers = groupList(xmlCountsHeaders2)

    with open('csv_file.csv', 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader();
        for xmlCounts in xmlCountsList:
            counts = xmlCounts.getCounts()
            writer.writerow(counts)
        

def getHeaders():
    cols = ["Title", "Date", "Volume", "Issue", "TotalDivCount", "TotalNoteCount"]
    for divType in DivTypeEnum:
        cols.append("DivCount_" + divType.name.capitalize())
    for divType in DivTypeEnum:
        cols.append("NoteCount_" + divType.name.capitalize())
    return cols

def getHeaders2(existingHeaders, divs):
    retval = []
    for div in divs:
        if div.NoteCount > 0:
            existingHeaders.append(div.getName())
    return existingHeaders


def main():
    # test()
    # gets the file paths for all xml files in the directory and puts them in a list
    # returned list looks like below, where directory run against is "C:/exampleDirectory"
    # ["C:/exampleDirectory/examplefile1.xml", "C:/exampleDirectory/examplefile2.xml"]
    xmlFilePaths = getXmlFilePathsFromCurrentDirectory() 

    # parses the xml files and returns a list of tree objects
    # this allows more easy interaction with the contents of the files in code
    xmlTrees = parseXmlFiles(xmlFilePaths)

    xmlCountsList = getDivAndNoteCounts(xmlTrees)
    writeCsvTest(xmlCountsList)



main()



#treeList = getTreeListFromXmlFiles()
#tagFrequencyList = getTagFrequencyList(treeList)
#writeTagFrequencyListToCsvFile(tagFrequencyList)


   
#total div count
#counts of divs per type

#total note count
#counts of note within each div type
#counts note per div type 

#<div type=article>
    #<note>
#<div type=article>
    #<note>

 #article div 1, article div 2
 #1, 1

#inside <bibl>
#get title, date, volume issue

#count of note tags per article div instance
#note = footnote