"""
Simple verification that works without external dependencies.
"""

import sys
from pathlib import Path

def check_structure():
    """Check that all files exist."""
    print("📁 Checking Project Structure...")
    
    required_files = [
        "README.md",
        "requirements.txt", 
        ".env.example",
        "main.py",
        "config/settings.py",
        "src/bot.py", 
        "src/auth/oauth.py",
        "src/commands/base.py",
        "src/commands/basic.py", 
        "SETUP.md"
    ]
    
    all_present = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_present = False
    
    return all_present


def check_code_syntax():
    """Check that Python files have valid syntax."""
    print("\n🔍 Checking Code Syntax...")
    
    python_files = [
        "main.py",
        "config/settings.py", 
        "src/bot.py",
        "src/auth/oauth.py",
        "src/commands/base.py",
        "src/commands/basic.py"
    ]
    
    all_valid = True
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path}")
        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_valid = False
    
    return all_valid


def check_requirements():
    """Check that requirements.txt contains expected packages."""
    print("\n📦 Checking Requirements...")
    
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        expected_packages = [
            "twitchio",
            "requests", 
            "python-dotenv"
        ]
        
        for package in expected_packages:
            if package in requirements.lower():
                print(f"✅ {package} found in requirements")
            else:
                print(f"❌ {package} missing from requirements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


def main():
    """Run simple verification."""
    print("🚀 Twitch Bot - Simple Verification")
    print("=" * 50)
    
    tests = [
        ("Structure", check_structure),
        ("Syntax", check_code_syntax), 
        ("Requirements", check_requirements)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Project structure looks good!")
        print("\nTo get started:")
        print("1. pip install -r requirements.txt")
        print("2. cp .env.example .env") 
        print("3. Edit .env with your credentials")
        print("4. python main.py")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)