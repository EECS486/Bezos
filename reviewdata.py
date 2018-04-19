import json
import sys
import os.path


# container class for review information
class Review:
    def __init__(self, reviewerID, productID, upVotes, totalVotes, reviewText, unixReviewTime, overallRating):
        self.reviewerID = reviewerID
        self.productID = productID
        self.upVotes = upVotes
        self.totalVotes = totalVotes
        self.reviewText = reviewText
        self.unixReviewTime = unixReviewTime
        self.overallRating = overallRating
        # metrics
        self.favorableRating = float(upVotes) / float(totalVotes)
        self.reviewAge = 0
        # reviewer dict
        self.reviewedAlsoBought = 0
        self.reviewedAlsoViewed = 0
        self.reviewedAlsoBoughtTogether = 0
        self.NumberOfUserReviews = 0
        self.AverageReviewRating = 0
        # product dict
        self.reviewDeviationFromMean = 0
        self.reviewProductMean = 0
        # nlp library
        self.reviewLength = 0
        self.numberStopWords = 0
        self.numberOfPunctuations = 0
        self.averageWordLength = 0
        self.averageSentanceLength = 0
        self.numberExclamationPoints = 0
        self.numberQuestionMarks = 0
        self.readability = 0
        self.namedEntities = 0
        self.numberNouns = 0
        self.numberPassiveVerbs = 0
        self.numberActiveVerbs = 0
        self.numberAdjectives = 0
        self.numberPronous = 0
        self.helpfulLabel = "NA"

    def getPrintString(self):
        printString = "Reviewer ID: " + str(self.reviewerID) + "\n"
        printString += "Product ID: " + str(self.productID) + "\n"
        printString += "Up Votes: " + str(self.upVotes) + "\n"
        printString += "Total Votes: " + str(self.totalVotes) + "\n"
        printString += "overallRating: " + str(self.overallRating) + "\n"
        printString += "favorableRating: " + str(self.favorableRating) + "\n"
        printString += "reviewAge: " + str(self.reviewAge) + "\n"
        printString += "reviewedAlsoBought: " + str(self.reviewedAlsoBought) + "\n"
        printString += "reviewedAlsoViewed: " + str(self.reviewedAlsoViewed) + "\n"
        printString += "reviewedAlsoBoughtTogether: " + str(self.reviewedAlsoBoughtTogether) + "\n"
        printString += "AverageReviewRating: " + str(self.AverageReviewRating) + "\n"
        printString += "reviewDeviationFromMean: " + str(self.reviewDeviationFromMean) + "\n"
        printString += "reviewProductMean: " + str(self.reviewProductMean) + "\n"
        printString += "reviewLength: " + str(self.reviewLength) + "\n"
        printString += "numberStopWords: " + str(self.numberStopWords) + "\n"
        printString += "numberOfPunctuations: " + str(self.numberOfPunctuations) + "\n"
        printString += "averageWordLength: " + str(self.averageWordLength) + "\n"
        printString += "averageSentanceLength: " + str(self.averageSentanceLength) + "\n"
        printString += "numberExclamationPoints: " + str(self.numberExclamationPoints) + "\n"
        printString += "numberQuestionMarks: " + str(self.numberQuestionMarks) + "\n"
        printString += "readability: " + str(self.readability) + "\n"
        printString += "namedEntities: " + str(self.namedEntities) + "\n"
        printString += "numberNouns: " + str(self.numberNouns) + "\n"
        printString += "numberPassiveVerbs: " + str(self.numberPassiveVerbs) + "\n"
        printString += "numberActiveVerbs: " + str(self.numberActiveVerbs) + "\n"
        printString += "numberAdjectives: " + str(self.numberAdjectives) + "\n"
        printString += "numberPronous: " + str(self.numberPronous) + "\n"
        printString += "helpfulLabel: " + str(self.helpfulLabel) + "\n"

        return printString

    def to_dict(self):
        return {
            'upVotes': self.upVotes,
            'totalVotes': self.totalVotes,
            'overallRating': self.overallRating,
            'favorableRating' : self.favorableRating,
            'reviewAge': self.reviewAge,
            'reviewedAlsoBought': self.reviewedAlsoBought,
            'reviewedAlsoViewed': self.reviewedAlsoViewed,
            'reviewedAlsoBoughtTogether': self.reviewedAlsoBoughtTogether,
            'NumberOfUserReviews': self.NumberOfUserReviews,
            'AverageReviewRating': self.AverageReviewRating,
            'reviewDeviationFromMean': self.reviewDeviationFromMean,
            'reviewProductMean': self.reviewProductMean,
            'reviewLength': self.reviewLength,
            'numberStopWords': self.numberStopWords,
            'numberOfPunctuations': self.numberOfPunctuations,
            'averageWordLength': self.averageWordLength,
            'averageSentanceLength': self.averageSentanceLength,
            'numberExclamationPoints': self.numberExclamationPoints,
            'numberQuestionMarks': self.numberExclamationPoints,
            'namedEntities': self.namedEntities,
            'numberNouns': self.numberNouns,
            'numberPassiveVerbs': self.numberPassiveVerbs,
            'numberActiveVerbs': self.numberActiveVerbs,
            'numberAdjectives': self.numberAdjectives,
            'numberPronous': self.numberPronous,
            'readability': self.readability,
            'helpfulLabel': self.helpfulLabel
        }

# Read in review data if there is no pre calculated file
def readInReviewRaw(fileName, preCalcFileName, minVoteThreshold, minReviewLength):
    reviewsList = []
    dataStore = []

    for line in open(fileName, 'r'):
        # Get data from json file
        data = json.loads(line)

        # Grab each data component
        reviewerID = data['reviewerID']
        productID = data['asin']
        upVotes = data['helpful'][0]
        totalVotes = data['helpful'][1]
        reviewText = data['reviewText']
        unixReviewTime = data['unixReviewTime']
        rating = data['overall']

        # Initialize data components into review class
        # Only add to list of reviews if review meets minimum vote threshold and minimum text length threshold
        if (totalVotes >= minVoteThreshold) and (len(reviewText) >= minReviewLength):
            reviewEntry = Review(reviewerID, productID, upVotes, totalVotes, reviewText, unixReviewTime, rating)
            reviewsList.append(reviewEntry)
            dataStore.append(data)

    return reviewsList
