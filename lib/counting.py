import sys, os, pickle
sys.path.insert(0, os.getcwd())
from lib.create_db import Street
from collections import Counter, defaultdict

TARGET = 'routes.pickle'

def count(countObj, iterable):
    unique = {item.name for item in iterable}
    countObj.update(unique)

def search(db, name):
    leests = (mydb[key] for key in mydb.keys())
    found = []
    for leest in leests:
        for street in leest:
            if name == street.name:
                found.append(street)
    return found

with open(TARGET, 'rb') as f:
    mydb = pickle.load(f)
    leests = (mydb[key] for key in mydb.keys())
    c = Counter()
    for leest in leests:
        count(c, leest)

    for key in c.keys():
        if c[key] > 1:
            print("{} : {}".format(key, c[key]))

    print('+'*50)
    leests = (mydb[key] for key in mydb.keys())
    check = defaultdict(set)
    for leest in leests:
        for item in leest:
            check[item.name].add(item.route)

    checked = {k:v for k,v in check.items() if len(v) > 1}
    for k,v in checked.items():
        print(k, v)

    with open('special.pickle', 'wb') as out:
        pickle.dump(checked, out)
