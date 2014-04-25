wget http://mirror.switch.ch/mirror/apache/dist/cassandra/2.0.7/apache-cassandra-2.0.7-src.tar.gz

tar -xvf apache-cassandra-2.0.7-src.tar.gz

cd apache-cassandra-2.0.7-src/

ant

sudo mkdir -p /var/log/cassandra  
sudo chown -R `whoami` /var/log/cassandra  
sudo mkdir -p /var/lib/cassandra  
sudo chown -R `whoami` /var/lib/cassandra

