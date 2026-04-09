import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself).",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_directory_abs, directory))
        valid_target_dir = os.path.commonpath([working_directory_abs, target_dir]) == working_directory_abs

        if valid_target_dir == False:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if os.path.isdir(target_dir) == False:
            return f'Error: "{directory}" is not a directory'
        
        results = []
        for file in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file)
            results.append(f"- {os.path.basename(file_path)}: file_size={os.path.getsize(file_path)}, is_dir={os.path.isdir(file_path)}")
        return "\n".join(results)
    
    except Exception as e:
        return f"Error: {e}"



