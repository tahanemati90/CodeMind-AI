from codemind.diagnostics.explainer import DiagnosticExplainer
from codemind.diagnostics.autofixer import AutoFixer

buggy_code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""

print("🚀 CodeMind AI - Final Showcase Start!")
print("-" * 40)

# ۱. ارسال رشته‌ی خطا به متد explain
explainer = DiagnosticExplainer()
explanation = explainer.explain("ZeroDivisionError: division by zero")
print(f"🧠 AI Explanation:\n{explanation}\n")

# ۲. نمایش اصلاح خودکار با ارسال کد و نوع خطا/پیام
autofixer = AutoFixer()
fixed_code = autofixer.fix(buggy_code, error_code="ZeroDivisionError")
print(f"🔧 Auto-Fixed Code:\n{fixed_code}")

print("-" * 40)
print("✅ Showcase completed successfully!")
