# XmlParseAndCount

Parses XML files in specified or working directory.
Groups on defined set of div types
and return counts of div tags by type, note tags by parent div tag types,
instanced note tags by parents div tag types.

 ## E.g.
 ### Sample XML
`<div type="section">
    <div type="article">
        <note></note>
        <note></note>
    </div>
    <div type="article">
        <note></note>
    </div>
</div>`

### Sample Results
TotalDivCount: 3
TotalNoteCount: 3

DivsOfType_Section: 1
DivsOfType_Article: 2

NotesInDivOfType_Section: 3
NotesInDivOfType_Article: 3

NotesInDivOfTypeAndInstance_Section_1: 3
NotesInDivOfTypeAndInstance_Article_1: 2
NotesInDivOfTypeAndInstance_Article_2: 1



## Optional Arguments

-s --Source
source directory where your xml files are located 
If no source argument is specified, the script will look in the directory where it is located for XML files 

-f --Filename
output filename 
If no filename argument is specified, the script has a default filename

