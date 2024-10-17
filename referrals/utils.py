from django.core.cache import cache
import logging

logger = logging.getLogger('referrals')

CACHE_KEY_PREFIX = 'referral_code_'


def set_referral_code(referral_code):
    """
    Сохраняет реферальный код в кэше.
    """
    cache.set(f"{CACHE_KEY_PREFIX}{referral_code.code}", referral_code,
              timeout=None)
    logger.info(f"Referral code cached: {referral_code.code}")


def get_referral_code(code):
    """
    Получает реферальный код из кэша по его коду
    """
    cached_code = cache.get(f"{CACHE_KEY_PREFIX}{code}")
    logger.info(f"Retrieved cached referral code: "
                f"{cached_code.code if cached_code else 'None'}")
    return cached_code


def delete_referral_code(code):
    """
    Удаляет реферальный код из кэша по его коду.
    """
    cache.delete(f"{CACHE_KEY_PREFIX}{code}")
    logger.info(f"Deleted cached referral code: {code}")
