# Tweet Ranking System

Built a integrated Tweet Ranking System by using vector space retrieval and page rank techniques. 


## Implementation
The implementation consist of three parts:

### 1. A vector space retrieval system on tweets
This vector space retrieval system only bases on tweets' texts. I extracted tweets texts from Json file. For each tweet, tokenized each tweet's text using whitespaces and punctuations as delimiters, and changed all letters to lowercase. Then, used tf-idf to build the vector space model. Each tweet text can be considered as a document, the system returns results ordered by the cosine similarity between the tf-idf of the tweet text and the query.

* Tweets with higher similarity to the query should be first.
* Using vector space retrieval instead of a pure AND search, but if the tweets do not contain any terms in the query, I do not calculate the cosine similarity
* If a query returns more than 50 results, only return the first 50.
* If any of the tokens in the query do not occur in the tweet corpus, then the idf will be undefined, the system should return no results.


### 2. A page rank system on users
The second part implements the classic PageRank algorithm on the tweet corpus. Rather than scoring each tweet, however, I wanted to figure out the PageRank score of users. I built a graph structure based on @mentions. In the the twitter graph:

* The nodes of graph are users.
* The edges are binary and directed. If Karen mentions Alice once, in 10 tweets, or 10 times in one tweet, there is an edge from Karen to Alice, but there is not an edge from Alice to Karen.
* The edges are unweighted. If Karen mentions Alice once, in 10 tweets, or 10 times in one tweet, there is only one edge from Karen to Alice.
* If a user mentions herself, ignore it.
* If a user is never mentioned and does not mention anyone, their pagerank should be zero. I did not include the user in the calculation.

Assume all nodes start out with equal probability and the probability of the random surfer teleporting is 0.1. When the error reaches 10 ** (-6), stop running the PageRank calculation.

This system also returns the top 50 results (which are  users, not tweets) with highest PageRank scores.


### 3.Integrated tweet ranking system
First, I normalized each cosine similarity score between the tf-idf of the tweet text and the query by dividing the maximal score of the total similarity scores. Also, I normalized each user's page-rank score by dividing the maximal score of the total page rank scores. Second, for each query, I added its normalized cosine similarity score and page-rank score as its integrated score. Then, when query words are input, it returns the top 50 relevant tweet_ids and the integrated scores.



