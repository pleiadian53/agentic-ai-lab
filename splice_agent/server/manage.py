#!/usr/bin/env python
"""
Management script for Chart Agent API service.

Usage:
    python manage.py start   # Start the service
    python manage.py stop    # Stop the service
    python manage.py restart # Restart the service
    python manage.py status  # Check service status
"""

import sys
import subprocess
import signal
import time
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from config import HOST, PORT


def get_pid_on_port(port: int) -> int:
    """Get PID of process listening on port"""
    try:
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
    except Exception:
        pass
    return None


def is_service_running() -> bool:
    """Check if service is running"""
    pid = get_pid_on_port(PORT)
    return pid is not None


def start_service():
    """Start the Chart Agent API service"""
    if is_service_running():
        print(f"⚠ Service already running on port {PORT}")
        return False
    
    print(f"Starting Chart Agent API on {HOST}:{PORT}...")
    
    # Start service in background
    subprocess.Popen(
        [sys.executable, 'chart_service.py'],
        cwd=Path(__file__).parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for service to start
    for i in range(10):
        time.sleep(1)
        if is_service_running():
            print(f"✓ Service started successfully")
            print(f"  URL: http://{HOST}:{PORT}")
            print(f"  Docs: http://{HOST}:{PORT}/docs")
            return True
        print(f"  Waiting for startup... ({i+1}/10)")
    
    print("✗ Service failed to start")
    return False


def stop_service():
    """Stop the Chart Agent API service"""
    pid = get_pid_on_port(PORT)
    
    if pid is None:
        print(f"No service running on port {PORT}")
        return True
    
    print(f"Stopping Chart Agent API (PID: {pid})...")
    
    try:
        # Send SIGTERM for graceful shutdown
        process = psutil.Process(pid) if psutil else None
        
        if process:
            process.terminate()
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                print("✓ Service stopped gracefully")
                return True
            except psutil.TimeoutExpired:
                print("⚠ Graceful shutdown timeout, forcing...")
                process.kill()
                print("✓ Service stopped (forced)")
                return True
        else:
            # Fallback without psutil
            import os
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for i in range(10):
                time.sleep(1)
                if not is_service_running():
                    print("✓ Service stopped")
                    return True
            
            # Force kill
            os.kill(pid, signal.SIGKILL)
            print("✓ Service stopped (forced)")
            return True
            
    except Exception as e:
        print(f"✗ Error stopping service: {e}")
        return False


def restart_service():
    """Restart the Chart Agent API service"""
    print("Restarting Chart Agent API...")
    stop_service()
    time.sleep(2)
    return start_service()


def service_status():
    """Check and display service status"""
    pid = get_pid_on_port(PORT)
    
    if pid is None:
        print(f"Status: ✗ Not running")
        print(f"Port: {PORT} (available)")
        return False
    
    print(f"Status: ✓ Running")
    print(f"PID: {pid}")
    print(f"Port: {PORT}")
    print(f"URL: http://{HOST}:{PORT}")
    print(f"Docs: http://{HOST}:{PORT}/docs")
    
    if psutil:
        try:
            process = psutil.Process(pid)
            print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
            print(f"CPU: {process.cpu_percent(interval=0.1):.1f}%")
            print(f"Uptime: {time.time() - process.create_time():.0f}s")
        except Exception:
            pass
    
    return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        success = start_service()
    elif command == 'stop':
        success = stop_service()
    elif command == 'restart':
        success = restart_service()
    elif command == 'status':
        success = service_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
