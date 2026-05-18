import os
import re
import subprocess
import sys
from getpass import getpass
from pathlib import Path


def sanitize_stem(name):
    cleaned = re.sub(r"[^\w\-]+", "_", name, flags=re.U).strip("_")
    return cleaned or "paper"


def parse_path_input(raw):
    text = raw.strip().strip('"').strip("'")
    if not text:
        return None
    return Path(text).expanduser().resolve()


def parse_output_path(raw, repo_root):
    text = raw.strip().strip('"').strip("'")
    if not text:
        return None
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    else:
        path = path.resolve()
    return path


def prompt_choice(question, options):
    print(question)
    for key, label in options:
        print(f"  {key}) {label}")
    while True:
        value = input("请输入选项编号: ").strip()
        valid = {k for k, _ in options}
        if value in valid:
            return value
        print("输入无效，请重新输入。")


def prompt_yes_no(question, default=True):
    tip = "Y/n" if default else "y/N"
    while True:
        value = input(f"{question} [{tip}]: ").strip().lower()
        if not value:
            return default
        if value in ("y", "yes", "1"):
            return True
        if value in ("n", "no", "0"):
            return False
        print("请输入 y 或 n。")


def prompt_text(question, default=None, required=False):
    while True:
        if default is None:
            value = input(f"{question}: ").strip()
        else:
            value = input(f"{question} [{default}]: ").strip()
            if not value:
                value = default
        if value or not required:
            return value
        print("该项不能为空，请重新输入。")


def check_env_vars(names):
    missing = [name for name in names if not str(os.getenv(name, "")).strip()]
    if not missing:
        return True
    print("\n检测到缺少环境变量：")
    for name in missing:
        print(f"- {name}")
    print("\n请先在 PowerShell 设置，例如：")
    for name in missing:
        print(f'$env:{name}="你的值"')
    return False


def configure_ai_env():
    print("\n=== AI 环境配置 ===")
    print("回车可沿用当前值。")

    current_provider = os.getenv("AI_PROVIDER", "deepseek").strip() or "deepseek"
    provider = prompt_text("AI_PROVIDER（openai/deepseek）", default=current_provider, required=True).strip().lower()

    api_key = getpass("请输入 AI_API_KEY（输入时不显示）: ").strip()
    if not api_key:
        raise RuntimeError("AI_API_KEY 不能为空。")

    model_default = os.getenv(
        "AI_MODEL",
        "deepseek-v4-pro" if provider == "deepseek" else "gpt-4o-mini",
    ).strip() or ("deepseek-v4-pro" if provider == "deepseek" else "gpt-4o-mini")
    model = prompt_text("AI_MODEL", default=model_default, required=True).strip()

    if provider == "deepseek":
        base_default = os.getenv("AI_BASE_URL", "https://api.deepseek.com").strip()
    elif provider == "openai":
        base_default = os.getenv("AI_BASE_URL", "https://api.openai.com").strip()
    else:
        base_default = os.getenv("AI_BASE_URL", "").strip()
    base_url = prompt_text("AI_BASE_URL（可留空）", default=base_default).strip()

    os.environ["AI_PROVIDER"] = provider
    os.environ["AI_API_KEY"] = api_key
    os.environ["AI_MODEL"] = model
    if base_url:
        os.environ["AI_BASE_URL"] = base_url
    elif "AI_BASE_URL" in os.environ:
        del os.environ["AI_BASE_URL"]

    print("AI 环境已就绪。")


def configure_zotero_env():
    print("\n=== Zotero 环境配置 ===")
    print("回车可沿用当前值。")

    user_id_default = os.getenv("ZOTERO_USER_ID", "").strip()
    user_id = prompt_text("ZOTERO_USER_ID", default=user_id_default or None, required=True).strip()

    api_key = getpass("请输入 ZOTERO_API_KEY（输入时不显示）: ").strip()
    if not api_key:
        raise RuntimeError("ZOTERO_API_KEY 不能为空。")

    library_default = os.getenv("ZOTERO_LIBRARY_TYPE", "user").strip().lower() or "user"
    while True:
        library_type = prompt_text("ZOTERO_LIBRARY_TYPE（user/group）", default=library_default, required=True).strip().lower()
        if library_type in ("user", "group"):
            break
        print("仅支持 user 或 group。")

    os.environ["ZOTERO_USER_ID"] = user_id
    os.environ["ZOTERO_API_KEY"] = api_key
    os.environ["ZOTERO_LIBRARY_TYPE"] = library_type

    print("Zotero 环境已就绪。")


def run_command(cmd, cwd):
    print("\n>>> 运行命令", flush=True)
    print(" ".join(f'"{part}"' if " " in part else part for part in cmd), flush=True)
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败，退出码: {result.returncode}")


def build_pdf_flow(repo_root, use_ai):
    pdf_raw = prompt_text("请输入本地 PDF 路径", required=True)
    pdf_path = parse_path_input(pdf_raw)
    if pdf_path is None or not pdf_path.exists():
        raise RuntimeError(f"PDF 不存在: {pdf_path}")

    default_json = repo_root / "input" / f"{sanitize_stem(pdf_path.stem)}.json"
    output_raw = prompt_text("JSON 输出路径（可留空使用默认）")
    output_path = parse_output_path(output_raw, repo_root) or default_json

    if use_ai and not check_env_vars(["AI_API_KEY"]):
        raise RuntimeError("AI 环境变量未配置完成。")
        fill_mode = choose_fill_mode()

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "pdf_to_json.py"),
        str(pdf_path),
        "--output",
        str(output_path),
    ]
    if use_ai:
        cmd.extend(["--ai-summary", "--ai-fill-mode", "all", "--ai-overwrite", "--ai-all-fields"])

    return {
        "step_commands": [cmd],
        "json_path": output_path,
    }


def build_zotero_flow(repo_root, use_ai):
    configure_zotero_env()

    item_key = prompt_text("请输入 Zotero item key（例如 7ERPHPWY）", required=True).strip()
    include_annotations = prompt_yes_no("是否拉取批注", default=True)
    extract_image = prompt_yes_no("是否抽取主图（framework image）", default=False)
    pdf_path = None
    max_pages = 8

    if extract_image:
        pdf_raw = prompt_text("请输入本地 PDF 路径（抽图必填）", required=True)
        pdf_path = parse_path_input(pdf_raw)
        if pdf_path is None or not pdf_path.exists():
            raise RuntimeError(f"PDF 不存在: {pdf_path}")
        max_pages_text = prompt_text("抽图最多扫描前几页", default="8")
        try:
            max_pages = max(1, int(max_pages_text))
        except ValueError as exc:
            raise RuntimeError("页数必须是整数。") from exc
    elif use_ai and prompt_yes_no("是否提供本地 PDF 给 AI 增强回填（推荐）", default=True):
        pdf_raw = prompt_text("请输入本地 PDF 路径（用于 AI 回填）", required=True)
        pdf_path = parse_path_input(pdf_raw)
        if pdf_path is None or not pdf_path.exists():
            raise RuntimeError(f"PDF 不存在: {pdf_path}")

    default_json = repo_root / "input" / f"{sanitize_stem(item_key)}.json"
    output_raw = prompt_text("JSON 输出路径（可留空使用默认）")
    output_path = parse_output_path(output_raw, repo_root) or default_json

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "zotero_to_json.py"),
        "--item-key",
        item_key,
        "--output",
        str(output_path),
    ]
    if include_annotations:
        cmd.append("--include-annotations")
    if extract_image:
        cmd.extend(
            [
                "--extract-framework-image",
                "--pdf-path",
                str(pdf_path),
                "--max-figure-pages",
                str(max_pages),
            ]
        )

    ai_cmd = None
    final_json = output_path
    if use_ai:
        if not check_env_vars(["AI_API_KEY"]):
            raise RuntimeError("AI 环境变量未配置完成。")
        ai_cmd = [
            sys.executable,
            str(repo_root / "scripts" / "ai_enrich_json.py"),
            str(output_path),
            "--fill-mode",
            "all",
            "--overwrite",
            "--all-fields",
        ]
        if pdf_path is not None:
            ai_cmd.extend(["--pdf-path", str(pdf_path)])
        final_json = output_path.with_name(output_path.stem + "_enriched.json")

    commands = [cmd]
    if ai_cmd:
        commands.append(ai_cmd)

    return {
        "step_commands": commands,
        "json_path": final_json,
    }


def main():
    repo_root = Path(__file__).resolve().parent.parent
    print("=== Paper Reading Workflow 一条龙 ===")
    use_ai_first = prompt_yes_no("第一步：这次要不要使用 AI", default=False)
    if use_ai_first:
        configure_ai_env()

    source_choice = prompt_choice(
        "请选择起点",
        [("1", "从本地 PDF 开始"), ("2", "从 Zotero item key 开始")],
    )

    if source_choice == "1":
        flow = build_pdf_flow(repo_root, use_ai_first)
    else:
        flow = build_zotero_flow(repo_root, use_ai_first)

    run_md = prompt_yes_no("最后是否自动生成 Markdown", default=True)

    print("\n将执行以下步骤：")
    step_idx = 1
    for cmd in flow["step_commands"]:
        print(f"{step_idx}. " + " ".join(f'"{part}"' if " " in part else part for part in cmd))
        step_idx += 1
    if run_md:
        md_preview = [
            sys.executable,
            str(repo_root / "scripts" / "generate_note.py"),
            str(flow["json_path"]),
        ]
        print(f"{step_idx}. " + " ".join(f'"{part}"' if " " in part else part for part in md_preview))

    if not prompt_yes_no("确认开始执行", default=True):
        print("已取消执行。")
        return

    for cmd in flow["step_commands"]:
        run_command(cmd, repo_root)

    md_output = None
    if run_md:
        md_cmd = [
            sys.executable,
            str(repo_root / "scripts" / "generate_note.py"),
            str(flow["json_path"]),
        ]
        run_command(md_cmd, repo_root)
        md_output = repo_root / "output"

    print("\n=== 执行完成 ===")
    print(f"JSON: {flow['json_path']}")
    if md_output:
        print(f"Markdown 输出目录: {md_output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n失败: {e}")
        sys.exit(1)
