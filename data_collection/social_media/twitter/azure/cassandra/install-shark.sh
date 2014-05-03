wget https://s3.amazonaws.com/spark-related-packages/shark-0.9.1-bin-hadoop1.tgz
tar zxvf shark-0.9.1-bin-hadoop1.tgz
wget http://download1uk.softpedia.com/dl/fa075de8508970c21fa12c0fbfcf7bec/53642c48/100235649/software/database/hive-0.11.0-bin.tar.gz
tar xzf hive-0.11.0-bin.tar.gz
wget http://www.scala-lang.org/files/archive/scala-2.10.3.tgz
tar zxvf scala-2.10.3.tgz

echo "
export SPARK_MEM=1g
export SHARK_MASTER_MEM=1g
export SCALA_HOME=\"~/scala-2.10.3\"
export HIVE_HOME=\"~/hive-0.11.0-bin\"
export SPARK_HOME=\"~/shark-0.9.1-bin-hadoop1\"
export MASTER=\"spark://humanitas1:7077\"
" >> .bashrc

git clone https://github.com/tuplejump/cash.git
sudo apt-get install maven2
cd cash/cassandra-handler
mvn package
cp target/hive-cassandra-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-thrift-1.2.9.jar ../../hive-0.11.0-bin/lib/
cp target/dependency/cassandra-all-1.2.9.jar ../../hive-0.11.0-bin/lib/


