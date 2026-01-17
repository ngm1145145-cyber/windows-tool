import os as o
import time as t
i = 0
def server():
    import asyncio
    print("端口为", port)
    async def handle_echo(reader, writer):
        data = await reader.read(100000000)  # Read up to 100 bytes from the stream at once.
        message = data.decode()
        addr = writer.get_extra_info('peername')
        con = (f"{message}")
        o.system(con)
        succ="执行成功！"
        bytes_data = bytes(succ, encoding='utf-8')
        writer.write(bytes_data)  # Echo the received data back to the client.
        await writer.drain()  # Ensure the data is fully written to the socket before proceeding.
        writer.close()
    async def main():
        server = await asyncio.start_server(handle_echo, '127.0.0.1', port)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
            await server.serve_forever()
    asyncio.run(main())
def client():
    import asyncio
    print("端口为", port)
    
    # 1. 重命名内部协程函数，避免与外部函数名冲突
    async def client_coroutine():
        # 2. 将连接建立移到while循环外，保持长连接
        reader, writer = await asyncio.open_connection('127.0.0.1', port)
        print("✅ 已连接到服务器，输入'exit'退出")
        
        try:
            while True:
                message = input("请输入要执行的命令: ")
                if message == "exit":
                    break
                    
                try:
                    # 3. 发送命令
                    writer.write(message.encode())
                    await writer.drain()
                    
                    # 4. 接收结果
                    data = await reader.read(100000000)
                    print('Received from server:', data.decode())
                    
                except ConnectionResetError:
                    print("服务器连接已断开，正在尝试重连...")
                    # 5. 重连逻辑
                    reader, writer = await asyncio.open_connection('127.0.0.1', port)
                    print("重新连接成功")
                except Exception as e:
                    print(f"命令执行失败: {str(e)}")
        finally:
            # 6. 退出时关闭连接
            writer.close()
            await writer.wait_closed()
            print("已断开与服务器的连接")
    
    asyncio.run(client_coroutine())

print('模式1：被操控者')
print('模式2：操控者')
mode = input('请输入你要的模式：')
while True:
    if mode == "被操控者":
        t.sleep(1)
        port = input("请输入要共享的端口：")
        while True:
            print("等待连接中" , i * '.')
            i = i+1
            if i == 10:
                break
            server()

    elif mode == "操控者":
        t.sleep(1)
        port = input("请输入要链接的端口：")
        while True:
            print("等待连接中" , i * '.')
            i = i+1
            if i == 10:
                break
        client()
    else:
        print("输入无效！")
        mode = input()
        

