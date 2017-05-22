# -*- coding: utf-8 -*-
import pytest
from datetime import datetime
from plexapi.exceptions import BadRequest, NotFound
from . import conftest as utils


def test_video_Movie(movies, movie):
    movie2 = movies.get(movie.title)
    assert movie2.title == movie.title


def test_video_Movie_delete(monkeypatch, movie):
    monkeypatch.delattr('requests.sessions.Session.request')
    with pytest.raises(AttributeError):
        movie.delete()


def test_video_Movie_getStreamURL(movie):
    key = movie.ratingKey
    assert movie.getStreamURL() == '{0}/video/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F{1}&X-Plex-Token={2}'.format(utils.SERVER_BASEURL, key, utils.SERVER_TOKEN)  # noqa
    assert movie.getStreamURL(videoResolution='800x600') == '{0}/video/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F{1}&videoResolution=800x600&X-Plex-Token={2}'.format(utils.SERVER_BASEURL, key, utils.SERVER_TOKEN)  # noqa


def test_video_Movie_isFullObject_and_reload(plex):
    movie = plex.library.section('Movies').get('Sita Sings the Blues')
    assert movie.isFullObject() is False
    movie.reload()
    assert movie.isFullObject() is True
    movie_via_search = plex.library.search(movie.title)[0]
    assert movie_via_search.isFullObject() is False
    movie_via_search.reload()
    assert movie_via_search.isFullObject() is True
    movie_via_section_search = plex.library.section('Movies').search(movie.title)[0]
    assert movie_via_section_search.isFullObject() is False
    movie_via_section_search.reload()
    assert movie_via_section_search.isFullObject() is True
    # If the verify that the object has been reloaded. xml from search only returns 3 actors.
    assert len(movie_via_section_search.roles) > 3


def test_video_Movie_isPartialObject(movie):
    assert movie.isPartialObject()


def test_video_Movie_iterParts(movie):
    assert len(list(movie.iterParts())) >= 1


def test_video_Movie_download(monkeydownload, tmpdir, movie):
    filepaths1 = movie.download(savepath=str(tmpdir))
    assert len(filepaths1) >= 1
    filepaths2 = movie.download(savepath=str(tmpdir), videoResolution='500x300')
    assert len(filepaths2) >= 1


def test_video_Movie_attrs(movies):
    movie = movies.get('Sita Sings the Blues')
    assert len(movie.locations[0]) >= 10
    assert utils.is_datetime(movie.addedAt)
    assert utils.is_metadata(movie.art)
    assert movie.audienceRating == 8.5
    assert movie.audienceRatingImage == 'rottentomatoes://image.rating.upright'
    movie.reload()  # RELOAD
    assert movie.chapterSource is None
    assert movie.collections == []
    assert movie.contentRating in utils.CONTENTRATINGS
    assert all([i.tag in ['US', 'USA'] for i in movie.countries])
    assert [i.tag for i in movie.directors] == ['Nina Paley']
    assert movie.duration >= 160000
    assert movie.fields == []
    assert sorted([i.tag for i in movie.genres]) == ['Animation', 'Comedy', 'Fantasy', 'Musical', 'Romance']
    assert movie.guid == 'com.plexapp.agents.imdb://tt1172203?lang=en'
    assert utils.is_metadata(movie._initpath)
    assert utils.is_metadata(movie.key)
    if movie.lastViewedAt:
        assert utils.is_datetime(movie.lastViewedAt)
    assert int(movie.librarySectionID) >= 1
    assert movie.listType == 'video'
    assert movie.originalTitle is None
    assert movie.originallyAvailableAt.strftime('%Y-%m-%d') in ('2008-01-11', '2008-02-11')
    assert movie.player is None
    assert movie.playlistItemID is None
    if movie.primaryExtraKey:
        assert utils.is_metadata(movie.primaryExtraKey)
    assert [i.tag for i in movie.producers] == []
    assert float(movie.rating) >= 6.4
    assert movie.ratingImage == 'rottentomatoes://image.rating.ripe'
    assert movie.ratingKey >= 1
    assert sorted([i.tag for i in movie.roles])[:4] == ['Aladdin Ullah', 'Annette Hanshaw', 'Aseem Chhabra', 'Debargo Sanyal']  # noqa
    assert movie._server._baseurl == utils.SERVER_BASEURL
    assert movie.sessionKey is None
    assert movie.studio is None
    assert utils.is_string(movie.summary, gte=100)
    assert movie.tagline == 'The Greatest Break-Up Story Ever Told'
    assert utils.is_thumb(movie.thumb)
    assert movie.title == 'Sita Sings the Blues'
    assert movie.titleSort == 'Sita Sings the Blues'
    assert movie.transcodeSession is None
    assert movie.type == 'movie'
    assert movie.updatedAt > datetime(2017, 1, 1)
    assert movie.userRating is None
    assert movie.username is None
    assert movie.viewCount == 0
    assert utils.is_int(movie.viewOffset, gte=0)
    assert movie.viewedAt is None
    assert sorted([i.tag for i in movie.writers][:4]) == ['Nina Paley']  # noqa
    assert movie.year == 2008
    # Audio
    audio = movie.media[0].parts[0].audioStreams()[0]
    if audio.audioChannelLayout:
        assert audio.audioChannelLayout in utils.AUDIOLAYOUTS
    assert audio.bitDepth is None
    assert utils.is_int(audio.bitrate)
    assert audio.bitrateMode is None
    assert audio.channels in utils.AUDIOCHANNELS
    assert audio.codec in utils.CODECS
    assert audio.codecID is None
    assert audio.dialogNorm is None
    assert audio.duration is None
    assert audio.id >= 1
    assert audio.index == 1
    assert utils.is_metadata(audio._initpath)
    assert audio.language == 'English'
    assert audio.languageCode == 'eng'
    assert audio.samplingRate == 48000
    assert audio.selected is True
    assert audio._server._baseurl == utils.SERVER_BASEURL
    assert audio.streamType == 2
    assert audio.title is None
    assert audio.type == 2
    # Media
    media = movie.media[0]
    assert media.aspectRatio >= 1.3
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=160000)
    assert utils.is_int(media.height)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    assert media.optimizedForStreaming in [None, False, True]
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=200)
    # Video
    video = movie.media[0].parts[0].videoStreams()[0]
    assert video.bitDepth == 8
    assert utils.is_int(video.bitrate)
    assert video.cabac is None
    assert video.chromaSubsampling == '4:2:0'
    assert video.codec in utils.CODECS
    assert video.codecID is None
    assert video.colorSpace == 'bt709'
    assert video.duration is None
    assert utils.is_float(video.frameRate, gte=20.0)
    assert video.frameRateMode is None
    assert video.hasScallingMatrix is None
    assert utils.is_int(video.height, gte=250)
    assert utils.is_int(video.id)
    assert utils.is_int(video.index, gte=0)
    assert utils.is_metadata(video._initpath)
    assert video.language == 'English'
    assert video.languageCode == 'eng'
    assert utils.is_int(video.level)
    assert video.profile in utils.PROFILES
    assert utils.is_int(video.refFrames)
    assert video.scanType is None
    assert video.selected is False
    assert video._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(video.streamType)
    assert video.title is None
    assert video.type == 1
    assert utils.is_int(video.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.container in utils.CONTAINERS
    assert utils.is_int(part.duration, 160000)
    assert len(part.file) >= 10
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(part.size, gte=1000000)
    # Stream 1
    stream1 = part.streams[0]
    assert stream1.bitDepth == 8
    assert utils.is_int(stream1.bitrate)
    assert stream1.cabac is None
    assert stream1.chromaSubsampling == '4:2:0'
    assert stream1.codec in utils.CODECS
    assert stream1.codecID is None
    assert stream1.colorSpace == 'bt709'
    assert stream1.duration is None
    assert utils.is_float(stream1.frameRate, gte=20.0)
    assert stream1.frameRateMode is None
    assert stream1.hasScallingMatrix is None
    assert utils.is_int(stream1.height, gte=250)
    assert utils.is_int(stream1.id)
    assert utils.is_int(stream1.index, gte=0)
    assert utils.is_metadata(stream1._initpath)
    assert stream1.language == 'English'
    assert stream1.languageCode == 'eng'
    assert utils.is_int(stream1.level)
    assert stream1.profile in utils.PROFILES
    assert utils.is_int(stream1.refFrames)
    assert stream1.scanType is None
    assert stream1.selected is False
    assert stream1._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(stream1.streamType)
    assert stream1.title is None
    assert stream1.type == 1
    assert utils.is_int(stream1.width, gte=400)
    # Stream 2
    stream2 = part.streams[1]
    if stream2.audioChannelLayout:
        assert stream2.audioChannelLayout in utils.AUDIOLAYOUTS
    assert stream2.bitDepth is None
    assert utils.is_int(stream2.bitrate)
    assert stream2.bitrateMode is None
    assert stream2.channels in utils.AUDIOCHANNELS
    assert stream2.codec in utils.CODECS
    assert stream2.codecID is None
    assert stream2.dialogNorm is None
    assert stream2.duration is None
    assert utils.is_int(stream2.id)
    assert utils.is_int(stream2.index)
    assert utils.is_metadata(stream2._initpath)
    assert stream2.language == 'English'
    assert stream2.languageCode == 'eng'
    assert utils.is_int(stream2.samplingRate)
    assert stream2.selected is True
    assert stream2._server._baseurl == utils.SERVER_BASEURL
    assert stream2.streamType == 2
    assert stream2.title is None
    assert stream2.type == 2


def test_video_Show(show):
    assert show.title == 'Game of Thrones'


def test_video_Show_attrs(show):
    assert utils.is_datetime(show.addedAt)
    assert utils.is_metadata(show.art, contains='/art/')
    assert utils.is_metadata(show.banner, contains='/banner/')
    assert utils.is_int(show.childCount)
    assert show.contentRating in utils.CONTENTRATINGS
    assert utils.is_int(show.duration, gte=1600000)
    assert utils.is_section(show._initpath)
    # Check reloading the show loads the full list of genres
    assert sorted([i.tag for i in show.genres]) == ['Adventure', 'Drama', 'Fantasy']
    show.reload()
    assert sorted([i.tag for i in show.genres]) == ['Adventure', 'Drama', 'Fantasy']
    # So the initkey should have changed because of the reload
    assert utils.is_metadata(show._initpath)
    assert utils.is_int(show.index)
    assert utils.is_metadata(show.key)
    if show.lastViewedAt:
        assert utils.is_datetime(show.lastViewedAt)
    assert utils.is_int(show.leafCount)
    assert show.listType == 'video'
    assert len(show.locations[0]) >= 10
    assert show.originallyAvailableAt.strftime('%Y-%m-%d') == '2011-04-17'
    assert show.rating >= 8.0
    assert utils.is_int(show.ratingKey)
    assert sorted([i.tag for i in show.roles])[:4] == ['Aidan Gillen', 'Alexander Siddig', 'Alfie Allen', 'Amrita Acharia']
    assert sorted([i.tag for i in show.actors])[:4] == ['Aidan Gillen', 'Alexander Siddig', 'Alfie Allen', 'Amrita Acharia']
    assert show._server._baseurl == utils.SERVER_BASEURL
    assert show.studio == 'HBO'
    assert utils.is_string(show.summary, gte=100)
    assert utils.is_metadata(show.theme, contains='/theme/')
    assert utils.is_metadata(show.thumb, contains='/thumb/')
    assert show.title == 'Game of Thrones'
    assert show.titleSort == 'Game of Thrones'
    assert show.type == 'show'
    assert utils.is_datetime(show.updatedAt)
    assert utils.is_int(show.viewCount, gte=0)
    assert utils.is_int(show.viewedLeafCount, gte=0)
    assert show.year == 2011


def test_video_Show_watched(tvshows):
    show = tvshows.get('The 100')
    show.episodes()[0].markWatched()
    watched = show.watched()
    assert len(watched) == 1 and watched[0].title == 'Pilot'


def test_video_Show_unwatched(tvshows):
    show = tvshows.get('The 100')
    episodes = show.episodes()
    episodes[0].markWatched()
    unwatched = show.unwatched()
    assert len(unwatched) == len(episodes) - 1


def test_video_Show_location(plex):
    # This should be a part of test test_video_Show_attrs but is excluded
    # because of https://github.com/mjs7231/python-plexapi/issues/97
    show = plex.library.section('TV Shows').get('The 100')
    assert len(show.locations) >= 1


def test_video_Show_reload(plex):
    show = plex.library.section('TV Shows').get('Game of Thrones')
    assert utils.is_metadata(show._initpath, prefix='/library/sections/')
    assert len(show.roles) == 3
    show.reload()
    assert utils.is_metadata(show._initpath, prefix='/library/metadata/')
    assert len(show.roles) > 3


def test_video_Show_episodes(tvshows):
    show = tvshows.get('The 100')
    episodes = show.episodes()
    episodes[0].markWatched()
    unwatched = show.episodes(viewCount=0)
    assert len(unwatched) == len(episodes) - 1


def test_video_Show_download(monkeydownload, tmpdir, show):
    episodes = show.episodes()
    filepaths = show.download(savepath=str(tmpdir))
    assert len(filepaths) == len(episodes)


def test_video_Season_download(monkeydownload, tmpdir, show):
    season = show.season('Season 1')
    filepaths = season.download(savepath=str(tmpdir))
    assert len(filepaths) >= 4


def test_video_Episode_download(monkeydownload, tmpdir, episode):
    f = episode.download(savepath=str(tmpdir))
    assert len(f) == 1
    with_sceen_size = episode.download(savepath=str(tmpdir), **{'videoResolution': '500x300'})
    assert len(with_sceen_size) == 1


def test_video_Show_thumbUrl(show):
    assert utils.SERVER_BASEURL in show.thumbUrl
    assert '/library/metadata/' in show.thumbUrl
    assert '/thumb/' in show.thumbUrl


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Show_analyze(show):
    show = show.analyze()


def test_video_Show_markWatched(show):
    show.markWatched()
    assert show.isWatched


def test_video_Show_markUnwatched(show):
    show.markUnwatched()
    assert not show.isWatched


def test_video_Show_refresh(show):
    show.refresh()


def test_video_Show_get(show):
    assert show.get('Winter Is Coming').title == 'Winter Is Coming'


def test_video_Show_isWatched(show):
    assert not show.isWatched


def test_video_Show_section(show):
    section = show.section()
    assert section.title == 'TV Shows'


def test_video_Episode(show):
    episode = show.episode('Winter Is Coming')
    assert episode == show.episode(season=1, episode=1)
    with pytest.raises(BadRequest):
        show.episode()
    with pytest.raises(NotFound):
        show.episode(season=1337, episode=1337)


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Episode_analyze(tvshows):
    episode = tvshows.get('Game of Thrones').episode(season=1, episode=1)
    episode.analyze()


def test_video_Episode_attrs(episode):
    assert utils.is_datetime(episode.addedAt)
    assert episode.contentRating in utils.CONTENTRATINGS
    assert [i.tag for i in episode.directors] == ['Tim Van Patten']
    assert utils.is_int(episode.duration, gte=120000)
    assert episode.grandparentTitle == 'Game of Thrones'
    assert episode.index == 1
    assert utils.is_metadata(episode._initpath)
    assert utils.is_metadata(episode.key)
    assert episode.listType == 'video'
    assert episode.originallyAvailableAt.strftime('%Y-%m-%d') == '2011-04-17'
    assert utils.is_int(episode.parentIndex)
    assert utils.is_metadata(episode.parentKey)
    assert utils.is_int(episode.parentRatingKey)
    assert utils.is_metadata(episode.parentThumb, contains='/thumb/')
    assert episode.player is None
    assert episode.rating >= 7.7
    assert utils.is_int(episode.ratingKey)
    assert episode._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_string(episode.summary, gte=100)
    assert utils.is_metadata(episode.thumb, contains='/thumb/')
    assert episode.title == 'Winter Is Coming'
    assert episode.titleSort == 'Winter Is Coming'
    assert episode.transcodeSession is None
    assert episode.type == 'episode'
    assert utils.is_datetime(episode.updatedAt)
    assert episode.username is None
    assert utils.is_int(episode.viewCount, gte=0)
    assert episode.viewOffset == 0
    assert [i.tag for i in episode.writers] == ['David Benioff', 'D. B. Weiss']
    assert episode.year == 2011
    assert episode.isWatched in [True, False]
    # Media
    media = episode.media[0]
    assert media.aspectRatio == 1.78
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=150000)
    assert utils.is_int(media.height, gte=200)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    if media.optimizedForStreaming:
        assert isinstance(media.optimizedForStreaming, bool)
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.container in utils.CONTAINERS
    assert utils.is_int(part.duration, gte=150000)
    assert len(part.file) >= 10
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(part.size, gte=30000000)


def test_video_Season(show):
    seasons = show.seasons()
    assert len(seasons) >= 1
    assert ['Season 1', 'Season 2'] == [s.title for s in seasons[:2]]
    assert show.season('Season 1') == seasons[0]


def test_video_Season_attrs(show):
    season = show.season('Season 1')
    assert utils.is_datetime(season.addedAt)
    assert season.index == 1
    assert utils.is_metadata(season._initpath)
    assert utils.is_metadata(season.key)
    if season.lastViewedAt:
        assert utils.is_datetime(season.lastViewedAt)
    assert utils.is_int(season.leafCount, gte=3)
    assert season.listType == 'video'
    assert utils.is_metadata(season.parentKey)
    assert utils.is_int(season.parentRatingKey)
    assert season.parentTitle == 'Game of Thrones'
    assert utils.is_int(season.ratingKey)
    assert season._server._baseurl == utils.SERVER_BASEURL
    assert season.summary == ''
    assert utils.is_metadata(season.thumb, contains='/thumb/') 
    assert season.title == 'Season 1'
    assert season.titleSort == 'Season 1'
    assert season.type == 'season'
    assert utils.is_datetime(season.updatedAt)
    assert utils.is_int(season.viewCount, gte=0)
    assert utils.is_int(season.viewedLeafCount, gte=0)
    assert utils.is_int(season.seasonNumber)


def test_video_Season_show(show):
    season = show.seasons()[0]
    season_by_name = show.season('Season 1')
    assert show.ratingKey == season.parentRatingKey and season_by_name.parentRatingKey
    assert season.ratingKey == season_by_name.ratingKey


def test_video_Season_watched(tvshows):
    show = tvshows.get('Game of Thrones')
    season = show.season(1)
    sne = show.season('Season 1')
    assert season == sne
    season.markWatched()
    assert season.isWatched


def test_video_Season_unwatched(tvshows):
    season = tvshows.get('Game of Thrones').season(1)
    season.markUnwatched()
    assert not season.isWatched


def test_video_Season_get(show):
    episode = show.season(1).get('Winter Is Coming')
    assert episode.title == 'Winter Is Coming'


def test_video_Season_episode(show):
    episode = show.season(1).get('Winter Is Coming')
    assert episode.title == 'Winter Is Coming'


def test_video_Season_episodes(show):
    episodes = show.season(2).episodes()
    assert len(episodes) >= 1


def test_that_reload_return_the_same_object(plex):
    # we want to check this that all the urls are correct
    movie_library_search = plex.library.section('Movies').search('Elephants Dream')[0]
    movie_search = plex.search('Elephants Dream')[0]
    movie_section_get = plex.library.section('Movies').get('Elephants Dream')
    movie_library_search_key = movie_library_search.key
    movie_search_key = movie_search.key
    movie_section_get_key = movie_section_get.key
    assert movie_library_search_key == movie_library_search.reload().key == movie_search_key == movie_search.reload().key == movie_section_get_key == movie_section_get.reload().key  # noqa
    tvshow_library_search = plex.library.section('TV Shows').search('The 100')[0]
    tvshow_search = plex.search('The 100')[0]
    tvshow_section_get = plex.library.section('TV Shows').get('The 100')
    tvshow_library_search_key = tvshow_library_search.key
    tvshow_search_key = tvshow_search.key
    tvshow_section_get_key = tvshow_section_get.key
    assert tvshow_library_search_key == tvshow_library_search.reload().key == tvshow_search_key == tvshow_search.reload().key == tvshow_section_get_key == tvshow_section_get.reload().key  # noqa
    season_library_search = tvshow_library_search.season(1)
    season_search = tvshow_search.season(1)
    season_section_get = tvshow_section_get.season(1)
    season_library_search_key = season_library_search.key
    season_search_key = season_search.key
    season_section_get_key = season_section_get.key
    assert season_library_search_key == season_library_search.reload().key == season_search_key == season_search.reload().key == season_section_get_key == season_section_get.reload().key  # noqa
    episode_library_search = tvshow_library_search.episode(season=1, episode=1)
    episode_search = tvshow_search.episode(season=1, episode=1)
    episode_section_get = tvshow_section_get.episode(season=1, episode=1)
    episode_library_search_key = episode_library_search.key
    episode_search_key = episode_search.key
    episode_section_get_key = episode_section_get.key
    assert episode_library_search_key == episode_library_search.reload().key == episode_search_key == episode_search.reload().key == episode_section_get_key == episode_section_get.reload().key  # noqa
