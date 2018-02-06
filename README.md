# Twotter



Twitter clone with some extra functions

Twitter clone where users may register and log in in order to post their thoughts online.
It also provides a RestFul API information from the databases used in this project
It is also possible to obtain information from the user's twitter account and convert it in json format

In order to access the API information type the following on the url:
<p>/users</p>
<p>/users/-id number-</p>
/user_id

To access specific information for twitter json format, head to twitter_api/main.py and modify the 'info' variable inside legit_twitter() or leave it blank to obtain all the information
*Note that the user will have to submit a twitter token generated from the twitter developer page
