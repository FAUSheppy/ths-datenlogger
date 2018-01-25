import unittest

from datetime import datetime
from datetime import timedelta
import random
import itertools

class Timeutil_Test(unittest.TestCase):
    DATES = []
    STEPS = [ (timedelta(hours=1)),timedelta(hours=4),timedelta(days=1),timedelta(minutes=1),timedelta(minutes=3)]
    def setUpClass():
        random.seed("0")
        for x in range(0,10000):
            tmp = datetime(2018,1,1) + ( (random.random()-0.5) * timedelta(days=2*365) )
            tmp = tmp.replace(microsecond=0)
            Timeutil_Test.DATES += [ tmp ]
        
    def test_between_dates(self):
        import plot_timeutils as tu
        d = Timeutil_Test.DATES
        count = 0
        while(count < len(d)-2):
            t  = d[count+0]
            d1 = d[count+1]
            d2 = d[count+2]
            self.assertEqual(btw_wrapper(tu.between_dates(t,d1,d2),    t), d1 < t < d2, "t: "+str(t)+", d1: "+str(d1)+", d2: "+str(d2) )
            self.assertEqual(btw_wrapper(tu.between_dates(t,d1,None),  t), d1 < t , "t: "+str(t)+", d1: "+str(d1)+", d2: "+str(d2) )
            self.assertEqual(btw_wrapper(tu.between_dates(t,None,d1),  t), d1 > t , "t: "+str(t)+", d1: "+str(d1)+", d2: "+str(d2) )
            self.assertEqual(btw_wrapper(tu.between_dates(t,None,None),t), True   , "t: "+str(t)+", d1: "+str(d1)+", d2: "+str(d2) )
            count+=1


    def test_parse_time_dbf(self):
        import plot_timeutils as tu
        ind = [43121.6821296,43121.6856018,43121.689074,43121.6925462,43121.6960185,43121.6994907,43121.7029629,43121.7064351,43121.7099074,43121.7133796,43121.7168518,43121.720324,43121.7237962,43121.7272685,43121.7307407,43121.7342129,43121.7376851,43121.7411574,43121.7446296,43121.7481018,43121.751574,43121.7550462,43121.7585185,43121.7619907,43121.7654629,43121.7689351,43121.7724074,43121.7758796,43121.7793518,43121.782824,43121.7862962,43121.7897685,43121.7932407,43121.7967129,43121.8001851,43121.8036574,43121.8071296,43121.8106018,43121.814074,43121.8175462,43121.8210185,43121.8244907,43121.8279629]
        outd = ["2018-01-21 18:22:15","2018-01-21 18:27:15","2018-01-21 18:32:15","2018-01-21 18:37:15","2018-01-21 18:42:15","2018-01-21 18:47:15","2018-01-21 18:52:15","2018-01-21 18:57:15","2018-01-21 19:02:15","2018-01-21 19:07:15","2018-01-21 19:12:15","2018-01-21 19:17:15","2018-01-21 19:22:15","2018-01-21 19:27:15","2018-01-21 19:32:15","2018-01-21 19:37:15","2018-01-21 19:42:15","2018-01-21 19:47:15","2018-01-21 19:52:15","2018-01-21 19:57:15","2018-01-21 20:02:15","2018-01-21 20:07:15","2018-01-21 20:12:15","2018-01-21 20:17:15","2018-01-21 20:22:15","2018-01-21 20:27:15","2018-01-21 20:32:15","2018-01-21 20:37:15","2018-01-21 20:42:15","2018-01-21 20:47:15","2018-01-21 20:52:15","2018-01-21 20:57:15","2018-01-21 21:02:15","2018-01-21 21:07:15","2018-01-21 21:12:15","2018-01-21 21:17:15","2018-01-21 21:22:15","2018-01-21 21:27:15","2018-01-21 21:32:15","2018-01-21 21:37:15","2018-01-21 21:42:15","2018-01-21 21:47:15","2018-01-21 21:52:15"]
        for i,o in zip(ind,outd):
            self.assertEqual(str(tu.parse_time_dbf(i)),o)
    
    def test_round_time_to_step(self):
        import plot_timeutils as tu
        for s in Timeutil_Test.STEPS:
            for d in Timeutil_Test.DATES:
                rounded = tu.round_time_to_step(d,s)
                if s < timedelta(minutes=60):
                    self.assertEquals(rounded.minute * 60 % s.seconds ,0,'date: '+str(d)+' rounded: '+str(rounded)+' step: '+str(s))
                elif s < timedelta(hours=24):
                    self.assertEquals(rounded.hour*60*60  % s.seconds ,0,'date: '+str(d)+' rounded: '+str(rounded)+' step: '+str(s))
                elif s >= timedelta(days=1):
                    self.assertEquals(rounded.day         % s.days    ,0,'date: '+str(d)+' rounded: '+str(rounded)+' step: '+str(s))
                else:
                    raise AssertionError(int(s.days),0,'date: '+str(d)+' rounded: '+str(rounded)+' step: '+str(s))
            

def btw_wrapper(inp,a):
    if inp == a:
        return True
    return False
