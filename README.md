<div align="center">

[![NonebotLogo](./docs/NoneBotPlugin.svg)](https://nonebot.dev/)

# nonebot-plugin-weatherpk

[![license](https://img.shields.io/github/license/hanasa2023/nonebot-plugin-weather-rank.svg)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-weather-rank.svg)](https://pypi.python.org/pypi/nonebot-plugin-ba-tools)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

</div>

## 📖 介绍

简单的天气排行榜

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>

在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```sh
    nb plugin install nonebot-plugin-weather-rank
```

</details>

<details>
<summary>使用包管理器安装</summary>

在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```sh
  pip install nonebot-plugin-weather-rank
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

```python
    plugins = ["nonebot_plugin_weather_rank"]
```

</details>

## 🎉 使用

### 💡 数据来源

[和风天气](https://dev.qweather.com)
[中国气象局](http://www.nmc.cn/publish/observations/hourly-temperature.html)

#### 插件配置

🔧 请在你的 bot 根目录下的`.env` `.env.*`中添加以下字段

|       字段       | 默认值 |       描述       |
| :--------------: | :----: | :--------------: |
| QWEATHER_API_KEY |   无   | 和风天气 api key |

### ✨ 功能介绍

- [x] 添加订阅城市
      ![addCity](./docs/add_city.png)
- [x] 查看已订阅城市气温/温差排行榜
      ![rank](./docs/rank.png)
- [x] 查看某地实时气温及预报
      ![rank](./docs/weather.png)
- [x] 查看全国气温地图(可能会有 1h 延迟)
      ![rank](./docs/map.png)
- [x] 获取插件帮助信息
      ![rank](./docs/help.png)

### 🚩 TODO

- [ ] 实现付费订阅 api 相应功能

### 🤖 指令表

⚠️ 此处示例中的"/"为 nb 默认的命令开始标志，若您设置了另外的标志，则请使用您设置的标志作为开头

调用插件的主命令为"天气"

|  子命令  | 权限 | 需要@ |                说明                 |          示例          |
| :------: | :--: | :---: | :---------------------------------: | :--------------------: |
| 添加城市 |  无  |  无   |       在此群聊中添加订阅城市        |  /天气 添加城市 上海   |
|  排行榜  |  无  |  无   |     查看已订阅的城市天气排行榜      | /天气 排行榜 气温/温差 |
| 当地天气 |  无  |  无   | 查看指定城市的当日天气及近 7 日天气 |  /天气 当地天气 上海   |
| 气温地图 |  无  |  无   |  查看最近的时间节点全国的气温地图   |     /天气 气温地图     |

|   指令   | 权限 | 需要@ |       说明       |   示例    |
| :------: | :--: | :---: | :--------------: | :-------: |
| 天气帮助 |  无  |  无   | 查看此插件的帮助 | /天气帮助 |
