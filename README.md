# ⚡️国家电网电力获取

## 简介
本项目是基于作者@ARC-MX的[sgcc_electricity_new](https://github.com/ARC-MX/sgcc_electricity_new)
项目开发，二次开发的原因是因为原作者采用Home Assistant API调用添加实体，在使用过程中发现重启Home Assistant后会出现实体丢失的问题，用户体验不佳。
因此我改造了原作者的项目，以接口的方式对外提供数据，该项目部署成功后，通过项目[sgcc_electricity_client](https://github.com/Javedhd/sgcc_electricity_client)调用接口在Home Assistant中创建实体。

## 安装与部署

### docker-compose部署
1. 安装docker与docker-compose

    [docker安装](https://docs.docker.com/engine/install/centos/)  
    [docker-compose安装](https://docs.docker.com/compose/install/linux/)

2. 克隆仓库
``` sh
git clone https://github.com/Javedhd/sgcc_electricity_web.git
```
3. 修改配置文件
``` sh
cd sgcc_electricity_web
cp src/config.yaml .
vim config.yaml
```

``` yaml
electricity:
  phone_number: ""                      # 这里写国家电网的注册手机号
  password: ""                          # 这里写国家电网的密码
  deiver_impltcity_wait_time: 60        # 浏览器默认等待时间，秒
  retry_times_limit: 5                  # 登录重试次数
  login_expected_time: 60               # 登录超时时间，秒
  retry_wait_time_offset_unit: 10
  data_retention_days: 7                # 记录的天数, 仅支持填写 7 或 30
                                        # 国网原本可以记录 30 天,现在不开通智能缴费只能查询 7 天造成错误
  ignore_user_id: []                    # 忽略的用户id

db:
  name: 'homeassistant.db'              # sqlite3数据库文件名称

logger:
  level: 'info'                         # 日志级别

data:
  path: '/app/data'                     # 数据存储路径，目前主要存储数据库文件

web:
  port: 8080                            # web服务端口
```

4. 启动
``` sh
docker-compose up -d
```

5. 查看启动日志判断是否启动成功
``` sh
docker-compose logs -f
```

第一次启动时日志如下所示：
``` log
sgcc_electricity_web | 2024-12-31 14:04:59,664 [INFO    ] chromium-driver version is 120
sgcc_electricity_web | 2024-12-31 14:04:59,668 [INFO    ] Adding job tentatively -- it will be properly scheduled when the scheduler starts
sgcc_electricity_web | 2024-12-31 14:04:59,672 [INFO    ] db is new created, will init electricity data!!!
sgcc_electricity_web | 2024-12-31 14:04:59,672 [INFO    ] Adding job tentatively -- it will be properly scheduled when the scheduler starts
sgcc_electricity_web | 2024-12-31 14:04:59,674 [INFO    ] Added job "fetch_electricity_task" to job store "default"
sgcc_electricity_web | 2024-12-31 14:04:59,674 [INFO    ] Added job "init_electricity_task" to job store "default"
sgcc_electricity_web | 2024-12-31 14:04:59,674 [INFO    ] Scheduler started
sgcc_electricity_web | 2024-12-31 14:04:59,683 [INFO    ] Serving on http://0.0.0.0:8080
```

## 接口介绍
1. 查询用户列表: /v1/electricity/user_list
``` json
[
  "1100**********",
  "1200**********"
]
```
2. 查询用户信息: /electricity/user_info/{userId}
``` json
{
  "balance": 67.15,
  "location": "北京市************1号1单元",
  "updateTime": "2025-01-07 22:38:38"
}
```
3. 查询用户电费余额: /electricity/balance/{userId}
``` json
{
  "balance": 108.52,
  "updateTime": "2024-12-31 07:04:01"
}
```
4. 查询用户近7天电费使用情况: /electricity/dailys/{userId}
``` json
[
  {
    "date": "2024-12-29",
    "usage": 13.85
  },
  {
    "date": "2024-12-28",
    "usage": 11.99
  },
  {
    "date": "2024-12-27",
    "usage": 8.96
  },
  {
    "date": "2024-12-26",
    "usage": 8.9
  },
  {
    "date": "2024-12-25",
    "usage": 9.89
  },
  {
    "date": "2024-12-24",
    "usage": 9.85
  },
  {
    "date": "2024-12-23",
    "usage": 9.25
  }
]
```
5. 查询用户上月电费使用情况: /electricity/latest_month/{userId}
``` json
{
  "charge": 152.88,
  "date": "2024-11-01",
  "usage": 284
}
```
6. 查询用户今年电费使用情况: /electricity/this_year/{userId}
``` json
{
  "charge": 2046.35,
  "date": "2024-01-01",
  "usage": 4069
}
```

### Buy Me a Coffee

<p align="center">
    <img src="assets/Alipay.png"  width=200 style="margin-right: 70px";/>
    <img src="assets/WeiChat.jpg"  width=200/>
</p>