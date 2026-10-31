# -*- coding: utf-8 -*-
"""门户 meta description 的**唯一生成口径**。

门户 index.html 是手写 HTML，但其中的学科名与题量必须来自 subjects/registry.json，
否则加学科/改题量后文案会悄悄过期——2026-10-31 实证：机器学习与数据可视化早已上线，
meta description 仍写着「接计划接入」，线上文案对外是错的。

本模块只做一件事：由 registry 算出这段文案。
build_all.py 负责把结果写回 index.html，validate_platform.py 负责核对，
两边共用同一函数——不会各写一份而再次漂移（D4 口径单一事实源的同一条纪律）。
"""
import re

# 只匹配 <meta name="description" content="..."> 这一种写法；
# 顺序固定，与模板里手写的一致。
META_RE = re.compile(r'(<meta\s+name="description"\s+content=")([^"]*)(">)')


def describe(subjects):
    """registry.json 的 subjects 列表 → meta description 文案。

    学科按题量降序排列：门户首屏给最大的一门，读者先看到平台的主体量。
    题量与总数全部来自 registry，**不在这里硬编码任何数字**。
    """
    if not subjects:
        raise ValueError("registry 里没有学科，无法生成门户文案")
    ordered = sorted(subjects, key=lambda s: (-int(s.get("total") or 0), s.get("name") or ""))
    parts = ["%s %d 题" % (s["name"], s["total"]) for s in ordered]
    total = sum(int(s.get("total") or 0) for s in ordered)
    return ("多学科大学课程刷题平台：%s，共 %d 题，全部上线。"
            "逐题解析与考点出处；客观题自动判分，主观题按采分点自评；"
            "进度只存在本机浏览器，可安装、可离线。"
            % ("、".join(parts), total))


def read_meta(html):
    """从 HTML 里取出当前 meta description；没有则返回 None。"""
    m = META_RE.search(html)
    return m.group(2) if m else None


def apply_meta(html, desc):
    """把 desc 写进 HTML 的 meta description，返回新 HTML。

    找不到唯一的 meta 标签时抛错——静默跳过等于让漂移继续潜伏。
    """
    new, n = META_RE.subn(lambda m: m.group(1) + desc + m.group(3), html, count=1)
    if n != 1:
        raise ValueError('index.html 里找不到 <meta name="description">（模板被改坏了？）')
    return new
