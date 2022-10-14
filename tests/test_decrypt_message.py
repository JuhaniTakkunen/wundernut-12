import pytest

from decrypt_message import decrypt_text, get_list_of_spells


def test_get_list_of_spells_cache_force_cache():
    res = get_list_of_spells(force_cache=True)
    assert isinstance(res, list)
    assert "Evanesco" in res


def test_get_list_of_spells_cache_without_force(socket_disabled):
    res = get_list_of_spells()
    assert isinstance(res, list)
    assert "Evanesco" in res


@pytest.mark.parametrize(
    "encrypted,decrypted",
    [
        ("MYHOVERCRAFTISFULLOFEELS", "my hovercraft is full of eels".upper()),
        ("CBOBOBBQQMF", "banana apple".upper()),
        ("TFMHCVBYPALZWLSSPZPTWLKPTLUAHIBAPAZOHYK", "my favourite spell is impedimenta but its hard".upper()),
    ]
)
def test_decrypt_text(encrypted, decrypted):
    assert decrypt_text(encrypted) == decrypted

