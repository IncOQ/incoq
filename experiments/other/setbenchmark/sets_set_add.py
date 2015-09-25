from incoq.runtime import Set

def make_set():
    return Set()

def run(s, nums):
    for n in nums:
        s.add(n)
