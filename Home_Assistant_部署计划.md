# 🏠 Home Assistant 国家电网电费监控系统部署计划

## 📋 项目概述

本文档提供了在Home Assistant中部署国家电网电费监控系统的完整部署计划。该系统由两个核心组件组成：

- **sgcc_electricity_web**：后端数据采集服务，负责从国家电网官网自动抓取电费数据
- **sgcc_electricity_client**：Home Assistant集成组件，将电费数据展示为传感器实体

## 🔍 系统架构和数据流

### 架构图
```
┌─────────────────────────┐    HTTP API     ┌──────────────────────────┐
│   sgcc_electricity_web  │ ◄─────────────► │ sgcc_electricity_client  │
│     (后端数据服务)        │                 │   (Home Assistant集成)    │
└─────────────────────────┘                 └──────────────────────────┘
           │                                            │
           ▼                                            ▼
┌─────────────────────────┐                 ┌──────────────────────────┐
│      国家电网官网        │                 │     Home Assistant       │
│   (数据源 - Web抓取)     │                 │      (智能家居平台)        │
└─────────────────────────┘                 └──────────────────────────┘
```

### 数据流程
```
手机号登录 → 获取户号列表 → 为每个户号抓取数据 → 存储到数据库 → API提供数据 → HA集成获取 → 创建传感器 → 显示在HA界面
```

### 传感器实体
系统会为每个户号创建以下6个传感器：
1. `sensor.electricity_[户号]_balance` - 账户余额 (元)
2. `sensor.electricity_[户号]_year_ele_num` - 年度累计用电 (kWh)
3. `sensor.electricity_[户号]_year_ele_cost` - 年度累计电费 (元)
4. `sensor.electricity_[户号]_last_month_ele_num` - 上个月用电 (kWh)
5. `sensor.electricity_[户号]_last_month_ele_cost` - 上个月电费 (元)
6. `sensor.electricity_[户号]_refresh_time` - 最近刷新时间

## 📝 详细部署步骤

### 🔧 第一阶段：环境准备

#### ✅ 任务1：准备部署环境和前置条件

**前置条件检查清单：**
- [ ] Home Assistant版本 ≥ 2023.1（支持自定义组件）
- [ ] Docker环境可用（用于运行Web服务）
- [ ] 网络环境稳定（能访问国家电网官网）
- [ ] Chrome/Chromium浏览器环境（用于Web抓取）

**准备材料：**
- [ ] 国家电网账号（手机号）
- [ ] 国家电网密码
- [ ] Home Assistant管理员权限

### 🚀 第二阶段：后端服务部署

#### ✅ 任务2：部署sgcc_electricity_web后端服务

**方式1：Docker Compose部署（推荐）**

1. 进入项目目录：
```bash
cd sgcc_electricity_web-0.0.4/sgcc_electricity_web-0.0.4
```

2. 编辑`docker-compose.yml`文件，确认配置正确

3. 启动服务：
```bash
docker-compose up -d
```

**方式2：Home Assistant Add-on部署**

1. 将项目作为Add-on添加到Home Assistant
2. 在Add-on Store中安装"SGCC Electricity WEB"
3. 配置Add-on参数

#### ✅ 任务3：配置Web服务

**配置文件位置：** `config.yaml` 或 Add-on配置界面

**必需配置项：**
```yaml
electricity:
  phone_number: "您的手机号"          # 国家电网登录手机号
  password: "您的密码"               # 国家电网登录密码
  deiver_impltcity_wait_time: 60     # 浏览器等待时间(秒)
  retry_times_limit: 5               # 重试次数限制
  login_expected_time: 60            # 登录预期时间(秒)
  retry_wait_time_offset_unit: 10    # 重试等待时间单位(秒)
  data_retention_days: 7             # 数据保留天数(7或30)
  ignore_user_id: []                 # 需要忽略的户号列表
  cron_hour: "7,19"                  # 定时任务执行时间

db:
  name: "homeassistant.db"           # 数据库文件名

logger:
  level: "info"                      # 日志级别
```

**可选配置项：**
```yaml
web:
  port: 8080                         # Web服务端口

data:
  path: "/config"                    # 数据存储路径
```

#### ✅ 任务4：测试Web服务API接口

**验证步骤：**

1. **检查服务状态：**
```bash
# Docker方式
docker-compose ps

# Add-on方式
# 在HA中查看Add-on日志
```

2. **测试API接口：**
```bash
# 获取用户列表
curl http://localhost:8080/v1/electricity/user_list

# 获取用户信息（替换USER_ID为实际户号）
curl http://localhost:8080/v1/electricity/user_info/USER_ID

# 获取账户余额
curl http://localhost:8080/v1/electricity/balance/USER_ID

# 获取近7天用电情况
curl http://localhost:8080/v1/electricity/dailys/USER_ID

# 获取上月用电情况
curl http://localhost:8080/v1/electricity/latest_month/USER_ID

# 获取今年用电情况
curl http://localhost:8080/v1/electricity/this_year/USER_ID
```

3. **预期响应示例：**
```json
// 用户列表响应
["户号1", "户号2", "户号3"]

// 余额响应
{
  "balance": 123.45,
  "updateTime": "2024-01-01 12:00:00"
}
```

### 🏠 第三阶段：Home Assistant集成

#### ✅ 任务5：安装Home Assistant集成组件

**安装步骤：**

1. **复制集成文件：**
```bash
# 进入HA配置目录
cd /config

# 创建自定义组件目录（如果不存在）
mkdir -p custom_components

# 复制集成组件
cp -r /path/to/sgcc_electricity_client/custom_components/sgcc_electricity_client custom_components/
```

2. **验证文件结构：**
```
/config/custom_components/sgcc_electricity_client/
├── __init__.py
├── config_flow.py
├── const.py
├── coordinator.py
├── electricity.py
├── manifest.json
├── sensor.py
├── strings.json
└── utils/
    ├── logger.py
    └── store.py
```

3. **重启Home Assistant**

4. **验证组件加载：**
   - 查看HA日志，确认没有加载错误
   - 在开发者工具中检查集成是否可用

#### ✅ 任务6：在HA中配置集成

**配置步骤：**

1. **添加集成：**
   - 进入 设置 → 设备与服务
   - 点击 "添加集成"
   - 搜索 "sgcc_electricity"
   - 选择 "SGCC Electricity Client"

2. **配置参数：**
   - **服务器地址：** `http://localhost:8080` （如果Web服务在同一主机）
   - **服务器地址：** `http://HOST_IP:8080` （如果Web服务在其他主机）
   - **服务器地址：** `http://a0d7b954-sgcc-electricity-web:8080` （如果使用Add-on）

3. **完成配置：**
   - 点击 "提交"
   - 等待集成验证连接
   - 确认集成添加成功

#### ✅ 任务7：验证传感器创建和数据显示

**验证清单：**

1. **检查传感器实体：**
   - 进入 设置 → 设备与服务 → SGCC Electricity Client
   - 确认每个户号都有对应的设备
   - 每个设备应包含6个传感器实体

2. **验证传感器数据：**
   - 进入 开发者工具 → 状态
   - 搜索 `sensor.electricity_`
   - 确认所有传感器都有数据且状态正常

3. **测试数据更新：**
   - 观察传感器的 `refresh_time` 是否定期更新
   - 默认更新间隔为5分钟

### 📊 第四阶段：优化和监控

#### ✅ 任务8：优化配置和监控运行状态

**性能优化：**

1. **调整更新频率：**
```yaml
# 在coordinator.py中修改更新间隔
update_interval=timedelta(seconds=300)  # 5分钟，可根据需要调整
```

2. **配置日志监控：**
```yaml
# 在configuration.yaml中添加
logger:
  default: warning
  logs:
    custom_components.sgcc_electricity_client: debug
```

3. **设置错误告警：**
```yaml
# 创建自动化，监控传感器状态
automation:
  - alias: "电费数据获取失败告警"
    trigger:
      - platform: state
        entity_id: sensor.electricity_户号_refresh_time
        to: "unavailable"
        for:
          minutes: 30
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "电费数据获取失败，请检查服务状态"
```

**仪表板配置：**

1. **创建电费监控仪表板：**
```yaml
# 在仪表板中添加卡片
type: entities
title: 电费监控
entities:
  - sensor.electricity_户号1_balance
  - sensor.electricity_户号1_year_ele_cost
  - sensor.electricity_户号1_last_month_ele_cost
  - sensor.electricity_户号1_refresh_time
```

2. **配置图表显示：**
```yaml
type: history-graph
title: 用电量趋势
entities:
  - sensor.electricity_户号1_last_month_ele_num
hours_to_show: 168  # 显示一周数据
```

## ⚠️ 重要注意事项

### 安全考虑
- **账号安全：** 使用HA的secrets功能存储敏感信息
```yaml
# secrets.yaml
sgcc_phone: "您的手机号"
sgcc_password: "您的密码"

# config.yaml
electricity:
  phone_number: !secret sgcc_phone
  password: !secret sgcc_password
```

### 网络要求
- **网络稳定性：** 确保能稳定访问国家电网官网（95598.cn）
- **防火墙设置：** 确保Web服务端口（默认8080）可访问
- **代理配置：** 如使用代理，需要在Docker中配置相应环境变量

### 故障排除
- **验证码识别失败：** 系统会自动重试，如持续失败请检查网络或账号状态
- **多户号问题：** 系统会自动获取手机号下所有户号，无需手动配置
- **数据更新延迟：** Web服务每天定时抓取2次，HA集成每5分钟检查一次

### 维护建议
- **定期检查日志：** 监控数据抓取和API调用状态
- **备份配置：** 定期备份数据库和配置文件
- **更新组件：** 关注项目更新，及时升级版本

## 🔧 故障排除指南

### 常见问题

**1. Web服务启动失败**
```bash
# 检查日志
docker-compose logs sgcc_electricity_web

# 常见原因：
# - 配置文件格式错误
# - 端口被占用
# - Chrome/Chromium环境问题
```

**2. API接口无响应**
```bash
# 检查服务状态
curl -I http://localhost:8080/health

# 检查防火墙
sudo ufw status
```

**3. HA集成添加失败**
- 检查custom_components目录权限
- 确认manifest.json格式正确
- 重启HA后重试

**4. 传感器无数据**
- 检查Web服务API是否正常
- 验证网络连接
- 查看HA日志中的错误信息

### 日志位置
- **Web服务日志：** Docker容器日志或Add-on日志
- **HA集成日志：** `/config/home-assistant.log`
- **数据库位置：** `/config/homeassistant.db`（Add-on模式）

## 📞 支持和反馈

如果在部署过程中遇到问题，可以：

1. 查看项目GitHub页面的Issues
2. 检查本文档的故障排除部分
3. 在HA社区论坛寻求帮助

---

**部署完成后，您将拥有：**
- ✅ 自动化的电费数据采集系统
- ✅ 实时的电费和用电量监控
- ✅ 多户号支持和独立管理
- ✅ 完整的Home Assistant集成体验

祝您部署顺利！🎉
