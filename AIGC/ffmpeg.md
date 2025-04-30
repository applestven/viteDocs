### ffmpeg 的命令  



1. ffmpeg 提取音频 

<!-- 注意这两条命令可能音频文件可能为mp3 aac等不同格式 ，实际应用可能需要统一转mp3 -->
``` bash
ffmpeg -i input_video.mp4 -vn -acodec copy output_audio.mp3


cuda ： 

ffmpeg -i 2小时.mp4 -vn -acodec copy -c:v h264_cuvid output.mp3 

```

2. ffmpeg 合并音视
``` bash

ffmpeg -i input_video.mp4 -i input_audio.mp3 -c:v copy -c:a aac -strict experimental output_video.mp4

```