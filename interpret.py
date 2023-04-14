# This file is the second part of the IPP 2023 project.
# sourceFile: intepret.py
# author: Jiri Charamza
# login: xchara04

import re
import argparse
import xml.etree.ElementTree as XML
import sys

def exitError(errorCode):
    match errorCode:
        case 10:
            print("Error: Invalid or missing argument", file = sys.stderr)
        case 11:
            print("Error: Unable to open input or sourse file", file = sys.stderr)
        case 12:
            print("Error: Unable to open output file", file = sys.stderr)
        case 31:
            print("Error: Unable to parse XML source file", file = sys.stderr)
        case 32:
            print("Error: Invalid XML source file structure", file = sys.stderr)
        case 52:
            print("Error: Semantic error in source file", file = sys.stderr)
        case 53:
            print("Error: Interpretation error - incorrect operand type", file = sys.stderr)
        case 54:
            print("Error: Interpretation error - accesing invalid variable", file = sys.stderr)
        case 55:
            print("Error: Interpretation error - frame does not exist", file = sys.stderr)
        case 56:
            print("Error: Interpretation error - missing value", file = sys.stderr)
        case 57:
            print("Error: Interpretation error - incorrect operand value", file = sys.stderr)
        case 58:
            print("Error: Interpretation error - incorrect string usage", file = sys.stderr)
    exit(errorCode)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="Source file", required=True)
parser.add_argument("--input", help="Input file", required=True)
args = vars(parser.parse_args())
#TODO: change exit code to 10

# Open source file
try:
    sourceFile = open(args["source"], "r")
except:
    exitError(11)

# Open input file
try:
    inputFile = open(args["input"], "r")
except:
    exitError(11)

# Parse xml
try:
    xml = XML.parse(sourceFile).getroot()
    if xml.tag != "program" and xml.attrib["language"] != "IPPcode21":
        raise Exception("ParseError")
    for instruction in xml:
        if instruction.tag != "instruction":
            raise Exception("ParseError")
        if "order" not in instruction.attrib or "opcode" not in instruction.attrib:
            raise Exception("ParseError")
        for arg in instruction:
            if arg.tag != "arg1" and arg.tag != "arg2" and arg.tag != "arg3":
                raise Exception("ParseError")
            if "type" not in arg.attrib:
                raise Exception("ParseError")
except Exception as exception:
    if exception.args[0] == "ParseError":
        exitError(32)
    else:
        exitError(31)



# Close files
sourceFile.close()
inputFile.close()