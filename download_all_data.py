import os
import subprocess
import sys

def run_script(script_path):
    """Run a Python script and forward its output to the console."""
    print(f"\n=== Running {script_path} ===")
    try:
        # Use sys.executable to ensure the script runs with the same Python interpreter
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            text=True,
            capture_output=True
        )
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Errors/Warnings:\n{result.stderr}")
        print(f"=== Completed {script_path} ===\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(f"Errors:\n{e.stderr}")
        return False

def main():
    """Run all data download scripts."""
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths to individual download scripts
    post1_script = os.path.join(base_dir, "posts", "post_01_timewarp", "download_data.py")
    streamlit_script = os.path.join(base_dir, "extras", "download_data.py")
    
    scripts = [
        ("Post 1 daily data", post1_script),
        ("Streamlit weekly data", streamlit_script)
    ]
    
    print("=== TWSCA Data Download Utility ===")
    print("This script will run the individual data download scripts for each component of the repository.")
    
    # Check if scripts exist
    for name, path in scripts:
        if not os.path.exists(path):
            print(f"Warning: {name} script not found at {path}")
    
    # Run each script
    results = []
    for name, path in scripts:
        if os.path.exists(path):
            print(f"\nDownloading {name}...")
            success = run_script(path)
            results.append((name, success))
        else:
            results.append((name, False))
    
    # Print summary
    print("\n=== Download Summary ===")
    all_success = True
    for name, success in results:
        status = "✅ Completed" if success else "❌ Failed"
        print(f"{status}: {name}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n✅ All data downloads completed successfully.")
    else:
        print("\n⚠️ Some data downloads failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 