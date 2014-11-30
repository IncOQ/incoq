// (C) Copyright Darren Willis, David James Pearce and James Noble 2005. 
// Permission to copy, use, modify, sell and distribute this software 
// is granted provided this copyright notice appears in all copies. 
// This software is provided "as is" without express or implied 
// warranty, and with no claim as to its suitability for any purpose.
//
// Email: david.pearce@mcs.vuw.ac.nz

package jqlexp;

import java.util.ArrayList;
import java.util.HashMap;

public class Attends {
    @jql.core.Cachable
    public Student student;
    @jql.core.Cachable
    public Course course;
    
    public Attends(Student s, Course c) {
        student = s;
        course = c;
    }
    
    public String toString() {
        return student + " ATTENDS " + course;
    }
    
    public ArrayList asTree() {
        ArrayList result = new ArrayList();
        result.add("Attends");
        HashMap<String, Object> attrs = new HashMap<String, Object>();
        attrs.put("student", student.asTree());
        attrs.put("course", course.asTree());
        result.add(attrs);
        return result;
    }
}
