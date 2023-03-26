# 请求入口
from socket import *
import threading

from todo.control import routes
from todo.config import *
from todo.utils import Request, Response


def make_response(request, headers=None):
    """构造响应报文"""
    # 默认状态码为 200
    status = 200
    # 处理静态资源请求
    if request.path.startswith('/static'):
        route, methods = routes.get('/static')
    else:
        route, methods = routes.get(request.path)

    # 如果请求方法不被允许返回 405 状态码
    if request.method not in methods:
        status = 405
        data = 'Method Not Allowed'
    else:
        # 请求首页时 route 实际上就是我们在 contro.py 中定义的 index 视图函数
        data = route(request)

    # 如果返回结果为 Response 对象，直接获取响应报文
    if isinstance(data, Response):
        response_bytes = bytes(data)
    else:
        # 返回结果为字符串，需要先构造 Response 对象，然后再获取响应报文
        response = Response(data, headers=headers, status=status)
        response_bytes = bytes(response)

    return response_bytes


def process_connection(client):
    """处理客户端请求"""
    request_bytes = b''
    while True:
        try:
            chunk = client.recv(BUFFER_SIZE)
        except BlockingIOError:
            break
        request_bytes += chunk
        if len(chunk) < BUFFER_SIZE:
            break

    # 请求报文
    request_message = request_bytes.decode('utf-8')
    # 解析请求报文，构造请求对象
    request = Request(request_message)
    # 根据请求对象构造响应报文
    response_bytes = make_response(request)
    # 返回响应
    client.sendall(response_bytes)

    # 关闭连接
    client.close()


def fire_server():
    """启动服务器"""
    listen_socket = socket(AF_INET, SOCK_STREAM)
    listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 允许端口复用
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(5)
    print("___________________________________________________________")
    print("  __          ________ _______")
    print("  \\ \\        / /  ____|  _____")
    print("   \\ \\  /\\  / /| |____  |____) )")
    print("    \\ \\/  \\/ / |  ____|  ____(   __  __     __ ___")
    print("     \\  /\\  /  | |____  |____) )(__ |_ \\  /|_ |___)")
    print("      \\/  \\/   |______|_______/  __)|__ \\/ |__|")
    print()
    print("            Welcome to use the Web Server!")
    print("                     Version 1.0")
    print("                       XueFeng")
    print(f"Server fire success, Please click http://127.0.0.1:{PORT}")
    print("___________________________________________________________")

    while True:
        # 等待客户端请求
        data_socket, addr = listen_socket.accept()
        print(f'Client Type: {type(data_socket)}, Addr: {addr}')

        # 一旦接受了一个客户端的请求便创建一个线程来处理该请求
        new_thread = threading.Thread(target=process_connection, args=(data_socket,))
        new_thread.start()


if __name__ == "__main__":
    fire_server()
