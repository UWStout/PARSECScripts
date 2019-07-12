import argparse

parser = argparse.ArgumentParser(description='Calculate X to the power of Y.')
group = parser.add_mutually_exclusive_group()
group.add_argument("-v","--verbose", action="store_true", help="Output will be verbose.")
group.add_argument("-s", "--simple", action="store_true", help="Output will be simple.")
parser.add_argument("x", type=int, help="The base.")
parser.add_argument("y", type=int, help="The exponent.")
args = parser.parse_args()
answer = args.x**args.y

if args.verbose:
    print("{} to the power of {} equals {}.".format(args.x, args.y, answer))
elif args.simple:
    print(answer)
else:
    print("{}^{} == {}".format(args.x, args.y, answer))