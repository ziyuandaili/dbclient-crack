# DB Tool Patcher

一款用于解除某 VSCode 数据库管理插件付费限制的工具，支持**自动扫描**所有 VSCode 系编辑器（VSCode、Cursor、Windsurf、Trae、Kiro 等各种魔改版），无需手动指定路径。

## ✨ 主要功能

1. 移除 Premium 限制标记
2. 启用所有付费功能
3. 移除连接数量限制
4. 绕过网络验证
5. 模拟付费用户状态

## 🚀 使用方式

### 方式一：Go 二进制（推荐）

前往 [Releases](../../releases) 下载对应平台的可执行文件，双击运行即可。

支持参数：
```bash
# 自动扫描并破解
./DBClientPatcher

# 指定插件目录
./DBClientPatcher -path /path/to/extension

# 还原备份
./DBClientPatcher -restore

# 强制重新破解（覆盖已破解的版本）
./DBClientPatcher -force
```

### 方式二：Python 脚本

确保已安装 Python 3，在任意位置运行：

```bash
python3 crack.py
```

脚本会自动扫描用户目录下所有编辑器的插件目录，找到目标插件并完成修补。

### 方式三：Node.js 脚本

1. 关闭编辑器
2. 运行对应平台的启动脚本：
   - Windows：双击 `run_crack.bat`
   - Linux/macOS：`chmod +x run_crack.sh && ./run_crack.sh`
3. 等待完成后重启编辑器

## 🔍 自动扫描机制

工具会自动扫描 `~/` 下所有编辑器的 `extensions` 目录，无需手动添加新编辑器的路径。无论你使用哪种 VSCode 魔改版，只要它遵循标准的 `~/.编辑器名/extensions/` 目录结构，都能被自动发现。

## ❓ 常见问题

如果修改后仍然看到限制标记，可以尝试：

1. 按 `F1` → `Developer: Reload Window` 刷新编辑器
2. 完全关闭编辑器后重新打开
3. 使用 `-force` 参数强制重新破解

## ⚠️ 免责声明

本项目仅供学习和研究目的使用，请尊重开发者的劳动成果，有条件的用户请购买正版软件。使用本工具所造成的一切后果由使用者自行承担。