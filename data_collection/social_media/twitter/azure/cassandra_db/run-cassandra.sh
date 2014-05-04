#to run cassandra in home dir
apache-cassandra-2.0.7-src/bin/cassandra # -f for foreground

# To stop the Cassandra process, find the Cassandra Java process ID (PID), and then kill the process using its PID number
ps auwx | grep cassandra
sudo kill <pid>

# Starting Cassandra as a Service (not installed so far)
sudo service cassandra start

# Stopping Cassandra as a Service
sudo service cassandra stop

#####
#Token Generator Interactive Mode
#--------------------------------
#
# How many datacenters will participate in this Cassandra cluster? 1
# How many nodes are in datacenter #1? 8
#
#DC #1:
#  Node #1:                                        0
#  Node #2:   21267647932558653966460912964485513216
#  Node #3:   42535295865117307932921825928971026432
#  Node #4:   63802943797675961899382738893456539648
#  Node #5:   85070591730234615865843651857942052864
#  Node #6:  106338239662793269832304564822427566080
#  Node #7:  127605887595351923798765477786913079296
#  Node #8:  148873535527910577765226390751398592512
