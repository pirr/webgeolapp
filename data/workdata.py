import csv
import ipdb


def data_return(file):
    with open(file) as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        data = []
        for row in spamreader:
            data.append(row)
        #     print(row['id'], 
        #         row['source'],
        #         row['name'],
        #         row['pi'],
        #         row['lon'],
        #         row['lat'])
    return data

        
if __name__ == '__main__':
    data_return()
