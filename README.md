## ql-bilibili

> 欢迎大家issue、pr，会一一回复！

## 使用流程

1、青龙部署。

2、订阅管理 -> 新增订阅

1. 链接：https://github.com/Pengfei00/ql-bilibili.git
2. 定时规则：0 0 * * *
3. 白名单: bili_
4. 依赖文件：common

3、依赖管理 -> 新建依赖 -> 依赖类型:python3 -> 名称: requests

4、添加BILIBILI_CK环境变量

## 环境变量

|             Name             |             归属             |  属性  | 说明                                                         |
| :--------------------------: | :--------------------------: | :----: | ------------------------------------------------------------ |
|     BILIBILI_CK     |     bilibili账号cookie     | 必须 |  |
|     BILIBILI_ACCESS_KEY     |     bilibili客户端access key     | 可选 |  |
|     BARK_PUSH     |     bark推送地址     | 可选 |  |


