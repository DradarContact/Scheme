import sys, os, csv, pickle
from collections import namedtuple
sys.path.insert(0, os.getcwd())

NUMSTART_COL = 0
NUMSTOP_COL = 1
ORDER_COL = 2
NAMSTREET_COL = 3
TYPESTREET_COL = 4

outfile = 'routes'
target_dir = os.getcwd() + os.sep + 'crid'

Street = namedtuple('Street', [
    'start',
    'stop',
    'name',
    'type',
    'route'
])

def parse_csv(directory):
    '''
    parses given directory that contains csv files. CSV files named after
    carrier route, contain street information, creates namedtuples for
    streets and stores in a dictionary with the carrier route as key
    '''

    # get files from directory
    filepath = os.getcwd()
    files = (f for f in os.listdir(directory))
    # open each file

    db = {}
    filepath = os.getcwd()
    for f in files:
        with open(target_dir + os.sep + f, 'r') as file:
            db[f.rstrip('.csv')] = [street for street in gen_streets(file, f)]
    return db

def gen_streets(file, route):
    reader = csv.reader(file)
    for row in reader:
        start_num = row[NUMSTART_COL]
        stop_num = row[NUMSTOP_COL]
        order_num = row[ORDER_COL]
        street_nam = row[NAMSTREET_COL]
        street_typ = row[TYPESTREET_COL]

        this_street = Street(
            start_num,
            stop_num,
            street_nam,
            street_typ,
            route.rstrip('.csv')
        )
        yield this_street

class DBPickler(pickle.Pickler):
    def persistent_id(self, obj):
        if isinstance(obj, Street):
            return "Street"
        else:
            return None

if __name__ == '__main__':
    mydb = parse_csv('crid')
    with open(outfile+'.pickle', 'wb') as out:
        pickle.dump(mydb, out)


    # parse lines
