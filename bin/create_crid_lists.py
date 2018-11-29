import os, sys
sys.path.insert(0, "D:\\Documents\\Coding\\Python\\Kivy\\projects\\Scheme")
from bin.crid_parser import CridParser

crid_dir = "html_captures\\Carrier_Routes_91941"
crid_html_list = os.listdir(crid_dir)
target_dir = "crid"

for crid_html in crid_html_list:
    with open(os.path.join(crid_dir, crid_html)) as infile:
        print("opened {}".format(crid_html))
        parser = CridParser(infile)
        filename = os.path.splitext(crid_html)[0]
        print("writing {}".format(filename+'.csv'))
        parser.parse_rows(os.path.join(target_dir,filename)+'.csv')
