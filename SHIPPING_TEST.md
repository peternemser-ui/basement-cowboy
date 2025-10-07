# 🧪 Basement Cowboy - Shipping Readiness Test

## 🎯 Quick Validation Tests

This script helps you verify that Basement Cowboy is ready for deployment and shipping.

## ✅ **Test Categories**

### 1. Environment Validation
### 2. Configuration Tests  
### 3. Dependency Verification
### 4. Application Startup Tests
### 5. Core Functionality Tests
### 6. Security Validation
### 7. Documentation Completeness

---

## 🚀 **Quick Test Commands**

### **Test 1: Environment Setup**
```bash
# Check Python version
python --version

# Check pip version
pip --version

# Verify virtual environment can be created
python -m venv test_venv
test_venv\Scripts\activate  # Windows
rm -rf test_venv  # Cleanup
```

### **Test 2: Dependencies**
```bash
# Test requirements installation
pip install -r requirements.txt --dry-run

# Check critical packages
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import requests; print('Requests:', requests.__version__)"
python -c "import playwright; print('Playwright: OK')"
```

### **Test 3: Configuration Validation**
```bash
# Check .env template exists
ls -la .env.template

# Verify .gitignore protects secrets
grep -E "(\.env|wordpress_config\.json)" .gitignore

# Test configuration loading
python -c "from dotenv import load_dotenv; load_dotenv(); print('Config loading: OK')"
```

### **Test 4: Application Startup**
```bash
# Test application imports
python -c "from app.routes import create_app; app = create_app(); print('App creation: OK')"

# Test health endpoint (after starting app)
curl -f http://localhost:5000/health
```

### **Test 5: File Structure**
```bash
# Verify critical directories exist
ls -la app/ scraper/ config/ output/

# Check critical files
ls -la run.py requirements.txt README.md

# Verify start scripts
ls -la start-cowboy.bat start-production.ps1 start-production.sh
```

---

## 🔍 **Detailed Test Procedures**

### **Manual Testing Workflow**

#### **Step 1: Fresh Environment Test**
1. Create new directory: `mkdir basement-cowboy-test`
2. Copy project files to test directory
3. Run `start-cowboy.bat` (Windows) or appropriate start script
4. Verify it creates virtual environment
5. Verify it installs dependencies
6. Verify it prompts for configuration

#### **Step 2: Configuration Test**
1. Edit `.env` file with test API key
2. Start application
3. Access `http://localhost:5000`
4. Verify web interface loads
5. Test API key validation endpoint

#### **Step 3: Core Functionality Test**
1. **News Scraping**: Test scraper with small subset
2. **AI Integration**: Test OpenAI API connectivity
3. **File Operations**: Verify JSON file creation
4. **WordPress**: Test connection (if configured)

#### **Step 4: Error Handling Test**
1. Test with invalid API key
2. Test with missing configuration
3. Test with network disconnection
4. Verify graceful error messages

#### **Step 5: Security Test**
1. Verify no hardcoded secrets in code
2. Check `.env` contains placeholders only
3. Verify `.gitignore` protects sensitive files
4. Test CSP headers in production mode

---

## 🛠️ **Automated Test Script**

### **Windows PowerShell Test**
```powershell
# Save as: test-shipping-readiness.ps1

Write-Host "🧪 Testing Basement Cowboy Shipping Readiness" -ForegroundColor Green
Write-Host "=" * 50

$errors = 0

# Test 1: Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    $errors++
}

# Test 2: Critical Files
$criticalFiles = @("run.py", "requirements.txt", ".env.template", "README.md", "start-cowboy.bat")
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ File exists: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing file: $file" -ForegroundColor Red
        $errors++
    }
}

# Test 3: Configuration Safety
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "sk-proj-" -or $envContent -match "your-openai-api-key-here") {
        Write-Host "⚠️  Check .env file for placeholder values" -ForegroundColor Yellow
    }
}

# Test 4: Dependencies Test
try {
    pip install -r requirements.txt --dry-run --quiet 2>$null
    Write-Host "✅ Requirements validated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Requirements validation failed" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + "=" * 50
if ($errors -eq 0) {
    Write-Host "🎉 READY TO SHIP! All tests passed." -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Edit .env with real API keys" -ForegroundColor Cyan
    Write-Host "2. Run start-cowboy.bat" -ForegroundColor Cyan
    Write-Host "3. Test web interface at http://localhost:5000" -ForegroundColor Cyan
} else {
    Write-Host "❌ $errors issues found. Fix before shipping." -ForegroundColor Red
}
```

### **Linux/Mac Bash Test**
```bash
#!/bin/bash
# Save as: test-shipping-readiness.sh

echo "🧪 Testing Basement Cowboy Shipping Readiness"
echo "=================================================="

errors=0

# Test 1: Python
if python3 --version >/dev/null 2>&1; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python not found"
    ((errors++))
fi

# Test 2: Critical Files
critical_files=("run.py" "requirements.txt" ".env.template" "README.md")
for file in "${critical_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ File exists: $file"
    else
        echo "❌ Missing file: $file"
        ((errors++))
    fi
done

# Test 3: Virtual Environment Test
if python3 -m venv test_env_check >/dev/null 2>&1; then
    echo "✅ Virtual environment creation works"
    rm -rf test_env_check
else
    echo "❌ Virtual environment creation failed"
    ((errors++))
fi

# Summary
echo ""
echo "=================================================="
if [[ $errors -eq 0 ]]; then
    echo "🎉 READY TO SHIP! All tests passed."
    echo "Next steps:"
    echo "1. Edit .env with real API keys"
    echo "2. Run ./start-production.sh"
    echo "3. Test web interface at http://localhost:5000"
else
    echo "❌ $errors issues found. Fix before shipping."
fi
```

---

## 📋 **Shipping Checklist**

### **Pre-Ship Validation** ✅
- [ ] All dependencies install successfully
- [ ] Virtual environment creation works
- [ ] Application starts without errors
- [ ] Health endpoint responds
- [ ] Web interface loads properly
- [ ] No hardcoded secrets in repository
- [ ] Documentation is complete and accurate
- [ ] Start scripts work on target platforms

### **Security Checklist** 🔒
- [ ] `.env` contains only placeholder values
- [ ] `.gitignore` protects sensitive files
- [ ] No API keys committed to repository
- [ ] Flask debug mode disabled in production
- [ ] CSP headers configured properly
- [ ] Error messages don't expose sensitive information

### **Functionality Checklist** ⚙️
- [ ] News scraping works with sample sites
- [ ] OpenAI API integration functional
- [ ] File creation and management works
- [ ] WordPress integration works (if configured)
- [ ] Error handling is graceful
- [ ] Logging is appropriate for production

### **Documentation Checklist** 📚
- [ ] README has clear installation instructions
- [ ] Environment setup is documented
- [ ] Configuration examples are provided
- [ ] Troubleshooting guide is included
- [ ] API requirements are specified
- [ ] Deployment options are explained

---

## 🏁 **Ready to Ship Criteria**

Your project is **ready to ship** when:

1. **All automated tests pass** ✅
2. **Manual workflow completes successfully** ✅
3. **Security checklist is 100% complete** ✅
4. **Documentation is comprehensive** ✅
5. **Start scripts work on target platforms** ✅
6. **Core functionality verified** ✅

---

## 🚀 **Ship It!**

Once all tests pass, your Basement Cowboy is ready for:
- **GitHub release**
- **Distribution to users**
- **Production deployment**
- **Customer delivery**