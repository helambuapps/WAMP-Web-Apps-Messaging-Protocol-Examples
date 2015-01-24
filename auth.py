from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from autobahn import wamp

import asyncio

USER = 'eddie'
PASSWORD = 'secret1'


class MyBackendComponent(ApplicationSession):
    USERDB = {
        'joe': {
            'secret': 'secret2',
            'role': 'backend'
        },
        'peter': {
            'secret': 'prq7+YkJ1/KlW1X0YczMHw==',
            'role': 'frontend',
            'salt': 'salt123',
            'iterations': 100,
            'keylen': 16
        }
    }

    @wamp.register('com.example.authenticate')
    def authenticate(self, realm, authid, details):
        print("authenticate called: realm = '{}', authid = '{}', details = '{}'".format(realm, authid, details))

        if authid in self.USERDB:
            return self.USERDB[authid]

    def onConnect(self):
        print("connected. joining realm {} asser {} ...".format(self.config.realm, USER))
        self.join(self.config.realm, ["wampcra"], USER)

    def onChallenge(self, challenge):
        print("authentication challenge received: {}".format(challenge))
        if challenge.method == "wampcra":
            if'salt' in challenge.extra:
                key = auth.derive_key(PASSWORD.encode('utf8'),
                                      challenge.extra['salt'].encode('utf8'),
                                      challenge.extra.get('iterations', None),
                                      challenge.extra.get('keylen', None))
            else:
                key = PASSWORD.encode('utf8')
            signature = auth.compute_wcs(key, challenge.extra['challenge'].encode('utf8'))
            return signature.decode('ascii')
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))

    @asyncio.coroutine
    def onJoin(self, details):
        res = yield from self.register(self)
        print("{} procedures registered.".format(len(res)))


    def onLeave(self, details):
        print("onLeave: {}".format(details))
        self.disconnect()


if __name__ == '__main__':
    from autobahn.asyncio.wamp import ApplicationRunner

    runner = ApplicationRunner(url="ws://localhost:9000/ws", realm="realm1")
    runner.run(MyBackendComponent)