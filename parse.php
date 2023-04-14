<?php
# This file is the first part of the IPP 2023 project.
# sourceFile: parse.php
# author: Jiri Charamza
# login: xchara04



# Function for checking if given string is a variable
function checkVariable($variable)
{
    if (preg_match('/^(GF|LF|TF)@([a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/', $variable)) return true;
    else return false;
}

# Function for checking if given string is a literal
function checkLiteral($literal)
{
    if (checkInt($literal) || checkBool($literal) || checkString($literal) || checkNil($literal)) return true;
    else return false;
}

# Function for checking if given string is a label
function checkLabel($label)
{
    if (preg_match('/^([a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/', $label)) return true;
    else return false;
}

# Functions for checking if given string is a integer
function checkInt($int)
{
    if (preg_match('/(int)@(-|\+)?([0-9]+)$/', $int)) return true;
    else return false;
}
# Functions for checking if given string is a boolean
function checkBool($bool)
{
    if (preg_match('/bool@true|false$/', $bool)) return true;
    else return false;
}

# Functions for checking if given string is a string
function checkString($string)
{
    if (preg_match('/^string@((\\\\[0-9]{3})|[^\\\\\s#])*$/', $string)) return true;
    else return false;
}

# Function for checking if given string is a nil
function checkNil($nil)
{
    if (preg_match('/nil@nil$/', $nil)) return true;
    else return false;
}

# Function for checking if given string is a type
function checkType($type)
{
    if (preg_match('/^(int|string|bool)$/', $type)) return true;
    else return false;
}

# Function for checking if argument is variable and ending program if not
function handleVariable($variable)
{
    if (!checkVariable($variable))
    {
        echo("Incorrect variable.");
        exit(23);
    }
}

# Function for checking if argument is symbol and ending program if not
function handleSymbol($symbol)
{
    if (!checkVariable($symbol) && !checkLiteral($symbol))
    {
        echo("Incorrect variable or literal.");
        exit(23);
    }
}

# Function for checking if argument is label and ending program if not
function handleLabel($label)
{
    if (!checkLabel($label))
    {
        echo("Incorrect label.");
        exit(23);
    }
}

# Function for checking if argument is type and ending program if not
function handleType($type)
{
    if (!checkType($type))
    {
        echo("Incorrect type.");
        exit(23);
    }
}

# Function for replacing special characters in strings
function handleString(&$string)
{
    $string = preg_replace('/&/', '&amp;', $string);
    $string = preg_replace('/>/', '&gt;', $string);
    $string = preg_replace('/</', '&lt;', $string);
}

# Function for checking number of arguments and ending program if not correct
function checkArgCount($argCount, $expectedCount)
{
    if ($argCount != $expectedCount)
    {
        echo("Incorrect number of arguments.");
        exit(23);
    }
}

# Function for printing arguments in XML format
function printArg($arg, $argNumber)
{
    if (checkVariable($arg))
    {
        handleString($arg);
        echo("\t\t<arg".$argNumber." type=\"var\">".$arg."</arg".$argNumber.">\n");
    }
    else if (checkType($arg))
    {
        echo("\t\t<arg".$argNumber." type=\"type\">".$arg."</arg".$argNumber.">\n");
    }
    else if(checkLabel($arg))
    {
        handleString($arg);
        echo("\t\t<arg".$argNumber." type=\"label\">".$arg."</arg".$argNumber.">\n");
    }
    else if(checkString($arg))
    {
        handleString($arg);
        echo("\t\t<arg".$argNumber." type=\"string\">".substr($arg, 7)."</arg".$argNumber.">\n");
    }
    else if (checkInt($arg))
    {
        echo("\t\t<arg".$argNumber." type=\"int\">".substr($arg, 4)."</arg".$argNumber.">\n");
    }
    else if (checkBool($arg))
    {
        echo("\t\t<arg".$argNumber." type=\"bool\">".substr($arg, 5)."</arg".$argNumber.">\n");
    }
    else if (checkNil($arg))
    {
        echo("\t\t<arg".$argNumber." type=\"nil\">".substr($arg, 4)."</arg".$argNumber.">\n");
    }
}


ini_set('display_errors', 'stderr');

# Checks if there are correct number of arguments
if ($argc > 2)
{
    echo("Incorrect number of arguments.\n");
    exit(10);
}
else if($argc == 2)
{
    # Checks if --help argument was given
    if ($argv[1] == "--help")
    {
       echo("This script is used for parsing IPPcode23 code into XML format.\n");
       echo("Usage: php parse.php [--help] <src.ippc\n");
       exit(0);
    }
    else
    {
        echo("Incorrect argument.\n");
        exit(10);
    }
}
$firstLine = true;
$instructionCount = 0;

# Main loop of program, reads line by line
while ($line = fgets(STDIN))
{
    # Removes comments
    $line = preg_replace('/#.*$/', '', $line);
    # Replaces multiple whitespaces with single space
    $line = preg_replace('/  +/', ' ', trim($line));
    # Removes end of line
    $line = preg_replace('/\n/', '', $line); # For Linux
    $line = preg_replace('/\r/', '', $line); # For Windows

    # Skips current line if it is empty
    if (empty($line)) continue;

    # Checks header
    if ($firstLine)
    {
        $firstLine = false;
        if (!preg_match('/^(\.IPPcode23)$/', $line))
        {
            echo("Incorrect header.");
            exit(21);
        }
        echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        echo("<program language=\"IPPcode23\">\n");
        continue;
    }

    # Splits line into tokens
    $lineTokens = explode(' ', $line);

    # Updates instruction count
    $instructionCount++;

    # Prints instruction
    echo("\t<instruction order=\"".$instructionCount."\" opcode=\"".strtoupper($lineTokens[0])."\">\n");

    # Checks validity of instruction and sets the number of arguments
    switch(strtoupper($lineTokens[0]))
    {
        # Frame instructions and calls
        case "MOVE":
            $argTypes = array("variable", "symbol");
            break;
        case "CREATEFRAME":
            $argTypes = array();
            break;
        case "PUSHFRAME":
            $argTypes = array();
            break;
        case "POPFRAME":
            $argTypes = array();
            break;
        case "DEFVAR":
            $argTypes = array("variable");
            break;
        case "CALL":
            $argTypes = array("label");
            break;
        case "RETURN":
            $argTypes = array();
            break;
        
        # Data stack instructions
        case "PUSHS":
            $argTypes = array("symbol");
            break;
        case "POPS":
            $argTypes = array("variable");
            break;
        
        # Arithmetic instructions
        case "ADD":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "SUB":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "MUL":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "IDIV":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "LT":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "GT":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "EQ":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "AND":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "OR":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "NOT":
            $argTypes = array("variable", "symbol");
            break;
        case "INT2CHAR":
            $argTypes = array("variable", "symbol");
            break;
        case "STRI2INT":
            $argTypes = array("variable", "symbol", "symbol");
            break;

        # Input/Output instructions
        case "READ":
            $argTypes = array("variable", "type");
            break;
        case "WRITE":
            $argTypes = array("symbol");
            break;
            
        # String instructions
        case "CONCAT":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "STRLEN":
            $argTypes = array("variable", "symbol");
            break;
        case "GETCHAR":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        case "SETCHAR":
            $argTypes = array("variable", "symbol", "symbol");
            break;
        
        # Type instructions
        case "TYPE":
            $argTypes = array("variable", "symbol");
            break;
        
        # Program flow instructions
        case "LABEL":
            $argTypes = array("label");
            break;
        case "JUMP":
            $argTypes = array("label");
            break;
        case "JUMPIFEQ":
            $argTypes = array("label", "symbol", "symbol");
            break;
        case "JUMPIFNEQ":
            $argTypes = array("label", "symbol", "symbol");
            break;
        case "EXIT":
            $argTypes = array("symbol");
            break;
        
        # Debug instructions
        case "DPRINT":
            $argTypes = array("symbol");
            break;
        case "BREAK":
            $argTypes = array();
            break;

        default:
            echo("Unknown instruction.");
            exit(22);
    }
    # Checks number of arguments, their validity and prints them
    checkArgCount(count($lineTokens) - 1, count($argTypes));
    for ($i = 1; $i <= count($argTypes); $i++)
    {
        if ($argTypes[$i - 1] == "variable")
        {
            handleVariable($lineTokens[$i]);
        }
        else if ($argTypes[$i - 1] == "symbol")
        {
            handleSymbol($lineTokens[$i]);
        }
        elseif ($argTypes[$i - 1] == "label")
        {
            handleLabel($lineTokens[$i]);
        }
        elseif ($argTypes[$i - 1] == "type")
        {
            handleType($lineTokens[$i]);
        }
        printArg($lineTokens[$i], $i);
    }

    # Prints end of instruction
    echo("\t</instruction>\n");

}
# Prints end of program
echo("</program>");

exit(0);
?>