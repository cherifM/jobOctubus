#!/usr/bin/env python3
"""
Utility to toggle job search services on/off by modifying the .env file
Usage: python toggle_service.py <service_name> <true/false>
Example: python toggle_service.py arbeitsagentur true
"""
import sys
import os

def toggle_service(service_name: str, enabled: str):
    """Toggle a job search service on/off"""
    valid_services = ['remoteok', 'arbeitsagentur', 'thelocal', 'linkedin', 'indeed']
    
    if service_name.lower() not in valid_services:
        print(f"❌ Invalid service: {service_name}")
        print(f"Valid services: {', '.join(valid_services)}")
        return False
    
    if enabled.lower() not in ['true', 'false']:
        print("❌ Value must be 'true' or 'false'")
        return False
    
    env_var = f"ENABLE_{service_name.upper()}"
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ .env file not found")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add the setting
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{env_var}="):
            lines[i] = f"{env_var}={enabled.title()}\n"
            updated = True
            break
    
    if not updated:
        # Add new setting
        lines.append(f"{env_var}={enabled.title()}\n")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated {service_name} to {'enabled' if enabled.lower() == 'true' else 'disabled'}")
    print("⚠️  Restart the backend server for changes to take effect")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python toggle_service.py <service_name> <true/false>")
        print("Example: python toggle_service.py arbeitsagentur true")
        print("Services: remoteok, arbeitsagentur, thelocal, linkedin, indeed")
        sys.exit(1)
    
    service_name = sys.argv[1]
    enabled = sys.argv[2]
    
    toggle_service(service_name, enabled)