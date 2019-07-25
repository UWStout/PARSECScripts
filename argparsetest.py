import argparse

parser = argparse.ArgumentParser(description='Quickly Process Photogrammetry Images.')
#parser.add_argument('-I', '-images', metavar='ImagePath', required=True,
                    #help='Path to the folder containing subject images.')
#parser.add_argument('-M', '-masks', metavar='MasksPath', required=True,
                    #help='Path to the folder containing images for background subtraction.')
#parser.add_argument('-N', '-name', metavar='NamePrefix', default='MetaPy',
                    #help='A prefix to apply to log and MetaShape file names.')
parser.add_argument('F', type=argparse.FileType(), help='Access a file.' )

args = parser.parse_args(['test.txt'])
print(args.F.read())
#print(args.N)
#print(args.I)
#print(args.M)
