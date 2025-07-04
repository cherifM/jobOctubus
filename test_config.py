#!/usr/bin/env python3
"""
Test script to verify job search service configuration
Run this after activating the virtual environment to see current settings
"""

try:
    from backend.config import settings
    print("✅ Job Search Service Configuration:")
    print(f"RemoteOK: {'✅ Enabled' if settings.enable_remoteok else '❌ Disabled'}")
    print(f"Arbeitsagentur: {'✅ Enabled' if settings.enable_arbeitsagentur else '❌ Disabled'}")
    print(f"TheLocal: {'✅ Enabled' if settings.enable_thelocal else '❌ Disabled'}")
    print(f"LinkedIn: {'✅ Enabled' if settings.enable_linkedin else '❌ Disabled'} (API Key: {'Present' if settings.linkedin_api_key and settings.linkedin_api_key != 'your_linkedin_key_here' else 'Missing'})")
    print(f"Indeed: {'✅ Enabled' if settings.enable_indeed else '❌ Disabled'} (API Key: {'Present' if settings.indeed_api_key and settings.indeed_api_key != 'your_indeed_key_here' else 'Missing'})")
    
    print("\n📋 To modify service configuration, edit the .env file:")
    print("ENABLE_REMOTEOK=True/False")
    print("ENABLE_ARBEITSAGENTUR=True/False") 
    print("ENABLE_THELOCAL=True/False")
    print("ENABLE_LINKEDIN=True/False")
    print("ENABLE_INDEED=True/False")
    
except ImportError as e:
    print(f"❌ Error importing configuration: {e}")
    print("Make sure to activate the virtual environment:")
    print("source venv/bin/activate")