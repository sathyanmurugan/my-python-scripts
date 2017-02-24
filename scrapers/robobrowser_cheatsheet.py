# Author: Sathyan Murugan (sathyan.murugan@blacklane.com)
# Year:   2017

#https://github.com/jmcarp/robobrowser/issues/22

from robobrowser import RoboBrowser
from io import StringIO
import pandas as pd


#Login
browser = RoboBrowser(history=True,parser='html.parser')
login_url = _login_url
browser.open(login_url)
login_form = browser.get_form(action='/login.php')
login_form['username']= 'user'
login_form['password']= 'pw'
browser.submit_form(login_form)

#Soup the page
soup = browser.parsed

#Go to next URL
target_url = _target_url
browser.open(target_url)
form = browser.get_form()
form[_control_1]= _some_value
form[_control_2]= [_some_values]
form[__control_3_pageaction]= _some_ajax_value
browser.submit_form(form,submit=form['export']) #name=export

#Download CSV and store in df
response = browser.response.content.decode('utf8')
data = StringIO(response)
df = pd.read_csv(data,index_col=False,encoding='latin1')
