from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorExplanation:
    error_type: str
    friendly_message: str
    suggested_fix: str
    patch_snippet: str | None = None


class DiagnosticExplainer:
    """ماژول تبدیل خطاهای فنی به توضیحات انسانی و پیشنهاد اصلاح."""

    def explain(self, error_code_or_msg: str) -> ErrorExplanation:
        cleaned = error_code_or_msg.strip()

        if "ZeroDivisionError" in cleaned or "CM002" in cleaned:
            return ErrorExplanation(
                error_type="ZeroDivisionError",
                friendly_message=(
                    "داری عدد رو به صفر تقسیم می‌کنی! "
                    "پایتون از این کارها خوشش نمیاد و جیغش درمیاد."
                ),
                suggested_fix=(
                    "قبل از تقسیم، مطمئن بشو که مخرج صفر نباشد "
                    "(مثلا بررسی کن `if b != 0:`)."
                ),
                patch_snippet="if divisor != 0: result = value / divisor else: result = 0",
            )
        elif "SyntaxError" in cleaned:
            return ErrorExplanation(
                error_type="SyntaxError",
                friendly_message=(
                    "یک خطای نگارشی (مثل جا ماندن پرانتز، "
                    "کالن یا کوتیشن) توی کدت داری."
                ),
                suggested_fix="خط اعلام‌شده رو بررسی کن و علامت‌های نگارشی رو کنترل کن.",
            )
        elif "NameError" in cleaned:
            return ErrorExplanation(
                error_type="NameError",
                friendly_message=(
                    "داری از متغییری استفاده می‌کنی که هنوز تعریفش "
                    "نکردی یا غلط املایی داره."
                ),
                suggested_fix="اطمینان حاصل کن که متغیر پیش از استفاده مقداردهی و املاش درست باشه.",
            )
        else:
            return ErrorExplanation(
                error_type="UnknownError",
                friendly_message=f"یک خطای ناشناخته رخ داده است: {cleaned[:100]}",
                suggested_fix="جزئیات خطا و تریس‌بک رو بررسی کن.",
            )
