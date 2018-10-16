import tweepy
import nltk
import string
import re
import operator
from time import sleep
from nltk.tokenize import RegexpTokenizer
from credentials import * #import twitter credentials from the file
from random import *
import datetime

#writes likes to a given file
def writefile(filename, toWrite):
    f = open(filename, 'a')
    f.write(toWrite)
    f.close()

def gethashtags(subject):
    tags = []
    tweets = api.search(subject)
    for tweet in tweets:
        words = re.split(' ', tweet.text)
        tags.extend(tag for tag in words if tag.startswith('#'))
    return tags
#takes the sentence and returns an array of the words in the sentence
def tokenize(sentence):
    tokens = re.split('[^A-Za-z]+', sentence.lower()) #grab the words
    tokens = list(filter(None, tokens)) #remove nulls
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
#uses wordcount as a weight to pseuo-randomly choose the next word
def chooseword(choices):
   total = sum(wc for word, wc in choices)
   r = uniform(0, total)
   count = 0
   for word, wc in choices:
      if count + wc > r:
         return word[1]
      count += wc
#uses a markov chain to create a sentence of given word size
def markov(words, chainlength=2, size=7):
    curr = choice(words)
    sentence = []
    gram2 = ngram(words, chainlength)
    for i in range(size): #number of  words for the sentence
        sentence.append(curr)
        choices = [element for element in gram2 if element[0][0] == curr]
        curr = chooseword(choices)
        if curr is None:
            break
    if len(sentence) < 3:
        markov(words, chainlength, size) # if our chain is bad try again
    return ' '.join(sentence)
#get rid of some of the unwanted things that are in normal tweets
def clean(tweet):
    tweet = re.sub("https?\:\/\/", "", tweet)   #links
    tweet = re.sub("#\S+", "", tweet)           #hashtags
    tweet = re.sub("\.?@", "", tweet)           #at mentions
    tweet = re.sub("RT.+", "", tweet)           #Retweets
    tweet = re.sub("rt.+", "", tweet)           #retweets in lower case
    tweet = re.sub("Video\:", "", tweet)        #Videos
    tweet = re.sub("\n", "", tweet)             #new lines
    tweet = re.sub("^\.\s.", "", tweet)         #leading whitespace
    tweet = re.sub("\s+", " ", tweet)           #extra whitespace
    tweet = re.sub("&amp;", "and", tweet)       #encoded ampersands
    return tweet
#returns an array with all the tokens from all the tweets
def gatherinfo(info):
    data = []
    tokens = []
    tweets = api.search(info)
    for tweet in tweets:
        data.append(clean(tweet.text))
    for d in data:
        gathered = tokenize(d)
        for t in gathered:
            tokens.append(t)
    return tokens
def trending():
    trending = api.trends_place(2487610)
    data = trending[0]
    trends = data['trends']
    hashtags = [trend['name'] for trend in trends]
    hashtag = hashtags[randint(0, len(hashtags))]
    return hashtag
#give it 2 times (in hours) you want to wait between and it gives you the number of seconds
def waittime(first, second):
    if (first > second):
        high = first *3600
        low = second *3600
    else:
        high = second *3600
        low = first *3600
    return randint(low, high)
#tweet the message given
def tweet(message):
    try:
        #print(message)
        api.update_status(message)
    except tweepy.TweepError as e:
        print(e.reason)
def main():
  work = True
  print('Its time to Tweet baby! :P')
  starttime =  'started at: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  writefile('errors.txt', starttime)
  while(work):
        #try:
          x = waittime(3, 6)  #wait 3 to 6 hrs to tweet
          context = True
          subject = trending()
          twt = markov(gatherinfo(subject), 25, randint(10,13))
          if twt is None or len(twt) is 1:
              context = False
          if context:  #if we got a None for the tweet just move on
            hashtags = gethashtags(subject) #otherwise we add a hashtag to it
            if hashtags is not None:
                twt += '. ' + hashtags[randint(0,len(hashtags)-1)]
            if len(twt) < 140:  #tweet too long
              tweet(twt)
          context = True  #reset context
          work = False
          #sleep(x) #only do this every so often
        #except:
          #err = 'error at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
          #writefile('errors.txt', err)
#access and authorize the twitter credentials from the file
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True) #run tweepy api and wait to do anything until the rate limit is gone
main()
