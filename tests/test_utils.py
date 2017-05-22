# -*- coding: utf-8 -*-
import pytest, time
import plexapi.utils as utils
from plexapi.exceptions import NotFound


def test_utils_toDatetime():
    assert str(utils.toDatetime('2006-03-03', format='%Y-%m-%d')) == '2006-03-03 00:00:00'
    assert str(utils.toDatetime('0'))[:-9] in ['1970-01-01', '1969-12-31']


def test_utils_threaded():
    def _squared(num, results, i):
        time.sleep(0.5)
        results[i] = num * num
    starttime = time.time()
    results = utils.threaded(_squared, [[1], [2], [3], [4], [5]])
    assert results == [1, 4, 9, 16, 25]
    assert (time.time() - starttime) < 1


@pytest.mark.req_client
def test_utils_downloadSessionImages():
    # TODO: Implement test_utils_downloadSessionImages()
    pass


def test_utils_searchType():
    st = utils.searchType('movie')
    assert st == 1
    movie = utils.searchType(1)
    assert movie == '1'
    with pytest.raises(NotFound):
        utils.searchType('kekekekeke')


def test_utils_joinArgs():
    test_dict = {'genre': 'action', 'type': 1337}
    assert utils.joinArgs(test_dict) == '?genre=action&type=1337'


def test_utils_cast():
    int_int = utils.cast(int, 1)
    int_str = utils.cast(int, '1')
    bool_str = utils.cast(bool, '1')
    bool_int = utils.cast(bool, 1)
    float_int = utils.cast(float, 1)
    float_float = utils.cast(float, 1.0)
    float_str = utils.cast(float, '1.2')
    float_nan = utils.cast(float, 'wut?')
    assert int_int == 1 and isinstance(int_int, int)
    assert int_str == 1 and isinstance(int_str, int)
    assert bool_str is True
    assert bool_int is True
    assert float_int == 1.0 and isinstance(float_int, float)
    assert float_float == 1.0 and isinstance(float_float, float)
    assert float_str == 1.2 and isinstance(float_str, float)
    assert float_nan != float_nan  # nan is never equal
    with pytest.raises(ValueError):
        bool_str = utils.cast(bool, 'kek')


def test_utils_download(episode):
    url = episode.getStreamURL()
    locations = episode.locations[0]
    session = episode._server._session
    assert utils.download(url, filename=locations, mocked=True)
    assert utils.download(url, filename=locations, session=session, mocked=True)
    assert utils.download(episode.thumbUrl, filename=episode.title, mocked=True)
