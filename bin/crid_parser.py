import csv, re
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

reg_street = "(?P<street>[\w\s]+) (?P<suffix>[\w]+)$"
regex = re.compile(reg_street)
target_col = 1

class CridParser():
    def __init__(self, html_file):
        self.soup = BeautifulSoup(html_file, 'html5lib')

    def parse_rows(self, outfile):
        """
        parses self.soup to create a .csv file that includes
        the contents from the second collumn (street name)
        """
        table = self.soup.find('table', class_='Tableresultborder')
        tbody = table.find('tbody')
        rowlist = tbody.find_all('tr')
        out_rows = []
        for i in range(2, len(rowlist)-1):
            row = rowlist[i]
            if len(row) <= 1:
                break
            #with rowlist[i].find_all('td') as cells:
            cells = rowlist[i].find_all('td')
            font_elem = cells[target_col].find('font')
            full_street = font_elem.string
            #full_street = row.td.td.string
            street, suffix = self.parse_street(full_street)
            out_row = ['', '', '', street, suffix]
            if out_row not in out_rows:
                out_rows.append(['', '', '', street, suffix])
            #out_rows.append(out_row)
        self.output_csv(out_rows, outfile)

    def output_csv(self, out_rows, outfile):
        """outputs csv file"""
        with open(outfile, 'w', newline='') as fp:
            streetwriter = csv.writer(fp)
            for row in out_rows:
                streetwriter.writerow(row)

    def parse_street(self, full_street):
        """
        receives string, uses regex to separate street
        name from stree suffix
        """
        match = regex.search(full_street)
        if match != None:
            return match.group('street'), match.group('suffix')
        else:
            return full_street, ''
