

    ## b站下载过程

  视频： https://www.bilibili.com/video/BV1vy411e7eM/?spm_id_from=333.1007.tianma.7-2-21.click&vd_source=0c88b82560db687e3ba0427782c655e3
  通过m4a过滤 ： 

  视频下载：  
  curl.exe -o video.m4s "https://xy120x240x78x229xy.mcdn.bilivideo.cn:8082/v1/resource/1625929629-1-100026.m4s?agrr=0&build=0&buvid=62FB0CD5-303F-2903-A771-90ED9BF1D62490741infoc&bvc=vod&bw=81698&deadline=1722152324&e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M%3D&f=u_0_0&gen=playurlv2&logo=A0020000&mcdnid=50006294&mid=238107654&nbs=1&nettype=0&og=cos&oi=3658655452&orderid=0%2C3&os=mcdn&platform=pc&sign=322836&traceid=trLbFEweJExkHc_0_e_N&uipk=5&uparams=e%2Cuipk%2Cnbs%2Cdeadline%2Cgen%2Cos%2Coi%2Ctrid%2Cmid%2Cplatform%2Cog&upsig=ec7c7a4bc46f16e718a2429d6328de00" -H "Accept: */*" -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" -H "Connection: keep-alive" -H "Origin: https://www.bilibili.com" -H "Range: bytes=0-43381890" -H "Referer: https://www.bilibili.com/video/BV1vy411e7eM/?spm_id_from=333.1007.tianma.7-2-21.click&vd_source=0c88b82560db687e3ba0427782c655e3" -H "Sec-Fetch-Dest: empty" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: cross-site" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  ffmpeg -i video.m4s -c copy output.mp4

  音频下载
  curl.exe -o audio.m4s "https://xy111x113x212x73xy.mcdn.bilivideo.cn:4483/upgcxcode/29/96/1625929629/1625929629-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1722152324&gen=playurlv2&os=mcdn&oi=3658655452&trid=0000cf3f7ed17236400380dfbdce91282881u&mid=238107654&platform=pc&og=cos&upsig=8d55d2a197e310a9cfb0f94414f84306&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&mcdnid=50006294&bvc=vod&nettype=0&orderid=0,3&buvid=62FB0CD5-303F-2903-A771-90ED9BF1D62490741infoc&build=0&f=u_0_0&agrr=0&bw=20427&logo=A0020000" -H "Accept: */*" -H "Accept-language: zh-CN,zh;q=0.9,en;q=0.8" -H "Range: bytes=0-10847185" -H "origin: https://www.bilibili.com" -H "Referer: https://www.bilibili.com/video/BV1vy411e7eM/?spm_id_from=333.1007.tianma.7-2-21.click&vd_source=0c88b82560db687e3ba0427782c655e3" -H "Sec-Fetch-Dest: empty" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: cross-site" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  ffmpeg -i audio.m4s -c copy audio.mp4  

  合并
  ffmpeg -i output.mp4 -i audio.mp4 -c copy fianl.mp4




  curl.exe -o audio.m4s "https://upos-hz-mirrorakam.akamaized.net/upgcxcode/31/87/1627668731/1627668731-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1722158877&gen=playurlv2&os=akam&oi=312631654&trid=9ecaa4d6e4214832b4d8a403d9b16736u&mid=238107654&platform=pc&og=hw&upsig=45c31a9bfc97c35395b66c8576b01324&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&hdnts=exp=1722158877~hmac=4dce8069219d74f5cad732b316d7999236948f5118cdb182886de7e8ae5210dc&bvc=vod&nettype=0&orderid=0,1&buvid=62FB0CD5-303F-2903-A771-90ED9BF1D62490741infoc&build=0&f=u_0_0&agrr=1&bw=10545&logo=80000000" -H "Accept: */*" -H "Accept-language: zh-CN,zh;q=0.9,en;q=0.8" -H "Range: bytes=0-17262852" -H "origin: https://www.bilibili.com" -H "Referer: https://www.bilibili.com/video/BV1vy411e7eM/?spm_id_from=333.1007.tianma.7-2-21.click&vd_source=0c88b82560db687e3ba0427782c655e3" -H "Sec-Fetch-Dest: empty" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: cross-site" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  ffmpeg -i audio.m4s -c copy audio.mp4  