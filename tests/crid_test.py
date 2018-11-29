import sys, os
sys.path.insert(0, "D:\\Documents\\coding\\Python\\Kivy\\projects\Scheme")
#print(sys.path)
from bin.crid_parser import CridParser

target_file = "./Html_captures/Carrier_Routes_91941/C002.html"

target = open(target_file)
parse = CridParser(target)
parse.parse_rows('test.csv')
