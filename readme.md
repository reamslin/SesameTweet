API: https://developer.twitter.com/en/docs

https://pypi.org/project/GetOldTweets3/


SESAME TWEET
sesametweet.herokuapp.com

This site is intended to be a subset of Twitter focused on only Sesame Street and the Sesame Street characters. It allows you to see a feed of tweets from those accounts and to navigate tweets by looking at people that are mentioned and hashtags that are used.

I implemented hashtgas and mentions. I decided to implement these as these are integral parts of Twitter, it also allowed users to discover tweets that talk about certain people or tweets about certain topics.

The main page allows users to see the basic feed of tweets from the sesame street accounts. There are buttons that navigate users to a list of people mentioned in tweets. Clicking on a name, will show a screen that has a smll profile page for the mentioned user and all the tweets that the user is mentioned in. There is also a tab that displays all hashtags used by the sesame street accounts. Clicking on a hashtag will display all the sesame street tweets that use the given hashtag. The last button lists all of the sesame street accounts. Clicking on a character will display a profile page for the account and all of the tweets from that account. In addition to the buttons, I also added links to the mentions and hashtags from the tweets directly. Lastly, I have added a twitter link to all twitter provided data that will take a user directly to the data on Twitter's website.

This app uses Flask, SQLalchemy,  Jinja, Bootstrap, HTML, CSS, and Javascript

