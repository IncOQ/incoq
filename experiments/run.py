import os
import traceback

import experiments.twitter as twitter
import experiments.jql as jql
import experiments.wifi as wifi
import experiments.django as django
import experiments.graddb as graddb
import experiments.rbac.corerbac as corerbac
import experiments.rbac.constrainedrbac as crbac
import experiments.distalgo
import experiments.other.setbenchmark as setbenchmark

sets = setbenchmark.Sets()
setstable = setbenchmark.SetsTable()

scaletime = twitter.ScaleTime()
scaletime_poster = twitter.ScaleTimePoster()
scalesize = twitter.ScaleSize()
scalesize_poster = twitter.ScaleSizePoster()

demandtime = twitter.DemandTimeOps()
demandsize = twitter.DemandSize()

factor1a = twitter.Factor1ATimeNorm()
factor1b = twitter.Factor1BTimeNorm()
factor1c = twitter.Factor1CTimeNorm()
factor1d = twitter.Factor1DTimeNorm()
factor1e = twitter.Factor1ETimeNorm()
factor1f = twitter.Factor1FTimeNorm()
factor2a = twitter.Factor2ATimeNorm()
factor2b = twitter.Factor2BTimeNorm()
factor2c = twitter.Factor2CTimeNorm()
factor2d = twitter.Factor2DTimeNorm()

densityloc = twitter.DensityLoc()
densitylocnorm = twitter.DensityLocNorm()
densitylocnormtable = twitter.DensityLocNormTable()
densitylocmem = twitter.DensityLocMem()
densitylocmemtable = twitter.DensityLocMemTable()
densityceleb = twitter.DensityCeleb()
densitycelebnorm = twitter.DensityCelebNorm()
densitycelebnormtable = twitter.DensityCelebNormTable()

tag = twitter.TagTime()

jqlratio1 = jql.Ratio1()
jqlratio1opt = jql.Ratio1Opt()
jqlratio2 = jql.Ratio2()
jqlratio2opt = jql.Ratio2Opt()
jqlratio3 = jql.Ratio3()
jqlscale1 = jql.Scale1()
jqlscale1opt = jql.Scale1Opt()
jqlscale2 = jql.Scale2()
jqlscale2smaller = jql.Scale2Smaller()
jqlscale2bigger = jql.Scale2Bigger()
jqlscale2opt = jql.Scale2Opt()
jqlscale2opttable = jql.Scale2OptTable()
jqlscale3 = jql.Scale3()
jqlscale3bigger = jql.Scale3Bigger()
jqlscale2gc = jql.Scale2GC()
jqlscale2gctable = jql.Scale2GCTable()

wifiscale = wifi.Wifi()
wifiopt = wifi.WifiOpt()
wifiopttable = wifi.WifiOptTable()

djangoscale = django.Scale()
djangodemand = django.DemandTime()
djangodemandnorm = django.DemandTimeNorm()

newstu = graddb.newstudents.NewStudentsScale()

coreroles = corerbac.CoreRoles()
coredemand = corerbac.CoreDemand()
coredemandnorm = corerbac.CoreDemandNorm()
crbacscale = crbac.CRBACScale()

clpaxos = experiments.distalgo.CLPaxos()
crleader = experiments.distalgo.CRLeader()
dscrash = experiments.distalgo.DSCrash()
hsleader = experiments.distalgo.HSLeader()
lamutexspecprocs = experiments.distalgo.LAMutexSpecProcs()
lamutexspecrounds = experiments.distalgo.LAMutexSpecRounds()
lamutexspecoptprocs = experiments.distalgo.LAMutexSpecOptProcs()
lamutexspecoptrounds = experiments.distalgo.LAMutexSpecOptRounds()
lamutexorigprocs = experiments.distalgo.LAMutexOrigProcs()
lamutexorigprocstable = experiments.distalgo.LAMutexOrigProcsTable()
lamutexorigrounds = experiments.distalgo.LAMutexOrigRounds()
lapaxos = experiments.distalgo.LAPaxos()
lapaxosexclude = experiments.distalgo.LAPaxosExclude()
ramutex = experiments.distalgo.RAMutex()
ramutextable = experiments.distalgo.RAMutexTable()
ratokenprocs = experiments.distalgo.RATokenProcs()
ratokenrounds = experiments.distalgo.RATokenRounds()
sktoken = experiments.distalgo.SKToken()
sktokentable = experiments.distalgo.SKTokenTable()
tpcommit = experiments.distalgo.TPCommit()
vrpaxos = experiments.distalgo.VRPaxos()

def main():
    
    ws = [
#        sets,
#        setstable,
        
        # DLS14 figures
#        scaletime,        # celeb_asymp_time
#        scalesize,        # celeb_asymp_space
#        demandtime,       # celeb_demand_time
#        demandsize,       # celeb_demand_space
#        tag,              # osq_auth_strategy
        
#        scaletime_poster,
#        scalesize_poster,
        
        # Other benchmarks:
#        factor1a,
#        factor1b,
#        factor1c,
#        factor1d,
#        factor1e,
#        factor1f,
#        factor2a,
#        factor2b,
#        factor2c,
#        factor2d,
        
#        densityloc,
#        densitylocnorm,
#        densitylocnormtable,
#        densitylocmem,
#        densitylocmemtable,
#        densityceleb,
#        densitycelebnorm,
#        densitycelebnormtable,
        
#        jqlratio1,
#        jqlratio2,       # jql_ratio
#        jqlratio3,
#        jqlscale1,
#        jqlscale2,
#        jqlscale2smaller, # jql_asymp
#        jqlscale2bigger,
#        jqlscale3,
#        jqlscale3bigger,
#        jqlscale2gc,
#        jqlscale2gctable,
        
#        coreroles,
#        coredemand,
#        coredemandnorm,
        
#        crbacscale,
        
#        wifiscale,
#        wifiopt,
#        wifiopttable,
#        djangoscale,
#        djangodemand,
#        djangodemandnorm,
#        newstu,
        
#        clpaxos,
#        crleader,
#        dscrash,
#        hsleader,
#        lamutexspecprocs,
#        lamutexspecrounds,
#        lamutexspecoptprocs,
#        lamutexspecoptrounds,
#        lamutexorigprocs,
#        lamutexorigrounds,
#        lapaxos,
#        lapaxosexclude,
#        ramutex,
#        ratokenprocs,
#        ratokenrounds
#        sktoken,
#        tpcommit,
#        vrpaxos,
        
        # PEPM 2016 figures:
#        densityloc,
#        densitylocnorm,
#        densitylocnormtable,
#        densitylocmem,
#        densitylocmemtable,
#        densityceleb,
#        densitycelebnorm,
#        densitycelebnormtable,
#        lamutexorigprocs,
#        lamutexorigprocstable,
#        ramutex,
#        ramutextable,
#        sktoken,
#        sktokentable,
#        wifiopt,
#        wifiopttable,
#        sets,
#        setstable,
#        jqlscale2opt,
#        jqlscale2opttable,
    ]
    
    # Change to directory of this file so we can find the
    # results/ subdirectory.
    os.chdir(os.path.join('.', os.path.dirname(__file__)))
    
    for w in ws:
        print('\n---- Running {} ----\n'.format(w.__class__.__name__))
        try:
#            w.generate()
#            w.benchmark()
            
#            w.verify()
            
            w.extract()
            w.view()
            
#            w.cleanup()
        except Exception:
            traceback.print_exc()
            print('\n^--- Skipping test\n')


if __name__ == '__main__':
    main()
