import secrets
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail


VERIFICATION_CODE_TTL = 60 * 10


def _verification_key(email):
    return f"register-verification:{email.lower()}"


def create_and_send_verification_code(email):
    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(_verification_key(email), code, timeout=VERIFICATION_CODE_TTL)
    send_mail(
        subject="Registratsiyani tasdiqlash kodi",
        message=f"Sizning tasdiqlash kodingiz: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def verify_code(email, code):
    key = _verification_key(email)
    saved_code = cache.get(key)
    if saved_code is None or not secrets.compare_digest(str(saved_code), str(code)):
        return False
    cache.delete(key)
    return True
