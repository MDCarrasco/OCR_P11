echo -e "\nStart LOCUST MASTER\n"
locust -f locustfile.py --master -u 6 --expect-workers=4 --host="http://127.0.0.1:5000"&
PID_MASTER=$!
echo "LOCUST MASTER PID = $PID_MASTER"
sleep 5

# start SLAVE (clients)
echo -e "\nStart LOCUST SLAVES\n"
PID_SLAVES=( )
for ((i = 1; i <= 4; i++));do
  locust -f locustfile.py --worker&
  PID_SLAVES+=( $! )
done
echo "LOCAST SLAVE PIDs = ${PID_SLAVES[@]}"