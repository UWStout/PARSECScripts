import argparse

#AIW Main parser
parser = argparse.ArgumentParser(prog='subparseTest', description='Testing subparser')
parser.add_argument('-P', '--project', help='Select project')
subparsers = parser.add_subparsers(help='Options for selected project')

#AIW Parser for loading existing project.ini
parser_l = subparsers.add_parser('-l', help='Load help')
parser_l.add_argument('--load', action='store_true', help='Loads project from specified filepath')

#AIW Parser for creating a new project.ini
parser_n = subparsers.add_parser('-n', help='New help')
parser_n.add_argument('--new', action='store_true', help='Saves project in specified location')
parser_n.add_argument('--images', help='Path to the folder containing subject images.')
parser_n.add_argument('--masks', help='Path to the images for background subtraction with filename pattern.')
parser_n.add_argument('--name', help='A prefix to apply to log and MetaShape file names.')

args = parser.parse_args()

if args.project == 'n':
    print('Creating new project')

if args.project == 'l':
    print('Loading existing project')