#!/usr/bin/env python3
"""
Generate all figures for climate-health-news analysis.

This script runs all plotting modules to generate the complete set of figures:
- figure1.png: Combined maps and time series visualization
- figure2.png: Urban/rural framing distribution (no health vs health)
- figure3.png: Inequality time series  
- figure4.png: Inequality types bar chart

Usage:
    python plots/make_figures.py
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_script(script_path, description):
    """
    Run a Python script and handle any errors.
    
    Args:
        script_path (str): Path to the Python script to run
        description (str): Description of what the script does
    
    Returns:
        bool: True if successful, False if error occurred
    """
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check if successful
        if result.returncode == 0:
            elapsed = time.time() - start_time
            print(f"✅ SUCCESS: {description} completed in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ ERROR: {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: Error running {script_path}: {e}")
        return False

def main():
    """Main function to generate all figures."""
    
    print("🎨 CLIMATE-HEALTH-NEWS FIGURE GENERATION")
    print("=" * 70)
    print("Generating all analysis figures...")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"Working directory: {os.getcwd()}")
    
    # Ensure output directory exists
    output_dir = Path("plots/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")
    
    # Define scripts to run in order
    scripts = [
        {
            'path': 'plots/plot_climate_health.py',
            'description': 'Combined maps and time series (figure1.png)',
            'output': 'plots/images/figure1.png'
        },
        {
            'path': 'plots/plot_urban_rural_barchart.py', 
            'description': 'Urban/rural framing distribution (figure2.png)',
            'output': 'plots/images/figure2.png'
        },
        {
            'path': 'plots/plot_inequality.py',
            'description': 'Inequality time series and types (figure3.png, figure4.png)', 
            'output': ['plots/images/figure3.png', 'plots/images/figure4.png']
        }
    ]
    
    # Track results
    successful = 0
    failed = 0
    start_total = time.time()
    
    # Run each script
    for script in scripts:
        success = run_script(script['path'], script['description'])
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    total_time = time.time() - start_total
    print(f"\n{'='*70}")
    print("🎯 FIGURE GENERATION SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    
    # Check output files
    print(f"\n📁 Generated files:")
    figure_files = ['figure1.png', 'figure2.png', 'figure3.png', 'figure4.png']
    for fig in figure_files:
        fig_path = output_dir / fig
        if fig_path.exists():
            size_mb = fig_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ {fig} ({size_mb:.1f} MB)")
        else:
            print(f"   ❌ {fig} (missing)")
    
    if failed == 0:
        print(f"\n🎉 SUCCESS: All figures generated successfully!")
        return 0
    else:
        print(f"\n⚠️  WARNING: {failed} script(s) failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())