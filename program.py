from asyncore import write
from collections import OrderedDict
from ctypes.wintypes import tagMSG
from doctest import testfile
import xml.etree.ElementTree as et
import csv
import os

def groupList(lst):
    res = [(el, lst.count(el)) for el in lst]
    return OrderedDict(res)

def getAllTagInstances(tree):
    tagList = []
    for el in tree.iter():
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix
        tagList.append(el.tag)
    return tagList

def getFirstTagText(tagName, tree):
    for el in tree.iter():
        if el.tag == tagName:
                return el.text
        # prefix, has_namespace, postfix = el.tag.partition('}')
        # if has_namespace:
        #     if postfix == tagName:
        #         return el.text

def getTagFrequency(tree):
    tags = getAllTagInstances(tree)
    return groupList(tags)

def writeCsvFile(tagFrequency):
    with open('csv_file', 'w', newline='') as csvFile:
        fieldNames = list(tagFrequency.keys())
        writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
        writer.writeheader();
        writer.writerow(tagFrequency)

def getDistinctTagNames(tagFrequencyList):
    tagNames = []
    for tagFrequency in tagFrequencyList:
        tagNames.extend(tagFrequency.keys())
    return set(tagNames)


def writeTagFrequencyListToCsvFile(tagFrequencyList):
    distinctTagNames = getDistinctTagNames(tagFrequencyList)
    with open('csv_file', 'w', newline='') as csvFile:
        fieldNames = list(distinctTagNames)
        writer = csv.DictWriter(csvFile, fieldnames=fieldNames)
        writer.writeheader();
        for tagFrequency in tagFrequencyList:
            writer.writerow(tagFrequency)

def getTreeListFromXmlFiles():
    treeList = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(".xml"):
            treeList.append(et.parse(os.path.join(os.getcwd(), file)))
    return treeList

def getTagFrequencyList(treeList):
    tagFrequencyList = []
    for tree in treeList:
        tagFrequency = getTagFrequency(tree)
        title = getFirstTagText('title', tree)
        date = getFirstTagText('date', tree)
        tagFrequency['ArticleName']=getFirstTagText('title', tree)
        tagFrequency['ArticleDate']=getFirstTagText('date', tree)
        tagFrequencyList.append(tagFrequency)
    return tagFrequencyList


treeList = getTreeListFromXmlFiles()
tagFrequencyList = getTagFrequencyList(treeList)
writeTagFrequencyListToCsvFile(tagFrequencyList)




