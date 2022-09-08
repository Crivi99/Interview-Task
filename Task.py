import csv
from collections import Counter

#We store the exchange rate from any currency to EUR in a dict
change_eur={
    'EUR':1,
    'USD':1,
    'GBP':1.18,
    'ITL':1/1936.27
    }

#This function will check if an input user has missing or wrong id , missing name and surname or missing yearly amount,
# Skipping the rows that have those issues 
def verify_user(person:dict,unique_ids:set,row_number):
    if (not person['id'].isdigit()) or int(person['id'])<1:
        return (f"ID {person['id']} NOT PRESENT or NOT VALID on row {row_number}")
    
    if person['id'] in unique_ids:
        return (f"ID {person['id']} already present , on row {row_number}")

    if person['name']=='' and person['surname']=='':
        return (f"Name and Surname absent for ID {person['id']} on row {row_number}")

    try:
        int(person['yearly-amount'])
    except:
        return (f"The ID {person['id']} has NO yearly amount")
    return True

#This function will convert any amount in any currency to EUR    
def to_eur(amount,currency):
    return float(amount)*change_eur[currency]

#This function will return a list with the contents of the csv
#each user being a dict with keys named as the columns
def from_csv_to_dict(file_name:str):

    people=[]

    #in order to check as fast as possible if an id is already present we use a set
    unique_ids=set()
    row_number=0
    with open(file_name) as f:
        #this kind of reading is the best for our use-case as it takes the first line as fieldnames
        reader = csv.DictReader(f)

        for line in reader:

            #for each line in the csv we create a dict deleting the white spaces at the beginning and end if any
            line={fieldname.strip(): value.strip() for (fieldname, value) in line.items()}

            #check the validity of the user , if no error is returned the we can add it to the list of users
            #otherwise we skip this user
            person_status = verify_user(line,unique_ids,row_number)
            if type(person_status)!=bool :
                print(person_status)
            else:
                people.append(line)
            
            #add the id to the set and increase the row number of the csv
            unique_ids.add(line['id'])
            row_number += 1

    return people

def task_1(people):

    #we initialize the first person as both poorest and richest
    poorest= people[0]['name']+' '+people[0]['surname']
    richest= people[0]['name']+' '+people[0]['surname']
    minimum = float(people[0]['yearly-amount'])
    maximum = float(people[0]['yearly-amount'])

    #we iterate the rest of the list and compare each time to see if the curent user
    #is richer or poorer, if it is one of them , it takes the place
    try:
        for person in people[1:]:
            if person['currency']=='':
                person['currency']='EUR'
            if to_eur(person['yearly-amount'],person['currency'])>maximum:
                richest= person['name']+' '+person['surname']
                maximum = to_eur(person['yearly-amount'],person['currency'])
            if to_eur(person['yearly-amount'],person['currency'])<minimum:
                poorest= person['name']+' '+person['surname']
                minimum = to_eur(person['yearly-amount'],person['currency'])

    #skip that step if there's only one user in the list
    except:
        pass

    print(f"Richest: {richest}, Poorest: {poorest}")


def task_2(people):

    #create a list of names for users that have their country as Greece in the users list
    greek_users=[person['name']+' '+person['surname'] for person in people if person['country']=='Greece']

    if(len(greek_users)==0):
        print("There are NO Greek users")
    else:
        print('Greek users: ',end='')
        for name in greek_users:
            print(name,end=', ')
        print()

def task_3(people):
    #we use a set(as it doesn't allow duplicates) to store the country of the users that have ITL as currency 
    countries_using_ITL=set(person['country'] for person in people if person['currency']=='ITL')

    if(len(countries_using_ITL)==0):
        print("There are NO countries using ITL")
    else:
        print('ITL using countries: ',end='')
        for name in countries_using_ITL:
            print(name,end=', ')
        print()

def task_4(people):

    #we count the number of times each country appears in the users list
    count= dict(Counter(person['country'] for person in people))

    #sort the result in increasing order by number of appearances
    count = dict(sorted(count.items(), key=lambda item: item[1]))

    #print only the last 5 countries or all of them if they are less than 5
    for country in list(count)[-1:max(-6,-len(count)):-1]:
        print(country,count[country])

def task_5(people):
    for person in people:
        #we initilize the change as 0 for users that don't have an amount
        #but if the do have , change will take that amount
        change=0
        if person['monthly-variation']!='':
            change=person['monthly-variation']
        
        #the next year amount will be the present amount + 12 times the rate of change for each month
        print(f"Next year {person['name']+' '+person['surname']} will have {int(person['yearly-amount'])+12*int(change)} {person['currency']}")

def compute_delta(person,people6):
    #here we add to the dict of the person wanted the values the same user (by ID) has in the second csv
    #as the new-amount and new-currency and compute the difference in EUR , after that we bring that amount back to the new-currency
    try:
        person['new-amount']=[int(person1['yearly-amount']) for person1 in people6 if person1['id']==person['id']][0]
        person['new-currency']=[person1['currency'] for person1 in people6 if person1['id']==person['id']][0]
        if(person['new-currency']==''):
            person['new-currency']='EUR'
        person['delta']= (to_eur(person['new-amount'],person['new-currency'])-to_eur(person['yearly-amount'],person['currency']))/change_eur[person['new-currency']]
        return person

    #if we can't find the user in the second csv , we say that the new-amount and new-currency are the same of the first csv
    #such that the delta will be 0
    except:
        print(f"Missing user with id {person['id']} from second file")
        person['new-amount']=int(person['yearly-amount'])
        person['new-currency']=person['currency']
        if(person['new-currency']==''):
            person['new-currency']='EUR'
        person['delta']= (to_eur(person['new-amount'],person['new-currency'])-to_eur(person['yearly-amount'],person['currency']))/change_eur[person['new-currency']]
        return person

def task_6(people,people6):
    #compute the delta of each user in the first csv
    people = [compute_delta(person,people6) for person in people]

    #we check each user and compute the delta and see if it's richer, poorer or neither
    for person in people:
        if person['delta']!=0:
            if person['delta']>0:
                status='richer'
            else:
                status='poorer'
            print(f"{person['name']+' '+person['surname']} is {abs(person['delta'])} {person['new-currency']} {status} than before")
    # people = [ {person,**{'bagbag':second_file['yearly-amount']}}  for second_file in people6 for person in people if second_file['id']==person['id']]
    # print(next(filter(lambda x: x != None, map(lambda x: {'bababa': x["yearly-amount"]} if x["id"] == person["id"] else None, people6))))
    # people = [{**person, **next(filter(lambda x: x != None, map(lambda x: {'bababa': x["yearly-amount"]} if x["id"] == person["id"] else None, people6)))} for person in people]
    # print(people)

#read the 2 csv files
people = from_csv_to_dict('csv_file.csv')
people6= from_csv_to_dict('csv_file1.csv')

#run the tasks if at least one person is present
if len(people)>0:
    task_1(people)
    task_2(people)
    task_3(people)
    task_4(people)
    task_5(people)
    task_6(people,people6)
else:
    print('No valid user in the csv file')