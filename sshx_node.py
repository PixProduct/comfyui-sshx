import os
import re
import shutil
import subprocess
import threading
import time

_STATE = {"proc": None, "url": ""}
_LOCK = threading.Lock()


def _ensure_installed():
    """Install the sshx binary if it is not already on PATH."""
    if shutil.which("sshx"):
        return shutil.which("sshx")
    local_bin = os.path.expanduser("~/.local/bin/sshx")
    if os.path.exists(local_bin):
        return local_bin
    subprocess.run(
        "curl -sSf https://sshx.io/get | sh",
        shell=True,
        check=False,
    )
    return shutil.which("sshx") or (local_bin if os.path.exists(local_bin) else "sshx")


def _start(binary, extra_args, timeout):
    """Start sshx in the background and capture the session URL it prints."""
    cmd = [binary] + [a for a in extra_args.split() if a]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    _STATE["proc"] = proc
    url = ""
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        match = re.search(r"https://sshx\.io/\S+", line)
        if match:
            url = match.group(0).rstrip(",.")
            break
    _STATE["url"] = url

    # keep draining stdout so the process does not block on a full pipe
    def _drain():
        for _ in proc.stdout:
            pass

    threading.Thread(target=_drain, daemon=True).start()
    return url


class SSHXLauncher:
    """Launches an sshx web terminal for this ComfyUI instance."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "extra_args": ("STRING", {"default": "-q", "multiline": False}),
                "timeout_seconds": ("INT", {"default": 60, "min": 5, "max": 600}),
                "restart": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sshx_url",)
    FUNCTION = "launch"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        # always re-evaluate so re-queuing can restart / re-report
        return float(time.time())

    def launch(self, enabled, extra_args="-q", timeout_seconds=60, restart=False):
        if not enabled:
            return {"ui": {"text": ["sshx disabled"]}, "result": ("sshx disabled",)}

        with _LOCK:
            proc = _STATE.get("proc")
            alive = proc is not None and proc.poll() is None

            if alive and not restart and _STATE.get("url"):
                url = _STATE["url"]
                return {"ui": {"text": [url]}, "result": (url,)}

            if alive and restart:
                try:
                    proc.terminate()
                except Exception:
                    pass
                _STATE["proc"] = None
                _STATE["url"] = ""

            binary = _ensure_installed()
            url = _start(binary, extra_args, timeout_seconds)

        if not url:
            msg = "sshx started but no URL captured yet - check the ComfyUI console logs"
            return {"ui": {"text": [msg]}, "result": (msg,)}
        print(f"[comfyui_sshx] terminal ready: {url}", flush=True)
        return {"ui": {"text": [url]}, "result": (url,)}


NODE_CLASS_MAPPINGS = {"SSHXLauncher": SSHXLauncher}
NODE_DISPLAY_NAME_MAPPINGS = {"SSHXLauncher": "SSHX Terminal Launcher"}
