'''
UMID: hbrendan, petermas
Names: Brendan Hart, Peter Mascheroni
Class: EECS 486
'''

import os
import sys
import re
import operator
import random
import math
import reviewdataNB
import linking_and_metrics

masterTok = []

months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]

wordBeforeYear = ["in", "during", "year"]

# mapping between punctuation to element with regex expression to remove unecessary punctionation
punctionation = {"." : ".", "," : ",", "(" : "\(", ")" : "\)", "?" : "\?", "=" : "=", ";" : ";", ":" : ":",
                 "{" : "{", "}" : "}", "--" : "--", "[" : "[", "]" : "]", "*" : "*", "/" : "\/"}

# list of contractions retrieved from here: https://en.wikipedia.org/wiki/Wikipedia:List_of_English_contractions
contractions = {
    "ain't": ["am not", "are not", "is not", "has not", "have not", "cash me outside"],
    "aren't": ["are not", "am not"],
    "can't": ["cannot"],
    "can't've": ["cannot have"],
    "'cause": ["because"],
    "could've": ["could have"],
    "couldn't": ["could not"],
    "couldn't've": ["could not have"],
    "didn't": ["did not"],
    "doesn't": ["does not"],
    "don't": ["do not"],
    "hadn't": ["had not"],
    "hadn't've": ["had not have"],
    "hasn't": ["has not"],
    "haven't": ["have not"],
    "he'd": ["he had", "he would"],
    "he'd've": ["he would have"],
    "he'll": ["he will"],
    "he'll've": ["he will have"],
    "he's": ["he has", "he is"],
    "how'd": ["how did"],
    "how'd'y": ["how do you"],
    "how'll": ["how will"],
    "how's": ["how has", "how is", "how does"],
    "I'd": ["I had", "I would"],
    "I'd've": ["I would have"],
    "I'll": ["I will"],
    "I'll've": ["I will have"],
    "I'm": ["I am"],
    "I've": ["I have"],
    "isn't": ["is not"],
    "it'd": ["it had", "it would"],
    "it'd've": ["it would have"],
    "it'll": ["it will"],
    "it'll've": ["it will have"],
    "it's": ["it has", "it is"],
    "let's": ["let us"],
    "ma'am": ["madam", "m'lady"],
    "mayn't": ["may not"],
    "might've": ["might have"],
    "mightn't": ["might not"],
    "mightn't've": ["might not have"],
    "must've": ["must have"],
    "mustn't": ["must not"],
    "mustn't've": ["must not have"],
    "needn't": ["need not"],
    "needn't've": ["need not have"],
    "o'clock": ["of the clock"],
    "oughtn't": ["ought not"],
    "oughtn't've": ["ought not have"],
    "she'd": ["she had", "she would"],
    "she'd've": ["she would have"],
    "she'll": ["she will"],
    "she'll've": ["she will have"],
    "she's": ["she has", "she is"],
    "should've": ["should have"],
    "shouldn't": ["should not"],
    "shouldn't've": ["should not have"],
    "so've": ["so have"],
    "so's": ["so as", "so is"],
    "that'd": ["that would", "that had"],
    "that'd've": ["that would have"],
    "that's": ["that has", "that is"],
    "there'd": ["there had", "there would"],
    "there'd've": ["there would have"],
    "there's": ["there has", "there is"],
    "they'd": ["they had", "they would"],
    "they'd've": ["they would have"],
    "they'll": ["they will"],
    "they'll've": ["they will have"],
    "they're": ["they are"],
    "they've": ["they have"],
    "to've": ["to have"],
    "wasn't": ["was not"],
    "we'd": ["we had", "we would"],
    "we'd've": ["we would have"],
    "we'll": ["we will"],
    "we'll've": ["we will have"],
    "we're": ["we are"],
    "we've": ["we have"],
    "weren't": ["were not"],
    "what'll": ["what will"],
    "what'll've": ["what will have"],
    "what're": ["what are"],
    "what's": ["what has", "what is"],
    "what've": ["what have"],
    "when's": ["when has", "when is"],
    "when've": ["when have"],
    "where'd": ["where did"],
    "where's": ["where has", "where is"],
    "where've": ["where have"],
    "who'll": ["who will"],
    "who'll've": ["who will have"],
    "who's": ["who has", "who is"],
    "who've": ["who have"],
    "why's": ["why has", "why is"],
    "why've": ["why have"],
    "will've": ["will have"],
    "won't": ["will not"],
    "won't've": ["will not have"],
    "would've": ["would have"],
    "wouldn't": ["would not"],
    "wouldn't've": ["would not have"],
    "y'all": ["you all"],
    "y'all'd": ["you all would"],
    "y'all'd've": ["you all would have"],
    "y'all're": ["you all are"],
    "y'all've": ["you all have"],
    "you'd": ["you had", "you would"],
    "you'd've": ["you would have"],
    "you'll": ["you will"],
    "you'll've": ["you will have"],
    "you're": ["you are"],
    "you've": ["you have"]
}

classes = ["nothelpful", "helpful"]

"""Porter Stemming Algorithm
This is the Porter stemming algorithm, ported to Python from the
version coded up in ANSI C by the author. It may be be regarded
as canonical, in that it follows the algorithm presented in

Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
no. 3, pp 130-137,

only differing from it at the points maked --DEPARTURE-- below.

See also http://www.tartarus.org/~martin/PorterStemmer

The algorithm as described in the paper could be exactly replicated
by adjusting the points of DEPARTURE, but this is barely necessary,
because (a) the points of DEPARTURE are definitely improvements, and
(b) no encoding of the Porter stemmer I have seen is anything like
as exact as this version, even with the points of DEPARTURE!

Vivake Gupta (v@nano.com)

Release 1: January 2001

Further adjustments by Santiago Bruno (bananabruno@gmail.com)
to allow word input not restricted to one word per line, leading
to:

release 2: July 2008
"""


class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

def stemWords(cleanTokens):
    stemmedTokens = []
    porter = PorterStemmer()
    for tok in cleanTokens:
        output = porter.stem(tok, 0, len(tok) - 1)
        stemmedTokens.append(output)

    return stemmedTokens

def removeStopwords(tokenizedText):
    stopWords = {'a', 'all', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 'few', 'from', 'for',
                 'have', 'he', 'her', 'here', 'him', 'his', 'how', 'i', 'in', 'is', 'it', 'its', 'many', 'me', 'my',
                 'none', 'of', 'on', 'or', 'our', 'she', 'some', 'the', 'their', 'them', 'there', 'they', 'that',
                 'this', 'to', 'us', 'was', 'what', 'when', 'where', 'which', 'who', 'why', 'will', 'with', 'you',
                 'your'}
    if tokenizedText in stopWords:
        return True
    else:
        return False

def tokenizeText(string_in, bigram):
    yearWords = {
        'in',
        'by',
        'during',
        'year',
        'january',
        'february',
        'march',
        'april',
        'may',
        'june',
        'july',
        'august',
        'september',
        'october',
        'november',
        'december'
    }

    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z']

    junk = ['//', ':', '=', '/', '?', ',', ';', '(', ')', '--', ".", "," , "(" , ")" , "?" , "=" , ";" , ":" ,
                 "{" , "}" , "--" , "[" , "]" , "*" , "/" ]

    wordList = string_in.split()
    tokenList = []

    previous_word = ''

    count = -1
    for word in wordList:
        count += 1

        # accrinym
        if word.isupper():
            continue

        word = word.lower()

        # remove standalone punctiation -> will cause infite loop
        if word == '.' or word == ',' or word == '/' or word == '(' or word == ')' or word == '?' or \
                word == "'" or word == ";" or word == ":" or word == "{" or word == "}" or \
                word == "-" or word == "[" or word == "]" or word == "=" or word == "*" or word == \
                "--" or word == "'":
            continue

        if word[-1] != "'" and ord(word[-1]) < 97 or ord(word[0]) > 122:
            word = word[:-1]
            if len(word) == 1 or len(word) == 0:
                continue

        # date check here
        if word.isdigit() and len(word) == 4 and wordList[count - 1] in yearWords:
            month = wordList[count - 1]
            tokenList = tokenList[:-1]
            tok = month + ' ' + word
            if removeStopwords(tok):
                continue
            if bigram:
                if previous_word is '' or previous_word is ' ':
                    previous_word = tok
                    continue
                toke_in = previous_word + ' ' + tok
                tokenList.append(toke_in)
                previous_word = tok
            else:
                tokenList.append(tok)
            continue
        if word.isdigit():
            continue


        # if word has number in it through out
        letterF = 0
        numkF = 0
        slashF = 0
        dotF = 0
        for l in word:
            if l in alphabet:
                letterF = 1
            if l in digits:
                numkF = 1
            if l == '/':
                slashF = 1
            if l == '.':
                dotF = 1
        if letterF and numkF and slashF:
            continue
        if letterF and numkF and slashF and dotF:
            continue

        for l in word:
            if l in junk:
                wordJunk = word.split()
                for j in wordJunk:
                    if len(j) > 1:
                        if removeStopwords(j):
                            continue
                        if bigram:
                            if previous_word is '' or previous_word is ' ':
                                previous_word = j
                                continue
                            toke_in = previous_word + ' ' + j
                            tokenList.append(toke_in)
                            previous_word = j
                        else:
                            tokenList.append(j)
                continue

        # remove non letters at beginning of words
        if ord(word[0]) < 97 or ord(word[0]) > 122:
            word = word.split(word[0])[0]
            if len(word) == 1:
                if word == 'a' or word == 'i':
                    if removeStopwords(word):
                        continue
                    if bigram:
                        if previous_word is '' or previous_word is ' ':
                            previous_word = word
                            continue
                        toke_in = previous_word + ' ' + word
                        tokenList.append(toke_in)
                        previous_word = word
                    else:
                        tokenList.append(word)
                else:
                    continue
            if len(word) == 0:
                continue

        # need to leave hyphen words

        # remove non letter at end of words:
        if ord(word[-1]) < 97 or ord(word[-1]) > 122:
            word = word[:-1]
            if len(word) == 1:
                if word == 'a' or word == 'i':
                    if removeStopwords(word):
                        continue
                    if bigram:
                        if previous_word is '' or previous_word is ' ':
                            previous_word = word
                            continue
                        toke_in = previous_word + ' ' + word
                        tokenList.append(toke_in)
                        previous_word = word
                    else:
                        tokenList.append(word)
                else:
                    continue
            if len(word) == 0:
                continue

        # contractions check here
        # if word in contractions:
        #     tokenList.append(contractions[word])
        #     continue
        if word[0] == "'" and word[-1] == "'":
            word = word.replace("'", '')
            if removeStopwords(word):
                continue
            if bigram:
                if previous_word is '' or previous_word is ' ':
                    previous_word = word
                    continue
                toke_in = previous_word + ' ' + word
                tokenList.append(toke_in)
                previous_word = word
            else:
                tokenList.append(word)
            continue
        elif word[0] == "'":
            word = word.replace("'", '')
            if removeStopwords(word):
                continue
            if bigram:
                if previous_word is '' or previous_word is ' ':
                    previous_word = word
                    continue
                toke_in = previous_word + ' ' + word
                tokenList.append(toke_in)
                previous_word = word
            else:
                tokenList.append(word)
            continue
        if "'s" in word and word[-1] == 's':
            words = word.split("'")
            if removeStopwords(words[0]):
                continue
            if bigram:
                if previous_word is '' or previous_word is ' ':
                    previous_word = word
                    continue
                toke_in = previous_word + ' ' + words[0]
                tokenList.append(toke_in)
                previous_word = words[0]
                toke_in = previous_word + ' ' + "'s"
                tokenList.append(toke_in)
                previous_word = "'s"
            else:
                tokenList.append(words[0])
                tokenList.append("'s")
            continue
        if len(word) == 1:
            if word is not 'a' or word is not 'i':
                continue
        if removeStopwords(word):
            continue
        if bigram:
            if previous_word is '' or previous_word is ' ':
                previous_word = word
                continue
            toke_in = previous_word + ' ' + word
            tokenList.append(toke_in)
            previous_word = word
        else:
            tokenList.append(word)

    return tokenList


def trainNaiveBayes(train_list_in, params, outfile_in):
    dicts = []

    numClasses = len(classes)

    for i in range(0, (numClasses)):
        dicts.append({})

    # get vocab, number of truth, lie docs, prob(class), # of word x in class c, # of words in c
    vocabulary = {}
    numDocsPerClass = {}
    totNumDocs = 0

    numWordsPerClass = {}

    for classy in classes:
        numWordsPerClass[classy] = 0

    helpful_benchmark = 0.5

    counter = 0
    mark = int(math.floor(len(train_list_in) * .1))
    percent = 0
    for file in train_list_in:
        counter += 1
        if counter % mark is 0:
            percent += 10
            print(str(percent) + '%')

        classDocBelongsTo = 0
        if file.favorableRating >= helpful_benchmark:
            classDocBelongsTo = 1

        if classes[classDocBelongsTo] in numDocsPerClass:
            numDocsPerClass[classes[classDocBelongsTo]] += 1
        else:
            numDocsPerClass[classes[classDocBelongsTo]] = 1

        # get text to base text
        baseText = file.reviewText

        # tokenize text
        tokens = tokenizeText(baseText, params['bigram'])

        # if params['stop'] == True:
        #     tokens = removeStopwords(tokens)

        if params['stem'] == True:
            tokens = stemWords(tokens)

        for tok in tokens:
            # vocabulary
            if tok in vocabulary:
                vocabulary[tok] += 1
            else:
                vocabulary[tok] = 1

            # num of word x in class c
            if tok in dicts[classDocBelongsTo]:
                dicts[classDocBelongsTo][tok] += 1
            else:
                dicts[classDocBelongsTo][tok] = 1

            # num words in class
            numWordsPerClass[classes[classDocBelongsTo]] += 1

        totNumDocs += 1

    vocab = len((vocabulary))

    # class probabilties
    for key, value in numDocsPerClass.items():
        numDocsPerClass[key] = float(value)/float(totNumDocs)

    # word conditional probabilities
    for counter, classDict in enumerate(dicts):
        for key, value in classDict.items():
            classDict[key] = (float(value) + 1)/(float(numWordsPerClass[classes[counter]]) + vocab)

    # print out top 10
    if params["condProb"] == True:
        for counter, classDict in enumerate(dicts):
            sortedCondProbs = sorted(classDict.items(), key=operator.itemgetter(1), reverse=True)
            count = 0
            outfile_in.write("Top 30 Conditional Probabilities for " + classes[counter] + " class" + "\n")
            for val in sortedCondProbs:
                if count == 30:
                    break
                outfile_in.write(str(val[0]) + " " + str(val[1]) + '\n')
                count += 1

    return numDocsPerClass, dicts, vocabulary, numWordsPerClass


def testNaiveBayes(testFile, classProbabilities, conditionalProbabilities, vocabulary, numWordsPerClass, params):


    # get text from file_class in
    baseText = testFile.reviewText

    # tokenize text
    tokens = tokenizeText(baseText, params['bigram'])

    # if params['stop'] == True:
    #     tokens = removeStopwords(tokens)

    if params['stem'] == True:
        tokens = stemWords(tokens)

    probPerClass = {}

    # init prob
    for classy in classes:
        probPerClass[classy] = 0

    numberVocab = len(vocabulary)

    for counter, classy in enumerate(classes):
        wordProbClass = 1
        for tok in tokens:
            probWord = 0
            if tok in conditionalProbabilities[counter]:
                probWord = conditionalProbabilities[counter][tok]
            else:
                probWord = 1.0/float((numberVocab + numWordsPerClass[classes[counter]]))

            wordProbClass = wordProbClass*probWord

        probClassStatment = wordProbClass * classProbabilities[classes[counter]]
        probPerClass[classes[counter]] = probClassStatment

    classification = max(probPerClass.items(), key=operator.itemgetter(1))[0]

    # print("Predicted classification: " + str(classification))
    return classification

def run_file_in(file_in):
    print('___MAIN_FUNCTION_BEGINNING___')
    porter = PorterStemmer()
    data_in = file_in
    min_votes = 10
    min_text_length = 10

    print('___START_TRAINING___')

    onlyfiles = reviewdataNB.readInReviewData(data_in, min_votes, min_text_length)
    print('reviews: ' + str(len(onlyfiles)))

    print('___FINISHED_READING_DATA___')
    random.shuffle(onlyfiles)

    train_range = int(math.floor(len(onlyfiles) * 0.3))
    training_list = onlyfiles[train_range:]
    test_list = onlyfiles[:train_range]

    right = 0
    wrong = 0

    params = {"stem": False, "stop": True, "condProb": True, 'bigram': True}

    outfile_name = 'output70|30/' + str(data_in.replace('.json', ''))
    outfile_name += str(min_votes) + '_' + str(min_text_length)
    if params['stem']:
        outfile_name += 'Stem'
    else:
        outfile_name += 'NoStem'
    outfile_name += 'Results.txt'
    outfile = open(outfile_name, 'w')

    wordProbabilitiesList = []

    # train on the 80% of input set
    classProbabilities, wordConditionalProbabilities, vocabulary, numWordsPerClass = trainNaiveBayes(training_list,
                                                                                                     params, outfile)

    print('___FINISHED_TRAINING___')

    helpful_benchmark = 0.5
    counter = 0
    mark = int(math.floor(len(test_list) * .1))
    percent = 0
    for review in test_list:
        counter += 1
        if counter % mark is 0:
            percent += 10
            print(str(percent) + '%')
        wordProbabilitiesList.append(wordConditionalProbabilities)
        classification = testNaiveBayes(review, classProbabilities, wordConditionalProbabilities,
                                        vocabulary, numWordsPerClass, params)

        # accuracy of classification
        identifyDoc = []
        if review.favorableRating >= helpful_benchmark:
            identifyDoc.append(1)
        else:
            identifyDoc.append(0)

        classDocBelongsTo = identifyDoc[0]
        if classification == classes[classDocBelongsTo]:
            right += 1
        else:
            wrong += 1

    rightAccuracy = float(right) / float(train_range)
    wrongAccuracy = float(wrong) / float(train_range)

    outfile.write("Total Docs right: " + str(right) + "\n")
    outfile.write("Percentage of docs classified as right: " + str(rightAccuracy) + "\n")
    outfile.write("Percentage of docs classified as wrong: " + str(wrongAccuracy) + "\n")

    print("Total Docs right: " + str(right))
    print("Percentage of docs classified as right: " + str(rightAccuracy))
    print("Percentage of docs classified as wrong: " + str(wrongAccuracy))

def main():
    file_list = [
        'reviews_Apps_for_Android.json',
        'reviews_Amazon_Instant_Video.json',
        'reviews_Grocery_and_Gourmet_Food.json',
        'reviews_Toys_and_Games.json',
        'reviews_Sports_and_Outdoors.json'
    ]

    ctr = 0
    for file in file_list:
        ctr += 1
        run_file_in(file)
        print('___FILE:_' + str(ctr) + '_DONE___')

    print('!!!END_OF_MAIN!!!')

if __name__ == '__main__':
    porter = PorterStemmer()
    main()
