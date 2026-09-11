#!/usr/bin/env python3
"""Build the distributable VSC catalog from skill frontmatter (maintainer tool)."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("目录构建需要 PyYAML；请在维护环境安装 tools/requirements.txt。")

ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = {"prompt", "image", "video", "workflow", "archive"}


def build_catalog(root: Path) -> dict:
    skills = []
    for path in sorted(root.glob("*/SKILL.md")):
        if path.parent.name == "vsc":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not match:
            raise ValueError(f"{path}: 缺少 YAML frontmatter")
        front = yaml.safe_load(match[1])
        if not isinstance(front, dict):
            raise ValueError(f"{path}: frontmatter 必须为映射")
        name = front.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or name != path.parent.name:
            raise ValueError(f"{path}: name 必须为目录名且使用小写字母、数字和连字符")
        meta = front.get("metadata", {})
        if not isinstance(meta, dict):
            raise ValueError(f"{path}: metadata 必须为映射")
        fields = {"description": front.get("description"),
                  "category": meta.get("vsc-category"),
                  "deliverables": meta.get("vsc-deliverables"),
                  "distinction": meta.get("vsc-distinction")}
        for key, value in fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{path}: 缺少或无效的路由字段 {key}")
        outputs = [value.strip() for value in fields["deliverables"].split(",")]
        if not set(outputs) <= DELIVERABLES or len(set(outputs)) != len(outputs):
            raise ValueError(f"{path}: 无效或重复的交付类型 {outputs}")
        skills.append({"name": name, **fields, "deliverables": outputs,
                       "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    if not skills:
        raise ValueError("没有发现可登记的 VSC 技能")
    return {"schema_version": 1, "skills": skills}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="仅检查已提交目录是否与技能一致")
    args = parser.parse_args()
    target = ROOT / "vsc" / "references" / "catalog.json"
    try:
        content = json.dumps(build_catalog(ROOT), ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                print("VSC 目录已过期；运行 python3 tools/build_vsc_catalog.py 后提交更新。", file=sys.stderr)
                return 1
            print("VSC 目录与全部技能元数据一致。")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            print(f"已生成 {target.relative_to(ROOT)}")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
