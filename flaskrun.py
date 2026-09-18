#!/usr/bin/env python3
"""
AEOLUS Flask Dashboard Launcher
Lightweight web dashboard - faster startup, lower resource usage
"""

import subprocess
import sys
from pathlib import Path

def check_flask():
    """Check if Flask is installed."""
    try:
        import flask
        print(f"✓ Flask {flask.__version__} found")
        return True
    except ImportError:
        return False

def install_flask():
    """Install Flask."""
    print("📦 Installing Flask...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "flask"])
        print("✓ Flask installed successfully\n")
        return True
    except subprocess.CalledProcessError:
        return False

def launch_dashboard():
    """Launch Flask dashboard."""
    script_dir = Path(__file__).parent
    app_file = script_dir / "web_app.py"

    if not app_file.exists():
        print(f"✗ Error: {app_file} not found!")
        return False

    print("\n" + "="*75)
    print("  ⚡ AEOLUS FLASK WEB DASHBOARD ⚡")
    print("="*75)
    print("\n📍 Starting Flask server...\n")
    print("   URL: http://localhost:5000")
    print("   Open in your browser now!")
    print("\n   Press Ctrl+C to stop the server\n")
    print("="*75 + "\n")

    try:
        subprocess.run([sys.executable, str(app_file)])
        return True
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    """Main entry point."""
    print("\n" + "="*75)
    print("  AEOLUS Flask Dashboard Launcher")
    print("="*75 + "\n")

    # Check Flask
    print("Checking dependencies...\n")

    if not check_flask():
        if not install_flask():
            print("\nFailed to install Flask.")
            print("Try manually: pip install flask")
            sys.exit(1)

    # Verify solver modules
    print("Checking solver modules...\n")
    solver_files = ["grid.py", "solver.py", "baseline.py", "diagnostics.py"]
    solver_dir = Path(__file__).parent

    for fname in solver_files:
        fpath = solver_dir / fname
        if fpath.exists():
            print(f"✓ {fname}")
        else:
            print(f"✗ {fname} NOT FOUND")
            sys.exit(1)

    interventions_dir = solver_dir / "interventions"
    if interventions_dir.exists():
        print(f"✓ interventions/\n")
    else:
        print(f"✗ interventions/ NOT FOUND\n")
        sys.exit(1)

    # Launch
    if launch_dashboard():
        print("\n✓ Flask dashboard session ended")
        sys.exit(0)
    else:
        print("\n✗ Failed to launch dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
