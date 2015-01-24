from autobahn.asyncio import wamp
from autobahn.wamp import auth

import asyncio

USER = 'peter'
PASSWORD = 'secret1'


class MyFrontendComponent(wamp.ApplicationSession):

    def onConnect(self):
        print("connected. joining realm {} asser {} ...".format(self.config.realm, USER))
        self.join(self.config.realm, [u"wampcra"], USER)

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
        res = yield from self.call('com.example.add2', 2, 3)
        print("called procedure add2 {}".format(res))

    def onLeave(self, details):
        print("onLeave: {}".format(details))
        self.disconnect()


if __name__ == '__main__':
    from autobahn.asyncio.wamp import ApplicationRunner

    runner = ApplicationRunner(url="ws://localhost:8080/ws", realm="realm1")
    runner.run(MyFrontendComponent)