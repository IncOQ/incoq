from incoq.runtime import Set

def make_set():
    return Set()

def run(s, nums):
    s_add = s.add
    for n in nums:
        s_add(n)
