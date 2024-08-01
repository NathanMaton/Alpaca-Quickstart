# Accelerating your build of an Alpaca trading bot:

Here’s some code that as of August 1, 2024 you could use to make your first trade using Alpaca, Alpaca-Py and a few other libraries. As anyone building things knows, online code/tutorials vary widely in quality. Much of the Alpaca documentation was out of date, and the Alpaca-py documentation was sparse.  

In my repo you can find here on GitHub, there are a few key files:

* Trade: This is the core engine where I’ve set up functions to make trades and has most of the logic/code.
* Evaluate: This file is for ongoing evaluation of your portfolio and I import it into a few other scripts.
* Buy/sell: This is setup to run on a scheduler. I ended up deploying this to Heroku and using their scheduler so I didn’t have to monitor it locally. I won’t go into the Heroku setup but feel free to reach out if you’re interested.

Check the code for more information.