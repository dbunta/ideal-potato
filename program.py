from enum import Enum
from collections import OrderedDict
from itertools import groupby
import itertools
import xml.etree.ElementTree as et
import csv
import os
import datetime
import argparse

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

def parseArguments():    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--Source", help="Use specified source directory of XML files")
    parser.add_argument("-f", "--Filename", help="Use specified filename for output CSV file")
    args = getArguments(parser.parse_args())
    return args

def getArguments(args):
    sourceDirectory = getSourceDirectory(args)
    outputFilename = getOutputFilename(args)
    return (sourceDirectory, outputFilename)

def getSourceDirectory(args):
    sourceDirectory = os.getcwd()
    if args.Source:
        sourceDirectory = args.Source
    else:
        printToConsole(f"No source specified, using {sourceDirectory}")
    return sourceDirectory

def getOutputFilename(args):
    outputFilename = f"XMLCounts {getDateTimeNow()}.csv"
    if args.Filename:
        outputFilename = args.Filename
        if not outputFilename.endswith(".csv"):
            outputFilename = outputFilename + ".csv"
    else:
        printToConsole(f"No outupt filename specified, using {outputFilename}")
    return outputFilename

# gets file paths for all xml files in the working directory
# return tuple<string, string>(fileName, filePath)
def getXmlFileNamesAndPathsFromCurrentDirectory(sourceDirectory):
    xmlFileNamesAndPaths = []
    printToConsole(f"Getting XML files from {sourceDirectory}")
    allFileNamesInWorkingDirectory = os.listdir(sourceDirectory)
    for fileName in allFileNamesInWorkingDirectory:
        if fileName.endswith(".xml"):
            filePath = os.path.join(sourceDirectory, fileName)
            xmlFileNamesAndPaths.append((fileName, filePath))
    printToConsole(f"Done getting XML files from {sourceDirectory}")
    return xmlFileNamesAndPaths

# parses list of xml files into objects easier to work with 
def parseXmlFiles(xmlFileInfos):
    xmlNamesAndTrees = []
    printToConsole("Parsing found files")
    for xmlFileInfo in xmlFileInfos:
        fileName = xmlFileInfo[0]
        filePath = xmlFileInfo[1]
        xmlTree = et.parse(filePath)
        removeNamespaceFromTagNames(xmlTree)
        xmlNamesAndTrees.append((fileName, xmlTree))
    printToConsole("Done parsing found files")
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
    printToConsole("Getting all <div> and <note> element counts from all parsed XML files")
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
    printToConsole("Done getting <div> and <note> counts")
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
def writeCsv(xmlCountsList, outputFilename):
    printToConsole(f"Writing counts to file: {outputFilename}")
    headers = getHeadersForCsv(xmlCountsList)
    with open(outputFilename, 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader();
        for xmlCounts in xmlCountsList:
            counts = xmlCounts.Counts
            writer.writerow(counts)
    printToConsole(f"Done writing counts to file: {outputFilename}")

def getHeadersForCsv(xmlCountsList):
    headers = [ColumnNames.FileName, ColumnNames.Title, ColumnNames.Date, ColumnNames.Volume, ColumnNames.Issue, ColumnNames.TotalDivCount, ColumnNames.TotalNoteCount]
    xmlCountsListHeadersLists = [xmlCounts.Headers for xmlCounts in xmlCountsList]
    xmlCountsListHeaders = list(itertools.chain.from_iterable(xmlCountsListHeadersLists))
    distinctValueHeaders = list(groupList(xmlCountsListHeaders))
    distinctValueHeaders.sort()
    headers.extend(distinctValueHeaders)
    return headers

# checks if directory contains any xml files
def xmlFileListIsEmpty(listOfFiles):
    fileCount = len(listOfFiles)
    printToConsole(f"Files found: {fileCount}")
    if fileCount == 0:
        printToConsole("Directory contains no XML files, stopping process")
        return True
    return False

# gets distinct list from simple list
def groupList(lst):
    res = [(el, lst.count(el)) for el in lst]
    return OrderedDict(res)

# prints to console with date
def printToConsole(message):
    print(f"{getDateTimeNow()} - {message}")

# gets formatted datetime
def getDateTimeNow():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')





def main():
    # get specified optional arguments if available
    # otherwise use default values for sourceDirectory
    # and outputFilename
    arguments = parseArguments()
    sourceDirectory = arguments[0]
    outputFilename = arguments[1]

    # gets the file names and paths for all xml files in the directory and puts them in a list
    # returned list looks like below, where directory run against is "C:/exampleDirectory"
    # ["C:/exampleDirectory/examplefile1.xml", "C:/exampleDirectory/examplefile2.xml"]
    xmlFileNamesAndPaths = getXmlFileNamesAndPathsFromCurrentDirectory(sourceDirectory) 
    
    # if no files are in directory, do not continue
    if xmlFileListIsEmpty(xmlFileNamesAndPaths):
        return

    # parses the xml files and returns a list of tree objects
    # this allows more easy interaction with the contents of the files in code
    xmlNamesAndTrees = parseXmlFiles(xmlFileNamesAndPaths)

    # calculates counts of div tags, note tags by total and type
    xmlCountsList = getDivAndNoteCounts(xmlNamesAndTrees)

    # writes xml counts to csv file
    writeCsv(xmlCountsList, outputFilename)


# executes program
main()