# Aqara Bridge for Home Assistant

基于 Aqara 开放平台，通过云端 API 进行设备控制及 RocketMQ 消息推送实现实时状态同步。

[![version](https://img.shields.io/github/manifest-json/v/HerbertGao/AqaraBridge?filename=custom_components%2Faqara_bridge%2Fmanifest.json)](https://github.com/HerbertGao/AqaraBridge/releases/latest) [![stars](https://img.shields.io/github/stars/HerbertGao/AqaraBridge)](https://github.com/HerbertGao/AqaraBridge/stargazers) [![issues](https://img.shields.io/github/issues/HerbertGao/AqaraBridge)](https://github.com/HerbertGao/AqaraBridge/issues) [![hacs](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)

## 兼容性

- Home Assistant 2025.1.0 ~ 2026.3+
- 架构：x86_64 / aarch64（自带 librocketmq 动态链接库）

## 支持设备

| 类型 | 示例设备 | HA 平台 |
|------|---------|---------|
| 墙壁开关 | 单火/零火 1~3 键 | switch |
| 智能插座 | 墙插/智能插座 | switch + sensor (功率/电量) |
| 智能灯 | 吸顶灯/灯泡/LED调光器 | light (亮度/色温/RGB) |
| 温湿度传感器 | 温湿度传感器 T1 | sensor |
| 人体传感器 | 人体传感器 P1/T1 | binary_sensor |
| 门窗传感器 | 门窗传感器 E1/T1/P1 | binary_sensor |
| 无线按钮 | 无线开关/旋钮 H1 | sensor (事件) |
| 水浸传感器 | 水浸传感器 | binary_sensor |
| 烟雾报警器 | 烟雾报警器 | binary_sensor |
| 空气质量传感器 | PM2.5/CO2e/TVOC | sensor |
| 窗帘电机 | 窗帘电机 E1 | cover + sensor (电池) |
| 智能门锁 | A100 Pro | sensor (锁状态/开门方式) + binary_sensor (门状态) |
| 空调伴侣 | 空调伴侣 P3 | climate + sensor (温度/湿度/功率/电量) + switch (继电器) |
| 魔方控制器 | 魔方控制器 | sensor (动作/旋转角度) |
| VRF 空调控制器 | VRF 控制器 T1 | climate |

如果发现有不支持的设备，可以在 [aiot_mapping.py](https://github.com/HerbertGao/AqaraBridge/blob/master/custom_components/aqara_bridge/core/aiot_mapping.py) 中添加设备映射。

## 安装

### 通过 HACS（推荐）

1. HACS -> 集成 -> 右上角菜单 -> 自定义存储库
2. 输入 `HerbertGao/AqaraBridge`，类别选择「集成」
3. 安装后重启 Home Assistant

### 手动安装

将 `custom_components/aqara_bridge` 目录复制到 HA 的 `config/custom_components/` 目录下，重启 Home Assistant。

## 配置

### 前置条件：申请开发者账号

1. 注册 [Aqara IoT Cloud](https://developer.aqara.com/register) 开发者账号并完成个人认证
2. 进入项目管理 -> 详情 -> 消息推送 -> 编辑 -> 选择中国服务、MQ 消息推送、全订阅 -> 保存
3. 返回概况，展开 Appid & 密钥，记录中国服务的 **AppId**、**AppKey**、**KeyId**

> 必须使用自己的开发者账号，使用插件自带信息会导致状态丢失。

### 添加集成

设置 -> 设备与服务 -> 添加集成 -> 搜索 "Aqara Bridge" -> 输入 AppId、AppKey、KeyId 及绿米账号信息。

## 版本修订

### 2026.1.0

- 升级 HA 兼容性至 2025.1 ~ 2026.3+
- 修复 token 刷新缺失 `await`、参数错误等 bug，新增定时主动刷新 + Store 持久化
- 灯光色温从 mireds 迁移到 kelvin（向后兼容旧版 HA）
- 空气质量传感器从废弃的 `AirQualityEntity` 迁移到独立 `SensorEntity`
- 替换废弃 HA API：`hass.components`、`async_add_job`、`asyncio.get_event_loop` 等
- 清理通配符导入，消除 40+ 条废弃常量警告
- 修复 button 实体 `state_class` 类型校验报错
- 新增设备支持：窗帘电机 E1、智能门锁 A100 Pro、空调伴侣 P3、魔方控制器
- 优化 N+1 API 调用：批量位置查询、设备资源名缓存
- 修复 `remote.py` 中 `time.sleep` 阻塞事件循环
- Token 有效期从 7 天延长至 10 年，减少重新登录频率

### 0.2.3

- 修复开发者配置问题，可以使用自己开发者信息

### 0.2.2

- 修复错误保存问题，增加启动依赖
- 修复 flow 的 option 操作错误，可以重新通过手机号刷新失效 token
- hass 图标已通过审核，可正常显示组件及设备厂商图标

### 0.2.1

- 整体合并到 master，将多个网关合并到账号，拆分开发者认证信息
- 新增部分组件配置：无线旋钮 H1、磁吸格栅灯、无线按钮（升级版）
- 墙壁开关拆分零火/单火，零火加入电量监测
