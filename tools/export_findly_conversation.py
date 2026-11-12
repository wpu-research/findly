import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_THREAD = "01a1a215-26f6-7b32-a8b0-49a05d3cb88a"


def export_conversation(root, session_id=None, source=None):
    thread_id = session_id or os.environ.get("CODEX_THREAD_ID") or ORIGINAL_THREAD
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    if source is None:
        matches = sorted((codex_home / "sessions").rglob(f"*{thread_id}*.jsonl"))
        if not matches:
            raise FileNotFoundError(f"Conversation session not found: {thread_id}")
        source = matches[-1]
    else:
        source = Path(source)
    folder = root / "docs" / "conversations"
    folder.mkdir(parents=True, exist_ok=True)
    messages = []
    tool_records = []
    for line in source.open(encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "response_item":
            continue
        payload = record.get("payload", {})
        kind = payload.get("type")
        if kind == "message" and payload.get("role") in {"user", "assistant"}:
            phase = payload.get("phase")
            if payload["role"] == "assistant" and phase not in {"commentary", "final_answer", "final"}:
                continue
            text = "\n".join(
                item.get("text", "")
                for item in payload.get("content", [])
                if isinstance(item, dict) and item.get("type") in {"input_text", "output_text"}
            )
            if not text.strip():
                continue
            messages.append({
                "session_id": thread_id,
                "timestamp": record.get("timestamp"),
                "id": payload.get("id"),
                "role": payload["role"],
                "phase": phase,
                "text": text,
            })
        elif kind in {"function_call", "function_call_output", "web_search_call"}:
            allowed_fields = ("type", "name", "call_id", "arguments", "output", "status", "action")
            tool_records.append({"timestamp": record.get("timestamp"), **{key: payload[key] for key in allowed_fields if key in payload}})
    message_path = folder / f"{thread_id}.messages.jsonl"
    message_path.write_text("".join(json.dumps(message, ensure_ascii=False) + "\n" for message in messages), encoding="utf-8")
    (folder / f"{thread_id}.tools.jsonl").write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in tool_records), encoding="utf-8")
    all_messages = []
    for archived in sorted(folder.glob("*.messages.jsonl")):
        all_messages.extend(json.loads(line) for line in archived.read_text(encoding="utf-8").splitlines() if line.strip())
    all_messages.sort(key=lambda message: message.get("timestamp") or "")
    exported_at = datetime.now(timezone.utc).isoformat()
    heading = [
        "# Findly / Findy — Konuşma Kaydı",
        "",
        f"Dışa aktarma zamanı (UTC): {exported_at}",
        "",
        "Görünür kullanıcı ve asistan mesajları özgün metinleriyle kaydedilmiştir. Araç kayıtları oturum bazında ayrıca tutulur. Sistem/geliştirici talimatları ve iç analiz/akıl yürütme kayıtları dışa aktarılmaz.",
        "",
        "Eski Downloads ve PartyAi yolları konuşma tarihçesinde aynen korunur; güncel dosyalar proje içindeki assets ve references klasörlerindedir.",
        "",
    ]
    transcript = list(heading)
    prompts = ["# Görsel ve Video Promptları", "", "Konuşmada verilen özgün promptlar. 15 saniyelik erken senaryo tarihsel sürümdür; son video süre talebi en fazla 10 saniyedir.", ""]
    prompt_count = 0
    for index, message in enumerate(all_messages, start=1):
        speaker = "Kullanıcı" if message["role"] == "user" else "Asistan"
        transcript.extend([f"## {index:03d} — {speaker} — {message['timestamp']}", "", message["text"], ""])
        if message["role"] == "assistant":
            for prompt in re.findall(r"```(?:text)?\s*\n(.*?)```", message["text"], flags=re.S):
                if not prompt.lstrip().startswith("Create"):
                    continue
                prompt_count += 1
                prompts.extend([f"## Prompt {prompt_count} — {message['timestamp']}", "", "```text", prompt.strip(), "```", ""])
    (root / "docs" / "conversation.md").write_text("\n".join(transcript), encoding="utf-8")
    (root / "docs" / "prompts.md").write_text("\n".join(prompts), encoding="utf-8")
    metadata = {
        "exported_at_utc": exported_at,
        "session_id": thread_id,
        "source_log": str(source),
        "messages_in_session": len(messages),
        "messages_in_archive": len(all_messages),
        "tool_records": len(tool_records),
        "prompts": prompt_count,
        "excluded_record_types": ["reasoning", "session_meta", "turn_context", "developer", "system"],
    }
    (folder / f"{thread_id}.metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id")
    parser.add_argument("--source", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(export_conversation(ROOT, arguments.session_id, arguments.source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
