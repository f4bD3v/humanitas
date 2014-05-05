#start master
spark-0.9.1/sbin/start-master.sh
#start slaves --> configure slaves in: conf/slaves
spark-0.9.1/sbin/start-slaves.sh
#start shark
shark-0.9.1-bin-hadoop1/bin/shark
#start worker and connect to master
spark-0.9.1/bin/spark-class org.apache.spark.deploy.work.Worker spark://100.88.212.102:7077 -p 7078
