from abc import ABC


class INetworkMapRepository(ABC):

    # TODO Define NetMap object
    def get_map(self) -> NetMap:
        pass

    def save_netmap(self, netmap: NetMap):
        pass