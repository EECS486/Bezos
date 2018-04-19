"""Metadata Parser document"""

import os
import sys
import json
import re

class metadata:
    def __init__(self, productID, title, price, imURL, alsoBought, alsoViewed, boughtTogether, salesRank, categories):
        self.productID = productID
        self.title = title
        self.price = price
        self.imURL = imURL
        self.alsoBought = alsoBought
        self.alsoViewed = alsoViewed
        self.boughtTogether = boughtTogether
        self.salesRank = salesRank
        self.categories = categories
        # metrics
        self.numAlsoBought = len(alsoBought)
        self.numAlsoViewed = len(alsoViewed)
        self.numAlsoBoughtTogether = len(boughtTogether)

    def to_dict(self):
        return {
            'productID': self.x,
            'title': self.y,
            'price': self.price,
            'imURL': self.imURL,
            'alsoBought': self.alsoBought,
            'alsoViewed': self.alsoViewed,
            'boughtTogether': self.boughtTogether,
            'salesRank': self.salesRank,
            'categories': self.categories,
            'numAlsoBought': self.numAlsoBought,
            'numAlsoViewed': self.numAlsoViewed,
            'numAlsoBoughtTogether': self.numAlsoBoughtTogether,
        }

    def getPrintString(self):
        printString = "Reviewer ID: " + str(self.productID) + "\n"
        printString += "Product ID: " + str(self.title) + "\n"
        printString += "Up Votes: " + str(self.price) + "\n"
        printString += "Total Votes: " + str(self.alsoBought) + "\n"
        printString += "Unix Review Time: " + str(self.alsoViewed) + "\n"
        printString += "Unix Review Time: " + str(self.boughtTogether) + "\n"
        return printString


# General review data intake function
def readInMetadataDecision(fileName):
    print("Returning Metadata Structure")
    return readInMetadata(fileName)

# get the metadata
def readInMetadata(fileName):
    metadataOut = {}

    for line in open(fileName, 'r'):
        # get json data from line of file
        strictJSON = json.dumps(eval(line))
        data = json.loads(strictJSON)

        # parts of metadata
        productID = data['asin']
        title = data['title'] if 'title' in data else ""
        price = float(data['price']) if 'price' in data else -1
        imURL = data['imUrl'] if 'imUrl' in data else ""
        relatedDict = data['related'] if 'related' in data else {}
        alsoBought = relatedDict['also_bought'] if 'also_bought' in relatedDict else []
        alsoViewed = relatedDict['also_viewed'] if 'also_viewed' in relatedDict else []
        boughtTogether = relatedDict['bought_together'] if 'bought_together' in relatedDict else []
        salesRank = data['salesRank'] if 'salesRank' in data else {}
        salesRank = next(iter(salesRank.values())) if len(salesRank) else -1
        categories = data['categories']

        metaEntry = metadata(productID, title, price, imURL, alsoBought, alsoViewed, boughtTogether, salesRank, categories)
        metadataOut[productID] = metaEntry

    print("Metadata structure written")

    return metadataOut


def main():
    print('___Start of Metadata Function___')

    fileName = 'meta_Cell_Phones_and_Accessories.json'
    if len(sys.argv) == 2:
        fileName = sys.argv[1]
    print('running on file: ' + str(fileName) + '\n')

    metadata = readInMetadataDecision(fileName)

    return metadata

if __name__ == '__main__':
    print('Main Function Beginning')
    main()
