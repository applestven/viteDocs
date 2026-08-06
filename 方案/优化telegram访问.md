

## 测试telegram访问
1. 
curl.exe -x http://127.0.0.1:7890 -o NUL -s -w "time:%{time_total}\n" https://api.telegram.org
time:0.843114


2. 测试下载速度（更接近视频）

curl.exe -x http://127.0.0.1:7890 -o NUL -w "%{speed_download}\n" http://speedtest.tele2.net/100MB.zip