import json
import random
from multiprocessing import Pool
import webbrowser
import os
import http.server  # 导入http.server模块
import urllib.parse  # 导入urllib.parse模块

# 自定义处理程序类，继承自http.server.SimpleHTTPRequestHandler
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加 "x-content-type-options" 头部到响应中
        self.send_header('x-content-type-options', 'nosniff')
        super().end_headers()

def generate_sudoku():
    # 生成一个空的数独游戏板
    board = [[0] * 9 for _ in range(9)]
    solve_sudoku(board)
    return board

def is_valid(board, row, col, num):
    # 检查行是否合法
    if num in board[row]:
        return False

    # 检查列是否合法
    if num in [board[i][col] for i in range(9)]:
        return False

    # 检查 3x3 方格是否合法
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False

    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def create_sudoku_data(index,difficulty):
    
    sudoku_board = generate_sudoku()
    # 根据难度参数确定挖去的空格数量
    if difficulty == 30:
        num_to_remove = 30
    elif difficulty == 40:
        num_to_remove = 40
    elif difficulty == 50:
        num_to_remove = 50
    for _ in range(num_to_remove):
        row, col = random.randint(0, 8), random.randint(0, 8)
        while sudoku_board[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        sudoku_board[row][col] = 0

    return {"puzzle": sudoku_board}

def write_sudoku_data_to_json(difficulty):
    all_sudoku_data = []

    # 使用多进程并行生成9个数独游戏数据
    with Pool(processes=9) as pool:
        sudoku_data = pool.starmap(create_sudoku_data, [(i, difficulty) for i in range(1, 10)])

    # 生成不同的 JSON 文件名并保存数据到对应的文件
    for i, data in enumerate(sudoku_data):
        filename = f"sudoku_data_{difficulty}_{i + 1}.json"
        with open(filename, "w") as f:
            json.dump(data, f)
    
    # 将每个数独游戏数据添加到列表中
    for i, data in enumerate(sudoku_data):
        all_sudoku_data.append(data)

    filename = f"all_sudoku_data_{difficulty}.json"
    # 将整个列表写入一个 JSON 文件
    with open(filename, "w") as f:
        json.dump(all_sudoku_data, f)   


#def open_index_html():
    # 打开同一目录下的index.html文件
#    webbrowser.open("file://" + os.path.abspath("index.html"))

if __name__ == "__main__":
    # 调用不同难度的数独游戏生成函数
    write_sudoku_data_to_json(30)  # 生成简单难度的数据
    write_sudoku_data_to_json(40)  # 生成中等难度的数据
    write_sudoku_data_to_json(50)  # 生成困难难度的数据
        
    # 启动本地服务器，监听端口
    server_address = ('', 8000)  # 可以根据需要选择任何可用的端口
    httpd = http.server.HTTPServer(server_address, MyRequestHandler)
    
    # 打开默认浏览器并访问服务器地址
    webbrowser.open("http://localhost:8000/index.html")
    
    try:
        # 启动服务器，Ctrl+C 停止服务器
        print("本地服务器已启动，按 Ctrl+C 停止服务器")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")