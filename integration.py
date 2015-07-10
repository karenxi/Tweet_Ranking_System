#PART3:Integrating Part1 and Part2
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
        # generate tweet_id-user relation dictionary
        tweet = tweets[tweet_id]
        user_screen_name = tweet['user']['screen_name']
        if tweet_id not in tweet_user_relation:
            tweet_user_relation[tweet_id] = user_screen_name
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
    #normalize similarity for part3
    max_similarity = max(tweet_query_similarity.values())
    for tweet_id in tweet_query_similarity:
        tweet_query_similarity[tweet_id] = tweet_query_similarity[tweet_id] / max_similarity

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

def generate_graph_structure(tweets):
    #key: userID; value: mentioned userIDs
    graph_structure = {}
    unique_user_screen_names = set()
    #print 'begin generating graph'
    for tweet_id in tweets:
        tweet = tweets[tweet_id]
        user_screen_name = tweet['user']['screen_name']
        mentioned_userList = tweet['entities']['user_mentions']
        for mentioned_user in mentioned_userList:
            mentioned_user_screen_name = mentioned_user['screen_name']
            if user_screen_name not in graph_structure:
                graph_structure[user_screen_name] = []
            if mentioned_user_screen_name not in graph_structure[user_screen_name]: 
                graph_structure[user_screen_name].append(mentioned_user_screen_name)
            unique_user_screen_names.add(mentioned_user_screen_name)
    new_users = unique_user_screen_names - set(graph_structure.keys())
    for user_screen_name in new_users:
        graph_structure[user_screen_name] = []
    #print 'graph is done'
    return graph_structure
    
def calculate_pagerank(graph_structure):
    ranked_users = {}
    pre_pagerank = {}
    cur_pagerank = {}
    error = 0.0
    for user_screen_name in graph_structure:
        pre_pagerank[user_screen_name] = 1.0
        cur_pagerank[user_screen_name] = 0.0
        error += abs(pre_pagerank[user_screen_name] - cur_pagerank[user_screen_name])
    while error > 10 ** (-6):
        for user_screen_name in cur_pagerank:
            cur_pagerank[user_screen_name] = 0.0
        # error should be 0.0 when every iteration begins
        error = 0.0
        # update the cur_pagerank from the pre_pagerank
        for user_screen_name in graph_structure:
            for mentioned_user_screen_name in graph_structure[user_screen_name]:
                #if mentioned_userID not in cur_pagerank:
                #cur_pagerank[mentioned_userID] = 0.0
                if len(graph_structure[user_screen_name]) != 0:
                    cur_pagerank[mentioned_user_screen_name] += pre_pagerank[user_screen_name] / len(graph_structure[user_screen_name])
        #print cur_pagerank
        # update cur_pagerank with teleporting:
        for user_screen_name in cur_pagerank:
            cur_pagerank[user_screen_name] = 0.9 * cur_pagerank[user_screen_name] + 0.1 * (1.0 / float(len(graph_structure)))
            error += abs(pre_pagerank[user_screen_name] - cur_pagerank[user_screen_name])
        # when iteration finish, pre_pagerank store the result from cur_pagerank for next iter
        temp_dict = pre_pagerank
        pre_pagerank = cur_pagerank
        cur_pagerank = temp_dict
    #normalization
    max_pagerank = max(pre_pagerank.values())
    for user_screen_name in pre_pagerank:
        pre_pagerank[user_screen_name] = pre_pagerank[user_screen_name] / max_pagerank 
    # rank and output
    ranked_users = sorted(
        pre_pagerank.items(), key = itemgetter(1), reverse = True)
    ranked_users = ranked_users[:min(len(ranked_users), 50)]
    return ranked_users, pre_pagerank

def integrate_similarity_pagerank(tweet_query_similarity, pre_pagerank, tweet_user_relation):
    integrated_result = {}
    # key: tweet_id, value: similarity score + pagerank score
    for tweet_id in tweet_query_similarity:
        if tweet_user_relation[tweet_id] in pre_pagerank:
            integrated_result[tweet_id] = tweet_query_similarity[tweet_id] + pagerank_dict[tweet_user_relation[tweet_id]]
        else:
            integrated_result[tweet_id] = tweet_query_similarity[tweet_id]

    ranked_integrated_result = sorted(integrated_result.items(), key = itemgetter(1), reverse = True)
    ranked_integrated_result = ranked_integrated_result[:min(len(ranked_integrated_result), 50)]
    return ranked_integrated_result

def main(query):
    filename = "example.json"  # change the example.json to your input json filename
    tweets = read_tweets(filename)
    #print tweets
    #print "tokens are", tweet
    tf_idf_vectors, idf_vector, tweet_user_relation = generate_tf_idf_vectors(tweets)
    retrieved_tweets_ids = retrieve_tweets(tf_idf_vectors, query)
    ranked_tweets_ids, tweet_query_similarity = rank_tweets(
        retrieved_tweets_ids, idf_vector, tf_idf_vectors, query)
    #output_tweets(ranked_tweets_ids, tweets)
    graph_structure = generate_graph_structure(tweets)
    pre_pagerank = calculate_pagerank(graph_structure) 
    print 'integrated results are:', integrate_similarity_pagerank(tweet_query_similarity, pre_pagerank, tweet_user_relation)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python tweets_retrieval.py 'query'"
    else:
        print sys.argv[1]
        main(sys.argv[1])
