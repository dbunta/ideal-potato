# XmlParseAndCount

Parses XML files in specified or working directory.
Groups on defined set of div types
and return counts of div tags by type, note tags by parent div tag types,
instanced note tags by parents div tag types.

 ## E.g.
 ### Sample XML
```
<div type="section">
    <div type="article">
        <note></note>
        <note></note>
    </div>
    <div type="article">
        <note></note>
    </div>
</div>
```
### Sample Results
TotalDivCount:  3
</br>
TotalNoteCount: 3

DivsOfType_Section: 1
</br>
DivsOfType_Article: 2

NotesInDivOfType_Section:   3
</br>
NotesInDivOfType_Article:   3

NotesInDivOfTypeAndInstance_Section_1:  3
</br>
NotesInDivOfTypeAndInstance_Article_1:  2
</br>
NotesInDivOfTypeAndInstance_Article_2:  1


## Optional Arguments

-s --Source
</br>
source directory in which the XML files are located
</br>
If no source argument is specified, the script will look in the directory where it is located for XML files 

-f --Filename
</br>
output filename (CSV file)
</br>
If no filename argument is specified, the script has a default filename

