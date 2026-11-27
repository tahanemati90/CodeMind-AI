class AutoFixer:
    """موتور اصلاح خودکار کدهای معیوب برای خطاهای شناخته‌شده."""

    def fix(self, source_code: str, error_code: str) -> str:
        code = source_code.strip()

        if error_code == "CM002" or "ZeroDivisionError" in code:
            # یک اصلاح ساده و ایمن برای جلوگیری از تقسیم بر صفر
            if "/" in code and "if" not in code:
                # تبدیل خط تقسیم ساده به یک ساختار امن
                return f"try:\n    result = {code}\nexcept ZeroDivisionError:\n    result = 0"

        return code
