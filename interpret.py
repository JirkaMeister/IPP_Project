# This file is the second part of the IPP 2023 project.
# sourceFile: intepret.py
# author: Jiri Charamza
# login: xchara04

import re
import argparse
import xml.etree.ElementTree as XML
import sys
import io
from collections import deque

class Program:
    def __init__(self):
        self.order = 0
        self.instructions = []
        self.globalFrame = Frame()
        self.localFrame = None
        self.temporaryFrame = None
        self.frameStack = deque()
        self.dataStack = deque()
        self.labels = {}
        self.callStack = deque()
        self.allowUndefinedVariables = False
    
    def __repr__(self):
        return str("Program:" + re.sub(r'[,\]\[]', '', str(self.instructions)))
    
    def printState(self):
        

        print("Instruction: " + str(self.instructions[self.order - 1].opcode), file = sys.stderr)
        print("Order: " + str(self.order), file = sys.stderr)
        print("Call stack: " + str(self.callStack), file = sys.stderr)
        print("Frame stack count: " + str(len(self.frameStack)) + " (Not including local frame on top)", file = sys.stderr)
        print("Global frame variables: " + str(self.globalFrame), file = sys.stderr)
        print("Local frame variables: " + str(self.localFrame), file = sys.stderr)
        print("Temporary frame variables: " + str(self.temporaryFrame) + "\n", file = sys.stderr)

    
            
    
    def checkVariableType(self, var, types = []):
        var = self.getVariable(var)
        if var[1] == None and self.allowUndefinedVariables == False:
            exitError(56)
        elif len(types) != 0 and var[1] not in types:   #puvodně [variable][1], ale bez [1] to fixlo problem
            exitError(53)
        
    
    # Expects the Argument object
    def handleVariable(self, var):
        if var.type != "var":
            exitError(53)
        if var.value[:2] == "GF" and var.value[3:] not in self.globalFrame.variables:
            exitError(54)
        elif var.value[:2] == "TF":
            if self.temporaryFrame == None:
                exitError(55)
            elif var.value[3:] not in self.temporaryFrame.variables:
                exitError(54)
        elif var.value[:2] == "LF":
            if self.localFrame == None:
                exitError(55)
            elif var.value[3:] not in self.localFrame.variables:
                exitError(54)

    # Expects the Argument object
    def assignVariable(self, var, value, type):
        self.handleVariable(var)
        if var.value[:2] == "GF":
            self.globalFrame.variables[var.value[3:]] = (value, type)
        elif var.value[:2] == "TF":
            self.temporaryFrame.variables[var.value[3:]] = (value, type)
        elif var.value[:2] == "LF":
            self.localFrame.variables[var.value[3:]] = (value, type)

    # Expects the Argument object
    def getVariable(self, var):
        self.handleVariable(var)
        if var.value[:2] == "GF":
            return self.globalFrame.variables[var.value[3:]]
        elif var.value[:2] == "TF":
            return self.temporaryFrame.variables[var.value[3:]]
        elif var.value[:2] == "LF":
            return self.localFrame.variables[var.value[3:]]

    # Expects the Argument object
    def handleSymbol(self, symb, allowedTypes = []):
        if symb.type == "var":
            self.handleVariable(symb)
            self.checkVariableType(symb, allowedTypes)
            var = self.getVariable(symb)
            return var
        elif symb.type in allowedTypes or allowedTypes == []:
            if symb.type == "string":
                if symb.value:
                    symb.value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1))), str(symb.value))
                else:
                    symb.value = ""
            elif symb.type == "bool":
                if symb.value.lower() == "true":
                    symb.value = True
                else:
                    symb.value = False
            elif symb.type == "int":
                symb.value = int(symb.value)
            return (symb.value, symb.type)
        else:
            exitError(53)
    
    def handleLabel(self, label):
        if label.type != "label":
            exitError(53)
        if label.value not in self.labels.keys():
            exitError(52)
    
    def checkForLabels(self):
        for instruction in self.instructions:
            if instruction.opcode == "LABEL":
                label = instruction.args[0]
                if label.type != "label":
                    exitError(53)
                if label.value in self.labels:
                    exitError(52)
                self.labels[label.value] = int(instruction.order)

    def addInstruction(self, instruction):
        self.instructions.append(instruction)

    def executeProgram(self):
        self.instructions.sort(key = lambda instruction: int(instruction.order))
        self.checkForLabels()
        while self.order < len(self.instructions):
            self.executeInstruction()

    def executeInstruction(self):
        instruction = self.instructions[self.order]
        self.order += 1
        getattr(self, instruction.opcode)(*instruction.args)

    def MOVE(self, var, symb):
        self.handleVariable(var)
        symb = self.handleSymbol(symb)
        if symb[1] == "string":
            self.assignVariable(var, re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1))), str(symb[0])) , "string")
        else:
            self.assignVariable(var, symb[0], symb[1])
    
    def CREATEFRAME(self):
        self.temporaryFrame = Frame()

    def PUSHFRAME(self):
        if self.temporaryFrame != None:
            if self.localFrame != None:
                self.frameStack.append(self.localFrame)
            self.localFrame = self.temporaryFrame
            self.temporaryFrame = None
        else:
            exitError(55)

    def POPFRAME(self):
        if self.localFrame != None:
            self.temporaryFrame = self.localFrame
            if len(self.frameStack) > 0:
                self.localFrame = self.frameStack.pop()
            else:
                self.localFrame = None
        else:
            exitError(55)
    
    def DEFVAR(self, var):
        if var.type != "var":
            exitError(53)
        if var.value[:2] == "GF":
            if var.value[3:] in self.globalFrame.variables:
                exitError(52)
            else:
                self.globalFrame.variables[var.value[3:]] = (None, None)
        elif var.value[:2] == "TF":
            if self.temporaryFrame == None:
                exitError(55)
            elif var.value[3:] in self.temporaryFrame.variables:
                exitError(52)
            else:
                self.temporaryFrame.variables[var.value[3:]] = (None, None)
        elif var.value[:2] == "LF":
            if self.localFrame == None:
                exitError(55)
            elif var.value[3:] in self.localFrame.variables:
                exitError(52)
            else:
                self.localFrame.variables[var.value[3:]] = (None, None)
    
    def CALL(self, label):
        self.handleLabel(label)
        self.callStack.append(self.order)
        if label.value in self.labels:
            self.order = self.labels[label.value]
        else:
            exitError(52)

    def RETURN(self):
        if len(self.callStack) > 0:
            self.order = self.callStack.pop()
        else:
            exitError(56)

    def PUSHS(self, symb):
        self.dataStack.append(self.handleSymbol(symb))

    def POPS(self, var):
        try:
            self.handleVariable(var)
            symb = self.dataStack.pop()
            self.assignVariable(var, symb[0], symb[1])
        except IndexError:
            exitError(56)

    def ADD(self, var, symb1, symb2):
        self.assignVariable(var, int(self.handleSymbol(symb1, ["int"])[0]) + int(self.handleSymbol(symb2, ["int"])[0]), "int")


    def SUB(self, var, symb1, symb2):
        self.assignVariable(var, int(self.handleSymbol(symb1, ["int"])[0]) - int(self.handleSymbol(symb2, ["int"])[0]), "int")

    def MUL(self, var, symb1, symb2):
        self.assignVariable(var, int(self.handleSymbol(symb1, ["int"])[0]) * int(self.handleSymbol(symb2, ["int"])[0]), "int")

    def IDIV(self, var, symb1, symb2):
        try:
            self.assignVariable(var, int(self.handleSymbol(symb1, ["int"])[0]) // int(self.handleSymbol(symb2, ["int"])[0]), "int")
        except ZeroDivisionError:
            exitError(57)

    def LT(self, var, symb1, symb2):
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool"])
        if symb1[1] == symb2[1]:
            self.assignVariable(var, symb1[0] < symb2[0], "bool")
        else:
            exitError(53)

    def GT(self, var, symb1, symb2):
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool"])
        if symb1[1] == symb2[1]:
            self.assignVariable(var, symb1[0] > symb2[0], "bool")
        else:
            exitError(53)

    def EQ(self, var, symb1, symb2):
        symb1 = self.handleSymbol(symb1, ["int", "string", "bool", "nil"])
        symb2 = self.handleSymbol(symb2, ["int", "string", "bool", "nil"])
        if symb1[1] == symb2[1]:
            self.assignVariable(var, symb1[0] == symb2[0], "bool")
        elif symb1[1] == "nil" or symb2[1] == "nil":
            self.assignVariable(var, False, "bool")
        else:
            exitError(53)

    def AND(self, var, symb1, symb2):
        self.assignVariable(var, self.handleSymbol(symb1, ["bool"])[0] and self.handleSymbol(symb2, ["bool"])[0], "bool")

    def OR(self, var, symb1, symb2):
        symb1 = self.handleSymbol(symb1, ["bool"])
        symb2 = self.handleSymbol(symb2, ["bool"])
        self.assignVariable(var, symb1[0] or symb2[0], "bool")

    def NOT(self, var, symb):
        self.assignVariable(var, not self.handleSymbol(symb, ["bool"])[0], "bool")

    def INT2CHAR(self, var, symb):
        try:
            self.assignVariable(var, chr(int(self.handleSymbol(symb, ["int"])[0])), "string")
        except ValueError:
            exitError(58)

    def STRI2INT(self, var, symb1, symb2):
        try:
            symb2 = int(self.handleSymbol(symb2, ["int"])[0])
            if symb2 < 0:
                exitError(58)
            self.assignVariable(var, ord(self.handleSymbol(symb1, ["string"])[0][symb2]), "int")
        except ValueError:
            exitError(58)
        except IndexError:
            exitError(58)

    def READ(self, var, type):
        inputData = inputFile.readline()
        if type.value not in ["int", "bool", "string"]:
            exitError(53)
        if len(inputData) > 0 and inputData[-1] == "\n":
            inputData = inputData[:-1]
        if type.value == "bool":
            self.assignVariable(var, inputData.lower() == "true", "bool")
        elif type.value == "int" and re.match(r"^-?[0-9]+$", inputData):
            self.assignVariable(var, int(inputData), "int")
        elif type.value == "string" and re.match(r"^([^\s#]|(\\[0-9]{3}))*$", inputData):
            self.assignVariable(var, re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1))), inputData), "string") #check
        else:
            self.assignVariable(var, None, "nil")
        #TODO zmenit na input()
    
    def WRITE(self, symb):
        symb = self.handleSymbol(symb)
        if symb[1] == "nil":
            print("", end="")
        elif symb[1] == "bool":
            print(str(symb[0]).lower(), end="")
        else:
            print(symb[0], end="")
    
    def CONCAT(self, var, symb1, symb2):
        self.assignVariable(var, self.handleSymbol(symb1, ["string"])[0] + self.handleSymbol(symb2, ["string"])[0], "string")

    def STRLEN(self, var, symb):
        self.assignVariable(var, len(self.handleSymbol(symb, ["string"])[0]), "int")

    def GETCHAR(self, var, symb1, symb2):
        try:
            if int(self.handleSymbol(symb2, ["int"])[0]) < 0:
                exitError(58)
            self.assignVariable(var, self.handleSymbol(symb1, ["string"])[0][int(self.handleSymbol(symb2, ["int"])[0])], "string")
        except IndexError:
            exitError(58)

    def SETCHAR(self, var, symb1, symb2):
        self.handleVariable(var)
        self.checkVariableType(var, "string")
        varTmp = self.getVariable(var)
        symb1 = self.handleSymbol(symb1, ["int"])
        symb2 = self.handleSymbol(symb2, ["string"])
        if len(var.value) > symb1[0] and symb1[0] >= 0 and len(symb2[0]) > 0:
            self.assignVariable(var, varTmp[0][:int(symb1[0])] + symb2[0][0] + varTmp[0][int(symb1[0])+1:], "string")
        else:
            exitError(58)
        #TODO

    def TYPE(self, var, symb):
        self.handleVariable(var)
        self.allowUndefinedVariables = True
        symb = self.handleSymbol(symb)
        if symb[1] == None:
            self.assignVariable(var, "", "string")
        else:
            self.assignVariable(var, symb[1], "string")
        self.allowUndefinedVariables = False

    def LABEL(self, label):
        if label.value in self.labels and self.labels[label.value] != self.order:
            exitError(52)
        self.labels[label.value] = self.order

    def JUMP(self, label):
        self.handleLabel(label)
        self.order = self.labels[label.value]

    def JUMPIFEQ(self, label, symb1, symb2):
        self.handleLabel(label)
        symb1 = self.handleSymbol(symb1)
        symb2 = self.handleSymbol(symb2)
        if symb1[1] == symb2[1]:
            if symb1[0] == symb2[0]:
                self.order = self.labels[label.value]
        elif symb1[1] == "nil" or symb2[1] == "nil":
            return
        else:
            exitError(53)
        #TODO nil
            

    def JUMPIFNEQ(self, label, symb1, symb2):
        self.handleLabel(label)
        symb1 = self.handleSymbol(symb1)
        symb2 = self.handleSymbol(symb2)
        if symb1[1] == symb2[1]:
            if symb1[0] != symb2[0]:
                self.order = self.labels[label.value]
        elif symb1[1] == "nil" or symb2[1] == "nil":
            self.order = self.labels[label.value]
        else:
            exitError(53)

    def EXIT(self, symb):
        symb = self.handleSymbol(symb, ["int"])
        if int(symb[0]) < 0 or int(symb[0]) > 49:
            exitError(57)
        else:
            exit(int(symb[0]))

    def DPRINT(self, symb):
        symb = self.handleSymbol(symb)
        print(symb, file=sys.stderr)

    def BREAK(self):
        self.printState()
    

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
    def __init__(self):
        self.variables = {}

    def __repr__(self):
        return str(self.variables)
    



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
    #program.printState()
    exit(errorCode)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Source file to be interpreted", required=False)
    parser.add_argument("--input", help="Input file", required=False)
    try:
        args = vars(parser.parse_args())
    except:
        if len(sys.argv) < 2:
            exitError(10)
        else:
            exit(0)

    # Open source file
    if args["source"] != None:
        try:
            sourceFile = open(args["source"], "r")
        except:
            exitError(11)
    else:
        sourceFile = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Open input file
    if args["input"] != None:
        try:
            inputFile = open(args["input"], "r")
        except:
            exitError(11)
    else:
        inputFile = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    if args["source"] == None and args["input"] == None:
        exitError(10)

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

    # Handle XML errors
    except Exception as exception:
        if exception.args[0] == "XML structure":
            exitError(32)
        else:
            exitError(31)

    # Execute program
    program.executeProgram()

    # Close files
    sourceFile.close()
    inputFile.close()