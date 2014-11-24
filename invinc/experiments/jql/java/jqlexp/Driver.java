/******************************************************************************
* Driver.java: Execute benchmark, handle I/O.                                 *
* Author: Jon Brandvein                                                       *
******************************************************************************/

package jqlexp;

import java.lang.management.ManagementFactory;

import java.util.List;
import java.util.ListIterator;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashSet;
import java.util.HashMap;

import java.io.FileDescriptor;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import org.json.simple.JSONValue;
import org.json.simple.parser.ParseException;

/**
 * Resumable cumulative timer.
 * 
 * Time is represented in nanoseconds.
 */
abstract class Timer
{
    private long ticks = 0;
    private long lastStart;
    private boolean running = false;
    
    protected abstract long getTicks();
    
    void start()
    {
        assert !running;
        running = true;
        lastStart = getTicks();
    }
    
    void stop()
    {
        assert running;
        ticks += getTicks() - lastStart;
        running = false;
    }
    
    long elapsed()
    {
        if (running)
        {
            long t = getTicks();
            ticks += t - lastStart;
            lastStart = t;
        }
        return ticks;
    }
}

class CpuTimer extends Timer
{
    protected long getTicks()
    {
        return ManagementFactory.getThreadMXBean().
               getCurrentThreadCpuTime();
    }
}

class WallTimer extends Timer
{
    protected long getTicks()
    {
        return System.nanoTime();
    }
}

class Metrics
{
    public Timer cpuTimer;
    public Timer wallTimer;
    public ArrayList outputs;
    public boolean timedout = false; 
    
    public Metrics()
    {
        cpuTimer = new CpuTimer();
        wallTimer = new WallTimer();
        outputs = new ArrayList();
    }
    
    public void begin()
    {
        cpuTimer.start();
        wallTimer.start();
    }
    
    public void end()
    {
        cpuTimer.stop();
        wallTimer.stop();
    }
    
    public void recordOutput(Object output)
    {
        outputs.add(output);
    }
    
    public double getTotalCpuTime()
    {
        return ((double) cpuTimer.elapsed()) / 1000000000;
    }
    
    public double getTotalWallTime()
    {
        return ((double) wallTimer.elapsed()) / 1000000000;
    }
    
    public HashMap<String, Object> formatTimeData()
    {
        HashMap<String, Object> results = new HashMap<String, Object>();
        if (!timedout)
        {
            results.put("time_cpu", getTotalCpuTime());
            results.put("time_wall", getTotalWallTime());
            results.put("stdmetric", getTotalCpuTime());
        }
        else
        {
            results.put("timedout", true);
        }
        return results;
    }
    
    public HashMap<String, Object> formatOutputData()
    {
        HashMap<String, Object> results = new HashMap<String, Object>();
        results.put("output", outputs);
        return results;
    }
}


/**
 * Execute and benchmark a trial.
 */
abstract class Driver
{
    private static final Integer Q = new Integer(1);
    private static final Integer UP = new Integer(2);
    
    // command line args
    private boolean caching;
    private boolean verifying;
    
    // params from stdin
    private long N;
    private double ratio;
    private List INIT_ATT;
    private List OPS;
    
    // results to stdout
    private Map results;
    
    // lists of objects for tracking purposes
    private ArrayList<Student> students;
    private ArrayList<Course> courses;
    private ArrayList<Attends> attends;
    
    // sets of objects for querying purposes,
    // accessed directly by derived class
    protected HashSet<Student> STUDENTS;
    protected HashSet<Course> COURSES;
    protected HashSet<Attends> ATTENDS;
    
    // argument passed to query
    private Course course0;
    
    public Driver()
    {
        results = new HashMap<String, Object>();
    }
    
    /**
     * Read command line arguments.
     */
    public void readArgs(String[] args)
    {
        if (args.length != 2)
        {
            throw new IllegalArgumentException("Two args required");
        }
        
        String sCache = args[0];
        if (sCache.equals("cache"))
        {
            caching = true;
        }
        else if (sCache.equals("nocache"))
        {
            caching = false;
        }
        else
        {
            throw new IllegalArgumentException(
                "Arg 1 must be 'cache' | 'nocache'");
        }
        
        String sVerify = args[1];
        if (sVerify.equals("benchmark"))
        {
            verifying = false;
        }
        else if (sVerify.equals("verify"))
        {
            verifying = true;
        }
        else
        {
            throw new IllegalArgumentException(
                "Arg 2 must be 'benchmark' | 'verify'");
        }
    }
    
    /**
     * Read input data from standard input.
     */
    public void importData() throws IOException, ParseException
    {
        FileReader fr = new FileReader(FileDescriptor.in);
        Object tree = JSONValue.parseWithException(fr);
        
        Map dataset = (Map) tree;
        N = ((Long) dataset.get("N")).longValue();
        ratio = (Double) dataset.get("ratio");
        INIT_ATT = (List) dataset.get("INIT_ATT");
        OPS = (List) dataset.get("OPS");
    }
    
    public void exportData() throws IOException
    {
        FileWriter fw = new FileWriter(FileDescriptor.out);
        JSONValue.writeJSONString(results, fw);
        fw.flush();
    }
    
    public void setUp()
    {
        // Instantiate helper lists and objects.
        
        students = new ArrayList<Student>();
        courses = new ArrayList<Course>();
        attends = new ArrayList<Attends>();
        STUDENTS = new HashSet<Student>();
        COURSES = new HashSet<Course>();
        ATTENDS = new HashSet<Attends>();
        
        for (int i = 0; i < N; ++i)
        {
            Student s = new Student("s" + Integer.toString(i));
            students.add(s);
            STUDENTS.add(s);
            Course c = new Course("c" + Integer.toString(i));
            courses.add(c);
            COURSES.add(c);
        }
        course0 = courses.get(0);
        
        for (Object elem : INIT_ATT)
        {
            int s = ((Long) ((List) elem).get(0)).intValue();
            int c = ((Long) ((List) elem).get(1)).intValue();
            Attends a = new Attends(students.get(s), courses.get(c));
            attends.add(a);
            ATTENDS.add(a);
        }
        
        /*
         * Preprocess operations. I did this rewriting in the Python
         * version of the driver, in order to avoid the artificial
         * overhead of a string comparison, just to determine what kind
         * of operation we're doing. In Java I'm not sure if the
         * optimization makes as much sense, but let's do it anyway
         * just to be safe for the sake of fairness.
         */
        for (int i = 0; i < OPS.size(); ++i)
        {
            List elem = (List) OPS.get(i);
            String opkind = (String) elem.get(0);
            if (opkind.equals("query"))
            {
                elem.set(0, Q);
            }
            else if (opkind.equals("update"))
            {
                elem.set(0, UP);
                List data = (List) elem.get(1);
                int si = ((Long) data.get(1)).intValue();
                int ci = ((Long) data.get(2)).intValue();
                data.set(1, students.get(si));
                data.set(2, courses.get(ci));
            }
            else
            {
                assert false;
            }
        }
    }
    
    public void execute()
    {
        Metrics metrics = new Metrics();
        
        metrics.begin();
        
        int loop_counter = 0;
        int check_interval = 100;
        double timeout = 300;
        
        for (Object elem : OPS)
        {
            // Check for timeout every so often.
            if (loop_counter % check_interval == 0)
            {
                if (metrics.getTotalCpuTime() > timeout)
                {
                    metrics.timedout = true;
                    break;
                }
            }
            
            List op = (List) elem;
            Integer kind = (Integer) op.get(0);
            // Yes, use == on kind, not .equals().
            // We constructed it from the static Q and UP
            // enum constants.
            
            if (kind == Q)
            {
                Object output = query(course0);
                
                if (verifying)
                {
                    metrics.recordOutput(formatOutput(output));
                }
            }
            else if (kind == UP)
            {
                List data = (List) op.get(1);
                int i = ((Long) data.get(0)).intValue();
                Student s = (Student) data.get(1);
                Course c = (Course) data.get(2);
                
                Attends new_att = new Attends(s, c);
                Attends old_att = attends.get(i);
                ATTENDS.add(new_att);
                ATTENDS.remove(old_att);
                attends.set(i, new_att);
            }
            else
            {
                assert false;
            }
        }
        
        metrics.end();
        
        if (verifying)
        {
            results = metrics.formatOutputData();
        }
        else
        {
            results = metrics.formatTimeData();
        }
    }
    
    public void run(String[] args)
    {
        readArgs(args);
        
        try
        {
            if (caching)
            {
                System.setProperty("jql.caching.policy", "always");
            }
            else
            {
                System.setProperty("jql.caching.policy", "dummy");
            }
            
            importData();
            setUp();
            execute();
            exportData();
        }
        catch (IOException exc)
        {
            System.err.println("IO exception: " + exc.toString());
            System.exit(1);
        }
        catch (ParseException exc)
        {
            System.err.println("JSON parse error: " + exc.toString());
            System.exit(1);
        }
    }
    
    public abstract Object query(Course c1);
    
    public abstract Object formatOutput(Object output);
}
