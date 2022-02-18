# iperf3tocsv

 - set iperf3 server to ouput in json (-J)
 - select server or client output
 - output to csv file
 
usage:
  For Server
    iperf3 -s -J | python -u iperf3tocsv.py -s
  For Client
    iperf3 -s -J | python -u iperf3tocsv.py -c


