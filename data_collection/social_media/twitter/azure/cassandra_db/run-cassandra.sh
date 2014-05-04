#to run cassandra in home dir
apache-cassandra-2.0.7-src/bin/cassandra # -f for foreground

# To stop the Cassandra process, find the Cassandra Java process ID (PID), and then kill the process using its PID number
ps auwx | grep cassandra
sudo kill <pid>

# Starting Cassandra as a Service (not installed so far)
sudo service cassandra start

# Stopping Cassandra as a Service
sudo service cassandra stop
