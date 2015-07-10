import re
import json
import math
import sys
from operator import itemgetter

def read_tweets(filename):
    tweets = {}
    f =open(filename, 'r')
    lines = f.readlines()
    for line in lines:
        tweet = json.loads(line)
        # key:id; value: total tweet document.
        tweets[tweet['id']] = tweet
    return tweets

def tokenize(text):
    tokens = []
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9_]',' ',text)
    tokens = text.split()
    return tokens

def generate_tf_idf_vectors(tweets):
    tf_idf_vectors = {}
    tf_vectors = {}
    idf_vector = {}
    tweet_user_relation = {}
    for tweet_id in tweets:
        tweet = tweets[tweet_id]
        # generate tf_vectors:
        tf_vector = {}
        words = tokenize(tweet['text'])
        for word in words:
            if word not in tf_vector:
                tf_vector[word] = 0
            tf_vector[word] += 1
        # generate idf_vector for the words that exist in tf_vector
        for word in tf_vector:
            if word not in idf_vector:
                idf_vector[word] = 0
            idf_vector[word] += 1
        # tf_vector dictionary is the value of tf_vectors, whoes keys are the tweest_id
        tf_vectors[tweet_id] = tf_vector
    N = len(tweets)  # the number of documents in collection
    print "number of d", N
    for word in idf_vector:
        idf_vector[word] = 1.0 * N / idf_vector[word]
    # call generate_document_tf_idf_vector function to calculte the weight
    # tf_idf_vector dictionary is the value of tf_idf_vectors
    for tweet_id in tweets:
        tf_idf_vectors[tweet_id] = generate_document_tf_idf_vector(
            tf_vectors[tweet_id],idf_vector)
    return tf_idf_vectors, idf_vector, tweet_user_relation

def log2(n):
    return math.log(n) / math.log(2)

def generate_document_tf_idf_vector(tf_vector, idf_vector):
    tf_idf_vector = {}
    total_sum = 0.0
    for word in tf_vector:
    # if any token in the query do not occur in the tweet corpus, 
    # then the idf will be unfined. Program should return no results.
        if word not in idf_vector:
            return None
        tf_idf_vector[word] = ((1 + log2(tf_vector[word])) * log2(idf_vector[word]))
        total_sum += tf_idf_vector[word] ** 2
    # NOMALIZATION
    for word in tf_idf_vector:
        tf_idf_vector[word] /= total_sum ** 0.5
    return tf_idf_vector

def calculate_cosine_similarity(tf_idf_vector,query_tf_idf_vector):
    cosine_similarity = 0.0
    for word in query_tf_idf_vector:
        if word in tf_idf_vector:
            cosine_similarity += query_tf_idf_vector[word] * tf_idf_vector[word]
    return cosine_similarity

# Return all the IDs for the tweets which have at least one word in the query.
def retrieve_tweets(tf_idf_vectors, query):
    retrieved_tweets_ids = []
    query_words = tokenize(query)
    for tweet_id in tf_idf_vectors:
        tf_idf_vector = tf_idf_vectors[tweet_id]
        for word in query_words:
            if word in tf_idf_vector:
                retrieved_tweets_ids.append(tweet_id)
                break 
    return retrieved_tweets_ids

def rank_tweets(retrieved_tweets_ids, idf_vector, tf_idf_vectors, query):
    ranked_tweets_ids = []
    query_vector = {}
    query_words = tokenize(query)
    # generate tf-idf vector for query
    query_tf_vector = {}
    for word in query_words:
        if word not in query_tf_vector:
            query_tf_vector[word] = 0
        query_tf_vector[word] += 1
    query_tf_idf_vector = generate_document_tf_idf_vector(query_tf_vector, idf_vector)
    # no tf-idf vector has been generated for the query
    if not query_tf_idf_vector:
        return [], {}

    tweet_query_similarity = {}
    for tweet_id in retrieved_tweets_ids:
        tweet_query_similarity[tweet_id] = calculate_cosine_similarity(
            tf_idf_vectors[tweet_id], query_tf_idf_vector)
        #print tweet_id, tweet_query_similarity[tweet_id]
    ranked_tweets = sorted(
        tweet_query_similarity.items(), key=itemgetter(1), reverse=True)
    for tweet_id, cosine_sim in ranked_tweets[:50]:
        ranked_tweets_ids.append(tweet_id)
    return ranked_tweets_ids, tweet_query_similarity

def output_tweets(tweets_ids, tweets):
    if len(tweets_ids) == 0:
        return []
    extracted_tweets = []
    for tweet_id in tweets_ids:
        print tweet_id, tweets[tweet_id]['text'],extracted_tweets.append(
        tweet_id)
    return extracted_tweets


def main(query):
    filename = "example.json"  # change example.json to your input json filename
    tweets = read_tweets(filename)
    tf_idf_vectors, idf_vector, tweet_user_relation = generate_tf_idf_vectors(tweets)
    retrieved_tweets_ids = retrieve_tweets(tf_idf_vectors, query)
    ranked_tweets_ids, tweet_query_similarity = rank_tweets(
        retrieved_tweets_ids, idf_vector, tf_idf_vectors, query)
    for tweet_id in ranked_tweets_ids:
        print tweet_id, tweet_query_similarity[tweet_id]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python tweets_retrieval.py 'query'"
    else:
        print sys.argv[1]
        main(sys.argv[1])
