__author__ = 'hanno'

import time, os, sys


class TPBattSwitch():
    def __init__(self, delay=1, hysteresis=5):

        # -- Delay --
        self.delay = delay    # Delay in microseconds

        # -- Hysteresis --
        self.hysteresis = hysteresis     # Hysteresis value

        # -- AC --
        self.__ACCHRGN = -1

        # -- Battery 0 stats --
        self.__BAT0MAX = -1     # Last full capacity
        self.__BAT0REM = -1     # Remaining capacity
        self.__BAT0STA = -1     # Battery status ['idle' | 'charging' | 'discharging']
        self.__BAT0PER = -1     # Battery percentage

        # -- Battery 1 stats --
        self.__BAT1MAX = -1     # Last full capacity
        self.__BAT1REM = -1     # Remaining capacity
        self.__BAT1STA = -1     # Battery status ['idle' | 'charging' | 'discharging']
        self.__BAT1PER = -1     # Battery percentage

        # -- tpsmapi --
        self.__SMPIPTH = '/sys/devices/platform/smapi/'     # Path to tpsmapi userland

        # -- File --
        self.__CURRFIL = -1

        # Update battery stats
        self.getbattstatus()

    def _readsmapi(self, battery_n, filename):
        fullfile = os.path.join(self.__SMPIPTH, battery_n, filename)

        try:
            self.__CURRFIL = open(fullfile)
        except IOError:
            print('Could not open file: ' + fullfile)
            return -1
        try:
            data = self.__CURRFIL.read()
        except IOError:
            print('Could not read file: ' + fullfile)
            return -1
        try:
            self.__CURRFIL.close()
        except IOError:
            print('Could not close file: ' + fullfile)
            return -1

        return data

    def _writesmapi(self, battery_n, filename, value):
        fullfile = os.path.join(self.__SMPIPTH, battery_n, filename)

        try:
            self.__CURRFIL = open(fullfile, 'w+')
        except IOError:
            print('Could not open file: ' + fullfile)
            return False
        try:
            self.__CURRFIL.write(value)
        except IOError:
            print('Could not write file: ' + fullfile)
            return False
        try:
            self.__CURRFIL.close()
        except IOError:
            print('Could not close file: ' + fullfile)
            return False

        return True

    def getbattstatus(self):
        self.__ACCHRGN = self._readsmapi('', 'ac_connected').rstrip()
        print self.__ACCHRGN
        self.__BAT0STA = self._readsmapi('BAT0', 'state').rstrip()
        self.__BAT1STA = self._readsmapi('BAT1', 'state').rstrip()
        self.__BAT0REM = self._readsmapi('BAT0', 'remaining_capacity')
        self.__BAT1REM = self._readsmapi('BAT1', 'remaining_capacity')
        self.__BAT0MAX = self._readsmapi('BAT0', 'last_full_capacity')
        self.__BAT1MAX = self._readsmapi('BAT1', 'last_full_capacity')

        self.__BAT0PER = float(self.__BAT0REM) / float(self.__BAT0MAX) * 100
        self.__BAT1PER = float(self.__BAT1REM) / float(self.__BAT1MAX) * 100

    def stopdischrg(self):
        self._writesmapi("BAT1", "force_discharge", "0")
        self._writesmapi("BAT0", "force_discharge", "0")

    def switchchrg(self):
        print("BAT0: %.2f" % self.__BAT0PER + " " + self.__BAT0STA +
              " - BAT1: %.2f" % self.__BAT1PER + " " + self.__BAT1STA)

        if self.__ACCHRGN == str(1):
            self.stopdischrg()
        else:
            if self.__BAT0PER - self.__BAT1PER >= self.hysteresis and "idle" in self.__BAT0STA:
                print("Switch to BAT0")
                self._writesmapi("BAT1", "force_discharge", "0")
                self._writesmapi("BAT0", "force_discharge", "1")

            elif self.__BAT1PER - self.__BAT0PER >= self.hysteresis and "idle" in self.__BAT1STA:
                print("Switch to BAT1")
                self._writesmapi("BAT0", "force_discharge", "0")
                self._writesmapi("BAT1", "force_discharge", "1")
        return

    def close(self):
        self.stopdischrg()
        try:
            self._CURRFIL.close()
        except:
            pass


def main():
    tpswitch = TPBattSwitch()
    tpswitch.delay = 1
    tpswitch.hysteresis = 5
    while True:
        try:
            os.system('clear')
            tpswitch.getbattstatus()
            tpswitch.switchchrg()
            time.sleep(tpswitch.delay)
        #except KeyboardInterrupt:
        #    print("Exiting...")
        #    tpswitch.close()
        #    sys.exit()
        except:
            tpswitch.close()
            sys.exit()

if __name__ == "__main__":
    main()