import subprocess
import time
import csv


first_run = True    
ip_list = 'nameservers.csv'
ip = []
array_position = 0

    
with open(ip_list) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        url = row['ip']
        ip.append(url)
        
array_count = len(ip)

        
def ping(server, count=5, wait_sec=5):
    cmd = "ping -c {0} -W {1} {2}".format(count, wait_sec, server).split(' ')
    try:
        t1 = time.time()
        output = subprocess.check_output(cmd).decode().strip()
        t2 = time.time()
        tt = round(t2 - t1, 4)
        #print(output)
        lines = output.split("\n")
        loss = lines[-2].split(',')[2].split()[0].replace("%", "")
        timing = lines[-1].split()[3].split('/')
        #return {
        #    'min': timing[0],
        #    'avg': timing[1],
        #    'max': timing[2],
        #    'mdev': timing[3],
        #    'total': tt,
        #    'loss': loss,
        #}
        return [float(timing[0]), float(timing[1]), float(timing[2]), float(timing[3]), float(tt), float(loss)]
    except Exception as e:
        print(e, server)
        return False
        
for i in range(array_count):
    latest_result = ping(ip[array_position])
    
    if latest_result != False:
        print(latest_result, ip[array_position])
        if first_run:
            first_run = False
            avg_result = latest_result
        
        l = [latest_result, avg_result]
        try:
            avg_result = [(x+y)/2 for x,y in zip(*l)]
        except:
            pass
        
        print(avg_result, 'avg',  time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        
    array_position += 1


#    
#else:
#    avg = np.array([[1, 2, 3], [5, 6, 7]])