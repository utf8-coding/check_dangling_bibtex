#!/usr/bin/env python3
"""
检查LaTeX文件中未引用的BibTeX条目

用法:
    python check_dangling_bibtex.py document.tex references.bib
"""

import re
import sys
from pathlib import Path


def extract_citekeys_from_tex(tex_path: Path) -> tuple[set[str], set[str]]:
    """从tex文件中提取所有引用的citekey
    
    返回: (active_citekeys, commented_citekeys)
    - active_citekeys: 正常未被注释的引用（仅从非注释行提取）
    - commented_citekeys: 被注释掉的引用（整行以%开头的行中的引用）
    """
    active_citekeys: set[str] = set()
    commented_citekeys: set[str] = set()
    
    content = tex_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # 预编译正则表达式
    cite_pattern = r'\\cite(?:p|t|alp|alt)?(?:\[[^\]]*\])?\{([^}]+)\}'
    bibentry_pattern = r'\\bibentry\{([^}]+)\}'
    nocite_pattern = r'\\nocite(?:\[[^\]]*\])?\{([^}]+)\}'
    
    # 分别处理注释行和非注释行
    for line in lines:
        stripped = line.lstrip()
        is_comment_line = stripped.startswith('%')
        
        # 提取引用命令
        for pattern in [cite_pattern, bibentry_pattern, nocite_pattern]:
            matches = re.findall(pattern, line)
            for match in matches:
                for key in match.split(','):
                    key = key.strip()
                    if key:
                        if is_comment_line:
                            commented_citekeys.add(key)
                        else:
                            active_citekeys.add(key)
    
    return active_citekeys, commented_citekeys
    
    return active_citekeys, commented_citekeys


def extract_citekeys_from_bib(bib_path: Path) -> set[str]:
    """从bib文件中提取所有条目的citekey"""
    citekeys: set[str] = set()
    
    content = bib_path.read_text(encoding='utf-8')
    
    # 匹配 @entrytype{citekay, 格式
    # 支持 @article{key, @book{key, @inproceedings{key, 等
    bib_pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,'
    matches = re.findall(bib_pattern, content)
    
    for entry_type, citekey in matches:
        citekeys.add(citekey.strip())
    
    return citekeys


def find_dangling_citations(tex_path: Path, bib_path: Path) -> tuple[set[str], set[str], set[str], list[str]]:
    """找出bib中存在但tex中未引用的citekey
    
    返回: (bib_citekeys, active_citekeys, commented_citekeys, dangling)
    """
    bib_citekeys = extract_citekeys_from_bib(bib_path)
    active_citekeys, commented_citekeys = extract_citekeys_from_tex(tex_path)
    
    # 差集：bib中有但tex中没有引用的（只考虑active的引用）
    dangling = sorted(bib_citekeys - active_citekeys)
    
    return bib_citekeys, active_citekeys, commented_citekeys, dangling


def main() -> int:
    if len(sys.argv) != 3:
        print(f"用法: python {Path(sys.argv[0]).name} document.tex references.bib")
        print("\n参数:")
        print("  document.tex   - LaTeX文档文件")
        print("  references.bib - BibTeX参考文献文件")
        return 1
    
    tex_path = Path(sys.argv[1])
    bib_path = Path(sys.argv[2])
    
    if not tex_path.exists():
        print(f"错误: 文件不存在: {tex_path}")
        return 1
    
    if not bib_path.exists():
        print(f"错误: 文件不存在: {bib_path}")
        return 1
    
    bib_citekeys, active_citekeys, commented_citekeys, dangling = find_dangling_citations(tex_path, bib_path)
    
    # 输出Bib文件中的所有citekey
    print("=" * 60)
    print(f"Bib文件 ({bib_path}) 中的 citekey ({len(bib_citekeys)} 个):")
    print("-" * 60)
    for key in sorted(bib_citekeys):
        print(f"  {key}")
    
    # 输出Tex文件中引用的所有citekey
    print("\n" + "=" * 60)
    print(f"Tex文件 ({tex_path}) 中引用的 citekey ({len(active_citekeys)} 个):")
    print("-" * 60)
    for key in sorted(active_citekeys):
        print(f"  {key}")
    
    # 输出被注释掉的引用
    if commented_citekeys:
        print("\n" + "=" * 60)
        print(f"Tex文件 ({tex_path}) 中被注释的 citekey ({len(commented_citekeys)} 个):")
        print("-" * 60)
        for key in sorted(commented_citekeys):
            print(f"  {key}")
    
    # 输出未被引用的citekey
    print("\n" + "=" * 60)
    if dangling:
        print(f"未在Tex中引用的 citekey ({len(dangling)} 个):")
        print("-" * 60)
        for key in dangling:
            print(f"  {key}")
    else:
        print("没有发现悬空引用，所有bib条目都在tex中被引用。")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
