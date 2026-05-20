import subprocess
import os
import sys
import time

def run_script(script_path):
    print(f"\n" + "="*60)
    print(f"RUNNING: {script_path}")
    print("="*60)
    
    start_time = time.time()
    try:
        # Run using the same python interpreter
        result = subprocess.run([sys.executable, script_path], check=True)
        elapsed = time.time() - start_time
        print(f"\nCOMPLETED: {script_path} in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nFAILED: {script_path} with exit code {e.returncode}")
        return False

def main():
    print("=== SOIL HEALTH DSS: UNIFIED PRODUCTION PIPELINE ===")
    print("Starting full system refresh...")
    
    pipeline = [
        os.path.join("scripts", "pipeline_1_build_ontology.py"),
        os.path.join("scripts", "pipeline_2_process_frameworks.py"),
        os.path.join("scripts", "pipeline_3_generate_results.py")
    ]
    
    overall_start = time.time()
    
    for script in pipeline:
        if not os.path.exists(script):
            print(f"Error: Script not found - {script}")
            sys.exit(1)
            
        success = run_script(script)
        if not success:
            print("\nPipeline aborted due to errors.")
            sys.exit(1)
            
    total_time = time.time() - overall_start
    print("\n" + "="*60)
    print(f"PIPELINE SUCCESSFUL!")
    print(f"Total processing time: {total_time/60:.2f} minutes")
    print("="*60)
    print("System is now synchronized and ready for dashboard visualization.")

if __name__ == "__main__":
    main()
