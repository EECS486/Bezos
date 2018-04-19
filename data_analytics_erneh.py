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
from tabulate import tabulate
import jsonReviewRead_vBlackfyre
import reviewdataNB

def main():
    categories = ['Amazon_Instant_Video', 'Apps_for_Android', 'Sports_and_Outdoors',
                  'Toys_and_Games', 'Grocery_and_Gourmet_Food']

    review_list_categories = {}
    for cat in categories:
        if os.path.isfile(cat + '_final_review_list' + '.pkl'):
            with open(cat + '_final_review_list' + '.pkl', 'rb') as f:
                review_list = pickle.load(f)
                review_list_categories[cat] = review_list

    review_list_num_reviews = {}
    review_list_review_text = {}
    review_favorable = {}
    review_active_verbs = {}
    review_named_entity = {}
    review_number_of_user_review = {}

    # calculate metrics for reviews
    for key, value in review_list_categories.items():
        review_list = value
        review_list_num_reviews[key] = len(review_list)

        review_text_list = []
        review_favorable_list = []
        review_active_verbs_list = []
        review_named_entity_list = []
        review_number_of_user_review_list = []

        for review in review_list:
            review_text_list.append(len(review.reviewText))
            review_favorable_list.append(review.favorableRating)
            review_active_verbs_list.append(review.numberActiveVerbs)
            review_named_entity_list.append(review.namedEntities)
            review_number_of_user_review_list.append(review.NumberOfUserReviews)

        review_list_review_text[key] = review_text_list
        review_favorable[key] = review_favorable_list
        review_active_verbs[key] = review_active_verbs_list
        review_named_entity[key] = review_named_entity_list
        review_number_of_user_review[key] = review_number_of_user_review_list

    print ("Number of Reviews for Each Category")
    tabulate_list = []
    for key, value in review_list_categories.items():
        num_reviews = review_list_num_reviews[key]
        table_data = [key, num_reviews]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Number of Reviews']))
    print("\n")


    print ("Mean for Review Text Length (in characters)")
    tabulate_list = []
    for key, value in review_list_categories.items():
        # by characters len
        review_text_len = review_list_review_text[key]
        table_data = [key, statistics.mean(review_text_len)]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Mean Review Text Length']))
    print("\n")

    print ("Median and Variance for Favorable Rating")
    tabulate_list = []
    for key, value in review_list_categories.items():
        # by characters len
        review_favorable_list = review_favorable[key]
        table_data = [key, statistics.median(review_favorable_list), statistics.variance(review_favorable_list)]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Median', 'Variance']))
    print("\n")

    print ("Mean for Number of Active Verbs")
    tabulate_list = []
    for key, value in review_list_categories.items():
        # by characters len
        table_data = [key, statistics.mean(review_active_verbs_list)]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Mean Number Active Verbs']))
    print("\n")

    print ("Text Processing Stats")
    tabulate_list = []
    for key, value in review_list_categories.items():
        # by characters len
        review_named_entity_list = review_named_entity[key]
        review_active_verbs_list = review_active_verbs[key]
        review_text_len = review_list_review_text[key]
        table_data = [key, statistics.mean(review_named_entity_list), statistics.mean(review_active_verbs_list), statistics.mean(review_text_len)]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Mean Named Entities', 'Mean Active Verbs', 'Mean Review Text Length']))
    print("\n")

    print ("Mean for Number of User Reviews")
    tabulate_list = []
    for key, value in review_list_categories.items():
        # by characters len
        review_number_of_user_review_list = review_number_of_user_review[key]
        table_data = [key, statistics.mean(review_number_of_user_review_list)]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Mean of User Reviews']))
    print("\n")

    # metadata metrics
    metadata_categories = {}
    for cat in categories:
        if os.path.isfile(cat + '_review_list_metadata' + '.pkl'):
            with open(cat + '_review_list_metadata' + '.pkl', 'rb') as f:
                junk, metadata_dict = pickle.load(f)
                metadata_categories[cat] = metadata_dict

    numAlsoBoughtTrack = {}
    numAlsoViewedTrack = {}
    numAlsoBoughtTogetherTrack = {}
    totAmountProducts = {}

    for key, value in metadata_categories.items():
        metadata_dict = value
        totAmountProducts[key] = len(metadata_dict)

        numAlsoBoughtMissing = 0
        numAlsoViewedMissing = 0
        numAlsoBoughtTogetherMissing = 0

        for lock, mutex in metadata_dict.items():
            if metadata_dict[lock].numAlsoBought == 0:
                numAlsoBoughtMissing += 1
            if metadata_dict[lock].numAlsoViewed == 0:
                numAlsoViewedMissing += 1
            if metadata_dict[lock].numAlsoBoughtTogether == 0:
                numAlsoBoughtTogetherMissing += 1

        numAlsoBoughtTrack[key] = numAlsoBoughtMissing
        numAlsoViewedTrack[key] = numAlsoViewedMissing
        numAlsoBoughtTogetherTrack[key] = numAlsoBoughtTogetherMissing

    print("Missing Data For Metadata to Total Products Ratio")
    tabulate_list = []
    for key, value in metadata_categories.items():
        numAlsoBoughtRatio = float(numAlsoBoughtTrack[key]) / float(totAmountProducts[key])
        numAlsoViewedRatio = float(numAlsoViewedTrack[key]) / float(totAmountProducts[key])
        numAlsoBoughtTogetherRatio = float(numAlsoBoughtTogetherTrack[key]) / float(totAmountProducts[key])
        table_data = [key, numAlsoBoughtRatio, numAlsoViewedRatio, numAlsoBoughtTogetherRatio]
        tabulate_list.append(table_data)
    print(tabulate(tabulate_list, headers=['Category', 'Num Also Bought Missing', 'Num Also Viewed Missing',
                                           'Num Also Bought Together Missing']))
    print("\n")




if __name__ == '__main__':
    print('Main Function Beginning')
    main()
    print('End of Main')