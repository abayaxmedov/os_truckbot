from __future__ import annotations

import hashlib
import hmac
import json
from decimal import Decimal
from urllib.parse import urlencode

import pytest

from app.core.telegram_auth import InitDataError, parse_user, verify_init_data
from app.core.utils import normalize_part_number, slugify
from app.services.commission import effective_commission, split_amount


def test_normalize_part_number():
    assert normalize_part_number("51.10100-6126") == "51101006126"
    assert normalize_part_number("51 10100 6126") == "51101006126"
    assert normalize_part_number("MAN 51.10100-6126") == "MAN51101006126"
    assert normalize_part_number("") == ""


def test_slugify_transliteration():
    assert slugify("Тормозная система") == "tormoznaya-sistema"
    assert slugify("Фильтры") == "filtry"


def test_split_amount_tz_example():
    # TZ §12: 1_000_000 @ 7% -> 70_000 marketplace, 930_000 seller
    commission, payout = split_amount(Decimal("1000000"), Decimal("7"))
    assert commission == Decimal("70000.00")
    assert payout == Decimal("930000.00")


def test_effective_commission_precedence():
    # seller override wins
    assert effective_commission(Decimal("5"), Decimal("10"), Decimal("7")) == Decimal("5")
    # then category override
    assert effective_commission(None, Decimal("10"), Decimal("7")) == Decimal("10")
    # then global default
    assert effective_commission(None, None, Decimal("7")) == Decimal("7")


def _build_init_data(bot_token: str, user: dict) -> str:
    fields = {"auth_date": "1700000000", "query_id": "AAA", "user": json.dumps(user)}
    check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def test_verify_init_data_valid():
    token = "123456:TEST"
    user = {"id": 42, "first_name": "Ali", "username": "ali", "language_code": "uz"}
    init_data = _build_init_data(token, user)
    fields = verify_init_data(init_data, token)
    tg = parse_user(fields)
    assert tg.id == 42
    assert tg.language_code == "uz"


def test_verify_init_data_bad_hash():
    token = "123456:TEST"
    init_data = _build_init_data(token, {"id": 1})
    tampered = init_data.replace("hash=", "hash=deadbeef&_x=") + "z"
    with pytest.raises(InitDataError):
        verify_init_data(tampered, token)
