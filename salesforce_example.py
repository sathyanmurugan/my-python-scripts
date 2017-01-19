from salesforce.salesforce import Salesforce
from utilities.utilities import get_credentials

#Connect to Salesforce
c = get_credentials()
sf = Salesforce(c.salesforce_user,c.salesforce_pw)

query = "SELECT ID,Name FROM Account LIMIT 10"
query_result = sf.query(query)
print (query_result)

