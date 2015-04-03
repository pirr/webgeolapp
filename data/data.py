import csv
import ipdb

def data():
    with open('test.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            print(row['id'], 
                row['source'],
                row['name'],
                row['pi'],
                row['lon'],
                row['lat'])

if __name__ == '__main__':
    data()
