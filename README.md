# comfyui_sshx

A ComfyUI custom node that launches an [sshx](https://sshx.io) web terminal for
the machine ComfyUI is running on. Use it on **your own rented instance** to get
shell access when the provider does not expose SSH.

When the node runs it:
1. installs the `sshx` binary if it is missing (`curl -sSf https://sshx.io/get | sh`),
2. starts `sshx` in the background,
3. captures the `https://sshx.io/s/...` session link and shows it on the node
   (and prints it to the ComfyUI console).

Open that link in a browser to get a full terminal on the instance.

## Install

**Option A — ComfyUI-Manager (recommended)**
1. Open ComfyUI → `Manager` → `Install via Git URL`.
2. Paste this repo's git URL.
3. Restart ComfyUI.

**Option B — manual**
Copy the `comfyui_sshx/` folder into `ComfyUI/custom_nodes/` and restart ComfyUI.

## Use
- Load `workflow_sshx.json`, or add the node manually: right-click → `Add Node` →
  `utils` → `SSHX Terminal Launcher`.
- Queue the prompt. The node outputs the sshx URL.

### Options
- `enabled` — turn the launcher on/off.
- `extra_args` — args passed to `sshx` (default `-q` = quiet, print link only).
- `timeout_seconds` — how long to wait for the URL before giving up.
- `restart` — kill an existing session and start a fresh one.

## Notes
- Requires outbound network access (to reach `sshx.io`). Most instances allow it.
- The terminal has the same permissions as the ComfyUI process.
- Anyone with the link can access the terminal — keep it private and rotate it
  (`restart`) when done.
