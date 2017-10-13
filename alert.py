import time
import datetime
from cs50 import SQL

# Import smtplib for the actual sending function
import smtplib

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///yauction.db")

#get time and make it readable in SQL
time_temp = datetime.datetime.now()
time_now = time_temp.strftime('%Y-%m-%d %H:%M:%S')

# notify user if auctions is about to end (1 day length)
difference = datetime.timedelta(days=1)
time_end_temp = time_temp + difference
time_end = time_end_temp.strftime('%Y-%m-%d %H:%M:%S')

# get expiring items
expire_items = db.execute("SELECT item_id FROM items WHERE timestamp_end BETWEEN :time_now AND :time_end", time_now=time_now, time_end=time_end)

# put item_ids in a list
item_ids = []

for item in expire_items:
    item_ids.append(item["item_id"])

# get empty dictionary
items_user_ids = dict()

# populate it with all the users that chose that product { '67(prancha)': [usuario1,usuario2,usuario3] }
for item in item_ids:
    
    # put all the user ids for a single product in a temporary list
    temp_list = []
    
    dict_temp = dict()
    dict_temp = db.execute("SELECT bidder_id FROM bids WHERE item_id=:item_id", item_id=item)
    
    # append the bidder id to temporary list
    for temp in dict_temp:
        temp_list.append(temp["bidder_id"])
    
    # now copy to official items_user_ids dictionary, but ensure each user id only appears once 
    items_user_ids[item] = list(set(temp_list))
    

item_user_emails = dict()

# get a dictionary with all emails of users that bid in that auction { '67' : [usuario1@yale.edu, etc]
for item in items_user_ids:
    
    # create empty list
    email_list = []
    
    # iterate over all the items
    for userid in items_user_ids[item]:
        
        dict_temp = db.execute("SELECT email FROM users WHERE user_id=:userid", userid=userid)
        
        # populate the array with the emails for that specific expiring item
        for temp in dict_temp:
            
            # append email to auxiliary email_list
            email_list.append(temp["email"])
            
    # insert the array in the official item-emails dictionary
    item_user_emails[item] = email_list
    

# iterate through all the expiring items
for item in item_user_emails:
    item_name = db.execute("SELECT item_name from items WHERE item_id=:item_id", item_id = item)[0]
    
    # prepare the email headers
    gmail_user = "yauction.yale@gmail.com"
    gmail_pwd = "yauction123"
    FROM = "yauction.yale@gmail.com"
    recipients = item_user_emails[item]
    TO = ", ".join(recipients)
    SUBJECT = "Auction for {} is ending soon!".format(item_name["item_name"])
    TEXT = "Hello! Check out your auction at https://ide50-md2252.cs50.io/itm/{}".format(item)
    
    #send message to all the recipients that bid in the expiring item
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, recipients, message)
        server.close()
        print("successfully sent the mail")
    except:
        print("failed to send mail")
