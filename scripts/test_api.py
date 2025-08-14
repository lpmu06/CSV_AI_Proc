#!/usr/bin/env python3
"""
Script de teste para a API de processamento de CSV
"""

import asyncio
import httpx
from pathlib import Path
import sys

async def test_csv_processing():
    """Test CSV processing endpoint"""
    
    # Test file path
    test_file = Path("examples/input/Carga CMNS2.csv")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🧪 Testing CSV processing with file: {test_file}")
    
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            # Test health endpoint first
            print("🔍 Testing health endpoint...")
            health_response = await client.get("http://localhost:8000/health")
            
            if health_response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
            
            # Test CSV processing
            print("📄 Processing CSV file...")
            
            with open(test_file, 'rb') as f:
                files = {'file': (test_file.name, f, 'text/csv')}
                
                response = await client.post(
                    "http://localhost:8000/process-csv",
                    files=files
                )
            
            if response.status_code == 200:
                # Save the processed file
                output_file = Path("test_output.csv")
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ CSV processing successful! Output saved to: {output_file}")
                
                # Show first few lines of output
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]  # First 3 lines
                    print("\n📋 First few lines of output:")
                    for i, line in enumerate(lines, 1):
                        print(f"Line {i}: {line.strip()[:100]}...")
                
                return True
            else:
                print(f"❌ CSV processing failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

async def test_api_endpoints():
    """Test all API endpoints"""
    
    print("🚀 Starting API tests...\n")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test root endpoint
            print("🔍 Testing root endpoint...")
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ Root endpoint working")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
            
            print()
            
            # Test health endpoint
            print("🔍 Testing health endpoint...")
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
            
            print()
            
            # Test files endpoint
            print("🔍 Testing files listing endpoint...")
            response = await client.get("http://localhost:8000/files")
            if response.status_code == 200:
                print("✅ Files endpoint working")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Files endpoint failed: {response.status_code}")
            
            print()
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--csv":
        # Test CSV processing
        success = asyncio.run(test_csv_processing())
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n💥 Tests failed!")
            sys.exit(1)
    else:
        # Test basic endpoints
        asyncio.run(test_api_endpoints())
        print("\n✨ Basic API tests completed!")

if __name__ == "__main__":
    main()