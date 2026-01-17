import os as o
import time as t
import asyncio
from asyncio import StreamReader, StreamWriter

# -------------------------- 服务器端代码 --------------------------
def server():
    print("端口为", port)
    
    async def handle_echo(reader: StreamReader, writer: StreamWriter):
        data = await reader.read(100000000)  # 读取客户端发送的命令
        message = data.decode().strip()
        addr = writer.get_extra_info('peername')
        print(f"📥 收到来自 {addr} 的命令: {message}")
        
        try:
            # 执行系统命令（注意安全风险！）
            o.system(message)
            succ = "执行成功！"
        except Exception as e:
            succ = f"执行失败: {str(e)}"
        
        # 返回执行结果
        writer.write(succ.encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(f"📤 已向 {addr} 返回结果: {succ}")

    async def main():
        server = await asyncio.start_server(handle_echo, '127.0.0.1', port)
        addr = server.sockets[0].getsockname()
        print(f'🚀 服务器已启动，监听地址: {addr}')
        
        async with server:
            await server.serve_forever()

    asyncio.run(main())

# -------------------------- 客户端代码 --------------------------
class PersistentClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader: StreamReader | None = None
        self.writer: StreamWriter | None = None
        self._is_connected = False

    async def connect(self) -> bool:
        """建立或重新建立连接"""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self._is_connected = True
            print(f"✅ 成功连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            self._is_connected = False
            return False

    async def send_command(self, command: str) -> str | None:
        """发送命令并接收结果"""
        if not self._is_connected:
            print("⚠️ 未连接到服务器，请先连接")
            return None
        
        try:
            # 发送命令
            self.writer.write(command.encode('utf-8'))
            await self.writer.drain()
            
            # 接收结果
            data = await self.reader.read(100000000)
            return data.decode('utf-8').strip()
        except ConnectionResetError:
            print("⚠️ 服务器连接已断开")
            self._is_connected = False
            return None
        except Exception as e:
            print(f"❌ 发送命令失败: {str(e)}")
            return None

    async def close(self):
        """关闭连接"""
        if self.writer and not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()
        self._is_connected = False
        print("🛑 已断开与服务器的连接")

async def client():
    print("端口为", port)
    client = PersistentClient('127.0.0.1', port)
    
    # 尝试连接服务器
    while not await client.connect():
        print("⏳ 5秒后重试连接...")
        await asyncio.sleep(5)
    
    # 命令交互循环
    while True:
        command = input("请输入要执行的命令（输入exit退出）: ").strip()
        
        if command.lower() == "exit":
            await client.close()
            break
        
        if not command:
            print("⚠️ 命令不能为空")
            continue
        
        # 发送命令并获取结果
        result = await client.send_command(command)
        
        if result is None:
            # 尝试重连
            print("⏳ 尝试重新连接服务器...")
            if await client.connect():
                result = await client.send_command(command)
        
        if result is not None:
            print(f"📤 服务器返回结果: {result}")

# -------------------------- 主程序入口 --------------------------
if __name__ == "__main__":
    print('模式1：被操控者')
    print('模式2：操控者')
    
    while True:
        mode = input('请输入你要的模式：').strip()
        
        if mode == "被操控者":
            t.sleep(1)
            port = input("请输入要共享的端口：").strip()
            try:
                port = int(port)
                server()
            except ValueError:
                print("❌ 端口必须是数字")
            break
        
        elif mode == "操控者":
            t.sleep(1)
            port = input("请输入要链接的端口：").strip()
            try:
                port = int(port)
                asyncio.run(client())
            except ValueError:
                print("❌ 端口必须是数字")
            break
        
        else:
            print("输入无效！请输入'被操控者'或'操控者'")