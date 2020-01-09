# stock_helper
stock helper

TODO:
1. 环境部署在云主机上
2. 云主机开启stock-server服务
	1. main周期性(1分钟)获取所有股票信息
	2. 获取股票信息后Stock.parse_info改为并发
	3. parse_info后入库
	4. 获取某一个股票信息从数据库获取
	5. 提供用户注册机制，id name type(vpi general) phone等
	6. 数据库stock表 user表
3. 用户开启stock-client
	1. 用户添加自选股
	2. 用户添加持股信息(id, num, price)
	3. 及时提醒用户持股的动态(level1)
	4. 及时提醒用户自选股的动态(level2)
	5. 及时提醒用户有其他信息