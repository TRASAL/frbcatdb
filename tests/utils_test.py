from pyfrbcatdb import utils as pAutils

def test1_strip():
    for txt in [' test', 'test ', ' test ']:
        assert pAutils.strip(txt) == 'test'


def test2_strip():
    assert pAutils.strip(list('test')) == list('test')
