# docker-compose部署

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

第一次启动会初始化一次用户数据，第一次初始化成功后，后续就不会再次初始化了