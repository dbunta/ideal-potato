from enum import Enum
from collections import OrderedDict
from fileinput import filename
from itertools import groupby
import itertools
from wsgiref import headers
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



# common properties of Xml doc 
class CommonXmlInfo:
    FileName: str = None
    Title: str = None
    Date: str = None
    Volume: str = None
    Issue: str = None

    def __init__(self, xmlTree, fileName) -> None:
        self.FileName = fileName
        self.Title = self.getElementTextForPath(xmlTree, 'teiHeader/fileDesc/sourceDesc/bibl/ref/title', 'teiHeader/fileDesc/sourceDesc/bibl/title');
        self.Date = self.getElementTextForPath(xmlTree, 'teiHeader/fileDesc/sourceDesc/bibl/date');
        self.Volume = self.getElementTextForPath(xmlTree, "teiHeader/fileDesc/sourceDesc/bibl/biblScope[@unit='volume']");
        self.Issue = self.getElementTextForPath(xmlTree, "teiHeader/fileDesc/sourceDesc/bibl/biblScope[@unit='issue']");

    def getTitle(self, xmlTree):
        # the title tag can be nested in ref tag
        # check if title is nested, if so use that
        pathWithRef = 'teiHeader/fileDesc/sourceDesc/bibl/ref/title'
        pathNoRef = 'teiHeader/fileDesc/sourceDesc/bibl/title'
        elemWithRefPath = xmlTree.find(pathWithRef)
        if (elemWithRefPath != None):
            return elemWithRefPath.text
        return xmlTree.find(pathNoRef).text

    def getElementTextForPath(self, xmlTree, path, backupPath = None):
        elem = xmlTree.find(path)
        if elem == None and backupPath != None:
            elem = xmlTree.find(backupPath)
        text = elem.text
        return " ".join(text.split())
        
# enum to store all column names or column name prefixes
class ColumnNames(str, Enum):
    FileName = "File Name"
    Title = "Title"
    Date = "Date"
    Volume = "Volume"
    Issue = "Issue"
    TotalDivCount = "TotalDivCount"
    TotalNoteCount = "TotalNoteCount"
    DivCountPrefix = "DivCount_"
    NoteCountPrefix = "NoteCount_"
    DivNoteCountPrefix = "DivNoteCount_"

# enum for possible div types
class DivTypeEnum(Enum):
    none = 0
    masthead = 1
    issue = 2
    section = 3
    subsection = 4
    article = 5
    item = 6
    advert = 7
    nameplate = 8
    feature = 9
    frontMatter = 10
    backMatter = 11
    supplement = 12
    index = 13
    bulletin = 14
    appendix = 15
    observations = 16
    tableOfContents = 17

# class to encapsulate div tag instances and associated properties
# Element: original div tag object
# Type: type of div tag
# NoteCount: count of all notes nested in entire div tree
# Instance: 
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
        self.Name = self.getName()

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
        if self.NoteCount > 0:
            return ColumnNames.DivNoteCountPrefix + self.Type.name.capitalize() + "_" + str(self.Instance)
        return None

    def setName(self):
        self.Name = self.getName()

class XmlCounts:
    CommonXmlInfo: CommonXmlInfo = None
    Headers: list = None
    DivElementObjects: list = None
    TotalDivCount: int = None
    TotalNoteCount: int = None
    Counts: list = None
    
    def __init__(self, divElementObjects, commonInfo, totalNoteCount) -> None:
        self.DivElementObjects = divElementObjects
        self.TotalDivCount = len(divElementObjects)
        self.TotalNoteCount = totalNoteCount
        self.CommonXmlInfo = commonInfo
        self.Counts = self.getCounts()
        self.Headers = self.getHeaders()
        

    def getHeaders(self):
        # headers = ["FileName", "Title", "Date", "Volume", "Issue", "TotalDivCount", "TotalNoteCount"]
        headers = []
        for divType in DivTypeEnum:
            headers.append(ColumnNames.DivCountPrefix + divType.name.capitalize())
        for divType in DivTypeEnum:
            headers.append(ColumnNames.NoteCountPrefix + divType.name.capitalize())
        divNoteCountHeaders = []
        for div in self.DivElementObjects:
            if div.NoteCount > 0:
                headers.append(div.Name)
        return headers

    def getCounts(self):
        commonCounts = self.getCommonCounts()
        divAndNoteCountsByType = self.getDivAndNoteCountsByType(self.DivElementObjects)
        divNoteCountsByTypeInstance = self.getDivNoteCountsByTypeInstance(self.DivElementObjects)
        retval = {**divAndNoteCountsByType, **divNoteCountsByTypeInstance, **commonCounts}
        return retval

    def getCommonCounts(self):
        commonCounts = [
            (ColumnNames.FileName, self.CommonXmlInfo.FileName),
            (ColumnNames.Title, self.CommonXmlInfo.Title),
            (ColumnNames.Date, self.CommonXmlInfo.Date),
            (ColumnNames.Volume, self.CommonXmlInfo.Volume),
            (ColumnNames.Issue, self.CommonXmlInfo.Issue),
            (ColumnNames.TotalDivCount, self.TotalDivCount),
            (ColumnNames.TotalNoteCount, self.TotalNoteCount)
        ]
        return OrderedDict(commonCounts);

    def getDivNoteCountsByTypeInstance(self, divElementObjects):
        retval = []
        for divElementObject in divElementObjects:
            if divElementObject.NoteCount > 0:
                retval.append((divElementObject.getName(), divElementObject.getNoteCount()))
        return OrderedDict(retval)

    def getDivAndNoteCountsByType(self, divElementObjects):
        divTypesAndCounts = []
        sortedDivElementObjects = sorted(divElementObjects, key=lambda div: div.Type.name)
        groups = groupby(sortedDivElementObjects, lambda div: div.Type)
        for key, group in groups:
            divColName = self.getDivCountColumnNameFromType(key)
            noteColName = self.getNoteCountColumnNameFromType(key)
            listOfGroupedDivs = list(group)
            divTypesAndCounts.append((divColName, len(listOfGroupedDivs)))
            noteCount = sum(div.NoteCount for div in listOfGroupedDivs)
            if noteCount > 0:
                divTypesAndCounts.append((noteColName, noteCount))
        return OrderedDict(divTypesAndCounts)

    def getDivCountColumnNameFromType(self, type):
        return ColumnNames.DivCountPrefix + type.name.capitalize()

    def getNoteCountColumnNameFromType(self, type):
        return ColumnNames.NoteCountPrefix + type.name.capitalize()

# gets file paths for all xml files in the working directory
# return tuple<string, string>(fileName, filePath)
def getXmlFileNamesAndPathsFromCurrentDirectory():
    xmlFileNamesAndPaths = []
    currentDirectory = os.getcwd()
    allFileNamesInWorkingDirectory = os.listdir(currentDirectory)
    for fileName in allFileNamesInWorkingDirectory:
        if fileName.endswith(".xml"):
            filePath = os.path.join(currentDirectory, fileName)
            xmlFileNamesAndPaths.append((fileName, filePath))
    return xmlFileNamesAndPaths

# parses list of xml files into objects easier to work with 
def parseXmlFiles(xmlFileInfos):
    xmlNamesAndTrees = []
    for xmlFileInfo in xmlFileInfos:
        fileName = xmlFileInfo[0]
        filePath = xmlFileInfo[1]
        xmlTree = et.parse(filePath)
        removeNamespaceFromTagNames(xmlTree)
        xmlNamesAndTrees.append((fileName, xmlTree))
    return xmlNamesAndTrees

# if xml file has namespace defined, it is included in tagnames on parse
# remove it from all tagnames for provided xml tree
def removeNamespaceFromTagNames(xmlTree):
    for element in xmlTree.iter():
        prefix, has_namespace, postfix = element.tag.partition("}")
        if has_namespace:
            element.tag = postfix

# gets all div counts by type
# gets all note counts by type
# gets total div and note counts
# gets div note counts by instance and type
# returns all in a list per xml tree provided
def getDivAndNoteCounts(xmlNamesAndTrees):
    xmlCountsList = []
    for xmlNameAndTree in xmlNamesAndTrees:
        fileName = xmlNameAndTree[0]
        xmlTree = xmlNameAndTree[1]
        divs = getAllDivElementObjectsFromXmlTree(xmlTree)
        notes = getAllNotesFromXmlTree(xmlTree)
        totalNotesCount = len(notes)
        commonXmlInfo = CommonXmlInfo(xmlTree, fileName)
        xmlCounts = XmlCounts(divs, commonXmlInfo, totalNotesCount)
        xmlCountsList.append(xmlCounts)
    return xmlCountsList

# gets div counts by type
def getAllDivElementObjectsFromXmlTree(xmlTree):
    divs = getAllDivsFromXmlTree(xmlTree)
    divElementObjects = transformDivsToDivElementObjects(divs)
    return divElementObjects

# get all divs from provided xml tree
def getAllDivsFromXmlTree(xmlTree):
    return getElementsFromXmlTreeWithGivenTagName(xmlTree, "div")

# gets all notes from provided xml tree
def getAllNotesFromXmlTree(xmlTree):
    return getElementsFromXmlTreeWithGivenTagName(xmlTree, "note")

# gets all elements of given tagname from provided xml tree
def getElementsFromXmlTreeWithGivenTagName(xmlTree, tagName):
    tags = []
    for element in xmlTree.iter(tagName):
        tags.append(element)
    return tags

# creates list of DivElement objects (class defined above) from lsit of divs
# DivElement contains Type, Name, Instance, NoteCount
def transformDivsToDivElementObjects(divs):
    divElementObjects = []
    for div in divs:
        divElement = DivElement(div)
        if divElement.NoteCount > 0:
            numDivsOfType = len([x for x in divElementObjects if x.Type == divElement.Type and x.NoteCount > 0])
            divElement.Instance = numDivsOfType + 1
            divElement.setName()
        divElementObjects.append(divElement)
    return divElementObjects

# writes all counts provided in xmlCountsList to csv file
def writeCsv(xmlCountsList):
    headers = getHeadersForCsv(xmlCountsList)
    with open('new_counts.csv', 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader();
        for xmlCounts in xmlCountsList:
            counts = xmlCounts.Counts
            writer.writerow(counts)

def getHeadersForCsv(xmlCountsList):
    headers = [ColumnNames.FileName, ColumnNames.Title, ColumnNames.Date, ColumnNames.Volume, ColumnNames.Issue, ColumnNames.TotalDivCount, ColumnNames.TotalNoteCount]
    xmlCountsListHeadersLists = [xmlCounts.Headers for xmlCounts in xmlCountsList]
    xmlCountsListHeaders = list(itertools.chain.from_iterable(xmlCountsListHeadersLists))
    distinctValueHeaders = list(groupList(xmlCountsListHeaders))
    distinctValueHeaders.sort()
    headers.extend(distinctValueHeaders)
    return headers

# gets distinct list from simple list
def groupList(lst):
    res = [(el, lst.count(el)) for el in lst]
    return OrderedDict(res)


def main():
    # gets the file names and paths for all xml files in the directory and puts them in a list
    # returned list looks like below, where directory run against is "C:/exampleDirectory"
    # ["C:/exampleDirectory/examplefile1.xml", "C:/exampleDirectory/examplefile2.xml"]
    xmlFileNamesAndPaths = getXmlFileNamesAndPathsFromCurrentDirectory() 

    # parses the xml files and returns a list of tree objects
    # this allows more easy interaction with the contents of the files in code
    xmlNamesAndTrees = parseXmlFiles(xmlFileNamesAndPaths)
    xmlCountsList = getDivAndNoteCounts(xmlNamesAndTrees)
    writeCsv(xmlCountsList)

main()