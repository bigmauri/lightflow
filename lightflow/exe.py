import os
import shlex
import stat
import subprocess
import sys
import tempfile

from google.protobuf.json_format import MessageToDict, Parse


def run_temp_sh(script_text, timeout=None, env=None, pipe=None):
    """
    Create a temporary .sh script, execute it, and remove it.
    Returns: (exit_code, stdout, stderr)
    """
    # Create a named temp file — keep it (delete=False) so we can chmod & execute it
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False, encoding="utf-8")
    path = tmp.name
    try:
        # write script; ensure it has a shebang (optional but recommended)
        if not script_text.startswith("#!"):
            script_text = "#!/usr/bin/env bash\n" + script_text
        tmp.write(script_text)
        tmp.flush()
        tmp.close()  # close so the OS can execute it

        # Make the file executable by the owner
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR)

        # Execute the script directly (safer than shell=True).
        # If you need to pass arguments, use a list: [path, "arg1"]
        proc = subprocess.run(
            [path],
            text=True,
            timeout=timeout,
            env=(None if env is None else {**os.environ, **env}))
        return proc.returncode, proc.stdout, proc.stderr

    finally:
        # Always try to remove the temp file
        try:
            os.remove(path)
        except OSError:
            pass

def format_command(cmd):
    """Restituisce la stringa di comando shell completa."""
    parts = [cmd.name] + list(cmd.parameters)
    return " ".join(parts)

def run_command(cmd):
    print(f"\n> {' '.join(cmd)}")
    if "|" in cmd:
        subprocess.run(' '.join(cmd), shell=True)
    else:
        subprocess.run(cmd, shell=False)

def print_task(task, indent, dry_run=False):
    pad = " " * indent
    print(f"{pad}Task: {task.name} (type={task.type})")
    if task.priority:
        print(f"{pad}  Priority: {task.priority}")
    print(f"{pad}  Urgent: {task.is_urgent}")
    print(f"{pad}  Timestamp: {task.timestamp}")

    def shell(title, commands):
        if not commands:
            return
        print(f"{pad}  {title}:")
        for cmd in commands:
            if dry_run:
                print(f"{pad}    $ {format_command(cmd)}")
            else:
                run_command([cmd.name] + list(cmd.parameters))

    shell("\n\nBefore task", task.before_task)
    shell("\n\nCommands", task.commands)
    shell("\n\nAfter task", task.after_task)

def execute_pipeline(pipeline, dry_run):
    print(f"\nPipeline: {pipeline.name} (id={pipeline.id})")
    print(f"  OS: {pipeline.os}")
    print(f"  Environment: {pipeline.Environment.keys()[pipeline.env]}")
    print(f"  Timestamp: {pipeline.timestamp}")

    def print_task_section(title, tasks):
        if not tasks:
            return
        print(f"\n{title}:")
        for task in tasks:
            print_task(task, 4, dry_run)

    print_task_section("Before pipeline", pipeline.before_pipeline)
    print_task_section("Main tasks", pipeline.tasks)
    print_task_section("After pipeline", pipeline.after_pipeline)
