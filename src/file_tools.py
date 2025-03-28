from typing import Optional
import os
import tempfile
import base64
from mcp.server.fastmcp import FastMCP
from .adb_server import get_device, mcp

@mcp.tool()
async def list_files(dir_path: str = "/sdcard", device_id: Optional[str] = None) -> str:
    """列出指定目录的文件和子目录

    参数:
        dir_path: 要列出内容的目录路径，默认为/sdcard
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell(f"ls -la {dir_path}")
        return output.strip()
    except Exception as e:
        return f"列出文件失败: {str(e)}"

@mcp.tool()
async def push_file(local_path: str, device_path: str, device_id: Optional[str] = None) -> str:
    """将文件推送到设备

    参数:
        local_path: 本地文件路径
        device_path: 设备上的目标路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.push(local_path, device_path)
        return f"成功将文件 {local_path} 推送到设备 {device_path}"
    except Exception as e:
        return f"推送文件失败: {str(e)}"

@mcp.tool()
async def pull_file(device_path: str, local_path: str, device_id: Optional[str] = None) -> str:
    """从设备拉取文件

    参数:
        device_path: 设备上的文件路径
        local_path: 本地保存路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.pull(device_path, local_path)
        return f"成功将设备上的文件 {device_path} 拉取到本地 {local_path}"
    except Exception as e:
        return f"拉取文件失败: {str(e)}"

@mcp.tool()
async def read_text_file(device_path: str, device_id: Optional[str] = None) -> str:
    """读取设备上的文本文件

    参数:
        device_path: 设备上的文件路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        output = device.shell(f"cat {device_path}")
        
        if len(output) > 10000:
            output = output[:10000] + "...\n[文件太长，只显示前面部分]"
            
        return output
    except Exception as e:
        return f"读取文件失败: {str(e)}"

@mcp.tool()
async def download_file(device_path: str, device_id: Optional[str] = None) -> str:
    """下载设备上的文件并转换为base64

    参数:
        device_path: 设备上的文件路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 获取文件扩展名
        _, ext = os.path.splitext(device_path)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_path = temp_file.name
            
        # 拉取文件
        device.pull(device_path, temp_path)
        
        # 将文件转换为base64
        with open(temp_path, 'rb') as file:
            base64_data = base64.b64encode(file.read()).decode('utf-8')
            
        # 删除临时文件
        os.remove(temp_path)
        
        # 根据文件类型设置MIME类型
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.txt': 'text/plain'
        }
        
        mime_type = mime_types.get(ext.lower(), 'application/octet-stream')
        
        return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        return f"下载文件失败: {str(e)}"

@mcp.tool()
async def write_text_file(device_path: str, content: str, device_id: Optional[str] = None) -> str:
    """在设备上创建或覆盖文本文件

    参数:
        device_path: 设备上的文件路径
        content: 要写入的文本内容
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
            
        # 推送到设备
        device.push(temp_path, device_path)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return f"成功将内容写入设备文件: {device_path}"
    except Exception as e:
        return f"写入文件失败: {str(e)}"

@mcp.tool()
async def delete_file(device_path: str, device_id: Optional[str] = None) -> str:
    """删除设备上的文件

    参数:
        device_path: 要删除的文件路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"rm {device_path}")
        return f"成功删除文件: {device_path}"
    except Exception as e:
        return f"删除文件失败: {str(e)}"

@mcp.tool()
async def make_directory(device_path: str, device_id: Optional[str] = None) -> str:
    """在设备上创建目录

    参数:
        device_path: 要创建的目录路径
        device_id: 设备ID（可选，如果未提供则使用第一个可用设备）
    """
    try:
        device = get_device(device_id)
        device.shell(f"mkdir -p {device_path}")
        return f"成功创建目录: {device_path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}" 