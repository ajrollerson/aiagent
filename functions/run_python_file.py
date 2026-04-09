import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the specified Python file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional arguments.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))
        valid_target_file = os.path.commonpath([working_directory_abs, target_file]) == working_directory_abs

        if valid_target_file == False:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if os.path.isfile(target_file) == False:
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if target_file.endswith(".py") == False:
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]
        if args:
            command.extend(args)
        completed_process = subprocess.run(
        command, 
        cwd=working_directory_abs,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30
    )

        output_str = ""

        if completed_process.returncode != 0:
            output_str = f"Process exited with code {completed_process.returncode}"
        if completed_process.stdout == "" and completed_process.stderr == "":
            output_str += "\nNo output produced"
        if completed_process.stdout != "":
            output_str += f"STDOUT:\n{completed_process.stdout}"
        if completed_process.stderr != "":
            output_str += f"STDERR:\n{completed_process.stderr}" 

        return output_str

    except Exception as e:
        return f"Error: executing Python file: {e}"