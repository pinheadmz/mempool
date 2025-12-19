#!/usr/bin/env python3

# Add to /root/signet-wallet-challenge/datadir/node0/bitcoin.conf
#
# blocknotify=python /root/mempool/docker/opreturn/opreturn.py %s

from subprocess import run
from pathlib import Path
import json
import sys

HTML_FILE = Path(__file__).resolve().parent / "opreturn.html"
MARKER = "<!-- INSERT_ENTRIES_HERE -->"

def insert_entry(html_snippet: str):
    content = HTML_FILE.read_text(encoding="utf-8")
    updated = content.replace(
        MARKER,
        html_snippet + "\n" + MARKER,
        1
    )
    HTML_FILE.write_text(updated, encoding="utf-8")

def bcli(cmd: str):
    res = run(
            ["/root/bitcoin/build/bin/bitcoin-cli", "-datadir=/root/signet-wallet-project/datadir/node0"] + cmd.split(" "),
            capture_output=True,
            encoding="utf-8")
    if res.returncode == 0:
        return res.stdout.strip()
    else:
        raise Exception(res.stderr.strip())

block_hash = sys.argv[1]
block = json.loads(bcli(f"getblock {block_hash} 2"))

for tx in block["tx"][1:]:
    for out in tx["vout"]:
        asm = out["scriptPubKey"]["asm"]
        if "OP_RETURN" in asm:
            txid = tx["txid"]
            href = f"/tx/{txid}"
            text = ""
            words = asm.split(" ")
            for word in words[1:]:
                text += bytes.fromhex(word).decode("utf-8", errors="replace")

            entry_html = f"""
                <div class="entry">
                    <a class="txid" href="{href}" target="_blank" rel="noopener">
                        {txid}
                    </a>
                    <div class="opreturn">{text}</div>
                </div>
            """
            insert_entry(entry_html)
