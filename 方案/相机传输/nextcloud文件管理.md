# 分别存储在两个地方 



## nexcloud docker内部的文件存储地方 
docker exec -it 832b63643d79 bash
cd /var/www/html/data

## ftp文件上传存储地址 
ssh apple@10.147.47.20
cd /home/apple/ftp
ls
dudu  gk  home  jjz  Juliet  lhs  other  qiqi  szw  xiaoxiao
du -sh
49G

## 当前文件夹多大 
du -sh