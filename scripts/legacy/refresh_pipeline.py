import subprocess
import os
import sys

def run_script(script_path):
    print(f"\n>>> Running {script_path}...")
    # Use full path to avoid issues with current working directory
    abs_path = os.path.abspath(script_path)
    result = subprocess.run([sys.executable, abs_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully completed {script_path}")
        print(result.stdout)
    else:
        print(f"Error running {script_path}")
        print(result.stdout)
        print(result.stderr)
        return False
    return True

def main():
    scripts = [
        "pipeline_0_tag_sources.py",
        "pipeline_1_build_ontology.py",
        "pipeline_2_process_frameworks.py"
    ]
    
    # Scripts are in the scripts directory, but should be run from root
    os.chdir(r"c:\SOIL HEALTH")
    
    for script in scripts:
        script_path = os.path.join("scripts", script)
        if not run_script(script_path):
            print("\nPipeline failed. Stopping.")
            break
    else:
        print("\nFull pipeline refresh completed successfully!")

if __name__ == "__main__":
    main()
