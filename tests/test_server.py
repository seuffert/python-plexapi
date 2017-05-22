# -*- coding: utf-8 -*-
import pytest, re, time
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from plexapi.utils import download
from PIL import Image, ImageStat
from requests import Session
from . import conftest as utils


def test_server_attr(plex):
    assert plex._baseurl == utils.SERVER_BASEURL
    assert len(plex.friendlyName) >= 1
    assert len(plex.machineIdentifier) == 40
    assert plex.myPlex is True
    assert plex.myPlexMappingState == 'mapped'
    assert plex.myPlexSigninState == 'ok'
    assert utils.is_int(plex.myPlexSubscription, gte=0)
    assert re.match(utils.REGEX_EMAIL, plex.myPlexUsername)
    assert plex.platform in ('Linux', 'Windows')
    assert len(plex.platformVersion) >= 5
    assert plex._token == utils.SERVER_TOKEN
    assert utils.is_int(plex.transcoderActiveVideoSessions, gte=0)
    assert utils.is_datetime(plex.updatedAt)
    assert len(plex.version) >= 5


def test_server_alert_listener(plex, movies):
    try:
        messages = []
        listener = plex.startAlertListener(messages.append)
        movies.refresh()
        starttime, runtime = time.time(), 0
        while len(messages) < 3 and runtime <= 30:
            time.sleep(1)
            runtime = int(time.time() - starttime)
        assert len(messages) >= 3
    finally:
        listener.stop()


@pytest.mark.req_client
def test_server_session():
    # TODO: Implement test_server_session
    pass


def test_server_library(plex):
    # TODO: Implement test_server_library
    assert plex.library


def test_server_url(plex):
    assert 'ohno' in plex.url('ohno')


def test_server_transcodeImage(tmpdir, plex, show):
    width, height = 500, 500
    imgurl = plex.transcodeImage(show.banner, height, width)
    gray = imgurl = plex.transcodeImage(show.banner, height, width, saturation=0)
    resized_img = download(imgurl, savepath=str(tmpdir), filename='resize_image')
    original_img = download(show._server.url(show.banner), savepath=str(tmpdir), filename='original_img')
    grayscale_img = download(gray, savepath=str(tmpdir), filename='grayscale_img')
    with Image.open(resized_img) as image:
        assert width, height == image.size
    with Image.open(original_img) as image:
        assert width, height != image.size
    assert _detect_color_image(grayscale_img, thumb_size=150) == 'grayscale'


def _detect_color_image(file, thumb_size=150, MSE_cutoff=22, adjust_color_bias=True):
    # http://stackoverflow.com/questions/20068945/detect-if-image-is-color-grayscale-or-black-and-white-with-python-pil
    pilimg = Image.open(file)
    bands = pilimg.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pilimg.resize((thumb_size, thumb_size))
        sse, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            sse += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        mse = float(sse) / (thumb_size * thumb_size)
        return 'grayscale' if mse <= MSE_cutoff else 'color'
    elif len(bands) == 1:
        return 'blackandwhite'


def test_server_search(plex, movie):
    title = movie.title
    assert plex.search(title)
    assert plex.search(title, mediatype='movie')


def test_server_playlist(plex, show):
    episodes = show.episodes()
    playlist = plex.createPlaylist('test_playlist', episodes[:3])
    try:
        assert playlist.title == 'test_playlist'
        with pytest.raises(NotFound):
            plex.playlist('<playlist-not-found>')
    finally:
        playlist.delete()


def test_server_playlists(plex, show):
    playlists = plex.playlists()
    count = len(playlists)
    episodes = show.episodes()
    playlist = plex.createPlaylist('test_playlist', episodes[:3])
    try:
        playlists = plex.playlists()
        assert len(playlists) == count + 1
    finally:
        playlist.delete()



def test_server_history(plex):
    history = plex.history()
    assert len(history)


def test_server_Server_query(plex):
    assert plex.query('/')
    with pytest.raises(BadRequest):
        assert plex.query('/asdf/1234/asdf', headers={'random_headers': '1234'})
    with pytest.raises(BadRequest):
        # This is really requests.exceptions.HTTPError
        # 401 Client Error: Unauthorized for url
        PlexServer(utils.SERVER_BASEURL, '1234')


def test_server_Server_session():
    # Mock Sesstion
    class MySession(Session):
        def __init__(self):
            super(self.__class__, self).__init__()
            self.plexapi_session_test = True
    # Test Code
    plex = PlexServer(utils.SERVER_BASEURL, utils.SERVER_TOKEN, session=MySession())
    assert hasattr(plex._session, 'plexapi_session_test')


def test_server_token_in_headers(plex):
    headers = plex._headers()
    assert 'X-Plex-Token' in headers
    assert len(headers['X-Plex-Token']) >= 1


def test_server_createPlayQueue(plex, movie):
    playqueue = plex.createPlayQueue(movie, shuffle=1, repeat=1)
    assert 'shuffle=1' in playqueue._initpath
    assert 'repeat=1' in playqueue._initpath
    assert playqueue.playQueueShuffled is True


def _test_server_createPlaylist():
    # TODO: Implement _test_server_createPlaylist()
    # see test_playlists.py
    pass


def test_server_client_not_found(plex):
    with pytest.raises(NotFound):
        plex.client('<This-client-should-not-be-found>')


def test_server_Server_sessions(plex):
    assert len(plex.sessions()) >= 0


@pytest.mark.client
def test_server_clients(plex):
    assert len(plex.clients())
    client = plex.clients()[0]
    assert client._baseurl == 'http://127.0.0.1:32400'
    assert client.device is None
    assert client.deviceClass == 'pc'
    assert client.machineIdentifier == '89hgkrbqxaxmf45o1q2949ru'
    assert client.model is None
    assert client.platform is None
    assert client.platformVersion is None
    assert client.product == 'Plex Web'
    assert client.protocol == 'plex'
    assert client.protocolCapabilities == ['timeline', 'playback', 'navigation', 'mirror', 'playqueues']
    assert client.protocolVersion == '1'
    assert client._server._baseurl == 'http://138.68.157.5:32400'
    assert client.state is None
    assert client.title == 'Plex Web (Chrome)'
    assert client.token is None
    assert client.vendor is None
    assert client.version == '2.12.5'


def test_server_account(plex):
    account = plex.account()
    assert account.authToken
    # TODO: Figure out why this is missing from time to time.
    # assert account.mappingError == 'publisherror'
    assert account.mappingErrorMessage is None
    assert account.mappingState == 'mapped'
    assert re.match(utils.REGEX_IPADDR, account.privateAddress)
    assert int(account.privatePort) >= 1000
    assert re.match(utils.REGEX_IPADDR, account.publicAddress)
    assert int(account.publicPort) >= 1000
    assert account.signInState == 'ok'
    assert isinstance(account.subscriptionActive, bool)
    if account.subscriptionActive: assert len(account.subscriptionFeatures)
    else: assert account.subscriptionFeatures == []
    assert account.subscriptionState == 'Active' if account.subscriptionActive else 'Unknown'
    assert re.match(utils.REGEX_EMAIL, account.username)


def test_server_downloadLogs(tmpdir, plex):
    plex.downloadLogs(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1


def test_server_downloadDatabases(tmpdir, plex):
    plex.downloadDatabases(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1
