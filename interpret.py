# This file is the second part of the IPP 2023 project.
# sourceFile: intepret.py
# author: Jiri Charamza
# login: xchara04

import re
import argparse
import xml.etree.ElementTree

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="Source file", required=True)
parser.add_argument("--input", help="Input file", required=True)
args = vars(parser.parse_args())

