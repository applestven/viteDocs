## 一些console的用法  特效 


### 美化打印实现方法
参考：https://juejin.cn/post/7371716384847364147 
```js
js复制代码// 美化打印实现方法
const prettyLog = () => {
    const isProduction = import.meta.env.MODE === 'production';

    const isEmpty = (value: any) => {
        return value == null || value === undefined || value === '';
    };
    const prettyPrint = (title: string, text: string, color: string) => {
        if (isProduction) return;
        console.log(
            `%c ${title} %c ${text} %c`,
            `background:${color};border:1px solid ${color}; padding: 1px; border-radius: 2px 0 0 2px; color: #fff;`,
            `border:1px solid ${color}; padding: 1px; border-radius: 0 2px 2px 0; color: ${color};`,
            'background:transparent'
        );
    };
    const info = (textOrTitle: string, content = '') => {
        const title = isEmpty(content) ? 'Info' : textOrTitle;
        const text = isEmpty(content) ? textOrTitle : content;
        prettyPrint(title, text, '#909399');
    };
    const error = (textOrTitle: string, content = '') => {
        const title = isEmpty(content) ? 'Error' : textOrTitle;
        const text = isEmpty(content) ? textOrTitle : content;
        prettyPrint(title, text, '#F56C6C');
    };
    const warning = (textOrTitle: string, content = '') => {
        const title = isEmpty(content) ? 'Warning' : textOrTitle;
        const text = isEmpty(content) ? textOrTitle : content;
        prettyPrint(title, text, '#E6A23C');
    };
    const success = (textOrTitle: string, content = '') => {
        const title = isEmpty(content) ? 'Success ' : textOrTitle;
        const text = isEmpty(content) ? textOrTitle : content;
        prettyPrint(title, text, '#67C23A');
    };
    const table = () => {
        const data = [
            { id: 1, name: 'Alice', age: 25 },
            { id: 2, name: 'Bob', age: 30 },
            { id: 3, name: 'Charlie', age: 35 }
        ];
        console.log(
            '%c id%c name%c age',
            'color: white; background-color: black; padding: 2px 10px;',
            'color: white; background-color: black; padding: 2px 10px;',
            'color: white; background-color: black; padding: 2px 10px;'
        );

        data.forEach((row: any) => {
            console.log(
                `%c ${row.id} %c ${row.name} %c ${row.age} `,
                'color: black; background-color: lightgray; padding: 2px 10px;',
                'color: black; background-color: lightgray; padding: 2px 10px;',
                'color: black; background-color: lightgray; padding: 2px 10px;'
            );
        });
    };
    const picture = (url: string, scale = 1) => {
        if (isProduction) return;
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            const c = document.createElement('canvas');
            const ctx = c.getContext('2d');
            if (ctx) {
                c.width = img.width;
                c.height = img.height;
                ctx.fillStyle = 'red';
                ctx.fillRect(0, 0, c.width, c.height);
                ctx.drawImage(img, 0, 0);
                const dataUri = c.toDataURL('image/png');

                console.log(
                    `%c sup?`,
                    `font-size: 1px;
                    padding: ${Math.floor((img.height * scale) / 2)}px ${Math.floor((img.width * scale) / 2)}px;
                    background-image: url(${dataUri});
                    background-repeat: no-repeat;
                    background-size: ${img.width * scale}px ${img.height * scale}px;
                    color: transparent;
                    `
                );
            }
        };
        img.src = url;
    };

    // retu;
    return {
        info,
        error,
        warning,
        success,
        picture,
        table
    };
};
// 创建打印对象
const log = prettyLog();

```

### 打印魔方
```js
 
console.info(
  '%c ',
  `line-height:200px;padding-block:100px;padding-left:200px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cstyle%3E .wrapper %7B font-family: sans-serif; perspective: 500px; text-align: center; position: relative; width: 100%25; height: 100%25; %7D .cube %7B position: absolute; top: 20%25; left: 30%25; transform-style: preserve-3d; transform: rotateY(40deg) rotateX(-40deg); animation: wiggle_wiggle_wiggle_wiggle_wiggle_yeah 3s ease-in-out infinite alternate; %7D .side %7B width: 8rem; height: 8rem; background: rgba(0, 0, 0, 0.8); display: inline-block; position: absolute; line-height: 8rem; color: %23fff; text-align: center; box-sizing: border-box; border: 3px solid %23f00; font-size: 4rem; %7D .front %7B transform: translateZ(4rem); z-index: 1; %7D .back %7B transform: rotateY(180deg) translateZ(4rem); %7D .left %7B transform: rotateY(-90deg) translateZ(4rem); z-index: 1; %7D .right %7B transform: rotateY(90deg) translateZ(4rem); %7D .top %7B transform: rotateX(90deg) translateZ(4rem); %7D .bottom %7B transform: rotateX(-90deg) translateZ(4rem); %7D @keyframes wiggle_wiggle_wiggle_wiggle_wiggle_yeah %7B 0%25 %7B transform: rotateY(15deg) rotateX(-15deg); %7D 100%25 %7B transform: rotateY(60deg) rotateX(-45deg); %7D %7D %3C/style%3E%3CforeignObject width='100%25' height='100%25'%3E%3Cdiv xmlns='http://www.w3.org/1999/xhtml' class='wrapper'%3E%3Cdiv class='cube'%3E%3Cdiv class='side front'%3E1%3C/div%3E%3Cdiv class='side back'%3E6%3C/div%3E%3Cdiv class='side left'%3E3%3C/div%3E%3Cdiv class='side right'%3E4%3C/div%3E%3Cdiv class='side top'%3E2%3C/div%3E%3Cdiv class='side bottom'%3E5%3C/div%3E%3C/div%3E%3C/div%3E%3C/foreignObject%3E%3C/svg%3E")`
);

```
### 打印欢迎条幅
```js
console.info(
  '%c ',
  `padding-left:750px;padding-top:200px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 750 200'%3E%3Cstyle%3E text %7B font-family: sans-serif; font-weight: 100; fill: %23d8eaff; %7D %23stop1 %7B animation: recolor 40s linear infinite alternate %7D %23stop2 %7B animation: recolor 40s -32s linear infinite alternate %7D @keyframes recolor %7B 0%25 %7B stop-color: %23388bee; %7D 20%25 %7B stop-color: %2324c6dc; %7D 40%25 %7B stop-color: %23af74fd; %7D 60%25 %7B stop-color: %23c020d9; %7D 80%25 %7B stop-color: %23514a9d; %7D 100%25 %7B stop-color: %23053ece; %7D %7D %3C/style%3E%3Cdefs%3E%3ClinearGradient id='grad'%3E%3Cstop id='stop1' offset='0%25' stop-color='%23388bee'%3E%3C/stop%3E%3Cstop id='stop2' offset='100%25' stop-color='%23514a9d'%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='750' height='500' fill='url(%23grad)'%3E%3C/rect%3E%3Ctext text-anchor='end' font-size='50' x='725' y='125'%3E 欢迎来到 %3C/text%3E%3Ctext text-anchor='end' font-size='50' x='725' y='175'%3E code秘密花园 %3C/text%3E%3C/svg%3E")`
);
```


### 动效显示 
``` js
console.info(
  '%c ',
  `padding-left:840.42px;padding-top:80.75px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg class='container' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 840.42 80.75'%3E%3Cstyle%3E .container %7B background: linear-gradient(to left, %23112, %23223); %7D @keyframes draw %7B 40%25, 80%25 %7B opacity: 1; stroke-dashoffset: 0; stroke: %23ec0062; %7D 95%25, 100%25 %7B stroke-dashoffset: 0; opacity: 0; %7D %7D .line %7B fill: none; stroke: %23334; stroke-width: 4.75; stroke-linecap: round; stroke-miterlimit: 10; stroke-dasharray: 200; animation: draw 7s infinite ease-in-out; %7D .line-reverse %7B stroke-dashoffset: -200; %7D .line-forwards %7B stroke-dashoffset: 200; %7D %3C/style%3E%3C!-- A --%3E%3Cpolyline class='line line-forwards' points='2.38,77.83 33.4,6.55 64.42,77.83'%3E%3C/polyline%3E%3Cline class='line line-forwards' x1='17.96' y1='42.19' x2='38.47' y2='42.19'%3E%3C/line%3E%3C!-- M --%3E%3Cpolyline class='line line-forwards' points='81.87,78.01 81.87,6.37 113.21,42.55 143.91,6.37'%3E%3C/polyline%3E%3Cpath class='line line-forwards' d='M113.21,42.55'%3E%3C/path%3E%3Cpath class='line line-forwards' d='M113.21,42.55'%3E%3C/path%3E%3Cline class='line line-forwards' x1='143.91' y1='16.66' x2='143.91' y2='78.01'%3E%3C/line%3E%3C!-- E --%3E%3Cpolyline class='line line-forwards' points='223,6.73 160.96,6.73 160.96,78.01 222.95,78.01'%3E%3C/polyline%3E%3Cline class='line line-forwards' x1='171.25' y1='42.37' x2='213.59' y2='42.37'%3E%3C/line%3E%3C!-- L --%3E%3Cline class='line line-forwards' x1='240.14' y1='6.73' x2='240.14' y2='78.37'%3E%3C/line%3E%3Cpath class='line line-forwards' d='M240.14,6.73'%3E%3C/path%3E%3Cline class='line line-forwards' x1='250.43' y1='78.37' x2='302.18' y2='78.37'%3E%3C/line%3E%3C!-- I --%3E%3Cline class='line line-forwards' x1='319.21' y1='6.73' x2='319.21' y2='78.37'%3E%3C/line%3E%3C!-- Reverse A --%3E%3Cpolyline class='line line-reverse' points='398.4,77.83 367.38,6.55 336.36,77.83'%3E%3C/polyline%3E%3Cline class='line line-reverse' x1='382.81' y1='42.19' x2='362.31' y2='42.19'%3E%3C/line%3E%3C!-- C --%3E%3Cpath class='line line-reverse' d='M504.32,78.37h-9.41H478.1c-19.78,0-35.82-16.04-35.82-35.82c0-19.78,16.04-35.82,35.82-35.82h26.22'%3E%3C/path%3E%3C!-- A --%3E%3Cpolyline class='line line-forwards' points='521.62,77.83 552.64,6.55 583.66,77.83'%3E%3C/polyline%3E%3Cline class='line line-forwards' x1='537.21' y1='42.19' x2='557.71' y2='42.19'%3E%3C/line%3E%3C!-- R --%3E%3Cpath class='line line-reverse' d='M610.94,42.19h19.4c9.89,0,17.91-8.02,17.91-17.91s-8.02-17.91-17.91-17.91h-29.65v71.64'%3E%3C/path%3E%3Cline class='line line-forwards' x1='630.34' y1='42.19' x2='662.73' y2='78.01'%3E%3C/line%3E%3C!-- L --%3E%3Cline class='line line-forwards' x1='679.89' y1='6.73' x2='679.89' y2='78.37'%3E%3C/line%3E%3Cline class='line line-forwards' x1='690.18' y1='78.37' x2='741.93' y2='78.37'%3E%3C/line%3E%3C!-- I --%3E%3Cline class='line line-forwards' x1='758.96' y1='6.73' x2='758.96' y2='78.37'%3E%3C/line%3E%3C!-- E --%3E%3Cpolyline class='line line-forwards' points='838.04,6.73 776,6.73 776,78.01 837.99,78.01'%3E%3C/polyline%3E%3Cline class='line line-forwards' x1='786.29' y1='42.37' x2='828.63' y2='42.37'%3E%3C/line%3E%3C/svg%3E")`
);
```

### 下雪条幅

``` js
console.info(
  '%c ',
  `padding-left:800px;line-height:250px;padding-block:125px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg class='svg-snowscene' viewBox='0 0 800 250' xmlns='http://www.w3.org/2000/svg'%3E%3Cstyle%3E@keyframes snowing%7B0%25%7Bfill-opacity:1%7D100%25%7Bfill-opacity:0;transform:translateY(250px)%7D%7D.svg-snowscene%7Bbackground-color:%239cf;background-image:linear-gradient(%236af,%23bdf)%7Dtext%7Bfill:%23fff;font-family:cursive%7Dcircle%7Bfill:%23fff;animation-name:snowing;animation-iteration-count:infinite;animation-timing-function:ease-out%7Dcircle:nth-child(1n)%7Banimation-delay:-.2s;animation-duration:7s%7Dcircle:nth-child(2n)%7Banimation-delay:-.4s;animation-duration:6s%7Dcircle:nth-child(3n)%7Banimation-delay:-.6s;animation-duration:8s%7Dcircle:nth-child(4n)%7Banimation-delay:-.8s;animation-duration:9s%7Dcircle:nth-child(5n)%7Banimation-delay:-1s;animation-duration:8s%7Dcircle:nth-child(6n)%7Banimation-delay:-1.2s;animation-duration:10s%7Dcircle:nth-child(7n)%7Banimation-delay:-1.4s;animation-duration:10s%7Dcircle:nth-child(8n)%7Banimation-delay:-1.6s;animation-duration:10s%7Dcircle:nth-child(9n)%7Banimation-delay:-1.8s;animation-duration:8s%7Dcircle:nth-child(10n)%7Banimation-delay:-2s;animation-duration:9s%7Dcircle:nth-child(11n)%7Banimation-delay:-2.2s;animation-duration:7s%7Dcircle:nth-child(12n)%7Banimation-delay:-2.4s;animation-duration:8s%7Dcircle:nth-child(13n)%7Banimation-delay:-2.6s;animation-duration:9s%7Dcircle:nth-child(14n)%7Banimation-delay:-2.8s;animation-duration:10s%7Dcircle:nth-child(15n)%7Banimation-delay:-3s;animation-duration:10s%7Dcircle:nth-child(16n)%7Banimation-delay:-3.2s;animation-duration:6s%7Dcircle:nth-child(17n)%7Banimation-delay:-3.4s;animation-duration:7s%7Dcircle:nth-child(18n)%7Banimation-delay:-3.6s;animation-duration:6s%7Dcircle:nth-child(19n)%7Banimation-delay:-3.8s;animation-duration:8s%7Dcircle:nth-child(20n)%7Banimation-delay:-4s;animation-duration:6s%7Dcircle:nth-child(21n)%7Banimation-delay:-4.2s;animation-duration:9s%7Dcircle:nth-child(22n)%7Banimation-delay:-4.4s;animation-duration:9s%7Dcircle:nth-child(23n)%7Banimation-delay:-4.6s;animation-duration:8s%7Dcircle:nth-child(24n)%7Banimation-delay:-4.8s;animation-duration:7s%7Dcircle:nth-child(25n)%7Banimation-delay:-5s;animation-duration:8s%7Dcircle:nth-child(26n)%7Banimation-delay:-5.2s;animation-duration:7s%7Dcircle:nth-child(27n)%7Banimation-delay:-5.4s;animation-duration:6s%7Dcircle:nth-child(28n)%7Banimation-delay:-5.6s;animation-duration:8s%7Dcircle:nth-child(29n)%7Banimation-delay:-5.8s;animation-duration:10s%7Dcircle:nth-child(30n)%7Banimation-delay:-6s;animation-duration:10s%7Dcircle:nth-child(31n)%7Banimation-delay:-6.2s;animation-duration:9s%7Dcircle:nth-child(32n)%7Banimation-delay:-6.4s;animation-duration:10s%7Dcircle:nth-child(33n)%7Banimation-delay:-6.6s;animation-duration:10s%7Dcircle:nth-child(34n)%7Banimation-delay:-6.8s;animation-duration:6s%7Dcircle:nth-child(35n)%7Banimation-delay:-7s;animation-duration:6s%7Dcircle:nth-child(36n)%7Banimation-delay:-7.2s;animation-duration:10s%7Dcircle:nth-child(37n)%7Banimation-delay:-7.4s;animation-duration:7s%7Dcircle:nth-child(38n)%7Banimation-delay:-7.6s;animation-duration:9s%7Dcircle:nth-child(39n)%7Banimation-delay:-7.8s;animation-duration:9s%7Dcircle:nth-child(40n)%7Banimation-delay:-8s;animation-duration:8s%7Dcircle:nth-child(41n)%7Banimation-delay:-8.2s;animation-duration:6s%7Dcircle:nth-child(42n)%7Banimation-delay:-8.4s;animation-duration:10s%7Dcircle:nth-child(43n)%7Banimation-delay:-8.6s;animation-duration:7s%7Dcircle:nth-child(44n)%7Banimation-delay:-8.8s;animation-duration:9s%7Dcircle:nth-child(45n)%7Banimation-delay:-9s;animation-duration:10s%7Dcircle:nth-child(46n)%7Banimation-delay:-9.2s;animation-duration:6s%7Dcircle:nth-child(47n)%7Banimation-delay:-9.4s;animation-duration:7s%7Dcircle:nth-child(48n)%7Banimation-delay:-9.6s;animation-duration:9s%7Dcircle:nth-child(49n)%7Banimation-delay:-9.8s;animation-duration:7s%7Dcircle:nth-child(50n)%7Banimation-delay:-10s;animation-duration:7s%7D%3C/style%3E%3Ctext font-size='80' text-anchor='middle' x='400' y='140'%3E你好，code秘密花园%3C/text%3E%3Ccircle cx='25.995103990111105%25' cy='-77.81008995571561' r='2.749159658185124'%3E%3C/circle%3E%3Ccircle cx='89.62561554717637%25' cy='-46.78148229694086' r='2.393631489179748'%3E%3C/circle%3E%3Ccircle cx='5.135745159612563%25' cy='-38.81872689180804' r='2.841244102307123'%3E%3C/circle%3E%3Ccircle cx='40.819201884845775%25' cy='-34.58293639476059' r='1.4458270158519961'%3E%3C/circle%3E%3Ccircle cx='26.212971825618283%25' cy='-12.498573576229386' r='2.9709903306827465'%3E%3C/circle%3E%3Ccircle cx='76.68859580291824%25' cy='-62.21926850640058' r='1.1347363710323926'%3E%3C/circle%3E%3Ccircle cx='55.72266234658971%25' cy='-74.73326327616485' r='1.113806305196924'%3E%3C/circle%3E%3Ccircle cx='39.0317830273073%25' cy='-58.703705511039225' r='2.3100083626369976'%3E%3C/circle%3E%3Ccircle cx='89.7176436793289%25' cy='-10.281820667480222' r='2.0469063477660447'%3E%3C/circle%3E%3Ccircle cx='83.96827591096722%25' cy='-81.2478772998329' r='1.790201302779563'%3E%3C/circle%3E%3Ccircle cx='7.260053772750218%25' cy='-96.49215734429552' r='2.3545864333810256'%3E%3C/circle%3E%3Ccircle cx='26.883202292253728%25' cy='-37.108549732420656' r='1.9978674352572674'%3E%3C/circle%3E%3Ccircle cx='58.50316757093038%25' cy='-44.19563368875621' r='2.1333080325968745'%3E%3C/circle%3E%3Ccircle cx='49.153134743170924%25' cy='-96.61192814231214' r='1.0338012128288736'%3E%3C/circle%3E%3Ccircle cx='80.66335728120768%25' cy='-92.60017007342769' r='1.352444421725643'%3E%3C/circle%3E%3Ccircle cx='49.21716180537502%25' cy='-15.736517819787414' r='2.56514014572579'%3E%3C/circle%3E%3Ccircle cx='18.159072047777208%25' cy='-41.662630986758565' r='1.827289622857739'%3E%3C/circle%3E%3Ccircle cx='28.591656766804356%25' cy='-75.40392903873996' r='2.540805639719657'%3E%3C/circle%3E%3Ccircle cx='75.7560667785456%25' cy='-42.093604757726446' r='1.411351114203426'%3E%3C/circle%3E%3Ccircle cx='95.86623136857125%25' cy='-86.17237490881534' r='1.6437772466697007'%3E%3C/circle%3E%3Ccircle cx='66.57358996698223%25' cy='-33.05038635630268' r='1.224578596470813'%3E%3C/circle%3E%3Ccircle cx='37.87486333612133%25' cy='-91.98642442806697' r='1.5164858217037178'%3E%3C/circle%3E%3Ccircle cx='99.9780409949983%25' cy='-85.25670632025145' r='1.093408865757894'%3E%3C/circle%3E%3Ccircle cx='6.258195692333731%25' cy='-82.17612056080935' r='2.5970745236726915'%3E%3C/circle%3E%3Ccircle cx='76.92756548357505%25' cy='-39.05022432020484' r='1.3903120977596086'%3E%3C/circle%3E%3Ccircle cx='35.30776480586916%25' cy='-5.100866152259875' r='2.490933162143621'%3E%3C/circle%3E%3Ccircle cx='21.888577746640067%25' cy='-53.61306945430116' r='1.5911619566776065'%3E%3C/circle%3E%3Ccircle cx='5.408329205067845%25' cy='-25.216367465595514' r='1.7561674911504097'%3E%3C/circle%3E%3Ccircle cx='11.607577654364524%25' cy='-50.29316328357586' r='1.9271574194581076'%3E%3C/circle%3E%3Ccircle cx='80.61508259836967%25' cy='-56.47870637418366' r='2.7379039794681383'%3E%3C/circle%3E%3Ccircle cx='75.29235125946235%25' cy='-24.205675758687455' r='1.7921437262309654'%3E%3C/circle%3E%3Ccircle cx='97.78226376693122%25' cy='-32.21154549976014' r='1.529148319088483'%3E%3C/circle%3E%3Ccircle cx='73.75693711579706%25' cy='-23.004150289082606' r='2.4556699382045046'%3E%3C/circle%3E%3Ccircle cx='41.419838495897%25' cy='-65.31921232448768' r='2.8044281379588676'%3E%3C/circle%3E%3Ccircle cx='40.950298123173106%25' cy='-26.292156289520896' r='2.419680017572999'%3E%3C/circle%3E%3Ccircle cx='47.867691980584716%25' cy='-26.242657523185184' r='1.0923877243334101'%3E%3C/circle%3E%3Ccircle cx='62.81766527782989%25' cy='-89.701930860537' r='1.7949190430635444'%3E%3C/circle%3E%3Ccircle cx='48.69722811509327%25' cy='-10.958255978759077' r='2.861844670749401'%3E%3C/circle%3E%3Ccircle cx='34.57978264890831%25' cy='-1.1612908265357433' r='1.6199043038315515'%3E%3C/circle%3E%3Ccircle cx='37.96738880106298%25' cy='-12.825961059362545' r='2.8559531388340513'%3E%3C/circle%3E%3Ccircle cx='85.46233678220392%25' cy='-88.02351857384527' r='1.0984128042737793'%3E%3C/circle%3E%3Ccircle cx='64.4596084875124%25' cy='-19.803934792180392' r='2.6968494185321026'%3E%3C/circle%3E%3Ccircle cx='56.87846924216383%25' cy='-68.9330339781381' r='2.441322855837859'%3E%3C/circle%3E%3Ccircle cx='87.67115279021654%25' cy='-57.12781963683186' r='1.268498259959995'%3E%3C/circle%3E%3Ccircle cx='87.86909883390128%25' cy='-65.7354110827157' r='1.2941568814088011'%3E%3C/circle%3E%3Ccircle cx='30.16692089861322%25' cy='-34.69868021057453' r='1.082850239075611'%3E%3C/circle%3E%3Ccircle cx='63.21354400809286%25' cy='-48.79787125206968' r='2.6866316912738153'%3E%3C/circle%3E%3Ccircle cx='73.1130164281696%25' cy='-14.128826564618988' r='2.396208563109712'%3E%3C/circle%3E%3Ccircle cx='49.592435166991244%25' cy='-28.576612560341417' r='2.265863084175359'%3E%3C/circle%3E%3Ccircle cx='12.364052530549507%25' cy='-22.31568226585923' r='2.8058073048920886'%3E%3C/circle%3E%3Cscript%3Efunction r(min, max) %7B return Math.random() * (max - min) + min; %7D const s = document.querySelectorAll('circle'); function l() %7B for (let i = 0; i &amp;lt; s.length; i++) %7B let f = s%5Bi%5D; f.setAttribute('cx', r(1, 100) + '%25'); f.setAttribute('cy', '-' + r(1, 100)); f.setAttribute('r', r(1, 3)); %7D %7D l();%3C/script%3E%3C/svg%3E")`
);



```


### 文本阴影实现 3d 欢迎效果 


``` js
console.info(
  '%c你好，code 秘密花园',
  `color:white;font-size:40px;line-height:300px;text-shadow:-1px -1px red, 1px 1px #ff1700, 3px 2px #ff2e00, 5px 3px orangered, 7px 4px #ff5c00, 9px 5px #ff7300, 11px 6px #ff8a00, 13px 7px #ffa100, 14px 8px #ffb800, 16px 9px #ffcf00, 18px 10px #ffe600, 20px 11px #fffc00, 22px 12px #ebff00, 23px 13px #d4ff00, 25px 14px #bdff00, 27px 15px #a6ff00, 28px 16px #8fff00, 30px 17px #78ff00, 32px 18px #61ff00, 33px 19px #4aff00, 35px 20px #33ff00, 36px 21px #1cff00, 38px 22px #05ff00, 39px 23px #00ff12, 41px 24px #00ff29, 42px 25px #00ff40, 43px 26px #00ff57, 45px 27px #00ff6e, 46px 28px #00ff85, 47px 29px #00ff9c, 48px 30px #00ffb3, 49px 31px #00ffc9, 50px 32px #00ffe0, 51px 33px #00fff7, 52px 34px #00f0ff, 53px 35px #00d9ff, 54px 36px #00c2ff, 55px 37px #00abff, 55px 38px #0094ff, 56px 39px #007dff, 57px 40px #0066ff, 57px 41px #004fff, 58px 42px #0038ff, 58px 43px #0021ff, 58px 44px #000aff, 59px 45px #0d00ff, 59px 46px #2400ff, 59px 47px #3b00ff, 59px 48px #5200ff, 59px 49px #6900ff, 60px 50px #8000ff, 59px 51px #9600ff, 59px 52px #ad00ff, 59px 53px #c400ff, 59px 54px #db00ff, 59px 55px #f200ff, 58px 56px #ff00f5, 58px 57px #ff00de, 58px 58px #ff00c7, 57px 59px #ff00b0, 57px 60px #ff0099, 56px 61px #ff0082, 55px 62px #ff006b, 55px 63px #ff0054, 54px 64px #ff003d, 53px 65px #ff0026, 52px 66px #ff000f, 51px 67px #ff0800, 50px 68px #ff1f00, 49px 69px #ff3600, 48px 70px #ff4d00, 47px 71px #ff6300, 46px 72px #ff7a00, 45px 73px #ff9100, 43px 74px #ffa800, 42px 75px #ffbf00, 41px 76px #ffd600, 39px 77px #ffed00, 38px 78px #faff00, 36px 79px #e3ff00, 35px 80px #ccff00, 33px 81px #b5ff00, 32px 82px #9eff00, 30px 83px #87ff00, 28px 84px #70ff00, 27px 85px #59ff00, 25px 86px #42ff00, 23px 87px #2bff00, 22px 88px #14ff00, 20px 89px #00ff03, 18px 90px #00ff1a, 16px 91px #00ff30, 14px 92px #00ff47, 13px 93px #00ff5e, 11px 94px #00ff75, 9px 95px #00ff8c, 7px 96px #00ffa3, 5px 97px #00ffba, 3px 98px #00ffd1, 1px 99px #00ffe8, 7px 100px cyan, -1px 101px #00e8ff, -3px 102px #00d1ff, -5px 103px #00baff, -7px 104px #00a3ff, -9px 105px #008cff, -11px 106px #0075ff, -13px 107px #005eff, -14px 108px #0047ff, -16px 109px #0030ff, -18px 110px #001aff, -20px 111px #0003ff, -22px 112px #1400ff, -23px 113px #2b00ff, -25px 114px #4200ff, -27px 115px #5900ff, -28px 116px #7000ff, -30px 117px #8700ff, -32px 118px #9e00ff, -33px 119px #b500ff, -35px 120px #cc00ff, -36px 121px #e300ff, -38px 122px #fa00ff, -39px 123px #ff00ed, -41px 124px #ff00d6, -42px 125px #ff00bf, -43px 126px #ff00a8, -45px 127px #ff0091, -46px 128px #ff007a, -47px 129px #ff0063, -48px 130px #ff004d, -49px 131px #ff0036, -50px 132px #ff001f, -51px 133px #ff0008, -52px 134px #ff0f00, -53px 135px #ff2600, -54px 136px #ff3d00, -55px 137px #ff5400, -55px 138px #ff6b00, -56px 139px #ff8200, -57px 140px #ff9900, -57px 141px #ffb000, -58px 142px #ffc700, -58px 143px #ffde00, -58px 144px #fff500, -59px 145px #f2ff00, -59px 146px #dbff00, -59px 147px #c4ff00, -59px 148px #adff00, -59px 149px #96ff00, -60px 150px #80ff00, -59px 151px #69ff00, -59px 152px #52ff00, -59px 153px #3bff00, -59px 154px #24ff00, -59px 155px #0dff00, -58px 156px #00ff0a, -58px 157px #00ff21, -58px 158px #00ff38, -57px 159px #00ff4f, -57px 160px #00ff66, -56px 161px #00ff7d, -55px 162px #00ff94, -55px 163px #00ffab, -54px 164px #00ffc2, -53px 165px #00ffd9, -52px 166px #00fff0, -51px 167px #00f7ff, -50px 168px #00e0ff, -49px 169px #00c9ff, -48px 170px #00b3ff, -47px 171px #009cff, -46px 172px #0085ff, -45px 173px #006eff, -43px 174px #0057ff, -42px 175px #0040ff, -41px 176px #0029ff, -39px 177px #0012ff, -38px 178px #0500ff, -36px 179px #1c00ff, -35px 180px #3300ff, -33px 181px #4a00ff, -32px 182px #6100ff, -30px 183px #7800ff, -28px 184px #8f00ff, -27px 185px #a600ff, -25px 186px #bd00ff, -23px 187px #d400ff, -22px 188px #eb00ff, -20px 189px #ff00fc, -18px 190px #ff00e6, -16px 191px #ff00cf, -14px 192px #ff00b8, -13px 193px #ff00a1, -11px 194px #ff008a, -9px 195px #ff0073, -7px 196px #ff005c, -5px 197px #ff0045, -3px 198px #ff002e, -1px 199px #ff0017, -1px 200px red, 1px 201px #ff1700, 3px 202px #ff2e00, 5px 203px orangered, 7px 204px #ff5c00, 9px 205px #ff7300, 11px 206px #ff8a00, 13px 207px #ffa100, 14px 208px #ffb800, 16px 209px #ffcf00, 18px 210px #ffe600, 20px 211px #fffc00, 22px 212px #ebff00, 23px 213px #d4ff00, 25px 214px #bdff00, 27px 215px #a6ff00, 28px 216px #8fff00, 30px 217px #78ff00, 32px 218px #61ff00, 33px 219px #4aff00, 35px 220px #33ff00, 36px 221px #1cff00, 38px 222px #05ff00, 39px 223px #00ff12, 41px 224px #00ff29, 42px 225px #00ff40, 43px 226px #00ff57, 45px 227px #00ff6e, 46px 228px #00ff85, 47px 229px #00ff9c, 48px 230px #00ffb3, 49px 231px #00ffc9, 50px 232px #00ffe0, 51px 233px #00fff7, 52px 234px #00f0ff, 53px 235px #00d9ff, 54px 236px #00c2ff, 55px 237px #00abff, 55px 238px #0094ff, 56px 239px #007dff, 57px 240px #0066ff, 57px 241px #004fff, 58px 242px #0038ff, 58px 243px #0021ff, 58px 244px #000aff, 59px 245px #0d00ff, 59px 246px #2400ff, 59px 247px #3b00ff, 59px 248px #5200ff, 59px 249px #6900ff, 60px 250px #8000ff, 59px 251px #9600ff, 59px 252px #ad00ff, 59px 253px #c400ff, 59px 254px #db00ff, 59px 255px #f200ff, 58px 256px #ff00f5, 58px 257px #ff00de, 58px 258px #ff00c7, 57px 259px #ff00b0, 57px 260px #ff0099, 56px 261px #ff0082, 55px 262px #ff006b, 55px 263px #ff0054, 54px 264px #ff003d, 53px 265px #ff0026, 52px 266px #ff000f, 51px 267px #ff0800, 50px 268px #ff1f00, 49px 269px #ff3600, 48px 270px #ff4d00, 47px 271px #ff6300, 46px 272px #ff7a00, 45px 273px #ff9100, 43px 274px #ffa800, 42px 275px #ffbf00, 41px 276px #ffd600, 39px 277px #ffed00, 38px 278px #faff00, 36px 279px #e3ff00, 35px 280px #ccff00, 33px 281px #b5ff00, 32px 282px #9eff00, 30px 283px #87ff00, 28px 284px #70ff00, 27px 285px #59ff00, 25px 286px #42ff00, 23px 287px #2bff00, 22px 288px #14ff00, 20px 289px #00ff03, 18px 290px #00ff1a, 16px 291px #00ff30, 14px 292px #00ff47, 13px 293px #00ff5e, 11px 294px #00ff75, 9px 295px #00ff8c, 7px 296px #00ffa3, 5px 297px #00ffba, 3px 298px #00ffd1, 1px 299px #00ffe8, 2px 300px cyan, -1px 301px #00e8ff, -3px 302px #00d1ff, -5px 303px #00baff, -7px 304px #00a3ff, -9px 305px #008cff, -11px 306px #0075ff, -13px 307px #005eff, -14px 308px #0047ff, -16px 309px #0030ff, -18px 310px #001aff, -20px 311px #0003ff, -22px 312px #1400ff, -23px 313px #2b00ff, -25px 314px #4200ff, -27px 315px #5900ff, -28px 316px #7000ff, -30px 317px #8700ff, -32px 318px #9e00ff, -33px 319px #b500ff, -35px 320px #cc00ff, -36px 321px #e300ff, -38px 322px #fa00ff, -39px 323px #ff00ed, -41px 324px #ff00d6, -42px 325px #ff00bf, -43px 326px #ff00a8, -45px 327px #ff0091, -46px 328px #ff007a, -47px 329px #ff0063, -48px 330px #ff004d, -49px 331px #ff0036, -50px 332px #ff001f, -51px 333px #ff0008, -52px 334px #ff0f00, -53px 335px #ff2600, -54px 336px #ff3d00, -55px 337px #ff5400, -55px 338px #ff6b00, -56px 339px #ff8200, -57px 340px #ff9900, -57px 341px #ffb000, -58px 342px #ffc700, -58px 343px #ffde00, -58px 344px #fff500, -59px 345px #f2ff00, -59px 346px #dbff00, -59px 347px #c4ff00, -59px 348px #adff00, -59px 349px #96ff00, -60px 350px #80ff00, -59px 351px #69ff00, -59px 352px #52ff00, -59px 353px #3bff00, -59px 354px #24ff00, -59px 355px #0dff00, -58px 356px #00ff0a, -58px 357px #00ff21, -58px 358px #00ff38, -57px 359px #00ff4f, -57px 360px #00ff66, -56px 361px #00ff7d, -55px 362px #00ff94, -55px 363px #00ffab, -54px 364px #00ffc2, -53px 365px #00ffd9, -52px 366px #00fff0, -51px 367px #00f7ff, -50px 368px #00e0ff, -49px 369px #00c9ff, -48px 370px #00b3ff, -47px 371px #009cff, -46px 372px #0085ff, -45px 373px #006eff, -43px 374px #0057ff, -42px 375px #0040ff, -41px 376px #0029ff, -39px 377px #0012ff, -38px 378px #0500ff, -36px 379px #1c00ff, -35px 380px #3300ff, -33px 381px #4a00ff, -32px 382px #6100ff, -30px 383px #7800ff, -28px 384px #8f00ff, -27px 385px #a600ff, -25px 386px #bd00ff, -23px 387px #d400ff, -22px 388px #eb00ff, -20px 389px #ff00fc, -18px 390px #ff00e6, -16px 391px #ff00cf, -14px 392px #ff00b8, -13px 393px #ff00a1, -11px 394px #ff008a, -9px 395px #ff0073, -7px 396px #ff005c, -5px 397px #ff0045, -3px 398px #ff002e, -1px 399px #ff0017`
);

```

### 普通svg 条幅显示时间 

``` js
console.info(
  '%c ',
  `line-height:100px;padding-block:50px;padding-left:400px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 100'%3E%3Cstyle%3E text %7B font-family: sans-serif; font-weight: 100; fill: %23d8eaff; %7D %3C/style%3E%3Crect width='400' height='100'%3E%3C/rect%3E%3Ctext text-anchor='middle' font-size='15' x='200' y='50'%3ESaturday, December 16, 2023 at 6:28 PM%3C/text%3E%3Cscript%3E const text_element = document.querySelector('text'); text_element.textContent = new Date().toLocaleString(true, %7B weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' %7D); %3C/script%3E%3C/svg%3E")`
);

```

### 一些工具推荐
1. 控制台测试 CodePen：可以自动为你生成这些 console.info！将 SVG 粘贴到笔的 HTML 部分，运行它，然后打开控制台。控制台将向你显示消息的呈现方式以及用于生成消息的代码。https://codepen.io/ZachSaucier/pen/GRzypKq
2. 矢量编辑器 – 使用上面的 CodePen，你可以粘贴几乎任何 SVG 并获得有效的控制台命令。这意味着你可以使用 Inkscape、Adobe Illustator 或任何其他你想要用来生成 SVG 的工具！
css-doodle 可以用于创建在控制台中使用的 SVG。
https://css-doodle.com/
3. SVGOMG 压缩 SVG 以减小文件大小。这也可以帮助你尝试适应 Firefox 的字符限制。
https://jakearchibald.github.io/svgomg/
4. EZGIF 用于将常规图像转换为数据 URI。
https://ezgif.com/image-to-datauri/ezgif-4-975be6affc.jpg