
import da
PatternExpr_27 = da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Ready')])
PatternExpr_28 = da.pat.FreePattern('source')
PatternExpr_29 = da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Done'), da.pat.FreePattern('time')])
PatternExpr_30 = da.pat.FreePattern('source')
PatternExpr_31 = da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Start')])
PatternExpr_33 = da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Terminate')])
PatternExpr_32 = da.pat.TuplePattern([da.pat.FreePattern(None), da.pat.TuplePattern([da.pat.FreePattern(None), da.pat.FreePattern(None), da.pat.FreePattern(None)]), da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Start')])])
PatternExpr_34 = da.pat.TuplePattern([da.pat.FreePattern(None), da.pat.TuplePattern([da.pat.FreePattern(None), da.pat.FreePattern(None), da.pat.FreePattern(None)]), da.pat.TuplePattern([da.pat.ConstantPattern('CTL_Terminate')])])
import time
import json

class Controller(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_ControllerReceivedEvent_0', PatternExpr_27, sources=[PatternExpr_28], destinations=None, timestamps=None, record_history=None, handlers=[self._Controller_handler_3]), da.pat.EventPattern(da.pat.ReceivedEvent, '_ControllerReceivedEvent_1', PatternExpr_29, sources=[PatternExpr_30], destinations=None, timestamps=None, record_history=None, handlers=[self._Controller_handler_4])])

    def main(self):
        _st_label_98 = 0
        while (_st_label_98 == 0):
            _st_label_98 += 1
            if (self.readys == self.nprocs):
                _st_label_98 += 1
            else:
                super()._label('_st_label_98', block=True)
                _st_label_98 -= 1
        self.verboutput('Controller starting everyone')
        t1 = time.perf_counter()
        self._send(('CTL_Start',), self.ps)
        _st_label_102 = 0
        while (_st_label_102 == 0):
            _st_label_102 += 1
            if (self.dones == self.nprocs):
                _st_label_102 += 1
            else:
                super()._label('_st_label_102', block=True)
                _st_label_102 -= 1
        t2 = time.perf_counter()
        self.verboutput('Everyone done')
        jsondata = {'Wall time': (t2 - t1), 'Total process time': self.cputime}
        jsonoutput = json.dumps(jsondata)
        print(('OUTPUT: ' + jsonoutput))
        self._send(('CTL_Terminate',), self.ps)
        time.sleep(1)

    def setup(self, nprocs):
        self.nprocs = nprocs
        self.ps = set()
        self.readys = 0
        self.dones = 0
        self.cputime = 0
        self.verbose = True

    def verboutput(self, s):
        if self.verbose:
            self.output(s)

    def _Controller_handler_3(self, source):
        self.ps.add(source)
        self.readys += 1
        self.verboutput('Got Ready ({}/{})'.format(self.readys, self.nprocs))
    _Controller_handler_3._labels = None
    _Controller_handler_3._notlabels = None

    def _Controller_handler_4(self, time, source):
        self.dones += 1
        self.cputime += time
        self.verboutput('Got Done ({}/{})'.format(self.dones, self.nprocs))
    _Controller_handler_4._labels = None
    _Controller_handler_4._notlabels = None

class Controllee(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._ControlleeReceivedEvent_0 = []
        self._ControlleeReceivedEvent_1 = []
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_ControlleeReceivedEvent_0', PatternExpr_31, sources=None, destinations=None, timestamps=None, record_history=True, handlers=[]), da.pat.EventPattern(da.pat.ReceivedEvent, '_ControlleeReceivedEvent_1', PatternExpr_33, sources=None, destinations=None, timestamps=None, record_history=True, handlers=[])])

    def setup(self, ctl):
        self.ctl = ctl
        self.ctl_starttime = 0
        self.ctl_endtime = 0
        self.verbose = True

    def verboutput(self, s):
        if self.verbose:
            self.output(s)

    def ctl_begin(self):
        self._send(('CTL_Ready',), self.ctl)
        _st_label_120 = 0
        while (_st_label_120 == 0):
            _st_label_120 += 1
            if PatternExpr_32.match_iter(self._ControlleeReceivedEvent_0):
                _st_label_120 += 1
            else:
                super()._label('_st_label_120', block=True)
                _st_label_120 -= 1
        self.ctl_starttime = time.process_time()

    def ctl_end(self):
        self.ctl_endtime = time.process_time()
        self._send(('CTL_Done', (self.ctl_endtime - self.ctl_starttime)), self.ctl)
        _st_label_125 = 0
        while (_st_label_125 == 0):
            _st_label_125 += 1
            if PatternExpr_34.match_iter(self._ControlleeReceivedEvent_1):
                _st_label_125 += 1
            else:
                super()._label('_st_label_125', block=True)
                _st_label_125 -= 1
        self.verboutput('Terminating...')
