import re
import random

def message_manipulation(req_message):

	req_message_mod = req_message.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "").rstrip('0123456789')

	ids = re.sub('[^\d*\.?\d+]+', " ", req_message).strip().split(" ")

	message_string = re.sub('\d*\.?\d+', "", req_message_mod)

	return req_message_mod, message_string, ids 


# msg = '<request><id>59841</id><measur1234ement>123.60</measur98.78ement>'

# resp_msg, msg_string, req_ids = message_manipulation(msg)


# print(resp_msg, msg_string, req_ids)