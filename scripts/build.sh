#!/bin/bash
# Build script for the C++ compiler project

set -e  # Exit on error

echo "================================"
echo "Building C++ Compiler"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

required_version="3.7"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p build
mkdir -p dist
mkdir -p logs
echo "✓ Directories created"
echo ""

# Check source files
echo "Checking source files..."
required_files=(
    "src/lexer/__init__.py"
    "src/parser/__init__.py"
    "src/semantic/__init__.py"
    "src/ir/__init__.py"
    "src/codegen/__init__.py"
    "src/compiler.py"
    "main.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Missing required file: $file"
        exit 1
    fi
done
echo "✓ All required files present"
echo ""

# Validate Python syntax
echo "Validating Python syntax..."
for file in $(find src -name "*.py"); do
    python3 -m py_compile "$file" 2>/dev/null || {
        echo "Error: Syntax error in $file"
        exit 1
    }
done
python3 -m py_compile main.py 2>/dev/null || {
    echo "Error: Syntax error in main.py"
    exit 1
}
echo "✓ Python syntax OK"
echo ""

# Run quick smoke tests
echo "Running smoke tests..."

# Test 1: Simple compilation
cat > build/test_simple.cpp << 'EOF'
int add(int a, int b) {
    return a + b;
}
EOF

python3 main.py build/test_simple.cpp -o build/test_simple.s > /dev/null 2>&1 || {
    echo "Error: Smoke test failed"
    exit 1
}

if [ ! -f "build/test_simple.s" ]; then
    echo "Error: No output file generated"
    exit 1
fi

echo "✓ Smoke tests passed"
echo ""

# Build documentation (if tools available)
if command -v pandoc &> /dev/null; then
    echo "Building documentation..."
    for md_file in docs/*.md; do
        if [ -f "$md_file" ]; then
            html_file="build/$(basename ${md_file%.md}.html)"
            pandoc "$md_file" -o "$html_file" --standalone 2>/dev/null || true
        fi
    done
    echo "✓ Documentation built"
    echo ""
fi

# Create distribution package
echo "Creating distribution..."
tar -czf dist/compiler-$(date +%Y%m%d).tar.gz \
    src/ \
    examples/ \
    docs/ \
    main.py \
    README.md \
    --exclude="*.pyc" \
    --exclude="__pycache__"
echo "✓ Distribution package created: dist/compiler-$(date +%Y%m%d).tar.gz"
echo ""

echo "================================"
echo "Build completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run tests: ./scripts/run_tests.sh"
echo "  2. Try compiler: python3 main.py your_file.cpp"
echo "  3. View docs: open build/*.html (if generated)"