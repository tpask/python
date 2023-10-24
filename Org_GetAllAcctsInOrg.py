#!/usr/bin/python3

'''
This script lists all account in an organiztion - Must be run on the Org our deligate org account
'''
import boto3
import json


client = boto3.client('organizations')
rootId = client.list_roots()["Roots"][0]["Id"]
acctList=[]
ouList =[]

#get a list of ous and their parent path
# [{'ouId': 'sfxx12', 'ouName': 'DEV', 'ouPath': 'Dev/difdkfjd'

# traverse the tree to get all OUs under parent
def getChildren(id):
    childs = client.list_children(ParentId=id,ChildType='ORGANIZATIONAL_UNIT')
    return [child["Id"] for child in childs["Children"]]

def getAcctsForParent(Id, parentName = ""): 
  paginator = client.get_paginator('list_accounts_for_parent')
  page_iterator = paginator.paginate(ParentId=Id) #this gets the account list
  for page in page_iterator:
    for a in page['Accounts']:
      if a: #append accounts only if there is any
        a['Type'] = 'account'
        a['parent'] = parentName
        acctList.append(a)
  return   

def getAllOusIds(Id):
  full_result = []

  paginator = client.get_paginator('list_children')
  iterator  = paginator.paginate( ParentId=Id, ChildType='ORGANIZATIONAL_UNIT' )

  for page in iterator:
    for ou in page['Children']:
      full_result.append(ou['Id']) # 1. Add entry
      full_result.extend(getAllOusIds(ou['Id'])) # 2. Fetch children recursively
  return full_result

def getOuName(Id):
  resp = client.describe_organizational_unit( OrganizationalUnitId=Id )
  return resp['OrganizationalUnit']['Name']

# get a list of all accounts at root level
resp = getAcctsForParent(rootId, "root"); #print(json.dumps(acctList, indent=2, default=str))

#for fGen in firstGenOUs: # each first 
firstGenOUs = getChildren(rootId) # print(json.dumps(firstGenOUs, indent=2, default=str))

# for each 1st gen ou, get all the ous under it
for ou in firstGenOUs: 
  # get all accounts in 1st gen OU
  fGenName = getOuName(ou) ; #print(ouName)
  resp = getAcctsForParent(ou, fGenName)
  #get all children of 1 gent
  decendents = getAllOusIds(ou); #print(decendents)
  if len(decendents) >0 : #  if ou has children
    for d in decendents: 
      dName = getOuName(d)
      dName = fGenName+"/"+dName
      #get accounts for each decendent
      resp = getAcctsForParent(d, dName)

print(json.dumps(acctList, indent=2, default=str))
