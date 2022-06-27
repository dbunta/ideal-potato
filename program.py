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
        # if self.Instance and self.Instance > 1:
        #     return name + str(self.Instance)
        # return name

class XmlCounts:
    Headers: list = None
    DivElementObjects: list = None

    Title: str = None
    Date: str = None
    Volume: str = None
    Issue: str = None
    TotalDivCount: int = None
    TotalNoteCount: int = None
    MastheadCount: int = None
    IssueCount: int = None
    SectionCount: int = None
    SubsectionCount: int = None
    ArticleCount: int = None
    ItemCount: int = None
    AdvertCount: int = None
    NameplateCount: int = None
    FeatureCount: int = None
    FrontMatterCount: int = None
    BackMatterCount: int = None
    SupplementCount: int = None
    IndexCount: int = None
    BulletinCount: int = None
    AppendixCount: int = None
    ObservationsCount: int = None
    TableOfContentsCount: int = None
    MastheadNoteCount: int = None
    IssueNoteCount: int = None
    SectionNoteCount: int = None
    SubsectionNoteCount: int = None
    ArticleNoteCount: int = None
    ItemNoteCount: int = None
    AdvertNoteCount: int = None
    NameplateNoteCount: int = None
    FeatureNoteCount: int = None
    FrontMatterNoteCount: int = None
    BackMatterNoteCount: int = None
    SupplementNoteCount: int = None
    IndexNoteCount: int = None
    BulletinNoteCount: int = None
    AppendixNoteCount: int = None
    ObservationsNoteCount: int = None
    TableOfContentsNoteCount: int = None
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

    def setCounts(self):
        divAndNoteCountsByType = getDivAndNoteCountsByType(self.DivElementObjects)
        divNoteCountsByTypeInstance = getDivNoteCountsByTypeInstance(self.DivElementObjects)
        # to write:
        # need list of all headers (done)
        # need all counts in dictionary of header name and count (not done)
        # divCountsByType = divAndNoteCountsByType["DivCountsByType"]
        # noteCountsByType = divAndNoteCountsByType["NoteCountsByType"]
        
    def setHeaders(self):
        headers = getHeaders()
        self.Headers = getHeaders2(headers, self.DivElementObjects)

    # def getHeaders(self):
    #     for field in CsvWriteFields:
    #         print(field.name)
    #     for divElementObject in self.DivElementObjects:
    #         print(divElementObject.Type)

    
def getDivCountColumnNameFromType(type):
    return "DivCount_" + type.name.capitalize()

def getNoteCountColumnNameFromType(type):
    return "NoteCount_" + type.name.capitalize()

# def groupDivElementObjectsByType(divElementObjects):
def getDivAndNoteCountsByType(divElementObjects):
    noteTypesAndCounts = []
    divTypesAndCounts = []
    sortedDivElementObjects = sorted(divElementObjects, key=lambda div: div.Type.name)
    groups = groupby(sortedDivElementObjects, lambda div: div.Type)
    for key, group in groups:
        colName = getDivCountColumnNameFromType(key)
        listOfGroupedDivs = list(group)
        # 
        # divTypesAndCounts.append((colName, len(list(group))))
        divTypesAndCounts.append((getDivCountColumnNameFromType(key), len(listOfGroupedDivs)))
        noteCount = sum(div.NoteCount for div in listOfGroupedDivs)
        divTypesAndCounts.append((getNoteCountColumnNameFromType(key), noteCount))
        # divTypesAndCounts.append((colName, noteCount))
        # noteTypesAndCounts.append((colName, noteCount))
    return OrderedDict(divTypesAndCounts)
    # return {"DivCountsByType":OrderedDict(divTypesAndCounts), "NoteCountsByType": OrderedDict(noteTypesAndCounts)}

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
        # divs = getAllDivsFromXmlTree(xmlTree)
        # divElementObjects = transformDivsToDivElementObjects(divs)
        divs = getAllDivElementObjectsFromXmlTree(xmlTree)
        #count of all divs by type
        notes = getAllNotesFromXmlTree(xmlTree)
        totalNotesCount = len(notes)

        xmlCounts = XmlCounts(divs, totalNotesCount)
        xmlCountsList.append(xmlCounts)

    return xmlCountsList

        
        # divCountsByType = divAndNoteCountsByType["DivCountsByType"]
        # noteCountsByType = divAndNoteCountsByType["NoteCountsByType"]
        #iterate through divs to get instanced counts

def writeCsvTest(xmlCountsList):
    headers = getHeaders()
    #list(itertools.chain.from_iterable(lists)
    xmlCountsHeaders = [xmlCounts.Headers for xmlCounts in xmlCountsList]
    xmlCountsHeaders2 = list(itertools.chain.from_iterable(xmlCountsHeaders))
    headers = groupList(xmlCountsHeaders2)

    with open('csv_file.csv', 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader();
        for xmlCounts in xmlCountsList:
            counts = xmlCounts.getCounts()
            writer.writerow(counts)
    # headers = [headers, headers2]
        

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

def test2():
    with open('csv_file.csv', 'w', newline='') as csvFile:
        # fieldNames = getHeaders1()
        writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
        writer.writeheader();
        writer.writerow()

def writeCsvFile():
    countsDict = [
        {
            "Title": "TEst1",
            "TotalDivCount": 3
        },
        {
            "Title": "applejacks",
            "NameplateDivCount": 13
        }
    ]
    with open('csv_file', 'w', newline='') as csvFile:
        fieldNames = getHeaders()
        fieldNames = getHeaders2(fieldNames)
        writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
        writer.writeheader();
        for tagFrequency in countsDict:
            writer.writerow(tagFrequency)

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






# #gets all tagnames from xml tree
# def getAllTagInstances(tree):
#     tagList = []
#     for el in tree.iter():
#         prefix, has_namespace, postfix = el.tag.partition('}')
#         if has_namespace:
#             el.tag = postfix
#         tagList.append(el.tag)
#     return tagList

# def getAllTagsOfNameAndType(xml, name, type):
#     taglist = []
#     for el in xml.iter("div"):
#         prefix, has_namespace, postfix = el.tag.partition("}")
#         if has_namespace:
#             el.tag = postfix
#         taglist.append(el)
#     return taglist

# def getFirstTagText(tagName, tree):
#     for el in tree.iter():
#         if el.tag == tagName:
#                 return el.text
#         # prefix, has_namespace, postfix = el.tag.partition('}')
#         # if has_namespace:
#         #     if postfix == tagName:
#         #         return el.text

# def getTagFrequency(tree):
#     tags = getAllTagInstances(tree)
#     return groupList(tags)

def writeCsvFile(tagFrequency):
    with open('csv_file', 'w', newline='') as csvFile:
        fieldNames = list(tagFrequency.keys())
        writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
        writer.writeheader();
        writer.writerow(tagFrequency)

# def getDistinctTagNames(tagFrequencyList):
#     tagNames = []
#     for tagFrequency in tagFrequencyList:
#         tagNames.extend(tagFrequency.keys())
#     return set(tagNames)


# def writeTagFrequencyListToCsvFile(tagFrequencyList):
#     distinctTagNames = getDistinctTagNames(tagFrequencyList)
#     with open('csv_file', 'w', newline='') as csvFile:
#         fieldNames = list(distinctTagNames)
#         writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
#         writer.writeheader();
#         for tagFrequency in tagFrequencyList:
#             writer.writerow(tagFrequency)



# def getTagFrequencyList(treelist):
#     tagFrequencyList = []
#     for tree in treeList:
#         tagFrequency = getTagFrequency(tree)
#         title = getFirstTagText('title', tree)
#         date = getFirstTagText('date', tree)
#         tagFrequency['ArticleName']=getFirstTagText('title', tree)
#         tagFrequency['ArticleDate']=getFirstTagText('date', tree)
#         tagFrequencyList.append(tagFrequency)
#     return tagFrequencyList


# def getTreeListFromXmlFiles():
#     treeList = []
#     for file in os.listdir(os.getcwd()):
#         if file.endswith(".xml"):
#             treeList.append(et.parse(os.path.join(os.getcwd(), file)))
#     return treeList

# def getTypeCountsFromElements(elements):
#     elementTypes = getTypeValuesFromElements(elements)
#     typeCounts = groupList(elementTypes)
#     return typeCounts

# def getTypeValuesFromElements(elements):
#     elementTypes = []
#     for element in elements:
#         elementType = element.get("type")
#         elementTypes.append(elementType)
#     return elementTypes

#class CsvWriteFields(Enum):
#     Title = 0
#     Date = 1
#     Volume = 2
#     Issue = 3
#     TotalDivCount = 4
#     TotalNoteCount = 5
#     MastheadCount = 6
#     IssueCount = 7
#     SectionCount = 8
#     SubsectionCount = 9
#     ArticleCount = 10
#     ItemCount = 11
#     AdvertCount = 12
#     NameplateCount = 13
#     FeatureCount = 14
#     FrontMatterCount = 15
#     BackMatterCount = 16
#     SupplementCount = 17
#     IndexCount = 18
#     BulletinCount = 19
#     AppendixCount = 20
#     ObservationsCount = 21
#     TableOfContentsCount = 22
#     MastheadNoteCount = 23
#     IssueNoteCount = 24
#     SectionNoteCount = 25
#     SubsectionNoteCount = 26
#     ArticleNoteCount = 27
#     ItemNoteCount = 28
#     AdvertNoteCount = 29
#     NameplateNoteCount = 30
#     FeatureNoteCount = 31
#     FrontMatterNoteCount = 32
#     BackMatterNoteCount = 33
#     SupplementNoteCount = 34
#     IndexNoteCount = 35
#     BulletinNoteCount = 36
#     AppendixNoteCount = 37
#     ObservationsNoteCount = 38
#     TableOfContentsNoteCount = 39
