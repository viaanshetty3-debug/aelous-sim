#!/usr/bin/env python3
"""
AEOLUS Streamlit Dashboard Launcher
Handles Streamlit installation check and launches the interactive web dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit():
    """Check if Streamlit is installed."""
    try:
        import streamlit
        print(f"✓ Streamlit {streamlit.__version__} found")
        return True
    except ImportError:
        print("✗ Streamlit not installed")
        return False

def install_streamlit():
    """Install Streamlit and dependencies."""
    print("\n📦 Installing Streamlit and dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "streamlit", "plotly"])
        print("✓ Streamlit installed successfully\n")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install Streamlit")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    script_dir = Path(__file__).parent
    app_file = script_dir / "app.py"

    if not app_file.exists():
        print(f"✗ Error: {app_file} not found!")
        return False

    print("\n" + "="*75)
    print("  ⚡ AEOLUS INTERACTIVE WEB DASHBOARD ⚡")
    print("="*75)
    print("\n📍 Starting Streamlit server...\n")
    print("   The dashboard will open in your default browser.")
    print("   If not, navigate to: http://localhost:8501")
    print("\n   Press Ctrl+C to stop the server\n")
    print("="*75 + "\n")

    try:
        # Run Streamlit with optimized settings for lower-powered systems
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_file),
            "--client.showErrorDetails=false",
            "--client.toolbarMode=minimal",
            "--logger.level=warning"
        ])
        return True
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"\n✗ Error launching dashboard: {e}")
        return False

def main():
    """Main entry point."""
    print("\n" + "="*75)
    print("  AEOLUS Streamlit Dashboard Launcher")
    print("="*75 + "\n")

    # Check dependencies
    print("Checking dependencies...\n")

    if not check_streamlit():
        if not install_streamlit():
            print("\nFailed to install dependencies. Exiting.")
            sys.exit(1)

    # Verify required modules
    required_modules = [
        ("numpy", "NumPy"),
        ("plotly", "Plotly"),
        ("streamlit", "Streamlit")
    ]

    all_installed = True
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name} available")
        except ImportError:
            print(f"✗ {display_name} missing")
            all_installed = False

    if not all_installed:
        print("\n❌ Some dependencies are missing. Please install manually:")
        print("   pip install numpy plotly streamlit")
        sys.exit(1)

    # Check if solver modules exist
    solver_files = ["grid.py", "solver.py", "baseline.py", "diagnostics.py"]
    solver_dir = Path(__file__).parent

    print("\nChecking solver modules...")
    for fname in solver_files:
        fpath = solver_dir / fname
        if fpath.exists():
            print(f"✓ {fname}")
        else:
            print(f"✗ {fname} NOT FOUND")
            all_installed = False

    # Check interventions
    interventions_dir = solver_dir / "interventions"
    if interventions_dir.exists():
        print(f"✓ interventions/")
    else:
        print(f"✗ interventions/ directory NOT FOUND")
        all_installed = False

    if not all_installed:
        print("\n❌ Some solver modules are missing!")
        sys.exit(1)

    # Launch dashboard
    print("\n")
    if launch_dashboard():
        print("\n✓ Streamlit dashboard session ended normally")
        sys.exit(0)
    else:
        print("\n✗ Failed to launch dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
