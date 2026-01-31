from core.parser import CodeParser

parser = CodeParser()
result = parser.parse_file('../examples/sample.py')

print(f"\n📄 File: {result['filepath']}\n")
print(f"✨ Functions: {len(result['functions'])}")
for func in result['functions']:
    print(f"   • {func['name']}() - line {func['line']}")

print(f"\n📦 Classes: {len(result['classes'])}")
for cls in result['classes']:
    print(f"   • {cls['name']} - line {cls['line']}")

print(f"\n📥 Imports: {len(result['imports'])}")
for imp in result['imports']:
    print(f"   • {imp['statement']}")