# 通用网站数据抓取转Home Assistant实体架构说明

## 📋 项目概述

本文档基于国家电网电力获取项目，总结了一套通用的架构模式，可以复用于任意网站的数据抓取并转化为Home Assistant实体显示。

## 🏗️ 核心架构模式

```
┌─────────────────────────────────────┐
│           Flask Web应用              │
│  ┌─────────────────────────────────┐│
│  │    定时任务调度器                ││
│  │  (Flask-APScheduler)           ││
│  │  - 定时触发数据抓取              ││
│  │  - 可配置执行时间                ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │    网站数据抓取模块              ││
│  │  - 浏览器自动化 (Selenium)      ││
│  │  - 反检测技术                    ││
│  │  - 验证码处理 (ONNX/OCR)        ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │    数据存储层                    ││
│  │  - SQLite数据库                 ││
│  │  - 数据模型设计                  ││
│  │  - CRUD操作封装                 ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │    RESTful API层                ││
│  │  - Flask-RESTful               ││
│  │  - 标准化JSON响应               ││
│  │  - 错误处理                      ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
         ↓ HTTP API调用
┌─────────────────────────────────────┐
│        Home Assistant              │
│  - REST传感器配置                   │
│  - 自动实体创建                     │
│  - 数据可视化                       │
└─────────────────────────────────────┘
```

## 🔧 核心组件详解

### 1. 定时任务调度器 (Scheduler)

**技术栈**: Flask-APScheduler
**功能**: 定时触发数据抓取任务

```python
from flask_apscheduler import APScheduler

# 初始化调度器
scheduler = APScheduler()

# 配置定时任务
@scheduler.task('cron', id='fetch_data_task', hour='7,19')
def fetch_data_task():
    """定时数据抓取任务"""
    try:
        # 执行数据抓取
        data = data_fetcher.fetch()
        # 存储到数据库
        for item_id, item_data in data.items():
            database.insert_data(item_id, item_data)
        logging.info("数据抓取任务执行成功")
    except Exception as e:
        logging.error(f"数据抓取任务失败: {e}")
```

**复用要点**:
- 可配置执行时间 (`hour`, `minute`, `second`)
- 支持cron表达式
- 异常处理和日志记录
- 任务状态监控

### 2. 网站数据抓取模块 (Data Fetcher)

**技术栈**: Selenium + undetected_chromedriver + ONNX
**功能**: 自动化浏览器操作，抓取目标网站数据

```python
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DataFetcher:
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password
        # 验证码识别模型 (可选)
        self.captcha_solver = CaptchaSolver()
    
    def _get_webdriver(self):
        """获取浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')        # 无头模式
        chrome_options.add_argument('--no-sandbox')      # 沙盒模式
        chrome_options.add_argument('--disable-gpu')     # 禁用GPU
        driver = uc.Chrome(options=chrome_options)
        return driver
    
    def _login(self, driver):
        """登录目标网站"""
        driver.get(LOGIN_URL)
        
        # 输入用户名密码
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(self._username)
        password_input.send_keys(self._password)
        
        # 处理验证码 (如果需要)
        if self._has_captcha(driver):
            self._solve_captcha(driver)
        
        # 点击登录
        login_button = driver.find_element(By.ID, "login-btn")
        login_button.click()
        
        # 等待登录成功
        WebDriverWait(driver, 30).until(
            EC.url_changes(LOGIN_URL)
        )
        return True
    
    def _extract_data(self, driver):
        """提取目标数据"""
        data = {}
        
        # 导航到数据页面
        driver.get(DATA_URL)
        
        # 提取具体数据 - 根据目标网站定制
        elements = driver.find_elements(By.CLASS_NAME, "data-item")
        for element in elements:
            item_id = element.get_attribute("data-id")
            item_value = element.text
            data[item_id] = {
                'value': item_value,
                'timestamp': datetime.now().isoformat()
            }
        
        return data
    
    def fetch(self):
        """主要抓取方法"""
        driver = self._get_webdriver()
        try:
            if self._login(driver):
                return self._extract_data(driver)
            else:
                raise Exception("登录失败")
        finally:
            driver.quit()
```

**复用要点**:
- 模块化设计: 登录、数据提取、验证码处理分离
- 配置化: URL、选择器、等待时间可配置
- 错误处理: 登录失败、元素未找到等异常处理
- 反检测: 使用undetected_chromedriver避免检测

### 3. 数据存储层 (Database Layer)

**技术栈**: SQLite3
**功能**: 数据持久化存储和管理

```python
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据表"""
        cursor = self.connection.cursor()
        
        # 创建主数据表 - 根据业务需求定制
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS main_data (
                id TEXT PRIMARY KEY,
                value REAL,
                unit TEXT,
                category TEXT,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建历史数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                value REAL,
                timestamp TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES main_data (id)
            )
        """)
        
        self.connection.commit()
        cursor.close()
    
    def insert_data(self, item_id: str, value: float, unit: str = None, category: str = None):
        """插入或更新数据"""
        cursor = self.connection.cursor()
        
        # 插入主数据
        cursor.execute("""
            INSERT OR REPLACE INTO main_data (id, value, unit, category, update_time)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (item_id, value, unit, category))
        
        # 插入历史数据
        cursor.execute("""
            INSERT INTO historical_data (item_id, value, timestamp)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (item_id, value))
        
        self.connection.commit()
        cursor.close()
    
    def get_current_data(self, item_id: str):
        """获取当前数据"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT value, unit, category, update_time 
            FROM main_data 
            WHERE id = ?
        """, (item_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'value': result[0],
                'unit': result[1],
                'category': result[2],
                'update_time': result[3]
            }
        return None
    
    def get_historical_data(self, item_id: str, limit: int = 7):
        """获取历史数据"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT value, timestamp 
            FROM historical_data 
            WHERE item_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (item_id, limit))
        
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {'value': row[0], 'timestamp': row[1]} 
            for row in results
        ]
```

**复用要点**:
- 通用数据模型: 主数据表 + 历史数据表
- CRUD操作封装
- 事务处理
- 索引优化

### 4. RESTful API层

**技术栈**: Flask + Flask-RESTful
**功能**: 提供标准化的HTTP API接口

```python
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class DataResource(Resource):
    def get(self, item_id):
        """获取单个数据项"""
        try:
            data = database.get_current_data(item_id)
            if data:
                return data, 200
            else:
                return {'error': 'Data not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

class DataListResource(Resource):
    def get(self):
        """获取所有数据项列表"""
        try:
            data_list = database.get_all_data()
            return data_list, 200
        except Exception as e:
            return {'error': str(e)}, 500

class HistoricalDataResource(Resource):
    def get(self, item_id):
        """获取历史数据"""
        try:
            historical_data = database.get_historical_data(item_id)
            return historical_data, 200
        except Exception as e:
            return {'error': str(e)}, 500

# 注册API路由
api.add_resource(DataListResource, '/api/v1/data')
api.add_resource(DataResource, '/api/v1/data/<string:item_id>')
api.add_resource(HistoricalDataResource, '/api/v1/data/<string:item_id>/history')
```

**复用要点**:
- 标准化RESTful设计
- 统一错误处理
- JSON响应格式
- 版本控制 (`/api/v1/`)

## 🔄 Home Assistant集成模式

### 1. REST传感器配置

```yaml
# configuration.yaml
sensor:
  # 基础数据传感器
  - platform: rest
    name: "网站数据项1"
    resource: "http://your-api-server:8080/api/v1/data/item1"
    value_template: "{{ value_json.value }}"
    unit_of_measurement: "{{ value_json.unit }}"
    scan_interval: 3600  # 1小时更新一次
    
  - platform: rest
    name: "网站数据项2"
    resource: "http://your-api-server:8080/api/v1/data/item2"
    value_template: "{{ value_json.value }}"
    unit_of_measurement: "{{ value_json.unit }}"
    scan_interval: 3600

  # 历史数据传感器
  - platform: rest
    name: "网站数据项1_昨日"
    resource: "http://your-api-server:8080/api/v1/data/item1/history"
    value_template: "{{ value_json[1].value }}"  # 获取第二条记录(昨日)
    scan_interval: 86400  # 1天更新一次
```

### 2. 自动化规则示例

```yaml
# automations.yaml
automation:
  - alias: "数据异常告警"
    trigger:
      platform: numeric_state
      entity_id: sensor.wang_zhan_shu_ju_xiang_1
      above: 100  # 阈值
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "网站数据异常: {{ states('sensor.wang_zhan_shu_ju_xiang_1') }}"
        
  - alias: "定时数据报告"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      service: notify.mobile_app_your_phone
      data:
        message: >
          每日数据报告:
          数据项1: {{ states('sensor.wang_zhan_shu_ju_xiang_1') }}
          数据项2: {{ states('sensor.wang_zhan_shu_ju_xiang_2') }}
```

## 🛠️ 通用化配置文件

```yaml
# config.yaml - 通用配置模板
website:
  name: "目标网站名称"
  login_url: "https://example.com/login"
  data_url: "https://example.com/data"
  username: "your_username"
  password: "your_password"
  
scraping:
  schedule_hours: "7,19"          # 定时抓取时间
  retry_times: 3                  # 重试次数
  wait_time: 10                   # 等待时间(秒)
  headless: true                  # 无头模式
  
database:
  path: "/data/website_data.db"   # 数据库路径
  
api:
  host: "0.0.0.0"
  port: 8080
  version: "v1"
  
logging:
  level: "INFO"
  file: "/logs/scraper.log"

# 数据项配置
data_items:
  - id: "item1"
    name: "数据项1"
    selector: "#data-item-1"      # CSS选择器
    unit: "单位"
    category: "类别1"
    
  - id: "item2" 
    name: "数据项2"
    selector: ".data-value"
    unit: "单位2"
    category: "类别2"
```

## 📁 项目结构模板

```
universal_web_scraper/
├── config/
│   ├── __init__.py
│   └── config.py              # 配置文件解析
├── scraper/
│   ├── __init__.py
│   ├── base_fetcher.py        # 基础抓取类
│   ├── captcha_solver.py      # 验证码处理
│   └── site_specific.py       # 特定网站实现
├── database/
│   ├── __init__.py
│   ├── models.py              # 数据模型
│   └── manager.py             # 数据库管理
├── api/
│   ├── __init__.py
│   ├── resources.py           # API资源
│   └── app.py                 # Flask应用
├── utils/
│   ├── __init__.py
│   ├── logger.py              # 日志工具
│   └── helpers.py             # 辅助函数
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖包
├── config.yaml               # 配置文件
└── README.md                 # 说明文档
```

## 🚀 快速部署指南

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件
```bash
# 复制配置模板
cp config.yaml.example config.yaml

# 编辑配置文件
vim config.yaml
```

### 3. 启动服务
```bash
# 启动API服务
python main.py

# 或使用Docker
docker-compose up -d
```

### 4. Home Assistant配置
```yaml
# 添加到configuration.yaml
sensor: !include sensors.yaml

# 重启Home Assistant
```

## 🎯 复用指南

### 适用场景
1. **需要定期抓取数据的网站**
2. **需要登录认证的网站**
3. **有验证码的网站**
4. **需要在Home Assistant中显示数据**

### 自定义步骤
1. **修改抓取逻辑**: 根据目标网站调整`site_specific.py`
2. **配置数据项**: 在`config.yaml`中定义数据项
3. **调整数据模型**: 根据数据结构修改数据库表
4. **设置API端点**: 根据需要添加API接口
5. **配置HA传感器**: 在Home Assistant中添加传感器

### 注意事项
1. **遵守网站条款**: 确保抓取行为符合网站使用条款
2. **频率控制**: 避免过于频繁的请求
3. **错误处理**: 完善的异常处理机制
4. **数据验证**: 验证抓取数据的正确性
5. **安全性**: 保护登录凭据和敏感数据

## 📊 监控和维护

### 日志监控
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# 记录关键事件
logger.info("开始数据抓取")
logger.error("抓取失败: %s", error_message)
logger.info("数据存储成功")
```

### 健康检查
```python
@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        database.test_connection()
        
        # 检查最近数据更新时间
        last_update = database.get_last_update_time()
        if (datetime.now() - last_update).hours > 25:
            return {'status': 'warning', 'message': '数据更新延迟'}, 200
        
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
```

## 🔚 总结

这套架构提供了一个完整的、可复用的解决方案，用于将任意网站的数据转化为Home Assistant实体。通过模块化设计和配置化管理，可以快速适配不同的目标网站，实现自动化数据采集和智能家居集成。

核心优势：
- **通用性强**: 适用于各种网站结构
- **可扩展性好**: 模块化设计便于扩展
- **维护性强**: 配置化管理，易于维护
- **稳定性高**: 完善的错误处理和重试机制
- **集成性好**: 与Home Assistant无缝集成
