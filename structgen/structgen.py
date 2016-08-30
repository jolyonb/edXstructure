#! /usr/bin/python
"""
Convert a CSV file describing edX course structure into XML.
"""

import argparse, os, shutil, csv, collections

levels = {"course" : 0, "chapter" : 1, "sequential" : 2, "vertical" : 3, "html" : 4, "video" : 4, "problem" : 4}
content_type = {"html": 0, "video": 1, "problem": 2}
short = ["course", "chap", "seq", "vert", "html", "video", "problem"]

def interpret(line) :
    '''
    Reads a line, and returns a list containing the entry, url_name, display_name, and a list of any extras
    '''
    entry = line[0]
    url_name = ""
    display_name = ""
    extras = []
    if len(line) > 1 :
        url_name = line[1]
    if len(line) > 2 :
        display_name = line[2]
    if len(line) > 3 :
        extras = line[3:]
    return [entry, url_name, display_name, extras]

class Node :
    def __init__(self, line) :
        '''
        Store the information about this node
        '''
        self.entry, self.url_name, self.display_name, self.extras = interpret(line)
        self.children = []
        self.level = levels[self.entry]
        self.content_type = 0
        if self.level == 4 :
            self.content_type = content_type[self.entry]
        self.extratext = " ".join(self.extras)
        if len(self.extratext) > 0 : self.extratext = " " + self.extratext

    def create_ID(self, counts) :
        '''
        Creates a unique ID, and sets the url_name to this if it's empty
        '''
        self.ID = short[self.level + self.content_type] + "-" + str(counts[self.level + self.content_type])
        if self.url_name.strip() == "" :
            self.url_name = self.ID

    def print_node(self) :
        '''
        Prints itself and all of its children
        '''
        print "    " * self.level + self.entry + ": " + self.display_name
        for i in self.children :
            i.print_node()

    def write_node(self, file_handle) :
        '''
        Outputs the node and all children to file
        '''

        # Write the opening tag
        if self.level == 0 :
            file_handle.write("<course>\n")
        elif self.level == 4 :
            file_handle.write("    " * self.level + "<" + self.entry + " url_name=\"" + self.url_name + "\" />\n")
        else :
            file_handle.write("    " * self.level + "<" + self.entry + " url_name=\"" 
                + self.url_name + "\" display_name=\"" + self.display_name + "\"" + self.extratext + ">\n")

        # Write the children
        for i in self.children :
            i.write_node(file_handle)

        # Close the tag
        if self.level < 4 :
            file_handle.write("    " * self.level + "</" + self.entry + ">\n")

    def write_tree(self, location, file_handle, filename="") :
        '''
        Outputs the node and all children to file in a tree structure
        '''

        # Insert the link in the old file
        if not file_handle is None :        
            # Write the opening tag in the given file
            file_handle.write("    <" + self.entry + 
                " url_name=\"" + self.url_name + "\" />\n")

        # We write out courses, chapters, sequentials and verticals
        if self.level < 4 :
            # Come up with the filename to write
            if filename == "" :
                filename = os.path.join(location, self.entry, self.url_name + ".xml")
            else :
                filename = os.path.join(location, self.entry, filename)
            # Create a new file
            with open(filename, "w") as f :
                # Write this entry
                if self.level == 0 :
                    f.write("<course>\n")                    
                else :
                    f.write("<" + self.entry + " display_name=\"" + self.display_name 
                        + "\"" + self.extratext + ">\n")
                # Write the children
                for i in self.children :
                    i.write_tree(location, f)
                # Close this tag
                f.write("</" + self.entry + ">\n")

def read_csv_file(file):
    '''
    Read in a CSV file, returning a list of lists.
    Provide the filename to read.
    '''
    with open(file, 'r') as f:
        data = [row for row in csv.reader(f.read().splitlines())]
    return data

def strip_line(line):
    '''
    Takes in a list of fields from a line in a csv file.
    Trims all fields, and drops leading and trailing empty fields.
    '''
    newline = map(lambda s: s.strip(), line)
    for i in range(len(newline)) :
        if newline[i] != "" :
            result = newline[i:]
            break
    while result and result[-1] == "" :
        result.pop()
    return result

def strip_data(data):
    '''
    Data should be a list of lists from a csv file.
    Looks at each line of the csv file, and removes any trailing empty fields.
    Then, if the first character in the first field is a #, ignores this line.
    Also turns the first entry to lower case, for later ease.
    '''
    output = []
    for line in data :
        working = strip_line(line)
        if working == [] :
            continue
        if working[0][0] == "#" :
            continue
        working[0] = working[0].lower()
        output.append(working)
    return output

def validate(data) :
    '''
    Checks to make sure that all input into the CSV is readable.
    '''
    # Make sure all entries are understood and that structure is in the
    # correct order (eg no jumping from chapter to vertical)
    # Track the level. Level can only increase 1 level at a time, but can decrease arbitrarily.
    level = 0
    content = ["html", "video", "problem"]
    translation = ["to begin with.", "after chapter.", "after sequential."]
    for line in data :
        if line[0] in levels :
            newlevel = levels[line[0]]
        else :
            print "Error: Unknown entry \"" + line[0] + "\". Full line is as follows."
            print "\"" + "\", \"".join(line) + "\""
            return False
        if newlevel > level + 1 :
            print "Error: Inappropriate order of entries. Cannot have", line[0], translation[level], "Full line is as follows."
            print "\"" + "\", \"".join(line) + "\""
            return False
        level = newlevel

    return True

def xmlify(data) :
    '''
    Turn the data into an XML structure using our node class
    '''
    # The course is the root node
    course = Node(["course", "course", ""])

    # Iterate over everything, remembering what the last node of each level is
    last_nodes = [course, 0, 0, 0, 0]
    count_nodes = [1,0,0,0,0,0,0]
    for i in range(len(data)) :
        # Create the new node
        newnode = Node(data[i])
        # Add it to the last node of the next lower level
        last_nodes[newnode.level - 1].children.append(newnode)
        # Update the last_nodes list
        last_nodes[newnode.level] = newnode
        # Update the count
        count_nodes[newnode.level + newnode.content_type] += 1
        # Create the unique-id for the node
        newnode.create_ID(count_nodes)

    # Return the root
    return course, count_nodes

def make_dir(location, name) :
    '''
    Creates a directory if necessary
    '''
    path = os.path.join(location, name)
    if os.path.isdir(path) :
        return 
    os.mkdir(path)

def rm_dir(location, name) :
    '''
    Removes a directory, if it exists
    '''
    path = os.path.join(location, name)
    if os.path.isdir(path) :
        shutil.rmtree(path)

def scan_url_names(course) :
    namelist = collections.Counter()
    def traverse(node) :
        namelist[node.url_name] += 1
        for i in node.children :
            traverse(i)
    traverse(course)
    
    for elem, count in namelist.items() :
        if " " in elem :
            print "Warning: The url_name \"" + elem + "\" has spaces in it."
        if count > 1 :
            print "Warning: The url_name \"" + elem + "\" has " + str(count) + " instances."

print "edX Structure Generator v1.0"
print "by Jolyon Bloomfield, August 2016"

# Deal with the command line arguments
parser = argparse.ArgumentParser(description="Create edX XML course structure from CSV file")
parser.add_argument("csv_file", help="CSV file to read structure from")

# Write or test?
group = parser.add_mutually_exclusive_group()
group.add_argument("-t", "--test", help="Test only (do not write files)", 
    dest="write", action="store_false")
group.add_argument("-w", "--write", help="Write XML structure (default)", 
    dest="write", default=True, action="store_true")

# One file or multi-structure?
group2 = parser.add_mutually_exclusive_group()
group2.add_argument("-s", "--single", help="Write a single XML file", 
    dest="tree", action="store_false")
group2.add_argument("-T", "--tree", help="Write out an XML tree of files (default)", 
    dest="tree", default=True, action="store_true")

parser.add_argument("-l", dest="location", type=str, default="./",
    help="Set the output directory (defaults to \".\")")
parser.add_argument("-o", dest="filename", type=str, default="course.xml",
    help="Set the root file name (defaults to \"course.xml\")")
parser.add_argument("-c", "--counts", help="Print counts of each item", 
    default=False, action="store_true")
parser.add_argument("--clean", help="Clear all directories before writing (only for tree writes)", 
    default=False, action="store_true")
parser.add_argument("-m", "--map", help="Print the structure map to screen", 
    default=False, action="store_true")

# Parse the command line
args = parser.parse_args()
# print args
# exit()

# Read in the CSV file
try :
    data = read_csv_file(args.csv_file)
except IOError as e:
    print "Error reading", args.csv_file
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    exit()

# Trim the data to the stuff we need
data = strip_data(data)
# Validate the data
if not validate(data) : exit()
# Process the data
course, count_nodes = xmlify(data)
print "Structure read."

# Print item counts
courses, chapters, seqs, verticals, htmls, videos, problems = count_nodes
if args.counts :
    print "Chapters:", chapters
    print "Sequentials:", seqs
    print "Verticals:", verticals
    print "HTMLs:", htmls
    print "Videos:", videos
    print "Problems:", problems

# Print content map
if args.map :
    print "Content Map:"
    course.print_node()

# Scan for duplicate url_names
scan_url_names(course)

# Write content map
if args.write :
    print "Writing course structure."
    if args.tree == False :
        # Single file
        with open(os.path.join(args.location, args.filename), "w") as f :
            course.write_node(f)
    else :
        # Multi-file tree
        if args.clean :
            # Clean everything out before writing
            rm_dir(args.location, "course")
            rm_dir(args.location, "chapter")
            rm_dir(args.location, "sequential")
            rm_dir(args.location, "vertical")

        # Make sure directories exist (but only if necessary)
        if courses > 0 : make_dir(args.location, "course")
        if chapters > 0 : make_dir(args.location, "chapter")
        if seqs > 0 : make_dir(args.location, "sequential")
        if verticals > 0 : make_dir(args.location, "vertical")
        # Write the first node
        course.write_tree(args.location, None, filename=args.filename)

    print "Structure written."
