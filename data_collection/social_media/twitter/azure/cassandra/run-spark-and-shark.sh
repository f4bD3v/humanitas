#start master
bash sbin/start-master.sh
#start slaves --> configure slaves in: conf/slaves
bash sbin/start-slaves.sh
#start shark
bin/shark
