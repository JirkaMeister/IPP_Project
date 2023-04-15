# This file is the second part of the IPP 2023 project.
# sourceFile: intepret.py
# author: Jiri Charamza
# login: xchara04

import re
import argparse
import xml.etree.ElementTree as XML
import sys
from collections import deque

class Program:
    def __init__(self):
        self.order = 0
        self.instructions = []
        self.variables = {}
        self.dataStack = deque()
    
    def __repr__(self):
        return str("Program:" + re.sub(r'[,\]\[]', '', str(self.instructions)))
    
    def printState(self):
        print("Order: " + str(self.order), file = sys.stderr)
        print("Variables:")
        for variable in self.variables:
            print(" " + variable + ": value = " + str(self.variables[variable][0]) + "  " + str(self.variables[variable][1]), file = sys.stderr)
        #print("Data stack: " + str(self.dataStack), file = sys.stderr)
    
    def checkVariableExists(self, variable):
        if variable not in self.variables:
            exitError(54)

    def checkVariableType(self, variable, types = []):
        if self.variables[variable][1] not in types:
            exitError(53)
    
    def handleVariable(self, var):
        if var.type != "var":
            exitError(53)
        self.checkVariableExists(var.value)

    def handleSymbol(self, symb, allowedTypes = []):
        if symb.type == "var":
            self.checkVariableExists(symb.value)
            self.checkVariableType(symb.value, allowedTypes)
            return self.variables[symb.value]
        elif symb.type in allowedTypes or allowedTypes == []:
            return (symb.value, symb.type)
        else:
            exitError(32)


    def addInstruction(self, instruction):
        self.instructions.append(instruction)

    def sortByOrder(self):
        self.instructions.sort(key = lambda instruction: int(instruction.order))

    def executeProgram(self):
        while self.order < len(self.instructions):
            self.executeInstruction()

    def executeInstruction(self):
        instruction = self.instructions[self.order]
        self.order += 1
        getattr(self, instruction.opcode)(*instruction.args)
        self.printState()
        

    def MOVE(self, var, symb):
        self.handleVariable(var)
        symb = self.handleSymbol(symb)
        self.variables[var.value] = symb

    def CREATEFRAME(self):
        #TODO
        pass

    def PUSHFRAME(self):
        #TODO
        pass

    def POPFRAME(self):
        #TODO
        pass

    def DEFVAR(self, var):
        if var.type != "var":
            exitError(53)
        if var.value in self.variables:
            exitError(52)
        self.variables[var.value] = (None, None)

    def CALL(self, label):
        #TODO
        pass

    def RETURN(self):
        #TODO
        pass

    def PUSHS(self, symb):
        self.dataStack.append(symb)

    def POPS(self, var):
        self.checkVariableExists(var.value)
        self.variables[var.value] = self.dataStack.pop()

    def ADD(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int"])
        symb2 = self.handleSymbol(symb2, ["int"])
        self.variables[var.value] = (str(int(symb1[0]) + int(symb2[0])), "int")


    def SUB(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int"])
        symb2 = self.handleSymbol(symb2, ["int"])
        self.variables[var.value] = (str(int(symb1[0]) - int(symb2[0])), "int")

    def MUL(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int"])
        symb2 = self.handleSymbol(symb2, ["int"])
        self.variables[var.value] = (str(int(symb1[0]) * int(symb2[0])), "int")

    def IDIV(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int"])
        symb2 = self.handleSymbol(symb2, ["int"])
        if symb2[0] == 0:
            exitError(57)
        self.variables[var.value] = (str(int(symb1[0]) // int(symb2[0])), "int")

    def LT(self, var, symb1, symb2):
        #TODO nil
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool"])
        if symb1[1] == symb2[1]:
            self.variables[var.value] = (symb1[0] < symb2[0], "bool")

    def GT(self, var, symb1, symb2):
        #TODO nil
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool"])
        if symb1[1] == symb2[1]:
            self.variables[var.value] = (symb1[0] > symb2[0], "bool")

    def EQ(self, var, symb1, symb2):
        #TODO nil
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool"])
        if symb1[1] == symb2[1]:
            self.variables[var.value] = (symb1[0] == symb2[0], "bool")

    def AND(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["bool"])
        symb2 = self.handleSymbol(symb2, ["bool"])
        self.variables[var.value] = (symb1[0] and symb2[0], "bool")

    def OR(self, var, symb1, symb2):
        self.handleVariable(var)
        symb1 = self.handleSymbol(symb1, ["bool"])
        symb2 = self.handleSymbol(symb2, ["bool"])
        self.variables[var.value] = (symb1[0] or symb2[0], "bool")

    def NOT(self, var, symb):
        self.handleVariable(var)
        symb = self.handleSymbol(symb, ["bool"])
        self.variables[var.value] = (not symb[0], "bool")

    def INT2CHAR(self, var, symb):
        #TODO
        pass

    def STRI2INT(self, var, symb1, symb2):
        #TODO
        pass

    def READ(self, var, type):
        #TODO
        pass

    def WRITE(self, symb):
        #TODO
        pass

    def CONCAT(self, var, symb1, symb2):
        #TODO
        pass

    def STRLEN(self, var, symb):
        #TODO
        pass

    def GETCHAR(self, var, symb1, symb2):
        #TODO
        pass

    def SETCHAR(self, var, symb1, symb2):
        #TODO
        pass

    def TYPE(self, var, symb):
        #TODO
        pass

    def LABEL(self, label):
        #TODO
        pass

    def JUMP(self, label):
        #TODO
        pass

    def JUMPIFEQ(self, label, symb1, symb2):
        #TODO
        pass

    def JUMPIFNEQ(self, label, symb1, symb2):
        #TODO
        pass

    def EXIT(self, symb):
        #TODO
        pass

    def DPRINT(self, symb):
        #TODO
        pass

    def BREAK(self):
        #TODO
        pass
    

class Instruction:
    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode
        self.args = []

    def __repr__(self):
        return str("\n  Instruction: " + self.opcode + "  order=" + self.order + str(self.args))

    def addArg(self, arg):
        self.args.append(arg)


class Argument:
    def __init__(self, argumentType, value):
        self.type = argumentType
        self.value = value

    def __repr__(self):
        string = "\n      Arg: type=" + self.type
        if self.value != None:
            string += ", value=" + self.value
        return string


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
program.sortByOrder()

program.executeProgram()
# Close files
sourceFile.close()
inputFile.close()