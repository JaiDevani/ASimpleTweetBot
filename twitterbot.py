import tweepy
import nltk
import string
import re
import operator
from time import sleep
from nltk.tokenize import RegexpTokenizer
from credentials import * #import twitter credentials from the file
from random import *
def gethashtags(subject):
    tags = []
    tweets = api.search(subject)
    for tweet in tweets:
        words = re.split(' ', tweet.text)
        tags.extend(tag for tag in words if tag.startswith('#'))
    return tags
#takes the sentence and returns an array of the words in the sentence
def tokenize(sentence):
    result = re.sub(r"http\S+", "", sentence)
    #tokenizer = RegexpTokenizer(r'[A-Za-z]+')
    #tokens = tokenizer.tokenize(result)
    tokens = re.split('[^A-Za-z]+', result.lower()) #grab the words
    tokens = list(filter(None, tokens))
    return tokens
#takes 'info' and seraches twitter for tweets with that keyword and then
def ngram(words, n=2):
    gram = dict()
    assert n > 1 and n < 100
    #make a dictionary of words and their counts
    for i in range(len(words)-(n-1)):
        key = tuple(words[i:i+n])
        if key in gram:
            gram[key] +=1
        else:
            gram[key] = 1
    #now sort the list my frequency
    gram = sorted(gram.items(), key=operator.itemgetter(1))
    return gram
def chooseword(choices):
   total = sum(wc for word, wc in choices)
   r = uniform(0, total)
   count = 0
   for word, wc in choices:
      if count + wc > r:
         return word[1]
      count += wc
def markov(words, chainlength=2, size=7):
    curr = 'the'
    sentence = []
    gram2 = ngram(words, chainlength)
    for i in range(size): #number of  words for the sentence
        sentence.append(curr)
        choices = [element for element in gram2 if element[0][0] == curr]
        curr = chooseword(choices)
    return ' '.join(sentence)
#returns an array with all the tokens from all the tweets
def gatherinfo(info):
    data = []
    tokens = []
    tweets = api.search(info)
    for tweet in tweets:
        data.append(tweet.text)
    for d in data:
        gathered = tokenize(d)
        for t in gathered:
            tokens.append(t)
    return tokens
def generateSentence():
    sentence = []
    choice = randint(1, 5)
    start = 'I think that '
    if choice is 1:
        start = 'Can you believe '
    elif choice is 2:
        start = 'I wonder if '
    elif choice is 3:
        start = 'It is crazy that '
    elif choice is 4:
        start = 'Is it possible that '
    choice = randint(1,4)
    middle = ' would '
    if choice is 1:
        middle = ' can '
    elif choice is 2:
        middle = ' caused '
    elif choice is 3:
        middle = ' cannot '
    sentence.append(start)
    sentence.append(middle)
    return sentence
#fills out a madlib based off the words from a given search topic
def madlib(subject):
    tokens = gatherinfo(subject)
    pos = nltk.pos_tag(tokens)
    noun = 'Frog'  #set some default values
    verb = 'hop'
    adj = 'brown'
    noun1 = 'log'
    havenoun = False #set all 'found' variables to false
    haveverb = False
    haveadj = False
    havenoun1 = False
    sentence = generateSentence()
    for word in pos:
        if word[1] == 'NN' and havenoun is False:
            noun = word[0];
            if randint(1,5) != 1:  #add randomness so it doesn't pick the first vaules it sees
                havenoun = True
        if word[1] == 'VB' and haveverb is False:
            verb = word[0];
            if randint(1,5) != 3:
                haveverb = True
        if word[1] == 'JJ' and haveadj is False:
            adj = word[0];
            if randint(1,5) != 2:
                haveadj = True
        if word[1] == 'NN' and havenoun1 is False and word[0] != noun:
            noun1 = word[0];
            if randint(1,5) != 5:
                havenoun1 = True
    m = sentence[0] + subject + sentence[1] + verb + ' the ' + adj + ' ' + noun1 + ' #' + noun
    tweet(m)
#read lines from a file and returns them
def readfile(filename):
    # Open text file verne.txt (or your chosen file) for reading
    myfile = open(filename, encoding="utf8")

    # Read lines one by one from my_file and assign to file_lines variable
    lines = myfile.read()
    # Close file
    myfile.close()
    return lines
#writes likes to a given file
def writefile(filename, toWrite):
    f = open(filename, 'a')
    f.write(toWrite)
    f.close()
#return a trending hastag
def trending():
    trending = api.trends_place(2487610)
    data = trending[0]
    trends = data['trends']
    hashtags = [trend['name'] for trend in trends]
    hashtag = hashtags[randint(0, 10)]
    print(hashtag)
    return hashtag
#tweet the message given
def tweet(message):
    try:
        print(message)
        api.update_status(message)
    except tweepy.TweepError as e:
        print(e.reason)
#do task 1
def task1():
    f = input(' Give me the text file name: ')
    tweets = readfile(f)
    for tw in tweets:
        tweet(tw)
#do task 2
def task2():
    np = input(' What should I tweet about: ')
    madlib(np)
#do task 3
def task3():
    totweet = input(' What should I Tweet?:')
    tweet(totweet)
#do task 4
def task4():
    totweet = input(' What should I Tweet about?:')
    for x in range(12):
        madlib(totweet)
        sleep(300)
#do task 5
def task5():
    trending()
#do task 6
def task6():
    print("currently unavailable")
#tweet a trending topic
def task7():
    for x in range(4):
        madlib(trending())
        sleep(900)
def task8():
    try:
        subject = input('What should I Tweet about: ')
        twt = markov(gatherinfo(subject), randint(5,15), randint(12,15))
        hashtags = gethashtags(subject)
        twt += '. ' + hashtags[randint(0,len(hashtags)-1)]
        tweet(twt)
    except:
        print('I Gooped')
#quit the program
def q():
    print('Thank you for using A Simple Tweet Bot! :)')
    return False
#show menu options
def menu():
    run = True
    while(run):
        print('\n I can do many things, here are my current tasks:')
        print(' ----------------------------------------------------------')
        print('\t1: Read from a file given and tweet each line.')
        print('\t2: Fill out a Madlib using words from a tweet search.')
        print('\t3: Tweet a given string.')
        print('\t4: Tweet about a subject every 5 minutes.')
        print('\t5: Show the trending hashtag(#).')
        print('\t6: Update information codex with a trending hashtag.')
        print('\t7: Tweet a trending topic every 15 minutes')
        print('\t8: Create a sentence from a markov chain.')
        print('\tq: Quit the program.')
        task = input(' What shall I do: ')
        if task == '1':
            task1()
        elif task == '2':
            task2()
        elif task == '3':
            task3()
        elif task == '4':
            task4()
        elif task == '5':
            task5()
        elif task == '6':
            task6()
        elif task == '7':
            task7()
        elif task == '8':
            task8()
        elif task == 'q':
            run = q()
        else:
            print(' Im sorry that is not a command. :(')
#main
def main():
    print('\n Welcome to A Simple Tweet Bot.\n')
    menu()
#access and authorize the twitter credentials from the file
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
main()
