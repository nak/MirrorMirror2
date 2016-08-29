from abc import abstractmethod, ABCMeta


class BaseUpdater(object):
    __metaclass__ = ABCMeta

    #  We aggregate all the updates to be done in a single setInterval call
    #  This MAY be more efficient as the HTML updates occur within one such call,
    #  and then GUI updates should occur in one swoop (?)
    min_update_rate = None
    updates = []
    count = 0
    interval = None
    context = None

    def __init__(self, webview, update_rate):
        self.context = webview.get_main_frame().get_global_context()
        self.webview = webview
        self.update_rate = update_rate
        assert(BaseUpdater.context == self.context or BaseUpdater.context == None)
        if BaseUpdater.min_update_rate is None or BaseUpdater.min_update_rate > update_rate:
            BaseUpdater.min_update_rate = update_rate
            self.pause()

    @classmethod
    def pause(cls):
        """
        Pause GUI information updates
        """
        if cls.interval is not None and cls.context is not None:
            cancelInterval = cls.context.get_jsobject("window").clearInterval
            cancelInterval(BaseUpdater.interval)
            BaseUpdater.interval = None

    @classmethod
    def resume(cls):
        """
        Resome info updates based on current min rate
        """
        if cls.interval is None and cls.context is not None:
           setInterval = cls.context.get_jsobject("window").setInterval
           cls.interval = setInterval(BaseUpdater.update_all, BaseUpdater.min_update_rate)

    def start(self):
        self.webview.on_view_ready(self._start)

    def _start(self):
        self._ = self.context.get_jsobject("$")
        self.update()
        # only set context of class here, as it shouldn't be used until for "on_view_ready" happens
        BaseUpdater.context = self.context
        BaseUpdater.updates.append((self.update, self.update_rate))
        self.resume()

    @classmethod
    def update_all(cls):
        """
        Cycle through all updates a needed
        """
        cls.count += 1
        for update, update_rate in cls.updates:
            cycles = update_rate/BaseUpdater.min_update_rate
            try:
                # if it's our turn based on the schedule and update rates, do the update
                if cls.count % cycles == 0:
                    update()
            except:
                import traceback
                traceback.print_exc()
                pass

    @abstractmethod
    def update(self):
        """
        Perform necessary GUI updates for this updater
        """
        pass