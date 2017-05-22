# -*- coding: utf-8 -*-


def test_myplex_accounts(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    print('MyPlexAccount:')
    print('username: %s' % account.username)
    print('email: %s' % account.email)
    print('home: %s' % account.home)
    print('queueEmail: %s' % account.queueEmail)
    assert account.username, 'Account has no username'
    assert account.authenticationToken, 'Account has no authenticationToken'
    assert account.email, 'Account has no email'
    assert account.home is not None, 'Account has no home'
    assert account.queueEmail, 'Account has no queueEmail'
    account = plex.account()
    print('Local PlexServer.account():')
    print('username: %s' % account.username)
    print('authToken: %s' % account.authToken)
    print('signInState: %s' % account.signInState)
    assert account.username, 'Account has no username'
    assert account.authToken, 'Account has no authToken'
    assert account.signInState, 'Account has no signInState'


def test_myplex_resources(account):
    assert account, 'Must specify username, password & resource to run this test.'
    resources = account.resources()
    for resource in resources:
        name = resource.name or 'Unknown'
        connections = [c.uri for c in resource.connections]
        connections = ', '.join(connections) if connections else 'None'
        print('%s (%s): %s' % (name, resource.product, connections))
    assert resources, 'No resources found for account: %s' % account.name


def test_myplex_connect_to_resource(plex, account):
    servername = plex.friendlyName
    for resource in account.resources():
        if resource.name == servername:
            break
    assert resource.connect(timeout=10)


def test_myplex_devices(account):
    devices = account.devices()
    for device in devices:
        name = device.name or 'Unknown'
        connections = ', '.join(device.connections) if device.connections else 'None'
        print('%s (%s): %s' % (name, device.product, connections))
    assert devices, 'No devices found for account: %s' % account.name


def _test_myplex_connect_to_device(account):
    devices = account.devices()
    for device in devices:
        if device.name == 'some client name' and len(device.connections):
            break
    client = device.connect()
    assert client, 'Unable to connect to device'


def test_myplex_users(account):
    users = account.users()
    assert users, 'Found no users on account: %s' % account.name
    print('Found %s users.' % len(users))
    user = account.user(users[0].title)
    print('Found user: %s' % user)
    assert user, 'Could not find user %s' % users[0].title
