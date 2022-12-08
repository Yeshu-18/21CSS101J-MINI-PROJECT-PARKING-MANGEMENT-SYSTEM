import mysql.connector as mycon
con=mycon.connect(host='localhost',user='root',password="password")
cur=con.cursor()
cur.execute("create database if not exists Parking")
cur.execute("use Parking")
cur.execute("create table if not exists TEST6(V_No varchar(30) not null,Name varchar(20),V_Type varchar(20),Charged int, Timing datetime primary key, Status varchar(5) default 'in', Out_time datetime )")
con.commit()
print('|||||||||||||||||||||||||')
print('||                     ||')
print('|| Parking rack System ||')
print('||                     ||')
print('|||||||||||||||||||||||||')
print('------------------------------------------------------------')
print('LIFE IS A JOURNEY, BUT DONT WORRY YOU WILL FIND PARKING SPOT')
print('------------------------------------------------------------')
print('------------------------------------')
print('|$$$$$$$$$ AMOUNT CHARGED $$$$$$$$$|')
print('------------------------------------')
print('CAR PARKING Rs.50')
print("Bike PARKING Rs.25")
print("VAN AND OTHER LARGE VEHICLES Rs.100")
print('OTHER CYCLE etc. Rs.15')
print('-----------------------------------')
print('|$$$$$$$$$ ENTER DETAILS $$$$$$$$$|')
print('-----------------------------------')

# ------------TO ADD DETAILS-----------
def add():                             
    e=input("Enter Vehicle number:").lower()
    n=input("Enter Name of the Person Parking:")
    d=input("Enter Vehicle Type:")
    s=int(input("Enter Amount charged:"))
    t="now()"
    query="insert into TEST6(V_No,Name,V_Type,Charged,Timing) values('{}','{}','{}',{},{})".format(e,n,d,s,t)
    cur.execute(query)
    con.commit()
    print("## Details Saved ##\n")

# ------------TO SEARCH DETIALS----------
def details():                  #to display entire detials
        query="select * from TEST6 order by Timing desc"
        cur.execute(query)
        result=cur.fetchall()
        if cur.rowcount==0:
            print(" # There are no parked vehicles #")
        else:
            print("%10s"%"V_No","%20s"%"Name","%15s"%"V_Type","%10s"%"Amount","%25s"%"Entry_time","%10s"%"Status","%25s"%"Out_time")
            for row in result:
                 print("%10s"%row[0],"%20s"%row[1],"%15s"%row[2],"%10s"%row[3],"%25s"%row[4],"%10s"%row[5],"%25s"%row[6])
        print("-----------------------------------")
        print('\n')

def particular_detail():         #to search for a particular vehicle
        ans='y'
        while ans.lower()=='y':
            V_No=input("ENTER V_No TO SEARCH:")
            query="select * from TEST6 where V_No='{}' order by Timing desc".format(V_No)
            cur.execute(query)
            result=cur.fetchall()
            if cur.rowcount==0:
               print("Sorry! # Parking Detail Not Found #")
            else:
               print("%10s"%"V_No","%20s"%"Name","%15s"%"V_Type","%10s"%"Amount","%25s"%"Entry_time","%10s"%"Status","%25s"%"Out_time")
               for row in result:
                  print("%10s"%row[0],"%20s"%row[1],"%15s"%row[2],"%10s"%row[3],"%25s"%row[4],"%10s"%row[5],"%25s"%row[6])
            ans=input("SEARCH MORE(Y):")
            print("-----------------------------------")
            print('\n')

def parked_vehicles():
        query="select * from TEST6 where Status='{}' order by Timing desc".format('in')
        cur.execute(query)
        result=cur.fetchall()
        if cur.rowcount==0:
            print(" # There are no parked vehicles #")
        else:
            print("%10s"%"V_No","%20s"%"Name","%15s"%"V_Type","%10s"%"Amount","%25s"%"Entry_time","%10s"%"Status","%25s"%"Out_time")
            for row in result:
                  print("%10s"%row[0],"%20s"%row[1],"%15s"%row[2],"%10s"%row[3],"%25s"%row[4],"%10s"%row[5],"%25s"%row[6])
        print("-----------------------------------")
        print('\n')


def search():
    print('\'1\'->To dispaly all the vehicles')
    print('\'2\'->To search for a vehicle')
    print('\'3\'->To see the parked vehicles')
    ch=int(input('Enter your choice:'))              
    if ch==1:                          #to display entire details
       details()
       
    elif ch==2:                        #to search for a particular vehicle
        particular_detail()
        
    elif ch==3:
        parked_vehicles()
        
    else:
        print("## INVALID CHOICE ##")


# ------------TO MODIFY DETAILS----------- 
def status():
    ans='y'
    while ans.lower()=='y':
        V_No=input("ENTER V_No TO change its status as 'out':")
        query="select * from TEST6 where V_No='{}' order by Timing desc".format(V_No)
        cur.execute(query)
        result=cur.fetchall()
        if cur.rowcount==0:
            print("Sorry! # Parking Detail Not Found #")
        else:
            st='out'
            query="update TEST6 set Status='{}',Out_time={} where V_No='{}'".format(st,"now()",V_No)
            cur.execute(query)
            con.commit()
            print("## RECORD DETAIL UPDATED ##")
        ans=input("UPDATE MORE(y):")
    print("-----------------------------------")
    print('\n')

def delete():    
        ans='y'
        while ans.lower()=='y':
            V_No=input("ENTER V_No TO DELETE:")
            query="select * from TEST6 where V_No='{}' order by Timing desc".format(V_No)
            cur.execute(query)
            result=cur.fetchall()
            if cur.rowcount==0:
                print("Sorry! # Parking Detail Not Found #")
            else:
                print("\n")
                print("%10s"%"V_No","%20s"%"Name","%15s"%"V_Type","%10s"%"Amount","%25s"%"Entry_time","%15s"%"Status","%25s"%"Out_time")
                for row in result:
                 print("%10s"%row[0],"%20s"%row[1],"%15s"%row[2],"%10s"%row[3],"%25s"%row[4],"%10s"%row[5],"%25s"%row[6])
                choice=input("\n ##  ARE YOUR SURE TO  DELETE?(Y):")
                if choice.lower()=='y':
                    query="delete from TEST6 where V_No='{}'".format(V_No)
                    cur.execute(query)
                    con.commit()
                    print("## RECORD DELETED SUCCESSFULLY!=== ")
            ans=input("WANT TO DELETE MORE(y):")
        print("-----------------------------------\n")


def update():
        ans='y'
        while ans.lower()=='y':
            V_No=input("ENTER V_No TO UPDATE:")
            query="select * from test6 where V_No='{}' order by Timing desc".format(V_No)
            cur.execute(query)
            result=cur.fetchall()
            if cur.rowcount==0:
                print("Sorry! # Parking Detail Not Found #")
            else:
                print("\n")
                print("%10s"%"V_No","%20s"%"Name","%15s"%"V_Type","%10s"%"Amount","%25s"%"Entry_time","%15s"%"Status","%25s"%"Out_time")
                for row in result:
                 print("%10s"%row[0],"%20s"%row[1],"%15s"%row[2],"%10s"%row[3],"%25s"%row[4],"%10s"%row[5],"%25s"%row[6])
                choice=input("\n ##  ARE YOUR SURE WANT TO UPDATE?(Y):")
                if choice.lower()=='y':
                    print("==YOU CAN UPDATE ONLY V_Type AND Amount ==")
                    d=input("ENTER NEW V_Type:")
                    s=int(input("ENTER NEW Amount:"))
                    query="update TEST6 set V_Type='{}',Charged={} where V_No='{}'".format(d,s,V_No)
                    cur.execute(query)
                    con.commit()
                    print("## RECORD DETAIL UPDATED ##")
            ans=input("UPDATE MORE(y):")
            print("-----------------------------------")
            print('\n')
                
        
def modify():
    print('\'1\'-> To update details')
    print('\'2\'-> To delete details')
    print('\'3\'-> To change the status of the vehicle')
    ch=int(input('Enter your choice'))
    if ch==1:
        update()

    elif ch==2:
        delete()

    elif ch==3:
        status()

    else:
        print("## INVALID CHOICE ##")

# ------------MAIN_PROGRAM---------------
choice=None
while choice!=0:
    print("\'1\'->ADD vehicle details")
    print("\'2\'->Display vehicle details")
    print("\'3\'->Modify vehicle details")
    print("\'0\'->Exit")
    choice=int(input("Enter your Choice:"))
    if choice==1:
        add()
    elif choice==2:
        search()
    elif choice==3:
        modify()
    elif choice==0:
        print("## Bye!!! Thank you!!!##")
    else:
        print("## INVALID CHOICE ##")
