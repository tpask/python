#!/usr/bin/python3
#sample of how to work with Dynamodb

import boto3
import json
import time
import operator
from boto3.dynamodb.conditions import Key
import argparse
import os

verbose=False
r_list="list"
max_reserved = 4

#create table
def create(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table (
        TableName = table_name,
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )
    print("table status:", table.table_status)

#add  data to list
def add_to_list(name, table_name):
    # note: data must be a json with at least a name key
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    millisec = millisec = time.time_ns() // 1000000
    data = { 'name': name, 'added': str(millisec)}
    table.put_item( Item = data)

# get the entire list
def get_list(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    resp = table.scan()
    data = resp['Items']
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        data.extend(response['Items'])
    data = sort_list(data)
    return data

#sort the list
def sort_list(list_of_dict):
    sorted_list = sorted(list_of_dict, key=lambda k: (k['added']))
    return sorted_list


# delete user from list:
def delete_item(name, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    try:
        resp = table.delete_item(Key={ 'name': name })
    except Exception as e:
        return e
    return resp

#query list
def query_list(name, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    try:
        resp = table.get_item(Key={'name': name})
    except Exception as e:
        return e
    if 'Item' in resp: found=True
    else: found = False
    return (resp, found)

#where is user in line
def query_name_in_list(name, table_name):
    users = get_list(r_list)
    c=0; found = False; num = 0; msg=name+" not on any list"
    for user in users:
        c=c+1
        if user['name'] == name:
            if c <= max_reserved:
                found = True; num = c; msg=name+" is number "+str(num)+" on registered list."
            else: # on wait list
                in_waitlist = c - max_reserved
                found = True; num = c - max_reserved; msg=name+" is number "+str(num)+" on wait list."
    return(found, num, msg)

#load list
def load_test_list(table_mame):
    name = "JoBob"
    for n in range(7):
        name = name + str(n)
        resp = add_to_list(name, table_name)

#print names in list
def print_list(table_name):
    users = get_list(table_name);
    c=0
    for user in users:
        c=c+1
        if c <= max_reserved:
            list="reserved"; num=c
        else:
            list = "wait"; num=c-max_reserved
        print("%s - %s on %s list" %(user['name'], str(num), list))

# end def section
# this creates loads a test table if one does not exist
existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
if r_list not in existing_tables: create(r_list)

#print_list(r_list)
#find user in line
#my_name = "tony6"; (found, num, msg) = query_name_in_list(my_name, r_list); print(msg)
#resp = delete_item("jane0", r_list); print(resp)
#my_name="tony"; (resp, found)=query_list(my_name, r_list); print(resp, found)

#deals with arguements:
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('--add', '-a', action='store_true', help='add user to list. e.g.  users.py -a "Joe"')
group.add_argument('--registered', '-r', action='store_true', help='list registered users')
group.add_argument('--waitlist', '-w', action='store_true', help='list user in wait list')
group.add_argument('--delete', '-d', action='store_true', help='list user in wait list. e.g users.py -d "Joe"')
group.add_argument('--testdata', '-t', action='store_true', help='load table with bogus users')
group.add_argument('--find', '-f', action='store_true', help='look for name in list. e.g users.py -f "Joe" ')
group.add_argument('--prt', '-p', action='store_true', help='list users both lists.') #

parser.add_argument('name', type=str, help='username (e.g. "John Doe")', default="", nargs='?')
args = parser.parse_args()

if verbose: print(args)

#no paramater supplied | --prt | -p
if not any(vars(args).values()) or args.prt :
    print_list(r_list)
#add user to list
elif args.add:
    if args.name: add_to_list(args.name, r_list)
    else: exit("syntax: %s --add \"JoBob\"" %os.path.basename(__file__))
#print registered name
elif args.registered:
    list = get_list(r_list)
    print("These names are on reserved list: ")
    for c in range(min(len(list), max_reserved)):
        print(list[c]['name'])
#print waitlist
elif args.waitlist:
    list = get_list(r_list)
    if len(list) > max_reserved:
        print("These names are on wait list:")
        c=max_reserved
        waitlist = list[c:None]
        for c in range(len(waitlist)):
            print(waitlist[c]['name'])
    else:
        print("There is no name on wait list.")
#delete name from list
elif args.delete:
    if args.name: delete_item(args.name, r_list)
    else: exit("syntax: %s --delete \"JoBob\"" %os.path.basename(__file__))
#find a specific name
elif args.find:
    if args.name:
        (found, num, msg) = query_name_in_list(args.name, r_list)
        print(msg)
    else: exit("syntax: %s --find \"JoBob\"" %os.path.basename(__file__))
