from typing import Any, List, Optional
import os
import time
import base64
import tempfile
import json
from ppadb.client import Client as AdbClient
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("android_adb")

# ADB 常量
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037

# 辅助函数
def get_adb_client() -> AdbClient:
    """初始化并返回ADB客户端"""
    client = AdbClient(host=ADB_HOST, port=ADB_PORT)
    return client

def get_device(device_id: Optional[str] = None):
    """获取ADB设备，如果指定了device_id则返回该设备，否则返回第一个可用设备"""
    client = get_adb_client()
    devices = client.devices()
    
    if not devices:
        raise ValueError("未找到连接的设备")
    
    if device_id:
        for device in devices:
            if device.serial == device_id:
                return device
        raise ValueError(f"未找到指定的设备: {device_id}")
    
    return devices[0]  # 返回第一个设备

# 工具实现
@mcp.tool()
async def list_devices() -> str:
    """列出所有连接的Android设备"""
    client = get_adb_client()
    devices = client.devices()
    
    if not devices:
        return "未找到连接的设备"
    
    device_info = []
    for device in devices:
        try:
            model = device.shell("getprop ro.product.model").strip()
            android_version = device.shell("getprop ro.build.version.release").strip()
            device_info.append(f"设备ID: {device.serial}\n型号: {model}\nAndroid版本: {android_version}")
        except Exception as e:
            device_info.append(f"设备ID: {device.serial}\n获取详细信息时出错: {str(e)}")
    
    return "\n\n".join(device_info)

@mcp.tool()
async def take_screenshot(device_id: Optional[str] = None) -> str:
    """截取设备屏幕

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 创建临时文件存储截图
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 在设备上截图并保存到临时文件
        device.shell("screencap -p /sdcard/screenshot.png")
        device.pull("/sdcard/screenshot.png", temp_path)
        device.shell("rm /sdcard/screenshot.png")
        
        # 将图片转换为base64
        with open(temp_path, 'rb') as img_file:
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # 删除临时文件
        os.remove(temp_path)
        
        return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        return f"截图失败: {str(e)}"

@mcp.tool()
async def record_screen(duration: int = 5, device_id: Optional[str] = None) -> str:
    """录制设备屏幕

    参数:
        duration: 录制时长（秒），默认5秒
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 创建临时文件存储视频
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 在设备上录制屏幕
        device.shell(f"screenrecord --time-limit {duration} /sdcard/screenrecord.mp4")
        time.sleep(duration + 1)  # 等待录制完成
        
        # 将视频拉到本地
        device.pull("/sdcard/screenrecord.mp4", temp_path)
        device.shell("rm /sdcard/screenrecord.mp4")
        
        # 将视频转换为base64
        with open(temp_path, 'rb') as video_file:
            base64_data = base64.b64encode(video_file.read()).decode('utf-8')
        
        # 删除临时文件
        os.remove(temp_path)
        
        return f"data:video/mp4;base64,{base64_data}"
    except Exception as e:
        return f"录屏失败: {str(e)}"

@mcp.tool()
async def tap_screen(x: int, y: int, device_id: Optional[str] = None) -> str:
    """点击屏幕上的指定位置

    参数:
        x: 横坐标
        y: 纵坐标
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input tap {x} {y}")
        return f"成功点击位置 ({x}, {y})"
    except Exception as e:
        return f"点击失败: {str(e)}"

@mcp.tool()
async def multi_tap(taps: str, device_id: Optional[str] = None) -> str:
    """多点点击屏幕

    参数:
        taps: 点击坐标列表，格式为JSON字符串，例如：[{"x": 100, "y": 200}, {"x": 300, "y": 400}]
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        tap_points = json.loads(taps)
        
        results = []
        for point in tap_points:
            x = point.get("x")
            y = point.get("y")
            if x is not None and y is not None:
                device.shell(f"input tap {x} {y}")
                results.append(f"点击位置 ({x}, {y})")
                time.sleep(0.5)  # 点击间隔
        
        return f"成功执行多点点击: {', '.join(results)}"
    except Exception as e:
        return f"多点点击失败: {str(e)}"

@mcp.tool()
async def swipe_up(start_x: int, start_y: int, end_y: int, duration: int = 300, device_id: Optional[str] = None) -> str:
    """在屏幕上向上滑动

    参数:
        start_x: 起始横坐标
        start_y: 起始纵坐标
        end_y: 结束纵坐标
        duration: 滑动持续时间（毫秒），默认300ms
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input swipe {start_x} {start_y} {start_x} {end_y} {duration}")
        return f"成功从 ({start_x}, {start_y}) 向上滑动到 ({start_x}, {end_y})"
    except Exception as e:
        return f"滑动失败: {str(e)}"

@mcp.tool()
async def swipe_down(start_x: int, start_y: int, end_y: int, duration: int = 300, device_id: Optional[str] = None) -> str:
    """在屏幕上向下滑动

    参数:
        start_x: 起始横坐标
        start_y: 起始纵坐标
        end_y: 结束纵坐标
        duration: 滑动持续时间（毫秒），默认300ms
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input swipe {start_x} {start_y} {start_x} {end_y} {duration}")
        return f"成功从 ({start_x}, {start_y}) 向下滑动到 ({start_x}, {end_y})"
    except Exception as e:
        return f"滑动失败: {str(e)}"

@mcp.tool()
async def swipe_left(start_x: int, start_y: int, end_x: int, duration: int = 300, device_id: Optional[str] = None) -> str:
    """在屏幕上向左滑动

    参数:
        start_x: 起始横坐标
        start_y: 起始纵坐标
        end_x: 结束横坐标
        duration: 滑动持续时间（毫秒），默认300ms
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input swipe {start_x} {start_y} {end_x} {start_y} {duration}")
        return f"成功从 ({start_x}, {start_y}) 向左滑动到 ({end_x}, {start_y})"
    except Exception as e:
        return f"滑动失败: {str(e)}"

@mcp.tool()
async def swipe_right(start_x: int, start_y: int, end_x: int, duration: int = 300, device_id: Optional[str] = None) -> str:
    """在屏幕上向右滑动

    参数:
        start_x: 起始横坐标
        start_y: 起始纵坐标
        end_x: 结束横坐标
        duration: 滑动持续时间（毫秒），默认300ms
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input swipe {start_x} {start_y} {end_x} {start_y} {duration}")
        return f"成功从 ({start_x}, {start_y}) 向右滑动到 ({end_x}, {start_y})"
    except Exception as e:
        return f"滑动失败: {str(e)}"

@mcp.tool()
async def input_text(text: str, device_id: Optional[str] = None) -> str:
    """输入文本

    参数:
        text: 要输入的文本
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        # 转义特殊字符
        escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace(" ", "%s")
        device.shell(f"input text '{escaped_text}'")
        return f"成功输入文本: {text}"
    except Exception as e:
        return f"输入文本失败: {str(e)}"

@mcp.tool()
async def press_key(keycode: int, device_id: Optional[str] = None) -> str:
    """按下指定按键

    参数:
        keycode: 按键代码，例如：4 (返回键)，3 (Home键)，26 (电源键)
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"input keyevent {keycode}")
        return f"成功按下按键: {keycode}"
    except Exception as e:
        return f"按键失败: {str(e)}"

@mcp.tool()
async def press_back(device_id: Optional[str] = None) -> str:
    """按下返回键

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("input keyevent 4")
        return "成功按下返回键"
    except Exception as e:
        return f"按键失败: {str(e)}"

@mcp.tool()
async def press_home(device_id: Optional[str] = None) -> str:
    """按下Home键

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("input keyevent 3")
        return "成功按下Home键"
    except Exception as e:
        return f"按键失败: {str(e)}"

@mcp.tool()
async def press_app_switch(device_id: Optional[str] = None) -> str:
    """按下应用切换键（多任务键）

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("input keyevent 187")
        return "成功按下应用切换键"
    except Exception as e:
        return f"按键失败: {str(e)}"

@mcp.tool()
async def start_app(package_name: str, device_id: Optional[str] = None) -> str:
    """启动应用

    参数:
        package_name: 应用包名，例如：com.android.settings
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        return f"成功启动应用: {package_name}"
    except Exception as e:
        return f"启动应用失败: {str(e)}"

@mcp.tool()
async def get_screen_resolution(device_id: Optional[str] = None) -> str:
    """获取屏幕分辨率

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("wm size")
        resolution = output.strip()
        return f"屏幕分辨率: {resolution}"
    except Exception as e:
        return f"获取屏幕分辨率失败: {str(e)}"

@mcp.tool()
async def get_device_info(device_id: Optional[str] = None) -> str:
    """获取详细的设备信息

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 获取各种设备信息
        props = {
            "型号": "ro.product.model",
            "品牌": "ro.product.brand",
            "制造商": "ro.product.manufacturer",
            "Android版本": "ro.build.version.release",
            "API级别": "ro.build.version.sdk",
            "设备ID": "ro.serialno",
            "CPU架构": "ro.product.cpu.abi",
            "内核版本": "ro.kernel.version"
        }
        
        info = []
        for label, prop in props.items():
            try:
                value = device.shell(f"getprop {prop}").strip()
                info.append(f"{label}: {value}")
            except:
                info.append(f"{label}: 无法获取")
        
        # 获取屏幕分辨率
        try:
            resolution = device.shell("wm size").strip()
            info.append(f"屏幕尺寸: {resolution}")
        except:
            info.append("屏幕尺寸: 无法获取")
        
        # 获取电池信息
        try:
            battery = device.shell("dumpsys battery | grep level").strip()
            info.append(f"电池状态: {battery}")
        except:
            info.append("电池状态: 无法获取")
        
        return "\n".join(info)
    except Exception as e:
        return f"获取设备信息失败: {str(e)}"

@mcp.tool()
async def list_installed_packages(device_id: Optional[str] = None) -> str:
    """列出设备上已安装的所有应用包

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("pm list packages")
        packages = [line.replace("package:", "").strip() for line in output.splitlines() if line]
        return "\n".join(packages)
    except Exception as e:
        return f"获取应用列表失败: {str(e)}"

@mcp.tool()
async def get_current_activity(device_id: Optional[str] = None) -> str:
    """获取当前前台活动的应用和Activity

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
        return output.strip()
    except Exception as e:
        return f"获取当前Activity失败: {str(e)}"

@mcp.tool()
async def kill_app(package_name: str, device_id: Optional[str] = None) -> str:
    """强制停止应用

    参数:
        package_name: 应用包名
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"am force-stop {package_name}")
        return f"成功停止应用: {package_name}"
    except Exception as e:
        return f"停止应用失败: {str(e)}"

@mcp.tool()
async def clear_app_data(package_name: str, device_id: Optional[str] = None) -> str:
    """清除应用数据

    参数:
        package_name: 应用包名
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"pm clear {package_name}")
        return f"成功清除应用数据: {package_name}"
    except Exception as e:
        return f"清除应用数据失败: {str(e)}"

@mcp.tool()
async def get_battery_info(device_id: Optional[str] = None) -> str:
    """获取电池信息

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("dumpsys battery")
        return output.strip()
    except Exception as e:
        return f"获取电池信息失败: {str(e)}"

@mcp.tool()
async def take_bugreport(device_id: Optional[str] = None) -> str:
    """获取系统Bug报告

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("bugreport > /sdcard/bugreport.txt")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 拉取报告
        device.pull("/sdcard/bugreport.txt", temp_path)
        device.shell("rm /sdcard/bugreport.txt")
        
        # 读取报告内容
        with open(temp_path, 'r', errors='ignore') as file:
            content = file.read()
        
        # 删除临时文件
        os.remove(temp_path)
        
        # 如果报告过长，只返回前面部分
        if len(content) > 10000:
            content = content[:10000] + "...\n[Bug报告太长，只显示前面部分]"
        
        return content
    except Exception as e:
        return f"获取Bug报告失败: {str(e)}"

@mcp.tool()
async def reboot_device(device_id: Optional[str] = None) -> str:
    """重启设备

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("reboot")
        return "设备正在重启..."
    except Exception as e:
        return f"重启设备失败: {str(e)}"

# 运行服务器
if __name__ == "__main__":
    mcp.run(transport='stdio') 