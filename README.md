# edX Structure Generator

Jolyon Bloomfield, August 2016

Converts a CSV file into edX XML structure.


## Purpose

The studio interface for editing an edX course requires a lot of clicking, and experienced coders often feel that working with the raw XML will allow for more control and efficiency in constructing a course. However, getting the edX structure in place is somewhat tedious, and editing the structure XML in a text editor is a suboptimal approach.

The purpose of this code is to allow the edX XML structure to be generated from a CSV file, which can be easily constructed in a GUI spreadsheet program such as Excel. 


## Running the program:

The code is written in python 2.7 and has no external dependencies. It can be run as follows.

```
python structgen.py [-h] [-t | -w] [-s | -T] [-l location] [-c] [--clean] [-m] csv_file.csv
```

`csv_file.csv` is the file to read in, and is the only mandatory argument.

No installation is necessary; feel free to copy `structgen.py` and place it in an appropriate location in your course directory for ease of use.

### Options:

* `-h` Show help for the program
* `-t` Tests the CSV file, but does not write any structure to disk (incompatible with -s)
* `-w` Write structure to disk (default) (incompatible with -t)
* `-s` Write single file (course.xml) (incompatible with -T)
* `-T` Write entire tree (/course/course.xml, /chapter/chapters etc) (default) (incompatible with -s)
* `-l location` Specify the location to output the course structure. If single file output is selected, creates "course.xml" in this location. If tree structure output is selected, creates /course, /chapter etc folders in this location.
* `-o filename` Specify the filename for the root file in the XML structure. This defaults to `course.xml`, but you may want to change it to your appropriate run name.
* `-c` Display counts for each element type
* `--clean` Remove all content in /course, /chapter, /sequential and /vertical directories before outputting the XML tree (only used with -T)
* `-m` Output a map of the course structure to screen

### Examples:

Test a CSV file for integrity, output a map of the structure, and specify counts of each elements.

```
python structgen.py -t -c -m example/example.csv
```

Output a single course.xml file with all the structure to the ./course/ location.

```
python structgen.py -s -l course/ example/example.csv
```

Write the entire tree structure in the present location. Remove any old structure files.

```
python structgen.py --clean example/example.csv
```

# CSV File Format

This is a comma separated file format. Each line corresponds to an entry in a table, and has an arbitrary number of fields, separated by commas. If you need commas in your field, put the field in quotation marks. If you need quotation marks, use double quotation marks. Note that spreadsheet programs such as Excel will automatically export CSV files correctly, so you can just type what you want in the individual cells.

Here is an example line from a CSV file.

```
field1, field2, "field3 has a comma, in it", "field4 has a quotation mark after this "" but before this"
```

There is an example CSV file in `/structgen/example/` as well as the Excel spreadsheet it was saved from.

### CSV Specifics

* Each line is read and parsed. Each field is stripped of leading and trailing whitespace. Empty fields at the beginning and end of a line are ignored.
* If the first non-empty field of a line begins with a #, that line is treated as a comment and ignored.
* All remaining lines are read as follows:

```
entry_type, url_name, display_name, [extras]
```

* entry\_type can be one of "chapter", "sequential", "vertical", "html", "video" or "problem". For content entries (html, video and problems), all fields after url\_name are ignored.
* url\_name can be anything without spaces. If it's left empty, a url\_name will be automatically generated for that item (which will point nowhere if you use it for content). Duplicate url\_names will be flagged.
* display\_name can be anything.
* extras is a list of fields to be appended to the element. This may be used for open/due dates or other edX flags.

A chapter entry opens a new chapter. A sequential entry begins a new sequential in the previously opened chapter. A vertical entry does likewise in the previously opened sequential. Content entries are placed in the previously opened vertical. An error will result if you try to place an element in a container that is not built for it. For example, opening a vertical inside a chapter will not work without opening a sequential first.


## Contents

* `README` - this file.
* `structgen/structgen.py` - the program that generates the course structure.
* `structgen/example/` - an example Excel & CSV file to generate an example course structure, demonstrating various features of this program.


## FAQs

* Do you recommend leaving url\_name fields blank and having them be autogenerated for chapters/sequentials/verticals?

For most purposes, the url\_name fields are completely meaningless and it is completely safe to have them be autogenerated. They're internal tokens, but must be present and must be unique. The one situation they are useful for is to link to a specific location. We recommend setting a fixed url\_name for locations that you link to, as the autogenerated url\_name fields may change, which would ruin your links. (We haven't presently tested if you can use jump\_to\_id links to jump to a url_name for a content page rather than a structure page.)

Note that for content, the url\_name field actually points to the file that holds the content, so you don't want it to be autogenerated in that case.


* Is there any real reason to output the entire tree?

Not particularly. If you plan to edit the resulting XML structure by hand rather than editing the CSV file and outputting everything again, then you may find the tree structure useful. edX is completely happy to read in just the single file however.


* Can you comment out an item in the CSV file?

Yes, just put a # at the start of the line (it might be helpful for the first field on every line of your CSV file to be a comment field). To comment out an entire chapter though, you would need to put a # at the beginning of every element in that chapter.
