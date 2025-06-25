class TuneSignal(Device):
    sig = Cpt(EpicsSignalRO, ":tune")

    def trigger(self):
         def cb(**kwargs):
             print(f"Received new tune data {self.sig.name}")
             return True

         print(f"Received new tune data {self.sig.name}")
         return SubscriptionStatus(self.sig, cb, run=False, timeout=5)

class Tunes(Device):
    x = Cpt(TuneSignal, ":x")
    y = Cpt(TuneSignal, ":y")

    def trigger(self):
        return AndStatus(self.x.trigger(), self.y.trigger())
