"""Linking Metadata and Review Data document into pandas dataframe"""

import os
import sys
import json
import re
import metadata
import jsonReviewRead_vBlackfyre
import reviewdataNB
import nltk
import datetime
import readability
from pycorenlp import StanfordCoreNLP
import pickle
import statistics

def main():
    review_list = []
    metadata_dictionary = {}

    vote_thresh = 10
    text_thresh = 10

    category = 'Grocery_and_Gourmet_Food'
    if os.path.isfile(category + '_review_list_metadata' + '.pkl'):
        with open(category + '_review_list_metadata' + '.pkl', 'rb') as f:
            review_list, metadata_dictionary = pickle.load(f)
    else:
        if category is not 'Apps_for_Android':
            review_list = jsonReviewRead_vBlackfyre.readInReviewRaw('reviews_Grocery_and_Gourmet_Food.json', '', vote_thresh, text_thresh)
        else:
            review_list = reviewdataNB.readInReviewRaw('reviews_Apps_for_Android.json', '', vote_thresh, text_thresh)
        metadata_dictionary = metadata.readInMetadata('meta_Grocery_and_Gourmet_Food.json')
        with open(category + '_review_list_metadata' + '.pkl', 'wb') as f:
            pickle.dump([review_list, metadata_dictionary], f)

    # reviewerID -> list of products reviewed
    productList_dict = {}

    # reviewerID -> averageReviewRating [favorable rating number ratings]
    hahaha = {}

    nlp = StanfordCoreNLP('http://localhost:9000')
    # reviewerID -> average a
    averageSentiment_dict = {}

    # productID -> average product rating
    averageRating_dict = {}

    favorableRatingList = []
    for review in review_list:
        favorableRatingList.append(review.favorableRating)

    ratio_threshold = statistics.median(favorableRatingList)
    print("Ratio Threshold Used + Median Favorable Rating: " + str(ratio_threshold))

    counter = 0

    print("Number of reviews to be featurized: " + str(len(review_list)))

    for review in review_list:
        # set review age
        if category is not 'Apps_for_Android':
            d0 = datetime.datetime.fromtimestamp(int(review.unixReviewTime)).date()
            d1 = datetime.date(2018, 4, 16)
            delta = d1 - d0
            review.reviewAge = delta.days

        if review.favorableRating >= ratio_threshold:
            review.helpfulLabel = 1
        else:
            review.helpfulLabel = 0

        person = review.reviewerID
        if person in metadata_dictionary:
            review.reviewedAlsoBought = metadata_dictionary[person].reviewAlsoBought
            review.reviewedAlsoViewed = metadata_dictionary[person].reviewedAlsoViewed
            review.reviewedAlsoBoughtTogether = metadata_dictionary[person].reviewedAlsoBoughtTogether
            counter+=1
        # build the reviewer to product list dictionary
        if person not in productList_dict:
            productList_dict[person] = {review.productID: 1}
        else:
            productList_dict[person][review.productID] = 1

        # build the averageRating dictionary
        if review.productID not in averageRating_dict:
            averageRating_dict[review.productID] = {'avg': review.overallRating, 'num': 1}
        else:
            averageRating_dict[review.productID]['num'] += 1
            averageRating_dict[review.productID]['avg'] = float(averageRating_dict[review.productID]['avg'] + review.overallRating) / float(averageRating_dict[review.productID]['num'])

        if review.reviewerID in hahaha:
            denominator = hahaha[review.reviewerID][1]
            numerator = hahaha[review.reviewerID][0]
            hahaha[review.reviewerID] = [float(numerator + review.favorableRating)/float(denominator + 1), (denominator + 1)]
        else:
            hahaha[review.reviewerID] = [float(review.favorableRating), 1]

    for review in review_list:
        productsReviewed = productList_dict[review.reviewerID]
        alsoBoughtC = 0
        alsoViewedC = 0
        boughtTogetherC = 0

        for product in productsReviewed:
            if product in metadata_dictionary[review.productID].alsoBought:
                boughtTogetherC += 1
            if product in metadata_dictionary[review.productID].alsoViewed:
                alsoViewedC += 1
            if product in metadata_dictionary[review.productID].boughtTogether:
                alsoBoughtC += 1

        review.reviewedAlsoBought = alsoBoughtC
        review.reviewedAlsoViewed = alsoViewedC
        review.reviewedAlsoBoughtTogether = boughtTogetherC
        review.NumberOfUserReviews = hahaha[review.reviewerID][1]
        review.AverageReviewRating = hahaha[review.reviewerID][0]

        review.reviewDeviationFromMean = float(review.overallRating)/float(averageRating_dict[review.productID]['avg'])
        review.reviewProductMean = averageRating_dict[review.productID]['avg']

    print("Metadata + Reviewer metrics calculated")

    if os.path.isfile(category + '_final_review_list' + '.pkl'):
        with open(category + '_final_review_list' + '.pkl', 'rb') as f:
            review_list = pickle.load(f)
    else:
        for counter, review in enumerate(review_list):
            dummyText = review.reviewText
            dummyText = dummyText.split()
            review.reviewLength = len(dummyText)

            review.numberQuestionMarks = review.reviewText.count('?')
            review.numberExclamationPoints = review.reviewText.count('!')
            review.numberOfPunctuations = review.numberQuestionMarks + review.numberExclamationPoints + review.reviewText.count(
                '.')

            STOPWORDS = open('stopwords.txt', 'r')
            STOPWORDS = STOPWORDS.read()
            STOPWORDS = STOPWORDS.split()

            STOPWORDS_DICT = {}
            for word in STOPWORDS:
                STOPWORDS_DICT[word] = 1

            stopwordCount = 0
            for word in dummyText:
                if word in STOPWORDS_DICT:
                    stopwordCount += 1

            review.numberStopWords = stopwordCount

            output = nlp.annotate(review.reviewText, properties={
                'annotators': 'tokenize,ssplit,pos',
                'outputFormat': 'json'
            })

            try:
                numSentances = len(output["sentences"])
                numWords = 0
                jajaja = 0
                merryChristmas = 0

                noun = "NN"
                nounCount = 0
                pronoun = "PRP"
                pronounCount = 0
                active = "VBZ"
                activeCount = 0
                passive = "VBD"
                passiveCount = 0
                adj = "JJ"
                adjCount = 0
                title = "NNP"
                titleCount = 0

                for sent in output["sentences"]:
                    jajaja += len(sent["tokens"])
                    for tok in sent["tokens"]:
                        numWords += 1
                        merryChristmas += len(tok["word"])
                        if tok["pos"] == noun:
                            nounCount += 1
                        if tok["pos"] == pronoun:
                            pronounCount += 1
                        if tok["pos"] == active:
                            activeCount += 1
                        if tok["pos"] == passive:
                            passiveCount += 1
                        if tok["pos"] == adj:
                            adjCount += 1
                        if tok["pos"] == title:
                            titleCount += 1

                review.namedEntities = titleCount
                review.numberNouns = nounCount
                review.numberPassiveVerbs = passiveCount
                review.numberActiveVerbs = activeCount
                review.numberAdjectives = adjCount
                review.numberPronous = pronounCount

                review.averageSentanceLength = float(jajaja) / float(numSentances)
                review.averageWordLength = float(merryChristmas) / float(numWords)

                results = readability.getmeasures(review.reviewText, lang='en')
                allReviewScore = results['readability grades']['FleschReadingEase'] + \
                results['readability grades']['Kincaid'] + results['readability grades']['ARI'] + \
                results['readability grades']['Coleman-Liau'] + results['readability grades']['GunningFogIndex'] + \
                results['readability grades']['LIX'] + \
                results['readability grades']['SMOGIndex'] + results['readability grades']['RIX']
                review.readability = allReviewScore/float(8)

                print("Review Number: " + str(counter))
                if category is not 'Apps_for_Android':
                    print(review.getPrintString())
            except Exception as e:
                print(e)

        with open(category + '_final_review_list' + '.pkl', 'wb') as f:
            pickle.dump(review_list, f)

    print("Review metrics updated")

if __name__ == '__main__':
    print('Main Function Beginning')
    main()
    print('End of Main')