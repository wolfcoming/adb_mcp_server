# Android ADB MCP 服务器

这是一个基于 MCP 协议的 Android ADB 服务器，允许通过 Claude for Desktop 或其他 MCP 客户端远程控制连接到电脑的 Android 设备。

## 功能特点

- **设备管理**：列出已连接的 Android 设备
- **屏幕操作**：截图、点击、滑动（上下左右）
- **输入操作**：文本输入、按键模拟
- **应用管理**：安装/卸载应用、启动应用
- **系统操作**：获取屏幕分辨率等设备信息
- **网络工具**：获取网络状态、端口扫描、WIFI管理
- **文件工具**：文件上传/下载、文件管理
- **高级工具**：UI测试、性能分析、录屏、日志收集、增强型启动应用

## 前提条件

1. Python 3.10 或更高版本
2. ADB 已安装并添加到系统路径
3. Android 设备已启用 USB 调试并连接到电脑

## 安装

```bash
# 克隆或下载此仓库
cd adb_mcp_server

# 安装依赖
pip install -r requirements.txt

# 确保 ADB 服务器已启动
adb start-server
```

## 使用方法

### 在 Claude for Desktop 中配置

1. 安装 [Claude for Desktop](https://claude.ai/desktop)
2. 配置 MCP 服务器:
   - 找到 Claude for Desktop 配置文件，通常在 `~/Library/Application Support/Claude/claude_desktop_config.json`
   - 添加以下配置:

```json
{
    "mcpServers": {
        "android_adb": {
            "command": "python",
            "args": [
                "-m",
                "src.adb_server"
            ],
            "cwd": "/path/to/adb_mcp_server"
        }
    }
}
```

3. 重启 Claude for Desktop

### 在 Cursor 中配置

1. 找到 Cursor 配置文件，通常在 `~/.cursor/mcp.json`
2. 添加以下配置:

```json
{
    "mcpServers": {
        "android_adb": {
            "command": "python",
            "args": [
                "-m",
                "src.adb_server"
            ],
            "cwd": "/path/to/adb_mcp_server"
        }
    }
}
```

3. 重启 Cursor

## 支持的工具

### 设备管理
- `list_devices`: 列出所有连接的 Android 设备

### 屏幕操作
- `take_screenshot`: 截取设备屏幕
- `tap_screen`: 点击屏幕上的指定位置
- `swipe_up`: 向上滑动
- `swipe_down`: 向下滑动
- `swipe_left`: 向左滑动
- `swipe_right`: 向右滑动

### 输入操作
- `input_text`: 输入文本
- `press_key`: 按下指定按键
- `press_back`: 按下返回键
- `press_home`: 按下 Home 键

### 应用管理
- `start_app`: 启动应用
- `install_apk`: 安装APK
- `uninstall_app`: 卸载应用

### 系统操作
- `get_screen_resolution`: 获取屏幕分辨率

### 网络工具
- `get_ip_address`: 获取设备IP地址
- `ping`: 测试网络连接
- `scan_ports`: 扫描指定端口
- `get_wifi_status`: 获取WIFI状态
- `connect_wifi`: 连接到WIFI网络

### 文件工具
- `list_files`: 列出目录下的文件
- `upload_file`: 上传文件到设备
- `download_file`: 从设备下载文件
- `create_file`: 创建文件
- `delete_file`: 删除文件

### 高级工具
- `dump_ui_hierarchy`: 获取界面层次结构
- `run_ui_test`: 执行UI测试步骤
- `check_element_exists`: 检查界面元素是否存在
- `tap_element_by_text`: 点击包含指定文本的UI元素
- `collect_device_logs`: 收集设备日志
- `analyze_performance`: 分析应用性能
- `take_screen_recording`: 录制设备屏幕视频
- `enhanced_start_app`: 增强型应用启动功能，可绕过权限限制

## 示例用法

在 Claude for Desktop 中，可以这样使用:

```
# 设备相关
"我想查看连接的 Android 设备"
"请截取我的 Android 设备屏幕"

# 应用操作
"请安装这个APK文件: /path/to/app.apk"
"请启动设置应用(com.android.settings)"
"请使用增强型启动功能打开中国新闻网应用，即使遇到权限问题"

# 输入与交互
"请点击屏幕坐标 (500, 500)"
"请在屏幕上从底部向上滑动"
"请点击包含'设置'文本的按钮"

# 文件操作
"请列出设备上 /sdcard/ 目录下的文件"
"请将设备上的 /sdcard/DCIM/pic.jpg 下载到我的电脑"

# 网络操作
"请检查设备的WIFI状态"
"请连接到名为'MyWifi'的网络"

# 高级功能
"请分析'com.example.app'应用的性能，持续30秒"
"请录制10秒钟的屏幕视频"
"请收集最近的设备日志"
```

## 提示

- 如果遇到问题，确保 ADB 服务器已启动 (`adb start-server`)
- 确保 Android 设备已授权您的电脑进行 USB 调试
- 某些操作可能需要 root 权限
- 如果遇到"Permission Denial"权限问题，请使用`enhanced_start_app`高级工具 