from typing import Optional
from mcp.server.fastmcp import FastMCP
from .adb_server import get_device, mcp

@mcp.tool()
async def toggle_wifi(enable: bool, device_id: Optional[str] = None) -> str:
    """打开或关闭WiFi

    参数:
        enable: 是否启用WiFi（True为开启，False为关闭）
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        state = "enable" if enable else "disable"
        device.shell(f"svc wifi {state}")
        return f"WiFi已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作WiFi失败: {str(e)}"

@mcp.tool()
async def toggle_mobile_data(enable: bool, device_id: Optional[str] = None) -> str:
    """打开或关闭移动数据

    参数:
        enable: 是否启用移动数据（True为开启，False为关闭）
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        state = "enable" if enable else "disable"
        device.shell(f"svc data {state}")
        return f"移动数据已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作移动数据失败: {str(e)}"

@mcp.tool()
async def toggle_airplane_mode(enable: bool, device_id: Optional[str] = None) -> str:
    """打开或关闭飞行模式

    参数:
        enable: 是否启用飞行模式（True为开启，False为关闭）
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        mode = 1 if enable else 0
        device.shell(f"settings put global airplane_mode_on {mode}")
        # 广播飞行模式变化
        device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true")
        return f"飞行模式已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作飞行模式失败: {str(e)}"

@mcp.tool()
async def get_wifi_info(device_id: Optional[str] = None) -> str:
    """获取WiFi连接信息

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("dumpsys wifi | grep 'mNetworkInfo\\|SSID'")
        return output.strip()
    except Exception as e:
        return f"获取WiFi信息失败: {str(e)}"

@mcp.tool()
async def ping(host: str, count: int = 4, device_id: Optional[str] = None) -> str:
    """Ping网络主机

    参数:
        host: 要ping的主机地址
        count: ping的次数，默认4次
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell(f"ping -c {count} {host}")
        return output.strip()
    except Exception as e:
        return f"Ping失败: {str(e)}"

@mcp.tool()
async def get_ip_address(device_id: Optional[str] = None) -> str:
    """获取设备IP地址

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell("ip addr show wlan0 | grep 'inet ' | awk '{print $2}'")
        return f"设备IP地址: {output.strip()}"
    except Exception as e:
        return f"获取IP地址失败: {str(e)}" 