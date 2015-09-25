from incoq.runtime import RCSet

def make_set():
    return RCSet()

def run(s, nums):
    for n in nums:
        if n not in s:
            s.add(n)
        else:
            s.incref(n)
