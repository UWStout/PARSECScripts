import sys
import argparse

# Create the parser
parser = argparse.ArgumentParser(description='Quickly Process Photogrammetry Images.',
                                 fromfile_prefix_chars='@')

# Add possible arguments to the parser
parser.add_argument('-I', '-images', metavar='ImagePath', required=True,
                    help='Path to the folder containing subject images.')
parser.add_argument('-M', '-masks', metavar='MasksPath', required=True,
                    help='Path to the folder containing images for background subtraction.')
parser.add_argument('-N', '-name', metavar='NamePrefix', default='MetaPy',
                    help='A prefix to apply to log and MetaShape file names.')

# Parse arguments from the command line only
print("=========================")
args = parser.parse_args()
print(args.N)
print(args.I)
print(args.M)
print("=========================")

# Parse arguments from the file only
args = parser.parse_args(['@user.args'])
print(args.N)
print(args.I)
print(args.M)
print("=========================")

# Parse arguments from both the command line and the file
myArgList = sys.argv[1:]
myArgList.insert(0, '@user.args') # In this version (the @file comes first) the command line ones override the files ones
# myArgList.append('@user.args') # In this version (the @file comes last) the files ones override the command line ones

args = parser.parse_args(myArgList)
print(args.N)
print(args.I)
print(args.M)
print("=========================")
