# system libraries
import os
import sys
import json
import re
import pickle

# machine learning libraries
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier, plot_importance
import xgboost as xgb
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV

target = 'helpfulLabel'

def XGModelFit(XGBModel, df_reviews, features, plot, useTrainCV=True, cv_folds=7, early_stopping_rounds=25):
    if useTrainCV:
        xgb_param = XGBModel.get_xgb_params()
        xgtrain = xgb.DMatrix(df_reviews[features].values, label=df_reviews[target].values)
        cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=XGBModel.get_params()['n_estimators'], nfold=cv_folds,
                          metrics='auc', early_stopping_rounds=early_stopping_rounds, verbose_eval=True)
        XGBModel.set_params(n_estimators=cvresult.shape[0])

    XGBModel.fit(df_reviews[features], df_reviews[target], eval_metric='auc')

    df_review_predictions = XGBModel.predict(df_reviews[features])
    df_review_predprob = XGBModel.predict_proba(df_reviews[features])[:, 1]

    # Print model report:
    print("\nModel Report")
    print("Train AUC Score: %.4g" % metrics.roc_auc_score(df_reviews[target], df_review_predprob))
    print("Accuracy : %.4g" % metrics.accuracy_score(df_reviews[target].values, df_review_predictions))

    if plot:
        plot_importance(XGBModel, importance_type='gain')
        plt.show()

def main():
    category = 'Grocery_and_Gourmet_Food'
    review_list = []
    with open(category + '_final_review_list' + '.pkl', 'rb') as f:
            review_list = pickle.load(f)

    df_reviews = pd.DataFrame.from_records([t.to_dict() for t in review_list])

    test_split = 0.7


    features = ['Intercept', 'overallRating', 'readability',
                'reviewAge', 'reviewedAlsoBought', 'reviewedAlsoViewed', 'reviewedAlsoBoughtTogether',
                'NumberOfUserReviews', 'reviewDeviationFromMean',
                'reviewProductMean', 'reviewLength', 'numberStopWords', 'numberOfPunctuations',
                'averageWordLength', 'averageSentanceLength', 'numberExclamationPoints', 'numberQuestionMarks',
                'namedEntities', 'numberNouns', 'numberPassiveVerbs', 'numberActiveVerbs', 'numberAdjectives', 'numberPronous']

    features_Apps_for_Android = ['Intercept', 'overallRating', 'readability', 'reviewedAlsoBought', 'reviewedAlsoViewed',
                                 'reviewedAlsoBoughtTogether','NumberOfUserReviews', 'reviewDeviationFromMean',
                'reviewProductMean', 'reviewLength', 'numberStopWords', 'numberOfPunctuations',
                'averageWordLength', 'averageSentanceLength', 'numberExclamationPoints', 'numberQuestionMarks',
                'namedEntities', 'numberNouns', 'numberPassiveVerbs', 'numberActiveVerbs', 'numberAdjectives', 'numberPronous']

    if category is 'Apps_for_Android':
        features = features_Apps_for_Android

    # adjust reviewDeviationFromMean - made an oopsie in the
    actualDevFromMean = abs(df_reviews['overallRating'] - df_reviews['reviewProductMean'])
    df_reviews.assign(reviewDeviationFromMean=actualDevFromMean)

    #intercept term
    df_reviews.insert(0, 'Intercept', 1, allow_duplicates=True)
    if category is not 'Apps_for_Android':
        X = df_reviews[features].values
    else:
        X = df_reviews[features].values

    y = df_reviews['helpfulLabel'].values

    '''
    Data Exploration
    '''
    print("Number of features: " + str(len(features)))
    group_by_help = df_reviews.groupby('helpfulLabel').mean()

    '''
    Model Generation
    '''
    cross = False
    # using 7 fold cross validation

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=(1 - test_split), train_size=test_split, shuffle=True)
    print ("Logistic Regression Model Results: ")
    penalty = ["l1", "l2"]
    for pen in penalty:
        print("Using " + pen + " Regularization")
        logModel = LogisticRegression(penalty=pen, C=1)

        if cross:
            print("Performing Cross Validation")
            logModel = LogisticRegression(penalty=pen)
            params = {'C': [.1, .5, 1, 5, 10]}
            logModel = GridSearchCV(logModel, params, scoring='neg_log_loss', refit=True, cv=7)

            logModel.fit(X_train, y_train)
            bestParams = logModel.best_params_

            logModel = LogisticRegression(penalty=pen, C=bestParams['C'])

        logModel.fit(X_train, y_train)

        print("Score for training set")
        print(logModel.score(X_train, y_train))
        print("Null score for training set")
        print(y_train.mean())

        print("Coeficents for training set: ")
        df_coef = pd.DataFrame(data=logModel.coef_, columns=features, dtype=None, copy=False)
        with pd.option_context('display.max_rows', None, 'display.max_columns', len(features)):
            print(df_coef, file=open("model_data_analysis_" + category + ".txt", "a"))

        print("Predicted Labels: ")
        predicted = logModel.predict(X_test)
        print(predicted)

        print("Predicted probabilities for each label: ")
        probs = logModel.predict_proba(X_test)
        print(probs)

        print("Print accuracy score: ")
        print(metrics.accuracy_score(y_test, predicted))
        print("Print roc_auc_score: ")
        print(metrics.roc_auc_score(y_test, probs[:, 1]))

        print("Confusion matrix: ")
        print(metrics.confusion_matrix(y_test, predicted))
        print("Classification report: ")
        print(metrics.classification_report(y_test, predicted))

    if cross:
        print("Using Cross Validation to see if results hold up across all of the training set + model generalizes well: ")
        penalty = ["l1", "l2"]
        for pen in penalty:
            print("Using " + pen + " Regularization")
            scores = cross_val_score(LogisticRegression(penalty=pen), X, y, scoring='accuracy', cv=7)
            print(scores)
            print(scores.mean())

    # Random Forest
    print ("Random Forest: " )
    rf = RandomForestClassifier(n_estimators=500, oob_score=True) #oob_score makes cv unnecessary for paramater tuning
    rf.fit(X_train, y_train)

    print("Feature Importantces for training set: ")
    feature_imp = np.reshape(rf.feature_importances_, (1, len(features)))
    df_coef = pd.DataFrame(data=feature_imp, columns=features, dtype=None, copy=False)
    with pd.option_context('display.max_rows', None, 'display.max_columns', len(features)):
        print(df_coef, file=open("model_data_analysis_" + category + ".txt", "a"))

    print("Predicted Labels: ")
    predicted = rf.predict(X_test)
    print(predicted)

    print("Predicted probabilities for each label: ")
    probs = rf.predict_proba(X_test)
    print(probs)

    accuracy = metrics.accuracy_score(y_test, predicted)
    print('Out-of-bag score estimate:' + str(rf.oob_score_))
    print('Mean accuracy score: ' + str(accuracy))

    print("Confusion matrix: ")
    print(metrics.confusion_matrix(y_test, predicted))

    if cross:
        print("Using Cross Validation to see if results hold up across all of the training set + model generalizes well: ")
        scores = cross_val_score(RandomForestClassifier(n_estimators=500, oob_score=True), X, y, scoring='accuracy', cv=7)
        print(scores)
        print(scores.mean())

    # XGBoosted
    colsample_bytree = 0.9
    subsample = 0.9
    num_estimators = 90
    max_depth = 3
    min_child_weight = 5
    gamma = 0.2
    reg_alpha = 0.01

    '''
    Cross Validation
    '''
    if cross:
        tree_params_test_one = {
            'max_depth': range(1, 9, 2),
            'min_child_weight': range(1, 6, 2)
        }

        tree_search = GridSearchCV(estimator=XGBClassifier(learning_rate=0.1,gamma=0, n_estimators=90, max_depth=5,
                                                        min_child_weight=1, nthread=4,subsample=0.8, colsample_bytree=0.8,
                                                        objective='binary:logistic', scale_pos_weight=1),
                                param_grid=tree_params_test_one, scoring='roc_auc', n_jobs=4, iid=False, cv=7)

        tree_search.fit(df_reviews[features], df_reviews[target])

        print("Best Tree Params: ")
        print(tree_search.best_params_)

        max_depth = tree_search.best_params_['max_depth']
        min_child_weight = tree_search.best_params_['min_child_weight']

        print("Best Model Score: ")
        print(tree_search.best_score_)

        # tune gamma
        gamma_param = {
            'gamma': [i / 10.0 for i in range(0, 5)]
        }
        gamma_search = GridSearchCV(estimator=XGBClassifier(learning_rate=0.1, n_estimators=num_estimators, max_depth=max_depth,
                                                        min_child_weight=min_child_weight, gamma=0, subsample=0.8, colsample_bytree=0.8,
                                                        objective='binary:logistic', nthread=4, scale_pos_weight=1,
                                                        seed=27),
                                param_grid=gamma_param, scoring='roc_auc', n_jobs=4, iid=False, cv=7)
        gamma_search.fit(df_reviews[features], df_reviews[target])
        print("Best Tree Params: ")
        print(gamma_search.best_params_)

        gamma = gamma_search.best_params_['gamma']

        print("Best Model Score: ")
        print(gamma_search.best_score_)

        # tune subsample and colsample_bytree

        subsample_colsample_bytree = {
            'subsample': [i / 10.0 for i in range(6, 10)],
            'colsample_bytree': [i / 10.0 for i in range(6, 10)]
        }
        subsample_colsample_bytree_search = GridSearchCV(estimator=XGBClassifier(learning_rate=0.1, n_estimators=num_estimators, max_depth=max_depth,
                                                        min_child_weight=min_child_weight, gamma=gamma, subsample=0.8, colsample_bytree=0.8,
                                                        objective='binary:logistic', nthread=4, scale_pos_weight=1,
                                                        seed=27),
                                param_grid=subsample_colsample_bytree, scoring='roc_auc', n_jobs=4, iid=False, cv=7)

        subsample_colsample_bytree_search.fit(df_reviews[features], df_reviews[target])
        print("Best Tree Params: ")
        print(subsample_colsample_bytree_search.best_params_)

        subsample = subsample_colsample_bytree_search.best_params_['subsample']
        colsample_bytree = subsample_colsample_bytree_search.best_params_['colsample_bytree']

        print("Best Model Score: ")
        print(subsample_colsample_bytree_search.best_score_)

        # Tune regularization paramater
        reg_params = {
            'reg_alpha': [1e-5, 1e-2, 0.1, 1, 100]
        }
        reg_search = GridSearchCV(estimator=XGBClassifier(learning_rate=0.1, n_estimators=num_estimators, max_depth=max_depth,
                                                        min_child_weight=min_child_weight, gamma=gamma, subsample=subsample, colsample_bytree=colsample_bytree,
                                                        objective='binary:logistic', nthread=4, scale_pos_weight=1,
                                                        seed=27),
                                param_grid=reg_params, scoring='roc_auc', n_jobs=4, iid=False, cv=5)
        reg_search.fit(df_reviews[features], df_reviews[target])
        print("Best Tree Params: ")
        print(reg_search.best_params_)

        reg_alpha = reg_search.best_params_['reg_alpha']

        print("Best Model Score: ")
        print(reg_search.best_score_)

    # reduce learning rate and generate many trees
    # get non linear relationships
    modelXG = XGBClassifier(
        learning_rate=0.01,
        n_estimators=5000,
        max_depth=max_depth,
        min_child_weight=min_child_weight,
        gamma=gamma,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        reg_alpha=reg_alpha,
        objective='binary:logistic',
        nthread=4,
        scale_pos_weight=1,
        booster='gbtree')

    modelXG.fit(X_train, y_train)

    plot_importance(modelXG, importance_type='gain', xlabel='Information Gain') # plot importance of features by information gain
    plt.show()

    # make predictions for test data
    y_pred = modelXG.predict(X_test)
    predictions = [round(value) for value in y_pred]

    print("Predicted probabilities for each label: ")
    probs = modelXG.predict_proba(X_test)
    print(probs)

    accuracy = metrics.accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

if __name__ == '__main__':
    main()

