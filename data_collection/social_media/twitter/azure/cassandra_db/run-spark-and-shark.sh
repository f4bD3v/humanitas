#start master
spark-0.9.1/sbin/start-master.sh
#start slaves --> configure slaves in: conf/slaves
spark-0.9.1/sbin/start-slaves.sh
#start shark
shark-0.9.1-bin-hadoop1/bin/shark
#start worker and connect to master
sh distribute.sh -e "nohup /home/humaniac/spark-0.9.1/bin/spark-class org.apache.spark.deploy.worker.Worker spark://100.88.224.12:7077 -p 7078 -i 100.88.216.61 &> spark.out" -f 1

# run tweet processor
sh distribute.sh -e "cd twitter; nohup python tweet_processor.py /mnt/tweet_tmp_store/ False False >> nohup.out" -f 3

#conf
export SPARK_MEM=1g
export SHARK_MASTER_MEM=1g
export SCALA_HOME="~/scala-2.10.3"
export HIVE_HOME="~/hive-0.11.0-bin"
export SPARK_HOME="/home/humaniac/spark-0.9.1"
export SPARK_MASTER_IP=100.88.224.12
export MASTER="spark://100.88.224.12:7077"


