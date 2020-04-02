#!/usr/bin/python
import sys, telegram, tarfile

# create bot communication
bot = telegram.Bot(token='1127169649:AAG9pPjb_dXRmlgOyXCddOR6PHQcj37lU8Q')

# get message to send
message = sys.argv[1]

# send finished test message
bot.send_message(chat_id=74540520, text=message)

# send test results if the message is that the test finished
if message == "Test finished!":
    # get tar files
    caltar = tarfile.open(open("last_caltar.txt").read())
    srrtar = tarfile.open(open("last_srrtar.txt").read())
    
    # get pdf images with results
    srr_analog  = caltar.extractfile('srr_analog.pdf')
    srr_digital = srrtar.extractfile('srr_digital.pdf')
    
    # send pdfs
    bot.send_document(chat_id=74540520, document=srr_analog)
    bot.send_document(chat_id=74540520, document=srr_digital)
