import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_file = (
        os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    )
    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    if target_file[-3:] != ".py":
        return f'Error: "{file_path}" is not a Python file'

    command = ["python", target_file]
    if args := None:
        command.extend(args)

    try:
        output_string = ""
        output = subprocess.run(
            command, cwd=working_directory, capture_output=True, text=True, timeout=30
        )
        if output.returncode != 0:
            output_string += f"Process exited with code {output.returncode} "

        if output.stdout is None and output.stderr is None:
            output_string += "No output produced"
        else:
            output_string += f"STDOUT: {output.stdout}STDERR: {output.stderr}"

        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"
