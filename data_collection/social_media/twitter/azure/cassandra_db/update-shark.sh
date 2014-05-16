rm hive-0.11.0-bin.tar.gz*
rm -r hive-0.11.0-bin
wget http://archive.apache.org/dist/hive/hive-0.11.0/hive-0.11.0-bin.tar.gz
tar xzf hive-0.11.0-bin.tar.gz

echo '
export SPARK_MEM=1g
export SHARK_MASTER_MEM=1g
export SCALA_HOME=~/scala-2.10.3
export HIVE_HOME=~/hive-0.9.0-bin
export SPARK_HOME=/home/humaniac/spark-0.9.1
export SPARK_MASTER_IP=100.88.224.12
export MASTER=spark://100.88.224.12:7077
' >> .bashrc

export SPARK_MEM=1g
export SHARK_MASTER_MEM=1g
export SCALA_HOME=~/scala-2.10.3
export HIVE_HOME=~/hive-0.9.0-bin
export SPARK_HOME=/home/humaniac/spark-0.9.1
export SPARK_MASTER_IP=100.88.224.12
export MASTER=spark://100.88.224.12:7077

cd cash/cassandra-handler
cp target/hive-cassandra-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-thrift-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-all-1.2.9.jar ../../hive-0.11.0-bin/lib/


