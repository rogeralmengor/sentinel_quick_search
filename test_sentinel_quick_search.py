from .utils import *


def test_modify_year_in_date():
    date = "03.05.22"
    assert "20220503" == reverse_year_in_date(modify_year_in_date(date))

def test_reverse_year_in_date():
    date = "03052022"
    assert "20220503" == reverse_year_in_date(date) 