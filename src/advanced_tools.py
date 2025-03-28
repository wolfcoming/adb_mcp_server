from typing import Optional
import tempfile
import time
import os
import base64
from mcp.server.fastmcp import FastMCP
from .adb_server import get_device, mcp

@mcp.tool()
async def install_apk(apk_path: str, device_id: Optional[str] = None) -> str:
    """安装APK文件

    参数:
        apk_path: 本地APK文件路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.install(apk_path)
        return f"成功安装APK: {apk_path}"
    except Exception as e:
        return f"安装APK失败: {str(e)}"

@mcp.tool()
async def uninstall_app(package_name: str, device_id: Optional[str] = None) -> str:
    """卸载应用

    参数:
        package_name: 应用包名
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.uninstall(package_name)
        return f"成功卸载应用: {package_name}"
    except Exception as e:
        return f"卸载应用失败: {str(e)}"

@mcp.tool()
async def dump_ui_hierarchy(device_id: Optional[str] = None) -> str:
    """获取界面层次结构

    参数:
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("uiautomator dump /sdcard/ui_hierarchy.xml")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_file:
            temp_path = temp_file.name
            
        # 拉取文件
        device.pull("/sdcard/ui_hierarchy.xml", temp_path)
        device.shell("rm /sdcard/ui_hierarchy.xml")
        
        # 读取内容
        with open(temp_path, 'r', errors='ignore') as file:
            content = file.read()
            
        # 删除临时文件
        os.remove(temp_path)
        
        # 如果内容太长，只返回部分
        if len(content) > 10000:
            content = content[:10000] + "...\n[UI层次结构太长，只显示前面部分]"
            
        return content
    except Exception as e:
        return f"获取UI层次结构失败: {str(e)}"

@mcp.tool()
async def run_ui_test(test_steps: str, device_id: Optional[str] = None) -> str:
    """执行UI测试步骤

    参数:
        test_steps: UI测试步骤，格式为每行一个命令，支持的命令有:
                  tap x y - 点击坐标
                  swipe x1 y1 x2 y2 [duration] - 滑动
                  text "content" - 输入文本
                  wait seconds - 等待秒数
                  press keycode - 按下按键
                  home - 按Home键
                  back - 按返回键
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        results = []
        
        lines = test_steps.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            cmd = parts[0].lower()
            
            if cmd == 'tap' and len(parts) >= 3:
                x, y = int(parts[1]), int(parts[2])
                device.shell(f"input tap {x} {y}")
                results.append(f"点击 ({x}, {y})")
                
            elif cmd == 'swipe' and len(parts) >= 5:
                x1, y1, x2, y2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                duration = parts[5] if len(parts) >= 6 else "300"
                device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
                results.append(f"滑动 ({x1}, {y1}) 到 ({x2}, {y2})")
                
            elif cmd == 'text' and len(parts) >= 2:
                text = ' '.join(parts[1:])
                if text.startswith('"') and text.endswith('"'):
                    text = text[1:-1]
                escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace(" ", "%s")
                device.shell(f"input text '{escaped_text}'")
                results.append(f"输入文本: {text}")
                
            elif cmd == 'wait' and len(parts) >= 2:
                seconds = float(parts[1])
                time.sleep(seconds)
                results.append(f"等待 {seconds} 秒")
                
            elif cmd == 'press' and len(parts) >= 2:
                keycode = parts[1]
                device.shell(f"input keyevent {keycode}")
                results.append(f"按下按键 {keycode}")
                
            elif cmd == 'home':
                device.shell("input keyevent 3")
                results.append("按下Home键")
                
            elif cmd == 'back':
                device.shell("input keyevent 4")
                results.append("按下返回键")
                
            else:
                results.append(f"未识别的命令: {line}")
                
            # 每个操作后短暂等待
            time.sleep(0.5)
        
        return "执行结果:\n" + "\n".join(results)
    except Exception as e:
        return f"执行UI测试失败: {str(e)}"

@mcp.tool()
async def check_element_exists(text: str, device_id: Optional[str] = None) -> str:
    """检查界面上是否存在包含指定文本的元素

    参数:
        text: 要查找的文本内容
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell("uiautomator dump /sdcard/ui_hierarchy.xml")
        
        # 拉取文件内容
        output = device.shell("cat /sdcard/ui_hierarchy.xml")
        device.shell("rm /sdcard/ui_hierarchy.xml")
        
        # 检查文本是否存在
        if text in output:
            return f"找到包含文本 '{text}' 的元素"
        else:
            return f"未找到包含文本 '{text}' 的元素"
    except Exception as e:
        return f"检查元素失败: {str(e)}"

@mcp.tool()
async def tap_element_by_text(text: str, device_id: Optional[str] = None) -> str:
    """点击包含指定文本的UI元素

    参数:
        text: 元素包含的文本
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        # 将文本转义为shell安全
        escaped_text = text.replace("'", "\\'").replace('"', '\\"')
        
        # 尝试使用UI Automator点击元素
        cmd = f"am instrument -w -e class androidx.test.uiautomator.UiAutomator2Stub -e command 'findAndClick(\"{escaped_text}\")' androidx.test.uiautomator.v18.test/androidx.test.runner.AndroidJUnitRunner"
        
        # 更简单的方法，使用UI Automator的shell命令（可能在某些设备上不支持）
        alternative_cmd = f"uiautomator runtest UiAutomator.jar -c com.android.uiautomator.tests.UiAutomatorTests#testClickByText --e text '{escaped_text}'"
        
        # 尝试最简单的方法
        result = device.shell(f"input text '{escaped_text}'")
        if "error" in result.lower():
            # 如果失败，尝试使用content description查找
            device.shell("uiautomator dump /sdcard/ui_hierarchy.xml")
            ui_content = device.shell("cat /sdcard/ui_hierarchy.xml")
            device.shell("rm /sdcard/ui_hierarchy.xml")
            
            import re
            # 查找包含文本的元素坐标
            pattern = f'text="{re.escape(text)}"[^>]*bounds="\\[([0-9]+),([0-9]+)\\]\\[([0-9]+),([0-9]+)\\]"'
            matches = re.search(pattern, ui_content)
            
            if matches:
                x1, y1, x2, y2 = map(int, matches.groups())
                # 计算元素中心点
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                # 点击中心点
                device.shell(f"input tap {center_x} {center_y}")
                return f"已点击文本为 '{text}' 的元素，坐标: ({center_x}, {center_y})"
            else:
                return f"未找到包含文本 '{text}' 的元素"
        
        return f"已尝试点击文本为 '{text}' 的元素"
    except Exception as e:
        return f"点击文本元素失败: {str(e)}"

@mcp.tool()
async def collect_device_logs(duration: int = 10, device_id: Optional[str] = None) -> str:
    """收集设备日志

    参数:
        duration: 收集日志的时长（秒），默认10秒
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 清除旧日志
        device.shell("logcat -c")
        
        # 收集指定时长的日志
        print(f"正在收集 {duration} 秒的设备日志...")
        time.sleep(duration)
        
        # 获取日志
        logs = device.shell(f"logcat -d -v threadtime")
        
        # 如果日志太长，只返回最后部分
        if len(logs) > 10000:
            logs = "...\n[日志太长，只显示最后部分]\n" + logs[-10000:]
            
        return logs
    except Exception as e:
        return f"收集设备日志失败: {str(e)}"

@mcp.tool()
async def analyze_performance(package_name: str, duration: int = 10, device_id: Optional[str] = None) -> str:
    """分析应用性能

    参数:
        package_name: 应用包名
        duration: 分析时长（秒），默认10秒
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 启动应用
        device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        time.sleep(2)  # 等待应用启动
        
        # 收集性能数据
        print(f"正在收集 {duration} 秒的性能数据...")
        performance_data = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # 获取内存使用
            mem_info = device.shell(f"dumpsys meminfo {package_name}")
            
            # 获取CPU使用
            cpu_info = device.shell(f"top -n 1 | grep {package_name}")
            
            # 获取电池消耗
            battery_info = device.shell("dumpsys battery | grep level")
            
            performance_data.append(f"时间点: {time.time() - start_time:.2f}秒\n"
                                  f"CPU: {cpu_info.strip()}\n"
                                  f"电池: {battery_info.strip()}\n"
                                  f"内存摘要: {' '.join(mem_info.split()[:20]) if mem_info else '无法获取'}")
            
            time.sleep(1)
        
        return "性能分析结果:\n\n" + "\n\n".join(performance_data)
    except Exception as e:
        return f"分析应用性能失败: {str(e)}"

@mcp.tool()
async def take_screen_recording(duration: int = 10, device_id: Optional[str] = None) -> str:
    """录制设备屏幕视频

    参数:
        duration: 录制时长（秒），默认10秒
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 在设备上启动录制
        device.shell(f"screenrecord --time-limit {duration} /sdcard/screen_recording.mp4")
        print(f"正在录制视频，持续 {duration} 秒...")
        
        # 等待录制完成（额外多等待一秒以确保录制完成）
        time.sleep(duration + 1)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
            
        # 从设备拉取视频文件
        device.pull("/sdcard/screen_recording.mp4", temp_path)
        device.shell("rm /sdcard/screen_recording.mp4")
        
        # 转换为base64
        with open(temp_path, 'rb') as file:
            base64_data = base64.b64encode(file.read()).decode('utf-8')
            
        # 删除临时文件
        os.remove(temp_path)
        
        return f"data:video/mp4;base64,{base64_data}"
    except Exception as e:
        return f"录制屏幕视频失败: {str(e)}"

@mcp.tool()
async def enhanced_start_app(package_name: str, activity_name: Optional[str] = None, device_id: Optional[str] = None) -> str:
    """增强版应用启动功能，尝试多种方法解决权限问题
    
    参数:
        package_name: 应用包名，例如：com.android.settings
        activity_name: 活动名称，可选。如果不提供，会尝试查找启动活动或使用通用方法
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        result = ""
        success = False
        
        # 方法1: 使用monkey命令（最通用的方法）
        try:
            result += "尝试使用monkey命令启动应用...\n"
            output = device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            if "Error" not in output and "Exception" not in output:
                result += "monkey命令成功!\n"
                success = True
            else:
                result += f"monkey命令失败: {output}\n"
        except Exception as e:
            result += f"monkey命令异常: {str(e)}\n"
        
        # 如果monkey命令成功，直接返回
        if success:
            return f"成功启动应用: {package_name}\n{result}"
            
        # 方法2: 如果提供了具体activity，使用am start -n命令
        if activity_name and not success:
            try:
                result += f"尝试使用am start -n启动具体Activity: {activity_name}...\n"
                output = device.shell(f"am start -n {package_name}/{activity_name}")
                if "Error" not in output and "Exception" not in output and "Permission Denial" not in output:
                    result += "am start -n命令成功!\n"
                    success = True
                else:
                    result += f"am start -n命令失败: {output}\n"
            except Exception as e:
                result += f"am start -n命令异常: {str(e)}\n"
                
        # 方法3: 尝试查找启动Activity
        if not success:
            try:
                result += "尝试查找可能的启动Activity...\n"
                # 尝试常见的启动活动名称
                common_activities = [
                    f"{package_name}.SplashActivity",
                    f"{package_name}.MainActivity", 
                    f"{package_name}.StartActivity",
                    f"{package_name}.LauncherActivity",
                    f"{package_name}.ui.SplashActivity",
                    f"{package_name}.ui.MainActivity",
                    f"{package_name}.activity.SplashActivity",
                    f"{package_name}.activity.MainActivity"
                ]
                
                # 如果没有成功，尝试获取包信息找出导出的Activities
                output = device.shell(f"dumpsys package {package_name} | grep -A 20 'Activity Resolver Table'")
                if output:
                    result += "找到应用活动信息...\n"
                    lines = output.split('\n')
                    for line in lines:
                        if package_name in line and "filter" in line:
                            # 提取activity名称
                            parts = line.strip().split()
                            for part in parts:
                                if package_name in part and '/' in part:
                                    activity = part.split('/')[1]
                                    if activity.startswith('.'):
                                        activity = package_name + activity
                                    common_activities.append(activity)
                
                # 尝试启动找到的活动
                for activity in common_activities:
                    try:
                        output = device.shell(f"am start -n {package_name}/{activity}")
                        if "Error" not in output and "Exception" not in output and "Permission Denial" not in output:
                            result += f"成功启动活动: {activity}\n"
                            success = True
                            break
                    except:
                        continue
            except Exception as e:
                result += f"查找启动Activity异常: {str(e)}\n"
        
        # 方法4: 使用ACTION_MAIN作为替代方法
        if not success:
            try:
                result += "尝试使用ACTION_MAIN启动...\n"
                output = device.shell(f"am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {package_name}/.MainActivity")
                if "Error" not in output and "Exception" not in output and "Permission Denial" not in output:
                    result += "ACTION_MAIN命令成功!\n"
                    success = True
                else:
                    result += f"ACTION_MAIN命令失败: {output}\n"
            except Exception as e:
                result += f"ACTION_MAIN命令异常: {str(e)}\n"
        
        if success:
            return f"成功启动应用: {package_name}\n{result}"
        else:
            return f"尝试所有方法后仍无法启动应用: {package_name}\n{result}"
    except Exception as e:
        return f"启动应用失败: {str(e)}" 