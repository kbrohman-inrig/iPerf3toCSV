#!/usr/bin/env python3

"""
    Version: 1.1
    Author: Kirth Gersen
    Date created: 6/5/2016
    Date modified: 9/12/2016
    Python Version: 2.7
"""

from __future__ import print_function
import json
import sys
import csv
import os

db = {}

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    global db
    """main program"""

    csv.register_dialect('iperf3log', delimiter=',', quoting=csv.QUOTE_MINIMAL)
    csvwriter = csv.writer(sys.stdout, 'iperf3log')

    if len(sys.argv) == 2:
        if (sys.argv[1] != "-h"):
            sys.exit("unknown option")
        else:
            csvwriter.writerow(["date", "ip", "localport", "remoteport", "duration", "protocol", "num_streams", "cookie", "sent", "sent_mbps", "rcvd", "rcvd_mbps", "totalsent", "totalreceived"])
            sys.exit(0)

    # accummulate volume per ip in a dict
    db = {}
    
    # highly specific json parser
    # assumes top { } pair are in single line

    jsonstr = ""
    i = 0
    m = False
    for line in sys.stdin:
        i += 1
        if line == "{\n":
            jsonstr = "{"
            #print("found open line %d",i)
            m = True
        elif line == "}\n":
            jsonstr += "}"
            #print("found close line %d",i)
            if m:
                process(jsonstr,csvwriter)
            m = False
            jsonstr = ""
        else:
            if m:
                jsonstr += line
            #else:
                #print("bogus at line %d = %s",i,line)

def process(js,csvwriter):
    global db
    #print(js)
    try:
        obj = json.loads(js)
    except:
        eprint("bad json")
        pass
        return False 
    try:
        start = []
        end = []
        duration = []
        transfer = []
        bandwidth = []        
        length = len(obj["intervals"])
        
        # caveat: assumes multiple streams are all from same IP so we take the 1st one
        ip = (obj["start"]["connected"][0]["remote_host"]).encode('ascii', 'ignore')
        local_port = obj["start"]["connected"][0]["local_port"]
        remote_port = obj["start"]["connected"][0]["remote_port"]
        
        for i in range(length):
            start.append(obj["intervals"][i]["streams"][0]["start"])
            end.append(obj["intervals"][i]["streams"][0]["end"])
            duration.append(obj["intervals"][i]["streams"][0]["seconds"])
            transfer.append(obj["intervals"][i]["streams"][0]["bytes"])
            bandwidth.append(obj["intervals"][i]["streams"][0]["bits_per_second"])
            
        

        csvwriter.writerow(["Start","End","Duration","Time Unit","Transfer","Transfer Unit","Bandwidth","Bitrate Unit"])
        for i in range(length):
            if transfer[i] > 1000000000:
                transfer[i] /= 1000000000
                transferNot = "GBytes"
            elif transfer[i] > 1000000:
                transfer[i] /= 1000000
                transferNot = "MBytes"
            elif transfer[i] > 1000:
                transfer[i] /= 1000
                transferNot = "KBytes"
            else:
                transferNot = "Bytes"
                
            if bandwidth[i] > 1000000000:
                bandwidth[i] /= 1000000000
                bandwidthNot = "Gbits/sec"
            elif bandwidth[i] > 1000000:
                bandwidth[i] /= 1000000
                bandwidthNot = "Mbits/sec"
            elif bandwidth[i] > 1000:
                bandwidth[i] /= 1000
                bandwidthNot = "Kbits/sec"
            else:
                bandwidthNot = "Bits/sec"
                
            csvwriter.writerow([start[i],end[i],duration[i],"Seconds",transfer[i],transferNot,bandwidth[i],bandwidthNot])
        
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        eprint(exc_type, fname, exc_tb.tb_lineno)
        eprint("error or bogus test:", sys.exc_info()[0])
        pass
    return False

def dumpdb(database):
    """ dump db to text """
    for i in database:
        (s, r) = database[i]
        print("%s, %d , %d " % (i, s, r))

if __name__ == '__main__':
    main()