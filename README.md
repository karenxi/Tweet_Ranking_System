# Tweet Ranking System

## Introduction

## Implementation 

### Build a vector space retrieval system only based on tweets’ texts

Extract tweets data from Json format file.
 i use tf-idf to build my vector space model. Each tweet text can be considered as a document. This system can return results ordered by the cosine similarity between the tf-idf of the tweet text and the query.
Tweets with higher similarity to the query can be first.
vector space retrieval instead of a pure AND search, but if the tweets do not contain any terms in the query, I did not calculate the cosine similarity
If a query returns more than 50 results, only return the first 50.
If any of the tokens in the query do not occur in the tweet corpus, then the idf will be undefined. Your program should not return any results.

### Build a page rank system on users
the second step implemented the classic PageRank algorithm on the tweet corpus. Rather than scoring each tweet, however, i wanted to figure out the PageRank score of users. First I built a graph structure based on @mentions. In the the twitter graph:
the nodes of graph are users
The edges are binary and directed. If eva mentions Alice once, in 10 tweets, or 10 times in one tweet, there is an edge from eva to Alice, but there is not an edge from Alice to eva.
The edges are unweighted. If Bob mentions Alice once, in 10 tweets, or 10 times in one tweet, there is only one edge from eva  to Alice.
If a user mentions herself, ignore it.
If a user is never mentioned and does not mention anyone, their pagerank should be zero. I did not include the user in the calculation.
Assume all nodes start out with equal probability and the probability of the random surfer teleporting is 0.1, this program also returns the top 50 results (which are users, not tweets!) with highest PageRank scores.

### Integrated tweet ranking system
develop an integrated tweet ranking system by integrating the cosine similarity (per tweet) and PageRank score (per user)
First, I normalized each cosine similarity score between the tf-idf of the tweet text and the query by dividing the maxal score of the total similarity scores, also, I normalized each user's pagerank score by dividing the maximal score of the total page rank scores. Second, for each query, I added its normalized cosine similarity score and pagerank score as its integrated score. Then, when query words are input, it returns the top 50 relevant tweet_ids and the integrated scores.
