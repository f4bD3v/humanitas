wget https://s3.amazonaws.com/spark-related-packages/shark-0.9.1-bin-hadoop1.tgz
tar zxvf shark-0.9.1-bin-hadoop1.tgz
wget http://archive.apache.org/dist/hive/hive-0.11.0/hive-0.11.0-bin.tar.gz
tar xzf hive-0.11.0-bin.tar.gz
wget http://www.scala-lang.org/files/archive/scala-2.10.3.tgz
tar zxvf scala-2.10.3.tgz

echo "
export SPARK_MEM=1g
export SHARK_MASTER_MEM=1g
export SCALA_HOME=\"~/scala-2.10.3\"
export HIVE_HOME=\"~/hive-0.11.0-bin\"
export SPARK_HOME=\"~/shark-0.9.1-bin-hadoop1\"
export MASTER=\"spark://100.88.212.102:7077\"
export SPARK_MASTER_IP=100.88.212.102
" >> .bashrc

git clone https://github.com/tuplejump/cash.git
sudo apt-get install maven2
cd cash/cassandra-handler
mvn package
cp target/hive-cassandra-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-thrift-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-all-1.2.9.jar ../../hive-0.11.0-bin/lib/


