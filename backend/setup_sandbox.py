"""
Setup a safe sandbox directory for terminal sessions
"""
import os
import shutil

SANDBOX_DIR = "/tmp/shellguard_sandbox"

def setup_sandbox():
    """Create a safe sandbox directory with demo files"""
    # Create sandbox if it doesn't exist
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    
    # Create some demo files and directories
    demo_structure = {
        "documents": {
            "readme.txt": "Welcome to ShellGuard Demo!\nTry some commands to see the safety features.\n",
            "test.txt": "This is a test file.\n",
        },
        "projects": {
            "demo_project": {
                "main.py": "print('Hello, ShellGuard!')\n",
                "README.md": "# Demo Project\n\nThis is a demo project.\n",
            }
        },
        "scripts": {
            "hello.sh": "#!/bin/bash\necho 'Hello from script!'\n",
        }
    }
    
    def create_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                with open(path, 'w') as f:
                    f.write(content)
                if name.endswith('.sh'):
                    os.chmod(path, 0o755)
    
    create_structure(SANDBOX_DIR, demo_structure)
    
    # Create a .shellguard_info file
    with open(os.path.join(SANDBOX_DIR, ".shellguard_info"), 'w') as f:
        f.write("This is a sandboxed demo environment.\n")
        f.write("Your commands run here safely, isolated from the main application.\n")
    
    print(f"✅ Sandbox created at: {SANDBOX_DIR}")
    return SANDBOX_DIR

if __name__ == "__main__":
    setup_sandbox()
