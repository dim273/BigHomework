import random

class Node:
    def __init__(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None
        self.row = None

class ColumnNode(Node):
    def __init__(self):
        super().__init__()
        self.size = 0

class DLX:
    def __init__(self, columns):
        self.root = ColumnNode()
        self.columns = [ColumnNode() for _ in range(columns)]
        prev = self.root
        for col in self.columns:
            col.left = prev
            prev.right = col
            prev = col
        self.root.left = prev
        prev.right = self.root

    def cover(self, col):
        col.right.left = col.left
        col.left.right = col.right
        node = col.down
        while node != col:
            row_node = node.right
            while row_node != node:
                row_node.down.up = row_node.up
                row_node.up.down = row_node.down
                row_node.column.size -= 1
                row_node = row_node.right
            node = node.down

    def uncover(self, col):
        node = col.up
        while node != col:
            row_node = node.left
            while row_node != node:
                row_node.down.up = row_node
                row_node.up.down = row_node
                row_node.column.size += 1
                row_node = row_node.left
            node = node.up
        col.right.left = col
        col.left.right = col

    def solve(self, max_solutions=1):
        solutions = []
        self._search(0, [], solutions, max_solutions)
        return solutions

    def _search(self, k, solution, solutions, max_solutions):
        if self.root.right == self.root:
            solutions.append([node.row for node in solution])
            return len(solutions) >= max_solutions
        col = self._select_column()
        self.cover(col)
        nodes = []
        node = col.down
        while node != col:
            nodes.append(node)
            node = node.down
        random.shuffle(nodes)
        for node in nodes:
            solution.append(node)
            row_node = node.right
            while row_node != node:
                self.cover(row_node.column)
                row_node = row_node.right
            if self._search(k + 1, solution, solutions, max_solutions):
                return True
            solution.pop()
            row_node = node.left
            while row_node != node:
                self.uncover(row_node.column)
                row_node = row_node.left
        self.uncover(col)
        return False

    def _select_column(self):
        min_size = float('inf')
        selected_col = None
        col = self.root.right
        while col != self.root:
            if col.size < min_size:
                min_size = col.size
                selected_col = col
            col = col.right
        return selected_col


def sudoku_to_dlx(grid):
    dlx = DLX(324)
    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if val != 0:
                d = val - 1
                add_row(r, c, d, dlx)
            else:
                for d in range(9):
                    add_row(r, c, d, dlx)
    return dlx


def add_row(r, c, d, dlx):
    cell = r * 9 + c
    row_con = 81 + r * 9 + d
    col_con = 162 + c * 9 + d
    box = (r // 3) * 3 + (c // 3)
    box_con = 243 + box * 9 + d
    cols = [cell, row_con, col_con, box_con]
    nodes = []
    for col_idx in cols:
        col_node = dlx.columns[col_idx]
        node = Node()
        node.column = col_node
        node.row = (r, c, d + 1)
        node.down = col_node
        node.up = col_node.up
        col_node.up.down = node
        col_node.up = node
        col_node.size += 1
        nodes.append(node)
    for i in range(4):
        nodes[i].right = nodes[(i + 1) % 4]
        nodes[i].left = nodes[(i - 1) % 4]


def generate_sudoku():
    grid = [[0] * 9 for _ in range(9)]  # 创建一个9x9的全0网格
    dlx = sudoku_to_dlx(grid)          # 将数独转换为DLX模型
    solutions = dlx.solve(max_solutions=1)  # 使用DLX求解一个解
    sudoku = [[0] * 9 for _ in range(9)]
    for node in solutions[0]:           # 将解转换为数独终盘
        r, c, d = node
        sudoku[r][c] = d
    return sudoku


def dig_holes(sudoku, holes):
    dug = [row[:] for row in sudoku]
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    removed = 0
    for r, c in positions:
        if removed >= holes:
            break
        original = dug[r][c]
        dug[r][c] = 0
        if has_unique_solution(dug):
            removed += 1
        else:
            dug[r][c] = original
    return dug


def has_unique_solution(grid):
    dlx = sudoku_to_dlx(grid)
    solutions = dlx.solve(max_solutions=2)
    return len(solutions) == 1

def generate_interactive_html(difficulty="medium", filename="sudo.html"):
    """生成可交互数独网页（带智能提示）"""

    difficulty_levels = {
        "easy": (36, 45),  # 保留36-45个数字
        "medium": (27, 35),  # 保留27-35个数字
        "hard": (17, 26)  # 保留17-26个数字
    }
    min_keep, max_keep = difficulty_levels[difficulty]
    keep = random.randint(min_keep, max_keep)

    # 1. 生成完整数独
    solution = generate_sudoku()
    # 2. 挖空生成游戏盘面（保证唯一解）
    puzzle = dig_holes(solution, 81 - keep)


    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>智能数独 · 难度: {difficulty}</title>
    <style>
        body,html {{ 
            font-family: Arial, sans-serif; 
            text-align: center; 
            height: 100%;
            margin: 0;
        }}
        .background{{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('background1.jpg');
            background-size: cover;
            background-position: center;
            filter: opacity(40%);
            z-index: -1;
        }}
        h1 {{ color: #2c3e50; }}
        .sudoku {{
            border: 3px solid #34495e;
            border-collapse: collapse;
            margin: 20px auto;
        }}
        .sudoku td {{
            width: 50px;
            height: 50px;
            border: 1px solid #bdc3c7;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
        }}
        .thick-right {{ border-right: 3px solid #34495e !important; }}
        .thick-bottom {{ border-bottom: 3px solid #34495e !important; }}
        .fixed {{ color: #2c3e50; background-color: #ecf0f1; cursor: default; }}
        .user-input {{ color: #3498db; }}
        .hint {{ color: #f39c12; background-color: #fffacd; cursor: default; }}
        .error {{ background-color: #ffdddd !important; }}
        .highlight {{ background-color: #fffacd !important; }}
        .selected {{ background-color: #d4e6f1 !important; }}
        #controls {{ margin: 15px; }}
        button {{
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
            cursor: pointer;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
        }}
        #message {{ height: 30px; color: #e74c3c; font-weight: bold; }}
        select {{
            padding: 8px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="background"></div>
    <h1>智能数独 · 难度: <span id="difficulty">{difficulty}</span></h1>
    <div id="controls">
        <button onclick="checkSolution()">检查答案</button>
        <button onclick="showSmartHint()">智能提示</button>
    </div>
    <div id="message"></div>
    <table class="sudoku" id="board"></table>

    <script>
        // 初始数据
        let initialBoard = {str(puzzle)};
        let board = JSON.parse(JSON.stringify(initialBoard)); // 用户当前填写的板
        let solution = {str(solution)};
        let difficulty = "{difficulty}";
        let hintCells = {{}}; // 记录哪些格子是通过提示填写的
        let selectedCell = null;

        // 渲染数独
        function renderBoard() {{
            const table = document.getElementById("board");
            table.innerHTML = "";

            for (let y = 0; y < 9; y++) {{
                const row = document.createElement("tr");
                for (let x = 0; x < 9; x++) {{
                    const cell = document.createElement("td");
                    cell.textContent = board[y][x] || "";

                    // 固定数字（初始提示）
                    if (initialBoard[y][x] !== 0) {{
                        cell.classList.add("fixed");
                    }} 
                    // 提示数字
                    else if (hintCells[`${{y}},${{x}}`]) {{
                        cell.classList.add("hint");
                    }}
                    // 用户填写的数字或空格
                    else {{
                        cell.addEventListener("click", () => selectCell(cell, x, y));
                        if (board[y][x] !== 0) {{
                            cell.classList.add("user-input");
                        }}
                    }}

                    // 添加粗边框
                    if (x % 3 === 2 && x < 8) cell.classList.add("thick-right");
                    if (y % 3 === 2 && y < 8) cell.classList.add("thick-bottom");

                    row.appendChild(cell);
                }}
                table.appendChild(row);
            }}
        }}
        let selectedX = null; // 新增变量存储选中的x坐标
        let selectedY = null; // 新增变量存储选中的y坐标
        // 选择格子
        function selectCell(cell, x, y) {{
            if (selectedCell) {{
                selectedCell.classList.remove("selected");
            }}

            // 选中新格子并存储坐标
            selectedCell = cell;
            selectedX = x;
            selectedY = y;
            cell.classList.add("selected");

            // 聚焦到body以便接收键盘事件
            document.body.focus();
        }}

        // 处理键盘输入
        document.body.addEventListener('keydown', function(e) {{
            if (!selectedCell || selectedX === null || selectedY === null) return;

            const cell = selectedCell;
            const x = selectedX;
            const y = selectedY;

            // 检查是否是固定或提示格子
            if (cell.classList.contains("fixed") || cell.classList.contains("hint")) {{
                return;
            }}

            // 处理数字键 (1-9)
            if (e.key >= '1' && e.key <= '9') {{
                const num = parseInt(e.key);
                cell.textContent = num;
                board[y][x] = num;  // 使用存储的坐标
                cell.classList.add("user-input");
                cell.classList.remove("error");
            }}
            // 处理删除键
            else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {{
                cell.textContent = "";
                board[y][x] = 0;  // 使用存储的坐标
                cell.classList.remove("user-input", "error");
            }}
        }});

        // 检查答案
        function checkSolution() {{
            const message = document.getElementById("message");

            // 检查是否填完
            if (board.flat().includes(0)) {{
                message.textContent = "请填完所有格子！";
                message.style.color = "#e74c3c";
                return;
            }}

            // 检查是否正确
            if (JSON.stringify(board) === JSON.stringify(solution)) {{
                message.textContent = "✓ 恭喜！答案正确！";
                message.style.color = "#27ae60";
            }} else {{
                message.textContent = "× 答案错误，请继续检查！";
                message.style.color = "#e74c3c";
                highlightErrors();
            }}
        }}

        // 高亮错误
        function highlightErrors() {{
            const cells = document.querySelectorAll("#board td");
            for (let y = 0; y < 9; y++) {{
                for (let x = 0; x < 9; x++) {{
                    if (board[y][x] !== 0 && board[y][x] !== solution[y][x]) {{
                        cells[y * 9 + x].classList.add("error");
                    }}
                }}
            }}
        }}

        // 智能提示系统
        function showSmartHint() {{
            // 找出所有可能填写的空格
            const emptyCells = [];
            for (let y = 0; y < 9; y++) {{
                for (let x = 0; x < 9; x++) {{
                    if (board[y][x] === 0 && !hintCells[`${{y}},${{x}}`]) {{
                        emptyCells.push({{ x, y }});
                    }}
                }}
            }}

            if (emptyCells.length === 0) {{
                document.getElementById("message").textContent = "已经没有空格了！";
                return;
            }}

            // 找出最容易确定的格子（唯一可能数字的格子）
            for (const cell of emptyCells) {{
                const possible = getPossibleNumbers(cell.x, cell.y);
                if (possible.length === 1) {{
                    board[cell.y][cell.x] = possible[0];
                    hintCells[`${{cell.y}},${{cell.x}}`] = true;
                    renderBoard();
                    document.getElementById("message").textContent = 
                        `智能提示：位置(${{cell.y+1}},${{cell.x+1}})只能填${{possible[0]}}`;
                    document.getElementById("message").style.color = "#27ae60";
                    return;
                }}
            }}

            // 如果没有唯一解的空格，随机选择一个提示
            const randomCell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
            const possible = getPossibleNumbers(randomCell.x, randomCell.y);
            if (possible.length > 0) {{
                board[randomCell.y][randomCell.x] = solution[randomCell.y][randomCell.x];
                hintCells[`${{randomCell.y}},${{randomCell.x}}`] = true;
                renderBoard();
                document.getElementById("message").textContent = 
                    `提示：位置(${{randomCell.y+1}},${{randomCell.x+1}})可以填${{solution[randomCell.y][randomCell.x]}}`;
                document.getElementById("message").style.color = "#f39c12";
            }} else {{
                document.getElementById("message").textContent = "无法提供提示，可能有错误！";
                document.getElementById("message").style.color = "#e74c3c";
            }}
        }}

        // 获取某个格子可能填的数字
        function getPossibleNumbers(x, y) {{
            const used = new Set();

            // 检查行
            for (let i = 0; i < 9; i++) {{
                if (board[y][i] !== 0) used.add(board[y][i]);
            }}

            // 检查列
            for (let i = 0; i < 9; i++) {{
                if (board[i][x] !== 0) used.add(board[i][x]);
            }}

            // 检查宫
            const boxX = Math.floor(x / 3) * 3;
            const boxY = Math.floor(y / 3) * 3;
            for (let i = boxY; i < boxY + 3; i++) {{
                for (let j = boxX; j < boxX + 3; j++) {{
                    if (board[i][j] !== 0) used.add(board[i][j]);
                }}
            }}

            // 返回可能数字
            return [1, 2, 3, 4, 5, 6, 7, 8, 9].filter(num => !used.has(num));
        }}

        // 新游戏
        function newGame() {{
            // 使用当前选择的难度重新加载页面
            const newDifficulty = document.getElementById("difficulty-select").value;
            window.location.href = `sudoku.html?difficulty=${{newDifficulty}}`;
        }}

        // 初始化
        renderBoard();
        // 设置body可聚焦
        document.body.setAttribute('tabindex', '0');
    </script>
</body>
</html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成游戏: {filename}")

if __name__ == "__main__":
    import time
    import sys
    start_time = time.time()

    # 难度设置
    difficulty = sys.argv[1] if len(sys.argv) > 1 else "medium"
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"
    difficulty = "easy"

    # 生成可交互网页
    generate_interactive_html(difficulty=difficulty)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")