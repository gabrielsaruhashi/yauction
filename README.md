## Test
    flask run
## Design
- General -
HTML: We opted for an overarching layout.html file to better organize the pages in our navigation bar and to create distinct areas for logged-in and non-logged-in users.


CSS: CSS was used for overall aesthetic optimization with font choices, containers, etc. We customized our navbar to resemble that of prominent auction websites, such as Ebay.


Javascript: Javascript was used for form validations across the different pages, and to implement the search bar.


Python/Flask: Python was our programming language choice for the back-end. Flask was used as our micro framework.


SQL: Used to query our database.


- Database Infrastructure -
For storing the website’s data, we opted to create four databases (users, items, bids, and watchlist). Users’ primary information, such as their email_adresses, passwords and venmo usernames were stored in ‘users’, while the items informations was saved in “items”. All the bid operations were recorded in our ‘bids’ table. Finally, ‘watchlist’ stores auctions that a user has chosen to keep track of. We chose the design above in order to avoid redundancy between databases and more efficiently access data via SQL operations.
- Registering -
Email Checking: YAuction, as the name suggests, is created for Yale students. In order to ensure only Yalies could access the platform, we implemented a backend verification that checks if the user has a @yale.edu account. The email is then added to the database. In addition to javascript form validation, our application also queries our user database to ensure the user does not already have an account.


Password Checking: To ensure the user did not make any typos, we prompt them to write down their password twice. The password is then stored in our database as a hash through the pwd_context.encrypt().


Username & Venmo: Registrants are asked to include a username that will be used as their identifiers if they auction an item in the platform. Our application queries our database to ensure the username is not already taken/being used. Venmo accounts are used for payments and transactions. 


- Apology -
Returns an apology with a funny meme of a cat.


- Logging In -
Login: Users provide their username and password. Both are checked with information stored in the ‘users’ database and access is provided if both inputs match a row.


- Index -
Index: Upon logging in, up to 10 random live auctions are displayed in the screen. All include hyperlinks that redirect to their individual item pages.
Search:  Using JSON and Twitter’s Typehead, we implemented a search bar that jsonifies the rows similar to users’ typed keyword searches and allows them to quickly access item pages.


- My Bids - 
my_bids queries the ‘bids’ database for all bids placed by the user. Then, for each item that the user has bid on, it checks if the auction is still live. If it is, it queries for and displays the auction’s information on the My Bids page. If the user has no active bids, an apology is returned explaining as much.


- My Auctions -
my_auctions queries the ‘items’ database for all items sold by the user. Then, for each item that the user has listed, it checks if the auction is still live. If it is, it queries for and displays the auction’s information on the My Auctions page. If the user has no active bids, an apology is returned explaining as much.


- Watchlist -
Our implementation of watchlist queries the ‘watchlist’ table for all entries that match user’s id and then displays them in the Watchlist page.


- Sales History-
Our implementation of sales queries the ‘items’ database for all expired auctions created by the current user. These results are then displayed on the Sales History page.


- Purchase History -
Our implementation of history finds all the current user’s bids to get the item ids. It then uses this information to find all the expired auctions in which the current user had the winning bid. The relevant information is displayed in our Purchase History page. On this page, users can see each of the auctions they have won and access a venmo link to pay the seller the appropriate amount. 


- Item - 
The item dynamic route provides each item its own individual profile page and can be seen as the core of our project. Each item page can be accessed by the route .../itm/<item_id>. There are two methods to reach the page. 
Through the post method, users can post a bid form or an add to watchlist form. If user post a bid form, the code checks if it a valid number and if it actually tops the current winning bid. If these requirements are met, the bid is inserted into the ‘bids’ transactions database, the item’s current bid is updated with the bid, and the total number of bids is updated. Otherwise, if the user posts an add to watchlist form, the platform checks if the item is already in the user’s watchlist. If not, the item is then inserted into his watchlist. If it is, the ‘add to watchlist’ button becomes a ‘remove from watchlist’ button that deletes the item from the ‘watchlist’ database when clicked.
Through the get method, the item profile is selected and the code checks if it is still assigned as live. If so, we check whether the auction duration has expired, in which case we set the status code to 0 (inactive auction). If the auction is indeed live, we display the relevant information.


- Sell -
Users are prompted to provide the name, description, starting bid, duration and image for the product they want to auction. Form responses are validated both in the backend (Python) and frontend (Javascript). Only .jpg files are accepted for the images. 
Upon submitting a form in sell, users are automatically redirected to the newly created auction item page.


- Image Hosting -
YAuction stores product images in the /images folder within the /static directory. The user’s selected file is checked to make sure that it is a .jpg. If it is, it is automatically renamed in the format item_id_number.jpg for easy access across our web pages and to ensure that it can always be traced back to its corresponding item. If the user attempts to select a non-.jpg file, it will not be uploaded to the /images folder. If the user does not upload a file, a default image of a giant inflatable bulldog will be used.


- alert.py -
Alert.py is a separate script meant to be used with cron to send a reminder email to all users who placed bids in auctions that are about to expire in 24 hours or less. After multiple SQL Operations, we end up with a dictionary with keys that represent each item that is about to expire, and an array with all user emails that placed bids. For each of the item keys, we use SMTP to deliver customized emails from Yauction’s official email (yauction.yale@gmail.com) to the keys’ respective array of recipients announcing that the auction is about to end in the header, and then indicating the URL for the auction in the body of the email.
The script can be executed through crontab crontab.txt


- Cron Jobs -
CronJobs would be used to automatically run the alert.py once a day. Though we followed the instructions and invoked the Cron interface in the IDE, the script was not running as programmed for some reason. We believe that Cloud9 does not support Cron (https://community.c9.io/t/how-to-enable-run-cron/2250) at this moment in time.


## Documentation
Our project grew out of the same concepts we used for Finance, and as such relies on a similar basic framework. 


Starting the server
Starting the server is done in the usual way, by navigating into the project’s home directory (in this case /yauction/) and using the “flask run” command in the terminal. 


Creating an account
Click the link at top center that says “Register.” This will redirect you to the registration page, where you will be asked to input your preferred username, Yale e-mail address, password, and Venmo username. Note that even for testing, a real Yale email is required to receive mail from the email system that we implemented, and a real Venmo username is required for the redirect to function.


Logging in
Click the top banner or the link that says “Login.” This will redirect you to the login page, where you will be asked to provide your username and password. 


Index Page 
This will redirect you to the Index Page, which you can also access by clicking the colorful “YAuction” logo in the top left corner of the screen. This page displays a random sampling of 10 currently active auctions and includes search functionality if you are looking for a specific item. 
Note that you we leave it to you to sell and bid on items, which will require you to create multiple accounts. This was due to constraints imposed by our implementation of the auction duration timer, and also demonstrates both sides of our functionality well (from both the buyer's and seller's perspective). When testing, if you would like to avoid waiting a day or two for the auctions to expire on their own, note also that you can manually mark them as expired in phpliteadmin by changing the "status" column of entries in the 'items' table from 1 (active) to 0 (expired).  
Item Page
Clicking on an item from the Index Page (as well as many other pages) will bring you to the appropriate Item Page. On this page, you can view a variety of information about the item in question, including:
Item Name
Description
Starting Bid (set by the seller)
Total Number of Bids Placed on the Item
Current Bid
Product Image
Seller’s Username
Auction Endtime and Date
If the auction is still live and you are not the seller of the item, you can place a bid on the item. You may also add or remove the item from your watchlist. 


My YAuction: 
Mousing over My YAuction in the navbar will display a drop-down list of pages. These include the following: 


My Bids: 
This page displays all of the items that you are currently bidding on (that are still live). It also informs you of your last bid and the current bid. Clicking on an item will redirect you to that item’s Item Page. 


My Auctions: 
This page displays all of the items that you are currently selling (that are still live). It also informs you of the current bid amount. Clicking on an item will again redirect you to that item’s Item Page. 


Watchlist:
This page displays all of the items that are currently in your watchlist. Using this feature, you may save items that you are interested in following or purchasing, but that you do not yet want to bid on. As always, clicking on an item will redirect you to that item’s Item Page.


Purchase History: 
This page displays all of the items that you have successfully bid on and won. A link is included beneath each item that will redirect you to the seller’s Venmo profile. Unfortunately, Venmo discontinued their API recently so we were not able to integrate it to the extent we would have liked, but using this link and the helpful reminder of the exact sum owed, you can easily make payments. In actual implementation, some payments would likely rely on cash as well. To reflect this, we added the ability to see the seller's email address to contact them. 


Sale History: 
This page displays all of the items that you have put up for sale on YAuctions in the past (that are no longer live). It also displays the winning bidder's email address for ease of communication. 

Sell:
Next on the navbar you will find the Sell button. Clicking this will redirect you to the Sell Page, where you may enter a name, description, and starting price for your auction item as well as picking your desired duration for the auction and uploading a product image from your device in the .jpg format. If no image is uploaded, a stock image will be used. Feel free to add any listings you would like and explore them via the other pages previously mentioned. 

Logout: 
Finally, the Logout button in the top right will - of course - log you out from your account and redirect you to the login screen. 

Alert: 
We tried to implement an emailing system using would let users know when an item that they had bid on would be ending within 24 hours. It functions just fine, but in order for it to work autonomously, we would need to rely on the cron function which is not available in the IDE as far as we can tell. Our attempt relied on the crontab.txt file, which is included. More on this is included in the design section. You can call the function manually by typing “python alert.py” into the terminal, which will email all users who have placed bids on items ending in the next 24 hours.

CronJobs: 

