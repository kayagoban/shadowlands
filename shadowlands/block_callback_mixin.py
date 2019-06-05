from cached_property import cached_property
import logging

class BlockCallbackMixin():
    '''
    This mixin gives you free expiry of cached properties upon a new block.  
    Also lets the class implement new_block_callback()
    to implement custom behavior.

    Implementing class is responsible for implementing
    _block_callback_watcher.register_target(self)
    and
    _block_callback_watcher.unregister_target(self)
    '''
    def new_block_callback(self):
        '''
         Override this callback in your dapp to perform actions 
         upon new block
         '''
        pass


    def _new_block_callback(self):
        '''
        This is the private version of new_block_callback.
        It expires the caches of any cached_properties.
        '''
        self._expire_cached_properties()
        self.new_block_callback()

    def _expire_cached_properties(self):
        objects = self.__class__.__dict__.values()
        c_props = [x for x in objects if x.__class__ == cached_property]
        if len(c_props) == 0:
            return

        logging.info("{} attempting to expire {} properties".format(
            str(self.__class__),
            str(len(c_props))
        ))

        for prop in c_props:
            try:
                del self.__dict__[prop.func.__name__]
                logging.info("{} expired {}".format(
                    str(self.__class__),
                    prop.func.__name__
                ))
            except KeyError as e:
                logging.debug("no need to expire {}".format(str(e)))


