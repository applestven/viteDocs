curl --location --request POST 'https://openapi.intelink.net.cn/yjztwms/wms-saas-all/expose/wcp/pickUpTimeQuery' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'version: 1.0' \
--header 'sign: 3B140C469A6D1A5C4EDCC6E384C32472' \
--header 'locale: zh' \
--header 'Accept: */*' \
--header 'Host: openapi.intelink.net.cn' \
--header 'Connection: keep-alive' \
--data-raw '{
    "no": "TEST260409001",
    "noType": "307",
    "dateType": "1",
    "startDate": "2026-2-10",
    "endDate": "2026-4-09",
}'