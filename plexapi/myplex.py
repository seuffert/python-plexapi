# -*- coding: utf-8 -*-
import copy
import requests
import time
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, CONFIG, TIMEOUT
from plexapi import log, logfilter, utils
from plexapi.base import PlexObject
from plexapi.exceptions import BadRequest, NotFound
from plexapi.client import PlexClient
from plexapi.compat import ElementTree
from plexapi.server import PlexServer


class MyPlexAccount(PlexObject):
    """ MyPlex account and profile information. The easiest way to build
        this object is by calling the staticmethod :func:`~plexapi.myplex.MyPlexAccount.signin`
        with your username and password. This object represents the data found Account on
        the myplex.tv servers at the url https://plex.tv/users/account.

        Parameters:
            username (str): Your MyPlex username.
            password (str): Your MyPlex password.
            session (requests.Session, optional): Use your own session object if you want to
                cache the http responses from PMS
            timeout (int): timeout in seconds on initial connect to myplex (default config.TIMEOUT).

        Attributes:
            SIGNIN (str): 'https://my.plexapp.com/users/sign_in.xml'
            key (str): 'https://plex.tv/users/account'
            authenticationToken (str): Unknown.
            certificateVersion (str): Unknown.
            cloudSyncDevice (str): Unknown.
            email (str): Your current Plex email address.
            entitlements (List<str>): List of devices your allowed to use with this account.
            guest (bool): Unknown.
            home (bool): Unknown.
            homeSize (int): Unknown.
            id (str): Your Plex account ID.
            locale (str): Your Plex locale
            mailing_list_status (str): Your current mailing list status.
            maxHomeSize (int): Unknown.
            queueEmail (str): Email address to add items to your `Watch Later` queue.
            queueUid (str): Unknown.
            restricted (bool): Unknown.
            roles: (List<str>) Lit of account roles. Plexpass membership listed here.
            scrobbleTypes (str): Description
            secure (bool): Description
            subscriptionActive (bool): True if your subsctiption is active.
            subscriptionFeatures: (List<str>) List of features allowed on your subscription.
            subscriptionPlan (str): Name of subscription plan.
            subscriptionStatus (str): String representation of `subscriptionActive`.
            thumb (str): URL of your account thumbnail.
            title (str): Unknown. - Looks like an alias for `username`.
            username (str): Your account username.
            uuid (str): Unknown.
    """
    SIGNIN = 'https://my.plexapp.com/users/sign_in.xml'
    WEBHOOKS = 'https://plex.tv/api/v2/user/webhooks'
    key = 'https://plex.tv/users/account'

    def __init__(self, username=None, password=None, token=None, session=None, timeout=None):
        self._token = token
        self._session = session or requests.Session()
        data, initpath = self._signin(username, password, timeout)
        super(MyPlexAccount, self).__init__(self, data, initpath)

    def _signin(self, username, password, timeout):
        if self._token:
            return self.query(self.key), self.key
        username = username or CONFIG.get('auth.myplex_username')
        password = password or CONFIG.get('auth.myplex_password')
        data = self.query(self.SIGNIN, method=self._session.post, auth=(username, password), timeout=timeout)
        return data, self.SIGNIN

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self._token = logfilter.add_secret(data.attrib.get('authenticationToken'))
        self._webhooks = []
        self.authenticationToken = self._token
        self.certificateVersion = data.attrib.get('certificateVersion')
        self.cloudSyncDevice = data.attrib.get('cloudSyncDevice')
        self.email = data.attrib.get('email')
        self.guest = utils.cast(bool, data.attrib.get('guest'))
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.homeSize = utils.cast(int, data.attrib.get('homeSize'))
        self.id = data.attrib.get('id')
        self.locale = data.attrib.get('locale')
        self.mailing_list_status = data.attrib.get('mailing_list_status')
        self.maxHomeSize = utils.cast(int, data.attrib.get('maxHomeSize'))
        self.queueEmail = data.attrib.get('queueEmail')
        self.queueUid = data.attrib.get('queueUid')
        self.restricted = utils.cast(bool, data.attrib.get('restricted'))
        self.scrobbleTypes = data.attrib.get('scrobbleTypes')
        self.secure = utils.cast(bool, data.attrib.get('secure'))
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.username = data.attrib.get('username')
        self.uuid = data.attrib.get('uuid')
        # TODO: Fetch missing MyPlexAccount attributes
        self.subscriptionActive = None      # renamed on server
        self.subscriptionStatus = None      # renamed on server
        self.subscriptionPlan = None        # renmaed on server
        self.subscriptionFeatures = None    # renamed on server
        self.roles = None
        self.entitlements = None

    def device(self, name):
        """ Returns the :class:`~plexapi.myplex.MyPlexDevice` that matches the name specified.

            Parameters:
                name (str): Name to match against.
        """
        for device in self.devices():
            if device.name.lower() == name.lower():
                return device
        raise NotFound('Unable to find device %s' % name)

    def devices(self):
        """ Returns a list of all :class:`~plexapi.myplex.MyPlexDevice` objects connected to the server. """
        data = self.query(MyPlexDevice.key)
        return [MyPlexDevice(self, elem) for elem in data]

    def query(self, url, method=None, headers=None, timeout=None, **kwargs):
        method = method or self._session.get
        delim = '&' if '?' in url else '?'
        url = '%s%sX-Plex-Token=%s' % (url, delim, self._token)
        timeout = timeout or TIMEOUT
        log.debug('%s %s', method.__name__.upper(), url)
        allheaders = BASE_HEADERS.copy()
        allheaders.update(headers or {})
        response = method(url, headers=allheaders, timeout=timeout, **kwargs)
        if response.status_code not in (200, 201):
            codename = codes.get(response.status_code)[0]
            log.warn('BadRequest (%s) %s %s' % (response.status_code, codename, response.url))
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data.strip() else None

    def resource(self, name):
        """ Returns the :class:`~plexapi.myplex.MyPlexResource` that matches the name specified.

            Parameters:
                name (str): Name to match against.
        """
        for resource in self.resources():
            if resource.name.lower() == name.lower():
                return resource
        raise NotFound('Unable to find resource %s' % name)

    def resources(self):
        """ Returns a list of all :class:`~plexapi.myplex.MyPlexResource` objects connected to the server. """
        data = self.query(MyPlexResource.key)
        return [MyPlexResource(self, elem) for elem in data]

    def user(self, email):
        """ Returns the :class:`~myplex.MyPlexUser` that matches the email or username specified.

            Parameters:
                email (str): Username or email to match against.
        """
        for user in self.users():
            if email.lower() in (user.username.lower(), user.email.lower()):
                return user
        raise NotFound('Unable to find user %s' % email)

    def users(self):
        """ Returns a list of all :class:`~plexapi.myplex.MyPlexUser` objects connected to your account. """
        data = self.query(MyPlexUser.key)
        return [MyPlexUser(self, elem) for elem in data]

    # ---------------------
    # Webhook Commands
    def addWebhook(self, url):
        # copy _webhooks and append url
        urls = self._webhooks[:] + [url]
        return self.setWebhooks(urls)

    def deleteWebhook(self, url):
        urls = copy.copy(self._webhooks)
        if url not in urls:
            raise BadRequest('Webhook does not exist: %s' % url)
        urls.remove(url)
        return self.setWebhooks(urls)

    def setWebhooks(self, urls):
        log.info('Setting webhooks: %s' % urls)
        data = self.query(self.WEBHOOKS, self._session.post, data={'urls[]': urls})
        self._webhooks = self.listAttrs(data, 'url', etag='webhook')
        return self._webhooks

    @property
    def webhooks(self):
        data = self.query(self.WEBHOOKS)
        self._webhooks = self.listAttrs(data, 'url', etag='webhook')
        return self._webhooks


class MyPlexUser(PlexObject):
    """ This object represents non-signed in users such as friends and linked
        accounts. NOTE: This should not be confused with the :class:`~myplex.MyPlexAccount`
        which is your specific account. The raw xml for the data presented here
        can be found at: https://plex.tv/api/users/

        Attributes:
            TAG (str): 'User'
            key (str): 'https://plex.tv/api/users/'
            allowCameraUpload (bool): True if this user can upload images.
            allowChannels (bool): True if this user has access to channels.
            allowSync (bool): True if this user can sync.
            email (str): User's email address (user@gmail.com).
            filterAll (str): Unknown.
            filterMovies (str): Unknown.
            filterMusic (str): Unknown.
            filterPhotos (str): Unknown.
            filterTelevision (str): Unknown.
            home (bool): Unknown.
            id (int): User's Plex account ID.
            protected (False): Unknown (possibly SSL enabled?).
            recommendationsPlaylistId (str): Unknown.
            restricted (str): Unknown.
            thumb (str): Link to the users avatar.
            title (str): Seems to be an aliad for username.
            username (str): User's username.
    """
    TAG = 'User'
    key = 'https://plex.tv/api/users/'

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self.allowCameraUpload = utils.cast(bool, data.attrib.get('allowCameraUpload'))
        self.allowChannels = utils.cast(bool, data.attrib.get('allowChannels'))
        self.allowSync = utils.cast(bool, data.attrib.get('allowSync'))
        self.email = data.attrib.get('email')
        self.filterAll = data.attrib.get('filterAll')
        self.filterMovies = data.attrib.get('filterMovies')
        self.filterMusic = data.attrib.get('filterMusic')
        self.filterPhotos = data.attrib.get('filterPhotos')
        self.filterTelevision = data.attrib.get('filterTelevision')
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.id = utils.cast(int, data.attrib.get('id'))
        self.protected = utils.cast(bool, data.attrib.get('protected'))
        self.recommendationsPlaylistId = data.attrib.get('recommendationsPlaylistId')
        self.restricted = data.attrib.get('restricted')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.username = data.attrib.get('username')


class MyPlexResource(PlexObject):
    """ This object represents resources connected to your Plex server that can provide
        content such as Plex Media Servers, iPhone or Android clients, etc. The raw xml
        for the data presented here can be found at: https://plex.tv/api/resources?includeHttps=1

        Attributes:
            TAG (str): 'Device'
            key (str): 'https://plex.tv/api/resources?includeHttps=1'
            accessToken (str): This resources accesstoken.
            clientIdentifier (str): Unique ID for this resource.
            connections (list): List of :class:`~myplex.ResourceConnection` objects
                for this resource.
            createdAt (datetime): Timestamp this resource first connected to your server.
            device (str): Best guess on the type of device this is (PS, iPhone, Linux, etc).
            home (bool): Unknown
            lastSeenAt (datetime): Timestamp this resource last connected.
            name (str): Descriptive name of this resource.
            owned (bool): True if this resource is one of your own (you logged into it).
            platform (str): OS the resource is running (Linux, Windows, Chrome, etc.)
            platformVersion (str): Version of the platform.
            presence (bool): True if the resource is online
            product (str): Plex product (Plex Media Server, Plex for iOS, Plex Web, etc.)
            productVersion (str): Version of the product.
            provides (str): List of services this resource provides (client, server,
                player, pubsub-player, etc.)
            synced (bool): Unknown (possibly True if the resource has synced content?)
    """
    TAG = 'Device'
    key = 'https://plex.tv/api/resources?includeHttps=1'

    def _loadData(self, data):
        self._data = data
        self.name = data.attrib.get('name')
        self.accessToken = logfilter.add_secret(data.attrib.get('accessToken'))
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.device = data.attrib.get('device')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.lastSeenAt = utils.toDatetime(data.attrib.get('lastSeenAt'))
        self.provides = data.attrib.get('provides')
        self.owned = utils.cast(bool, data.attrib.get('owned'))
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.synced = utils.cast(bool, data.attrib.get('synced'))
        self.presence = utils.cast(bool, data.attrib.get('presence'))
        self.connections = self.findItems(data, ResourceConnection)

    def connect(self, ssl=None, timeout=None):
        """ Returns a new :class:`~server.PlexServer` object. Often times there is more than
            one address specified for a server or client. This function will prioritize local
            connections before remote and HTTPS before HTTP. After trying to connect to all
            available addresses for this resource and assuming at least one connection was
            successful, the PlexServer object is built and returned.

            Parameters:
                ssl (optional): Set True to only connect to HTTPS connections. Set False to
                    only connect to HTTP connections. Set None (default) to connect to any
                    HTTP or HTTPS connection.

            Raises:
                :class:`~plexapi.exceptions.NotFound`: When unable to connect to any addresses for this resource.
        """
        # Sort connections from (https, local) to (http, remote)
        # Only check non-local connections unless we own the resource
        connections = sorted(self.connections, key=lambda c: c.local, reverse=True)
        https = [c.uri for c in self.connections if self.owned or c.local]
        http = [c.httpuri for c in self.connections if self.owned or c.local]
        # Force ssl, no ssl, or any (default)
        if ssl is True: connections = https
        elif ssl is False: connections = http
        else: connections = https + http
        # Try connecting to all known resource connections in parellel, but
        # only return the first server (in order) that provides a response.
        listargs = [[PlexServer, url, self.accessToken, timeout] for url in connections]
        log.info('Testing %s resource connections..', len(listargs))
        results = utils.threaded(_connect, listargs)
        return _chooseConnection('Resource', self.name, results)


class ResourceConnection(PlexObject):
    """ Represents a Resource Connection object found within the
        :class:`~myplex.MyPlexResource` objects.

        Attributes:
            TAG (str): 'Connection'
            address (str): Local IP address
            httpuri (str): Full local address
            local (bool): True if local
            port (int): 32400
            protocol (str): HTTP or HTTPS
            uri (str): External address
    """
    TAG = 'Connection'

    def _loadData(self, data):
        self._data = data
        self.protocol = data.attrib.get('protocol')
        self.address = data.attrib.get('address')
        self.port = utils.cast(int, data.attrib.get('port'))
        self.uri = data.attrib.get('uri')
        self.local = utils.cast(bool, data.attrib.get('local'))
        self.httpuri = 'http://%s:%s' % (self.address, self.port)


class MyPlexDevice(PlexObject):
    """ This object represents resources connected to your Plex server that provide
        playback ability from your Plex Server, iPhone or Android clients, Plex Web,
        this API, etc. The raw xml for the data presented here can be found at:
        https://plex.tv/devices.xml

        Attributes:
            TAG (str): 'Device'
            key (str): 'https://plex.tv/devices.xml'
            clientIdentifier (str): Unique ID for this resource.
            connections (list): List of connection URIs for the device.
            device (str): Best guess on the type of device this is (Linux, iPad, AFTB, etc).
            id (str): MyPlex ID of the device.
            model (str): Model of the device (bueller, Linux, x86_64, etc.)
            name (str): Hostname of the device.
            platform (str): OS the resource is running (Linux, Windows, Chrome, etc.)
            platformVersion (str): Version of the platform.
            product (str): Plex product (Plex Media Server, Plex for iOS, Plex Web, etc.)
            productVersion (string): Version of the product.
            provides (str): List of services this resource provides (client, controller,
                sync-target, player, pubsub-player).
            publicAddress (str): Public IP address.
            screenDensity (str): Unknown
            screenResolution (str): Screen resolution (750x1334, 1242x2208, etc.)
            token (str): Plex authentication token for the device.
            vendor (str): Device vendor (ubuntu, etc).
            version (str): Unknown (1, 2, 1.3.3.3148-b38628e, 1.3.15, etc.)
    """
    TAG = 'Device'
    key = 'https://plex.tv/devices.xml'

    def _loadData(self, data):
        self._data = data
        self.name = data.attrib.get('name')
        self.publicAddress = data.attrib.get('publicAddress')
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.device = data.attrib.get('device')
        self.model = data.attrib.get('model')
        self.vendor = data.attrib.get('vendor')
        self.provides = data.attrib.get('provides')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.version = data.attrib.get('version')
        self.id = data.attrib.get('id')
        self.token = logfilter.add_secret(data.attrib.get('token'))
        self.screenResolution = data.attrib.get('screenResolution')
        self.screenDensity = data.attrib.get('screenDensity')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.lastSeenAt = utils.toDatetime(data.attrib.get('lastSeenAt'))
        self.connections = [connection.attrib.get('uri') for connection in data.iter('Connection')]

    def connect(self, timeout=None):
        """ Returns a new :class:`~plexapi.client.PlexClient` object. Sometimes there is more than
            one address specified for a server or client. After trying to connect to all available
            addresses for this client and assuming at least one connection was successful, the
            PlexClient object is built and returned.

            Raises:
                :class:`~plexapi.exceptions.NotFound`: When unable to connect to any addresses for this device.
        """
        listargs = [[PlexClient, url, self.token, timeout] for url in self.connections]
        log.info('Testing %s device connections..', len(listargs))
        results = utils.threaded(_connect, listargs)
        _chooseConnection('Device', self.name, results)

    def delete(self):
        """ Remove this device from your account. """
        key = 'https://plex.tv/devices/%s.xml' % self.id
        self._server.query(key, self._server._session.delete)


def _connect(cls, url, token, timeout, results, i):
    """ Connects to the specified cls with url and token. Stores the connection
        information to results[i] in a threadsafe way.
    """
    starttime = time.time()
    try:
        device = cls(baseurl=url, token=token, timeout=timeout)
        runtime = int(time.time() - starttime)
        results[i] = (url, token, device, runtime)
    except Exception as err:
        runtime = int(time.time() - starttime)
        log.error('%s: %s', url, err)
        results[i] = (url, token, None, runtime)


def _chooseConnection(ctype, name, results):
    """ Chooses the first (best) connection from the given _connect results. """
    # At this point we have a list of result tuples containing (url, token, PlexServer, runtime)
    # or (url, token, None, runtime) in the case a connection could not be established.
    for url, token, result, runtime in results:
        okerr = 'OK' if result else 'ERR'
        log.info('%s connection %s (%ss): %s?X-Plex-Token=%s', ctype, okerr, runtime, url, token)
    results = [r[2] for r in results if r and r[2] is not None]
    if results:
        log.info('Connecting to %s: %s?X-Plex-Token=%s', ctype, results[0]._baseurl, results[0]._token)
        return results[0]
    raise NotFound('Unable to connect to %s: %s' % (ctype.lower(), name))
