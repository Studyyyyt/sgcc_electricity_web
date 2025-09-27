# home assistant加载项部署(add-ones)

1. 进入设置->加载项  
![add-ones](../assets/add-ones.png)

2. 点击加载项商店  
![add-ones-market](../assets/add-ones-market.png)

3. 右上角点击仓库  
![add-ones-warehouse](../assets/add-ones-warehouse.png)

4. 将git项目地址写入对话框，点击添加  
![add-ones-add-warehouse](../assets/add-ones-add-warehouse.png)

5. 右上角点击检查更新  
![add-ones-update](../assets/add-ones-update.png)

6. 向下滑动，找到sgcc electricity web端  
![add-ones-sgcc-web](../assets/add-ones-sgcc-web.png)

7. 点击安装，等待安装完成  
![add-ones-install](../assets/add-ones-install.png)

8. 修改配置文件中的手机号与密码  
![add-ones-config](../assets/add-ones-config.png)

9. 点击启动  
![add-ones-startup](../assets/add-ones-startup.png)

10. 从日志中查看启动情况  
![add-ones-log](../assets/add-ones-log.png)

11. 启动成功之后的宿主名就是host名称，在HomeAssistant中通过 http://host:8080即可调用  
![add-ones-hostname](../assets/add-ones-hostname.png)

12. 如需配置client端，如下图配置即可  
![add-ones-client](../assets/add-ones-client.png)