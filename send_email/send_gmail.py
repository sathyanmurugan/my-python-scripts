import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from bs4 import BeautifulSoup
import pandas as pd
import io

def df_to_html(df):
    '''
    Converts a Pandas Dataframe to HTML, can be used to embed in email 
    '''
    table = io.StringIO()
    df.to_html(table,index=False,justify='left')
    html_table = table.getvalue()
    return html_table

def send_gmail(email_address, app_password, recipient_list, subject, message_parts, display_name=None):

	my_email = MIMEMultipart()
	my_email['To'] = ", ".join(recipient_list)
	my_email['From'] = formataddr((realname, email_address))
	my_email['Subject'] = subject

	for part in message_parts:
		#Check if html
		if bool(BeautifulSoup(part, 'html.parser').find()):
			text_type = 'html'
		else:
			text_type = 'plain'
		msg = MIMEText(part, text_type)
		my_email.attach(msg)

    # Login and send email
	with smtplib.SMTP('smtp.gmail.com', 587) as server:
		server.starttls()
		server.login(email_address, app_password)
		server.send_message(my_email)

