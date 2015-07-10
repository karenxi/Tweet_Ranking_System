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

def generate_graph_structure(tweets):
    #key: userID; value: mentioned userIDs
    graph_structure = {}
    unique_user_screen_names = set()
    # generate users nodes graph
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
    return ranked_users

def main():
    filename = "example.json"  # change example.json to your input json filename
    tweets = read_tweets(filename)
    graph_structure = generate_graph_structure(tweets)
    print 'ranked_users',calculate_pagerank(graph_structure)
   
if __name__ == "__main__":
    main()
