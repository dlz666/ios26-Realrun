# ios26-Realrun

> 在 **iPhone / iPad** 上按你自定义的路线，模拟 GPS 位置「自动跑步」。
> 适配 **iOS / iPadOS 17 ~ 26**（基于新版 pymobiledevice3，全异步重写）。

本项目基于 [iOSRealRun/iOSRealRun-cli-17](https://github.com/iOSRealRun/iOSRealRun-cli-17)（MPL 2.0），新增 iPadOS 26 支持、KML 路线转换、可配置坐标系与圈数。

---

## ⚠️ 使用须知

- 仅供学习与个人测试，请遵守相关 App 的用户协议与当地法规，**后果自负**。
- 全程请用 **`Ctrl + C`** 退出，**不要直接关窗口**，否则定位无法自动还原。
- 万一定位没还原：重启手机即可恢复。

---

## 一、准备工作（只需一次）

| # | 要求 | 说明 |
|---|---|---|
| 1 | 电脑系统 | Windows 或 macOS |
| 2 | 设备系统 | iPhone / iPad，**iOS 17 及以上** |
| 3 | iTunes | **仅 Windows 需要**，[去官网下载](https://www.apple.com/itunes/) 并安装 |
| 4 | Python | 安装 [Python 3](https://www.python.org/downloads/)（3.10+，勾选 *Add to PATH*） |
| 5 | 开发者模式 | 设备需开启：**设置 → 隐私与安全性 → 开发者模式**（首次运行程序会自动提醒） |

> ❗ 同一时间**只连一台**设备，多台会出错。

### 安装项目

```bash
git clone https://github.com/dlz666/ios26-Realrun.git
cd ios26-Realrun
pip install -r requirements.txt
```

---

## 二、画一条跑步路线

1. 打开 [Google My Maps](https://www.google.com/maps/d/)（或任何能导出 KML 的地图工具）
2. 用「画线」工具沿你想跑的路线点一圈（**首尾大致闭合**）
3. 导出为 **KML** 文件
4. 转换成项目可用的路线文件：

```bash
python kml_to_route.py 你的地图.kml zju_route.txt
```

> 看到 `converted N points -> zju_route.txt` 就成功了。

---

## 三、改配置 `config.yaml`

```yaml
v: 3.3                 # 跑步速度 (米/秒)，3.3 约等于配速 5 分/公里
routeConfig: "zju_route.txt"   # 上一步生成的路线文件
coordSystem: "wgs84"   # 坐标系，见下方说明
laps: 8                # 跑几圈；填 0 表示无限循环
```

**`coordSystem` 怎么选？** 这是最容易出错的地方（选错会偏移几百米）：

| 你的路线来自 | 填 |
|---|---|
| Google **卫星图** 上描的 | `wgs84` |
| Google / 高德 **普通地图**（有路名、建筑）上描的 | `gcj02` |
| 百度地图 | `bd09` |

> 拿不准就先跑一次，在手机上用**高德地图**看蓝点：落在真实路线上就对了；偏出去几百米，就把 `coordSystem` 换一个再试。

---

## 四、运行

1. 用数据线连接设备，**解锁**，弹出「信任此电脑」时点**信任**
2. 打开终端运行（**必须管理员 / root 权限**，因为要创建虚拟网卡）：

   **Windows**（用「管理员身份」打开 PowerShell 或 CMD）：
   ```bash
   python main.py
   ```

   **macOS**：
   ```bash
   sudo python3 main.py
   ```

3. 看到「已开始模拟跑步」后，程序会按路线自动跑满设定圈数，或一直循环到你按 `Ctrl + C`。

---

## 常见问题

| 现象 | 解决 |
|---|---|
| 提示「请以管理员权限运行」 | Windows 要**右键以管理员身份**打开终端；macOS 用 `sudo` |
| 一直说没有设备 / 连不上 | 确认数据线连好、设备已**解锁并信任**；Windows 确保 **iTunes 已安装并打开过**一次 |
| 提示开启开发者模式 | 按提示：设置 → 隐私与安全性 → 开发者模式，开启后重启设备，再运行 |
| 跑步位置整体偏移几百米 | `config.yaml` 里换一个 `coordSystem`（见上表） |
| 结束后定位没还原 | 一定要用 `Ctrl + C` 退出；若已直接关窗口，重启手机即可恢复 |

---

## 许可证

本项目以 [Mozilla Public License 2.0](LICENSE) 开源，沿用上游 [iOSRealRun/iOSRealRun-cli-17](https://github.com/iOSRealRun/iOSRealRun-cli-17) 的协议。
