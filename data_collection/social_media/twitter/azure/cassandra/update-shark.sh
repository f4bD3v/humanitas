rm hive-0.11.0-bin.tar.gz*
rm -r hive-0.11.0-bin
wget http://archive.apache.org/dist/hive/hive-0.11.0/hive-0.11.0-bin.tar.gz
tar xzf hive-0.11.0-bin.tar.gz

echo "
export MASTER=\"spark://100.88.212.102:7077\"
" >> .bashrc

cd cash/cassandra-handler
cp target/hive-cassandra-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-thrift-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-all-1.2.9.jar ../../hive-0.11.0-bin/lib/


