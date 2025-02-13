#!/usr/bin/env python3
import os
import re
import openai
import subprocess

CONVERSATION_LOG = "conversation_log.md"
MASTER_SYSTEM_PROMPT = """REPLACE_ME_AT_RUNTIME"""

def parse_gpt_output(full_text):
    blocks = re.findall(r"```(.*?)```", full_text, re.DOTALL)
    changes = []
    summary_text = ""

    for block in blocks:
        lines = block.strip().split('\n', 1)
        header = lines[0].strip() if lines else ""
        body = lines[1] if len(lines) > 1 else ""

        if header.startswith("run"):
            changes.append({"type": "run", "commands": body.strip()})
        elif header.startswith("branch="):
            b_match = re.search(r'branch\s*=\s*([^\s,]+)', header)
            p_match = re.search(r'path\s*=\s*([^\s,]+)', header)
            if b_match and p_match:
                br = b_match.group(1).strip()
                pt = p_match.group(1).strip()
                changes.append({"type": "file", "branch": br, "path": pt, "content": body})

    s_match = re.search(r'summary\s*=\s*(.*)', full_text)
    if s_match:
        summary_text = s_match.group(1).strip()

    return changes, summary_text

def main():
    openai.api_key = os.getenv("OPENAI_API_KEY_DECLAN", "")
    if not openai.api_key:
        print("[orchestrator] Missing OPENAI_API_KEY_DECLAN. Exiting.")
        return

    system_prompt = os.getenv("MASTER_SYSTEM_PROMPT_OVERRIDE", MASTER_SYSTEM_PROMPT)

    logs = ""
    if os.path.exists("fail_logs.txt"):
        with open("fail_logs.txt", "r") as f:
            logs = f.read()

    convo = ""
    if os.path.exists(CONVERSATION_LOG):
        with open(CONVERSATION_LOG, "r") as f:
            convo = f.read()

    user_msg = f"[FAIL_LOGS]\n{logs}\n\n[CONVERSATION_LOG]\n{convo}"

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=1800
        )
        content = resp["choices"][0]["message"]["content"]
        print("[orchestrator] GPT response:\n", content)
    except Exception as e:
        print("[orchestrator] GPT call failed:", e)
        return

    changes, summary_text = parse_gpt_output(content)
    with open(CONVERSATION_LOG, "a") as f:
        f.write("\n\n## GPT Update\n")
        f.write(summary_text + "\n")

    for c in changes:
        if c["type"] == "file":
            branch = c["branch"]
            path = c["path"]
            text = c["content"]
            try:
                subprocess.run(["git", "checkout", branch], check=False)
                current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                                capture_output=True, text=True).stdout.strip()
                if current_branch != branch:
                    subprocess.run(["git", "checkout", "-b", branch], check=True)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as ff:
                    ff.write(text)
                subprocess.run(["git", "add", path], check=True)
                subprocess.run(["git", "commit", "-m", f"Update {path} [skip ci]"], check=True)
                subprocess.run(["git", "push", "--set-upstream", "origin", branch, "--force"], check=True)
                print(f"[orchestrator] Updated {path} on branch {branch}.")
            except Exception as e:
                print(f"[orchestrator] Error updating {path} on branch {branch}: {e}")
        elif c["type"] == "run":
            print("[orchestrator] GPT wants to run:\n", c["commands"])
            # If you trust GPT fully, uncomment to run them automatically:
            # subprocess.run(c["commands"], shell=True)

if __name__ == "__main__":
    main()
