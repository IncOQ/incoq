from incoq.runtime import RCSet

def make_set():
    return RCSet()

def run(s, nums):
    for n in nums:
        s.add(n)
