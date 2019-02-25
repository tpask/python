#!/usr/bin/python

import argparse

def getArgs(): 
	parser = argparse.ArgumentParser()
	parser.add_argument("--verbose", "-v", "-d", "--debug", "-verbose", "-debug", help="increase output verbosity", action="store_true")
	args = parser.parse_args()
	return args

args = getArgs()
print args
print args.verbose

if args.verbose:
    print "verbose turned on"
