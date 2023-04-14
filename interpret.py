# This file is the second part of the IPP 2023 project.
# sourceFile: intepret.py
# author: Jiri Charamza
# login: xchara04

import re
import argparse
import xml.etree.ElementTree as XML
import sys

class Program:
    def __init__(self):
        self.order = 0
        self.instructions = []
    
    def __repr__(self):
        return str("Program:" + str(self.instructions))

    def getInstruction(self): 
        instruction = self.instructions[self.order]
        self.order += 1
        return instruction

    def addInstruction(self, instruction):
        self.instructions.append(instruction)


class Instruction:
    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode
        self.args = []

    def __repr__(self):
        return str("\n  Instruction: " + self.opcode + str(self.args))

    def addArg(self, arg):
        self.args.append(arg)


class Argument:
    def __init__(self, argumentType, value):
        self.type = argumentType
        self.value = value

    def __repr__(self):
        if self.value:
            return str("\n    Arg: type=" + self.type + "  value=" + self.value)
        else:
            return str("\n    Arg: " + self.type)


class Frame:
    pass


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
try:
    args = vars(parser.parse_args())
except:
    exitError(10)

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

# Check XML structure ans save instructions and arguments
program = Program()

try:
    xml = XML.parse(sourceFile).getroot()
    if xml.tag != "program" and xml.attrib["language"] != "IPPcode21":
        raise Exception("XML structure")
    for instrXml in xml:

        # Check instruction structure
        if instrXml.tag != "instruction":
            raise Exception("XML structure")
        if "order" not in instrXml.attrib or "opcode" not in instrXml.attrib:
            raise Exception("XML structure")
        
        # Create and save instruction
        instruction = Instruction(instrXml.attrib["order"], instrXml.attrib["opcode"])
        program.addInstruction(instruction)
        
        for argXml in instrXml:

            # Check arguments structure
            if not re.match(r'arg[1-3]', argXml.tag):
                raise Exception("XML structure")
            if "type" not in argXml.attrib:
                raise Exception("XML structure")
            
            # Create and save argument
            argument = Argument(argXml.attrib["type"], argXml.text)
            instruction.addArg(argument)

except Exception as exception:
    if exception.args[0] == "XML structure":
        print("huh")
        exitError(32)
    else:
        exitError(31)

# Print instructions and arguments
print(re.sub(r'[,\]\[]', '', program.__repr__()), file = sys.stderr)


# Close files
sourceFile.close()
inputFile.close()