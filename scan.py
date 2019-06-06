import threading
import time
import re
import mysql.connector
from mysql.connector import errorcode
import subprocess
from resource import ip_increase, server_control, is_connected, Cpu_mac

ignore = ['US', 'GB', 'IE', 'FR', 'DE', 'AU', 'BE', 'CA', 'IL', 'NL', 'UM']
res_list = []
sleep_time = 0

class new_scan(threading.Thread):
    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.ip = ip

    def run(self):
        scan(self.ip)

def whois(host):
    check = "whois {0} | grep country | head -n 1 | egrep -v \"US|GB|IE|FR|DE|AU|BE|CA|IL|NL|UM\" | wc -l".format(host)
    result = subprocess.Popen(check, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()[0].decode('ascii')
    time.sleep(0.5)
    #debug
    print(host, 'whois')
    print(output)
    #
    return output

# db conn
#Database.initialize()
# python-namp start
#nm = nmap.PortScanner()

def scan_controller():
    global nm
    # get last ip
    try:
        cnx1 = mysql.connector.connect(user='root', password='xxxxxx', host='127.0.0.1', database='scan')
        cursor1 = cnx1.cursor()
        q1 = "SELECT ip FROM `last_ip` WHERE id = 0"
        cursor1.execute(q1)
        for ip in cursor1:
            last_ip = ip[0]
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        cursor1.close()
        cnx1.close()
        
    print('last ip = {}'.format(last_ip))
    host = last_ip
    query = whois(host)
    
    for c in ignore:
        res = query.find(c)
        res_list.append(res)
    
    #print(all(r == -1 for r in res_list))
    try:
        if int(query) == 1:
            approved = True
        else:
            approved = False
    except:
        print(e)
        approved = False
        print('sleeping for 5m')
        time.sleep(500)
        
    for i in range(1, 257):
        # do scan as thread
        if approved:
            print('approved')
            # cpu / mem / sleep sec
            server_control('heavy')
            thread = new_scan(host)
            thread.start()
        # increase ip
        host = ip_increase(host, 'prod')
        
    # update db with increased host
    try:
        cnx2 = mysql.connector.connect(user='root', password='xxxxxx', host='127.0.0.1', database='scan')
        cursor2 = cnx2.cursor()
        q2 = "UPDATE last_ip SET ip=\'"+ host + "\' WHERE id=0"
        cursor2.execute(q2)
        cnx2.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        cursor2.close()
        cnx2.close()
    return


def scan(host):
    #debug
    print(host, 'scanning')
    #
    global nm
    # scan    
    check = "snmpget -v1 -cpublic {0} .1.3.6.1.2.1.1.5.0 -r 0 -t 2 2> /dev/null | grep STRING | wc -l".format(host)
    result = subprocess.Popen(check, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()[0].decode('ascii')
    #print(output)
    # check result
    if float(output) > 0:
        print(host, 'exploitable')
        try:
            cnx3 = mysql.connector.connect(user='root', password='xxxxxx', host='127.0.0.1', database='scan')
            cursor3 = cnx3.cursor()
            q3 = "INSERT INTO `exploitable` (`id`, `ip`, `date`) VALUES (NULL, \'" + host + "\', CURRENT_TIMESTAMP)"
            cursor3.execute(q3)
            cnx3.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            cursor3.close()
            cnx3.close()
    return


# timers for connection status
start_counter = time.time()
# always assume you are not connected
connected = False
# start with 0 sec delay in case off disconnect
sleep_time = 0
while True:
    end_counter = time.time()
    diff = end_counter - start_counter
    if diff > 60 or connected is False:
        # True or False for connected function result
        print('conn test')
        connected = is_connected('www.google.com')
        start_counter = time.time()
        sleep_time += 10
    else:
        pass
    if connected is True:
        sleep_time = 0
        # scan
        scan_controller()
    else:
        print('not connected')
        time.sleep(sleep_time)
