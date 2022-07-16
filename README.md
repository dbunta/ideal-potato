# XmlParseAndCount

Parses XML files in specified or working directory.
Groups on defined set of div types
and return counts of div tags by type, note tags by parent div tag types,
instanced note tags by parents div tag types.

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
Total Counts
<table>
    <tr>
        <th>TotalDivCount</th>
        <th>TotalNoteCount</th>
    </tr>
    <tr>
        <td>3</td>
        <td>3</td>
    </tr>
</table>

Total ```<div>``` Counts by Type
<table>
    <tr>
        <th>DivsOfType_Section</th>
        <th>DivsOfType_Article</th>
    </tr>
    <tr>
        <td>1</td>
        <td>2</td>
    </tr>
</table>

Total ```<note>``` Counts by Parent Div Type
<table>
    <tr>
        <th>NotesInDivOfType_Section</th>
        <th>NotesInDivOfType_Article</th>
    </tr>
    <tr>
        <td>3</td>
        <td>3</td>
    </tr>
</table>

Total ```<note>``` Counts by Parent Div Type and Instance
<table>
    <tr>
        <th>NotesInDivOfTypeAndInstance_Section_1</th>
        <th>NotesInDivOfTypeAndInstance_Article_1</th>
        <th>NotesInDivOfTypeAndInstance_Article_2</th>
    </tr>
    <tr>
        <td>3</td>
        <td>2</td>
        <td>1</td>
    </tr>
</table>