
# CPSC 449 Web Backend Engineering
## Project-1
### Project Members:
*  (@csu.fullerton.ed) | Role: Ops
* Mohit Kumar (mohit_kumar@csu.fullerton.edu) | Role: Dev
* Emily Pham (tpham523@csu.fullerton.edu) | Role: SDET

Installations:pip3 install flask, sudo apt install --yes gunicorn3


#### ---------------------------------- Dev Ops-------------------------------------------
1) Use this code for generating 3 instance of foreman in a terminal
```
foreman start -m post=3,vote=3
```

2) In separate terminal run
```
ulimit -n 8192 && caddy
```

3) Then go to localhost:2015/posts or localhost:2015/votes
ex: to get all post in Database run
http://localhost:2015/posts/filter

#### ---------------------------------- Post API-------------------------------------------
1. Create a new post: Send a POST request to route of create_post() fn
>
```
Example request:
curl -i -X POST -H 'Content-Type:application/json' -d '{"title":"Test post", "description":"This is a test post", "username":"some_guy_or_gal", "community_name":"449"}' http://localhost:2015/posts/create;
```

2. Delete an existing post: Send a GET request to route of delete_post() fn
```
Example request:
curl -i -X DELETE http://localhost:2015/posts/delete?post_id=4;
```

3. Retrieve an existing post: Send a GET request to route of get_post() fn
```
Example request:
curl -i http://localhost:2015/posts/get?post_id=2;
```

4. List the n most recent posts to a particular community: Send a GET request to route of get_posts_filter() fn with args (community_name and n)
```
Example request:
curl -i http://localhost:2015/posts/filter?n=2&community_name=calculus;
```

5. List the n most recent posts to any community: Send a GET request to route of get_posts_filter() fn with args (n)
```
Example request:
curl -i http://localhost:2015/posts/filter?n=2;
```

#### ---------------------------------- Vote API-------------------------------------------



1) Upvote a post:
```
Example request:
curl -i -X POST -H "Content-Type: application/json" -d '{"vote_id":"100"}' 'http://localhost:2015/votes/upvotes'
```

2) Downvote a post:
```
Example request:
curl -i -X POST -H "Content-Type: application/json" -d '{"vote_id":"100"}' 'http://localhost:2015/votes/downvotes'
```

3) Report the number of upvotes and downvotes for a post:
```
Example request:
curl -i 'http://localhost:2015/votes/get?vote_id=100';
```

4) List the n top-scoring posts to any community:
```
Example request:
curl -i 'http://localhost:2015/votes/getTop?n=3';
```

5) Given a list of post identifiers, return the list sorted by score.:
```
Example request:
curl -i -X POST -H "Content-Type: application/json" -d '{"post_ids":["1","3"]}' 'http://127.0.0.1:5000/getList'
```

## TESTING

##  Unit Testing 

We use Tavern to test each service. Test files are located under 'tests'.
configobj package is also needed to configure filepath for testing purpose.


1) How to install Tavern
```
pip3 install tavern[pytest]
```

2) How to install configobj
```
pip3 install configobj
```

3) How to run test

```
py.test 

```
 
#  Load Testing 

We use a framework called Locust to perform load test. This load test also simulates a user scenario in which user performs all tasks using both services.

We also use faker package to generate fake data for random testing.

1) How to install faker
```
pip3 install faker
```

2) How to install locust
```
pip3 install locustio
```

3) How to run test
```
locust -f tests/loadTest.py --host=http://localhost:2015 --no-web -c 100 -r 10

# -c 100: simulate number of users using the services, here it's 100
# -r 50: the rate of # users being spawned per second, here it's 50
```

4) To stress the services, we can increase the number of concurrent users to 500-1000
```
locust -f tests/loadTest.py --host=http://localhost:2015 --no-web -c 500 -r 50

```

