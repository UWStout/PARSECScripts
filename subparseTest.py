import argparse

parser = argparse.ArgumentParser(prog='subparseTest', description='Testing subparser')
parser.add_argument('-P', '--project', help='Select project')
subparsers = parser.add_subparsers(help='Options for selected project')

parser_l = subparsers.add_parser('-l', help='Load help')
parser_l.add_argument('--load', action='store_true', help='Loads project from specified filepath')

parser_n = subparsers.add_parser('-n', help='New help')
parser_n.add_argument('--new', action='store_true', help='Saves project in specified location')

args = parser.parse_args()

if args.project == 'n':
    print('Creating new project')

if args.project == 'l':
    print('Loading existing project')