// (C) Copyright Darren Willis, David James Pearce and James Noble 2005. 
// Permission to copy, use, modify, sell and distribute this software 
// is granted provided this copyright notice appears in all copies. 
// This software is provided "as is" without express or implied 
// warranty, and with no claim as to its suitability for any purpose.
//
// Email: darren.willis@mcs.vuw.ac.nz

package jqlexp;

import java.util.ArrayList;
import java.util.HashMap;

public class Student {
    @jql.core.Cachable
    public String name;
    
    public Student(String n) {
        name = n;
    }
    
    public String toString() {
        return "Student(" + name + ")";
    }
    
    public ArrayList asTree() {
        ArrayList result = new ArrayList();
        result.add("Student");
        HashMap<String, Object> attrs = new HashMap<String, Object>();
        attrs.put("name", name);
        result.add(attrs);
        return result;
    }
}
