import mechanize
from StringIO import StringIO
import pandas as pd

#Login to Website
br = mechanize.Browser()
br.set_handle_robots(False)
br.open(_url)

#List all forms
for form in br.forms():
	print ("Form name:", form.name)
	print (form)

#Select form either by selecting from list or specifying name
#br.select_form("form1")
br.form = list(br.forms())[0]

#Login with username and pw
br.form['username']= _username
br.form['password']= _pw
br.submit()

#Navigate to another page
br.open(_url2)

#Select another form
br.form = list(br.forms())[0]

#List all controls in a form
for control in br.form.controls:
	print (control)

#Select control in form	
control = br.form.find_control(_control_name)

#Set readonly as False if necessary
control.readonly = False

#Select value in control and submit page
control.value = [_value1, _value2]
response = br.submit()

#Assuming there is a 'pageaction' control,
#Select readonly as False,
#Set value as file, to download a file 
#(This really depends on the website, use "inspect" to test responses) 
control = br.form.find_control(_pageaction)
control.readonly = False
control.value = _file

#Download file and store in Pandas df
response = br.submit()
data = response.read()
formatted_data = StringIO(data)
df = pd.read_csv(formatted_data,index_col=False)

