from sqlalchemy import inspect

from database import Phone, Computer, SimCard


def test_device_models_have_note_column():
    assert 'note' in inspect(Phone).columns.keys()
    assert 'note' in inspect(Computer).columns.keys()
    assert 'note' in inspect(SimCard).columns.keys()
