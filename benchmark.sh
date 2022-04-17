#!/bin/bash

# imgproxy
ab -c10 -n200 -dSq 'localhost:8081/insecure/rs:fit:854:480/el:true/g:ce:0:0/plain/http://origin/1700KB.jpg'   > test-imgproxy.txt
echo -e '\n---\n'                                                                                            >> test-imgproxy.txt
ab -c10 -n200 -dSq 'localhost:8081/insecure/rs:fit:854:480/el:true/g:ce:0:0/plain/http://origin/17000KB.jpg' >> test-imgproxy.txt

sleep 15    # cold down CPU

# thumbor
ab -c10 -n200 -dSq 'localhost:8082/unsafe/854x480/http://origin/1700KB.jpg'   > test-thumbor.txt
echo -e '\n---\n'                                                            >> test-thumbor.txt
ab -c10 -n200 -dSq 'localhost:8082/unsafe/854x480/http://origin/17000KB.jpg' >> test-thumbor.txt

sleep 15

# weserv
ab -c10 -n200 -dSq 'localhost:8083/?url=http://origin/1700KB.jpg&w=854&h=480'   > test-weserv.txt
echo -e '\n---\n'                                                              >> test-weserv.txt
ab -c10 -n200 -dSq 'localhost:8083/?url=http://origin/17000KB.jpg&w=854&h=480' >> test-weserv.txt

sleep 15

# ownproxy
ab -c10 -n200 -dSq 'localhost:8086/?url=http://origin/1700KB.jpg&img_w=854&img_h=480'   > test-ownproxy.txt
echo -e '\n---\n'                                                                      >> test-ownproxy.txt
ab -c10 -n200 -dSq 'localhost:8086/?url=http://origin/17000KB.jpg&img_w=854&img_h=480' >> test-ownproxy.txt

