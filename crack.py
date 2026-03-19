#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Client 优化版解锁脚本
特点：
1. 自动搜索 VSCode 插件目录
2. 不依赖特定文件名 Hash，支持多版本
3. 移除无效的 Localhost 重定向，专注于逻辑覆盖
"""

import os
import re
import sys
import shutil
from pathlib import Path

# 配置部分
TARGET_EXTENSION_NAME = "cweijan.vscode-"  # 插件ID部分匹配
MOCK_USER_DATA = """{
    id: "cracked_by_script",
    email: "vip@cracked.com",
    username: "VIP_User",
    expireTime: 4102444800000,
    isPremium: true,
    license: "unlimited"
}"""

class PatchManager:
    def __init__(self):
        self.extension_dirs = self._find_extension_dirs()
        self.extension_dir = None # current working target
        
    # 明确排除的非编辑器隐藏目录（加速扫描、避免误报）
    EXCLUDE_DIRS = {
        '.npm', '.config', '.cache', '.local', '.ssh', '.git', '.gitconfig',
        '.docker', '.cargo', '.rustup', '.nvm', '.pyenv', '.volta',
        '.rbenv', '.gem', '.gradle', '.m2', '.pub-cache', '.cocoapods',
        '.Trash', '.bash_sessions', '.zsh_sessions', '.oh-my-zsh',
        '.gnupg', '.cups', '.oracle_jre_usage', '.DS_Store',
        '.CFUserTextEncoding', '.lesshst', '.node_repl_history',
    }

    def _find_extension_dirs(self):
        """自动扫描用户 home 目录下所有 VSCode 系编辑器的插件目录"""
        home = Path.home()
        
        print("正在自动扫描所有 VSCode 系编辑器的插件目录...")
        found_dirs = []
        found_editors = set()
        
        try:
            entries = sorted(home.iterdir())
        except PermissionError:
            entries = []
        
        for entry in entries:
            # 只关注隐藏目录
            if not entry.name.startswith('.') or not entry.is_dir():
                continue
            # 跳过已知的非编辑器目录
            if entry.name in self.EXCLUDE_DIRS:
                continue
            
            # 检查 extensions 子目录
            ext_path = entry / "extensions"
            if not ext_path.exists() or not ext_path.is_dir():
                continue
            
            # 在 extensions 目录中查找目标插件
            try:
                for d in ext_path.iterdir():
                    if d.is_dir() and d.name.startswith(TARGET_EXTENSION_NAME):
                        editor_name = entry.name.lstrip('.')
                        print(f"   => 发现目标 [{editor_name}]: {d}")
                        found_dirs.append(d)
                        found_editors.add(editor_name)
            except PermissionError:
                continue
        
        # 如果自动查找失败，尝试使用当前目录
        if not found_dirs:
            current_dir = Path(os.getcwd())
            if (current_dir / "package.json").exists() and (current_dir / "out").exists():
                print(f"   => 使用当前目录: {current_dir}")
                found_dirs.append(current_dir)
        
        if not found_dirs:
            print(f"❌ 未找到任何插件目录: {TARGET_EXTENSION_NAME}")
            print("请确认插件已安装，或将脚本放置在插件根目录下运行。")
            sys.exit(1)
            
        editors_str = ", ".join(sorted(found_editors)) if found_editors else "当前目录"
        print(f"✅ 共找到 {len(found_dirs)} 个安装位置 (编辑器: {editors_str})")
        return found_dirs

    def backup_file(self, file_path: Path):
        """创建备份，如果已存在备份则跳过"""
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        if not backup_path.exists():
            try:
                shutil.copy2(file_path, backup_path)
                print(f"   已备份: {file_path.name}")
            except Exception as e:
                print(f"   ⚠️ 备份失败: {e}")

    def patch_content(self, content, rules):
        """应用一系列正则替换规则"""
        modified_content = content
        count = 0
        for pattern, replacement, desc in rules:
            if re.search(pattern, modified_content):
                modified_content = re.sub(pattern, replacement, modified_content)
                count += 1
                # print(f"      应用规则: {desc}") 
        return modified_content, count

    def process_extension_js(self):
        """处理主进程文件 extension.js"""
        file_path = self.extension_dir / "out" / "extension.js"
        if not file_path.exists():
            print("⚠️ 未找到 out/extension.js，跳过后端补丁")
            return

        print(f"正在处理: {file_path.name}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.backup_file(file_path)
            
            rules = [
                # 1. 强制静态方法返回 True
                (r'static\s+isPremium\s*\(\s*\)\s*\{[\s\S]*?\}', 'static isPremium() { return true; }', "isPremium = true"),
                (r'static\s+isPay\s*\([^)]*\)\s*\{[\s\S]*?\}', 'static isPay(e) { return true; }', "isPay = true"),
                (r'static\s+isExpire\s*\([^)]*\)\s*\{[\s\S]*?\}', 'static isExpire(e) { return false; }', "isExpire = false"),
                
                # 2. 注入模拟用户
                (r'static\s+getUser\s*\(\s*\)\s*\{[\s\S]*?\}', f'static getUser() {{ return {MOCK_USER_DATA}; }}', "Mock User"),
                
                # 3. 绕过网络验证 (不修改 URL，直接修改调用结果)
                # 查找类似 checkLicense() { ... } 的异步函数并短路
                (r'async\s+checkLicense\s*\([^)]*\)\s*\{[\s\S]*?\}', 'async checkLicense() { return true; }', "Bypass checkLicense"),
                (r'async\s+verifyLicense\s*\([^)]*\)\s*\{[\s\S]*?\}', 'async verifyLicense() { return true; }', "Bypass verifyLicense"),
            ]
            
            new_content, count = self.patch_content(content, rules)
            
            if count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   ✅ 成功应用 {count} 处修改")
            else:
                print("   ⚠️ 未找到匹配特征，可能已修改或版本不支持")
                
        except Exception as e:
            print(f"   ❌ 处理出错: {e}")

    def process_webview_assets(self):
        """处理 Webview 资源文件"""
        assets_dir = self.extension_dir / "out" / "webview" / "assets"
        if not assets_dir.exists():
            print("⚠️ 未找到 assets 目录，跳过前端补丁")
            return

        print(f"正在扫描 assets 目录 ({len(list(assets_dir.glob('*.js')))} 个 JS 文件)...")
        
        # 通用规则，应用于所有 JS 文件
        common_rules = [
            # 强制前端判断为已付费
            (r'(!|\!)([a-zA-Z0-9_]+)\.isPay', 'false', "Force !isPay -> false"), 
            (r'([a-zA-Z0-9_]+)\.isPay', 'true', "Force isPay -> true"),
            # 移除连接限制文字
            (r'Database 5/3', 'Database ∞', "Remove DB limit text"),
            (r'Other 3/3', 'Other ∞', "Remove Other limit text"),
            # 隐藏 Premium 徽章 (通过修改 hidden 属性或 value)
            (r'value:(["\'])Premium Only\1', 'value:"",hidden:true', "Hide Premium Label 1"),
            (r'value=(["\'])Premium Only\1', 'value="",hidden=true', "Hide Premium Label 2"),
        ]

        # 特征规则：根据文件内容特征来决定是否应用特定补丁，而不是根据文件名
        specific_rules = [
            {
                "signature": "pay.connectNotice", # 包含这个字符串的文件通常是连接管理页面
                "rules": [
                    (r'innerHTML:.\.\$t\(`pay\.connectNotice`\)', 'innerHTML:""', "Clear connect notice"),
                ]
            },
            {
                "signature": "pricing", # 可能涉及价格显示的逻辑
                "rules": [
                    (r'"pricing"\s*:\s*"Trial"', '"pricing":"Free"', "Trial -> Free"),
                ]
            }
        ]

        patched_count = 0
        for js_file in assets_dir.glob('*.js'):
            if js_file.name.endswith('.bak'): continue
            
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_len = len(content)
                new_content = content
                
                # 1. 应用通用规则
                new_content, c_count = self.patch_content(new_content, common_rules)
                
                # 2. 应用基于特征的规则
                for spec in specific_rules:
                    if spec["signature"] in new_content:
                        new_content, s_count = self.patch_content(new_content, spec["rules"])
                        c_count += s_count

                if len(new_content) != original_len or c_count > 0:
                    self.backup_file(js_file)
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"   ✅ 已修补: {js_file.name}")
                    patched_count += 1
                    
            except Exception as e:
                print(f"   ❌ 处理 {js_file.name} 出错: {e}")
        
        print(f"前端资源处理完成，共修改 {patched_count} 个文件")

    def process_package_json(self):
        """修改 package.json"""
        pkg_path = self.extension_dir / "package.json"
        if not pkg_path.exists(): return
        
        print("正在检查 package.json...")
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '"pricing": "Trial"' in content:
                self.backup_file(pkg_path)
                content = content.replace('"pricing": "Trial"', '"pricing": "Free"')
                with open(pkg_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("   ✅ 已修改 pricing 模式")
            else:
                print("   无需修改或未找到 pricing 字段")
        except Exception as e:
            print(f"   ❌ 读取 package.json 失败: {e}")

    def run(self):
        print("🚀 开始执行 Database Client 解锁脚本 (优化版)")
        print("-" * 50)
        
        for idx, target in enumerate(self.extension_dirs, 1):
            self.extension_dir = target
            print(f"\n[{idx}/{len(self.extension_dirs)}] 正在处理: {target}")
            print("-" * 30)
            self.process_extension_js()
            self.process_webview_assets()
            self.process_package_json()
            
        print("-" * 50)
        print("🎉 所有操作完成！请重启对应的编辑器以生效。")
        print("💡 提示: 如果之前打开过 Database Client，请按 F1 -> 'Developer: Reload Window' 刷新。")

if __name__ == '__main__':
    # 检查权限
    try:
        PatchManager().run()
    except PermissionError:
        print("\n❌ 错误: 权限不足。")
        print("请使用管理员权限 (sudo/Administrator) 运行此脚本。")
