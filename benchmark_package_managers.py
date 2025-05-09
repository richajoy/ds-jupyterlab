import time
import subprocess
import sys
import os
from datetime import datetime

# Get current environment information
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"Python Environment: {python_version}")
print(f"Running benchmarks at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Packages to install and benchmark - a mix of simple and complex packages
packages = [
    "requests",           # Simple HTTP library
    "beautifulsoup4",     # HTML parsing 
    "pandas",             # Data manipulation
    "matplotlib",         # Visualization
    "seaborn",            # Statistical visualization
    "scikit-learn",       # Machine learning
    "transformers",       # Hugging Face transformers
    "pillow",             # Image processing
    "nltk",               # Natural language toolkit
    "pyyaml",             # YAML parser
    "tqdm"                # Progress bars
]

print(f"Benchmarking package installations for Python {python_version}")
print(f"Packages to test: {', '.join(packages)}")

# Suppress pip warnings about root user
pip_flags = "--quiet --disable-pip-version-check --no-warn-script-location --root-user-action=ignore"

# Function to measure installation time
def measure_install_time(manager_name, command):
    parts = command.split()
    package_name = parts[-1]  # Extract package name from the end of command
    
    print(f"\n==== {manager_name.upper()} INSTALL FOR '{package_name}' ====")
    print(f"Running: {command}")
    
    start_time = time.time()
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    elapsed = end_time - start_time
    success = process.returncode == 0
    
    print(f"Status: {'Success' if success else 'Failed'}")
    print(f"Time: {elapsed:.2f} seconds")
    
    # Only show error output if there was a failure
    if not success:
        print(f"Error: {process.stderr.strip()}")
    
    return {
        'elapsed_seconds': elapsed,
        'success': success,
        'package': package_name
    }

# Run benchmarks for each package
all_results = {}
python_details = f"Python {python_version}"

for package in packages:
    print(f"\n{'='*50}")
    print(f"BENCHMARKING PACKAGE: {package} on {python_details}")
    print(f"{'='*50}")
    
    # First ensure package is not installed
    print(f"Ensuring {package} is not installed...")
    subprocess.run(f"{sys.executable} -m pip uninstall -y {package}", 
                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Dictionary to store results for this package
    results = {}
    
    # Benchmark pip
    pip_cmd = f"{sys.executable} -m pip install {pip_flags} {package}"
    results['pip'] = measure_install_time("pip", pip_cmd)
    print(f"Removing {package} installed by pip...")
    subprocess.run(f"{sys.executable} -m pip uninstall -y {package}", 
                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Benchmark conda with a simpler package
    conda_cmd = f"conda install -y --no-update-deps -c conda-forge {package}"
    results['conda'] = measure_install_time("conda", conda_cmd)
    print(f"Removing {package} installed by conda...")
    subprocess.run(f"conda remove -y --force {package}", 
                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Benchmark uv with better flags for speed
    uv_cmd = f"uv pip install --system {package}"
    results['uv'] = measure_install_time("uv", uv_cmd)
    print(f"Removing {package} installed by UV...")
    subprocess.run(f"{sys.executable} -m pip uninstall -y {package}", 
                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Results summary for this package
    print(f"\n==== RESULTS SUMMARY FOR '{package}' ({python_details}) ====")
    for manager, result in results.items():
        if result['success']:
            print(f"{manager}: {result['elapsed_seconds']:.2f} seconds")
        else:
            print(f"{manager}: Failed")
    
    # Determine the fastest for this package
    successful_times = {m: r['elapsed_seconds'] for m, r in results.items() if r['success']}
    if successful_times:
        fastest = min(successful_times, key=successful_times.get)
        print(f"\nFastest package manager for '{package}': {fastest} ({successful_times[fastest]:.2f} seconds)")
        
        # Show speed comparison
        for manager, time_taken in successful_times.items():
            if manager != fastest:
                speedup = time_taken / successful_times[fastest]
                print(f"{fastest} is {speedup:.1f}x faster than {manager}")
    else:
        print(f"\nNo successful '{package}' installations to compare")
    
    # Store results for overall comparison
    all_results[package] = results

# Overall summary across all packages
print(f"\n{'='*50}")
print(f"OVERALL PERFORMANCE SUMMARY FOR {python_details}")
print(f"{'='*50}")

# Count successes per package manager
success_counts = {'pip': 0, 'conda': 0, 'uv': 0}
total_times = {'pip': 0, 'conda': 0, 'uv': 0}

for package, results in all_results.items():
    for manager, result in results.items():
        if result['success']:
            success_counts[manager] += 1
            total_times[manager] += result['elapsed_seconds']

print("\nSuccess rates:")
for manager, count in success_counts.items():
    print(f"{manager}: {count}/{len(packages)} packages successful")

print(f"\nTotal installation times ({python_details}):")
for manager, total_time in total_times.items():
    if success_counts[manager] > 0:
        print(f"{manager}: {total_time:.2f} seconds total, {total_time/success_counts[manager]:.2f} seconds average")
    else:
        print(f"{manager}: No successful installations")

# Determine overall fastest
if sum(success_counts.values()) > 0:
    # Only consider managers that succeeded for all packages
    full_success = {m: total_times[m] for m in total_times if success_counts[m] == len(packages)}
    
    if full_success:
        overall_fastest = min(full_success, key=full_success.get)
        print(f"\nOverall fastest package manager for {python_details}: {overall_fastest}")
        
        for manager, time in full_success.items():
            if manager != overall_fastest:
                speedup = time / full_success[overall_fastest]
                print(f"{overall_fastest} is {speedup:.1f}x faster than {manager} overall")
    else:
        partial_success = {m: total_times[m]/success_counts[m] for m in total_times if success_counts[m] > 0}
        if partial_success:
            fastest_avg = min(partial_success, key=partial_success.get)
            print(f"\nFastest average package manager for {python_details}: {fastest_avg}")
            print("(Note: Not all package managers succeeded for all packages)")

# Create a detailed summary table for all packages
print(f"\n{'='*50}")
print(f"DETAILED RESULTS TABLE ({python_details})")
print(f"{'='*50}")
print(f"{'Package':<15} {'pip (s)':<10} {'conda (s)':<10} {'uv (s)':<10} {'Fastest':<10}")
print(f"{'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

for package, results in all_results.items():
    pip_time = f"{results['pip']['elapsed_seconds']:.2f}" if results['pip']['success'] else "Failed"
    conda_time = f"{results['conda']['elapsed_seconds']:.2f}" if results['conda']['success'] else "Failed"
    uv_time = f"{results['uv']['elapsed_seconds']:.2f}" if results['uv']['success'] else "Failed"
    
    # Find fastest for this package
    fastest = "None"
    fastest_time = float('inf')
    for manager, result in results.items():
        if result['success'] and result['elapsed_seconds'] < fastest_time:
            fastest_time = result['elapsed_seconds']
            fastest = manager
            
    print(f"{package:<15} {pip_time:<10} {conda_time:<10} {uv_time:<10} {fastest:<10}")
