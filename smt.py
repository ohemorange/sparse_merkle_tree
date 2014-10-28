# extends http://www.links.org/files/RevocationTransparency.pdf
# usage:
# 
# construct
# builds an smt and returns the root, given a requested tree size
# and a list of (number, stringable) tuples
#
# proof
# returns a list of (hash, (start, finish)) tuples that can be
# used to reconstruct the tree's root, given a list of tuples
# and an index into the list indicating the (k,v) pair in question.
# empty subtrees are not indicated, since they can be easily inferred
#
# check_proof
# given the outputs of proof and a (k,v) pair, determine the root
# of the smt

from hashlib import sha256
from bisect import bisect_left

def Hash(a):
    return sha256(a).hexdigest()

def hex_to_int(hex):
    return int("0x"+hex,16)

# a cache of hashes for empty trees of various lengths
hStarEmptyCache = ['0']

# return the hash of an empty branch of proper depth
# n is depth of tree
def HStarEmpty(n):
    if len(hStarEmptyCache) <= n:
        t = HStarEmpty(n - 1)
        t = Hash(t + t)
        assert len(hStarEmptyCache) == n
        hStarEmptyCache.append(t)
    return hStarEmptyCache[n]

def helper(n, l, lo, hi, offset, v):
    t = hi - lo
    if n == 0:
        if t == 0:
            return '0'
        assert t == 1
        return str(v[lo])
    if t == 0:
        return HStarEmpty(n)
    split = (1 << (n - 1)) + offset # 2^(n-1) + offset
    i = bisect_left(l, split, lo, hi) # where should we insert 'split'
    left = helper(n - 1, l, lo, i, offset, v)
    right = helper(n - 1, l, i, hi, split, v)
    return Hash(left + right)

# construct a tree using a list l of (index, value) pairs
# return the root
# indices must be numbers, values can be any argument of str()
# n is the depth of the tree (= number of possible bits in the key)
def construct(n, l):
    l.sort() # sorts by first value of pair
    two_lists = [list(t) for t in zip(*l)]
    return helper(n, two_lists[0], 0, len(l), 0, two_lists[1])

def proof_helper(n, l, lo, hi, offset, v, path_from_leaf):
    t = hi - lo
    if n == 0:
        if t == 0:
            return '0'
        assert t == 1
        return str(v[lo])
    if t == 0:
        return HStarEmpty(n)
    split = (1 << (n - 1)) + offset # 2^(n-1) + offset
    i = bisect_left(l, split, lo, hi) # where should we insert 'split'
    left = helper(n - 1, l, lo, i, offset, v, path_from_leaf)
    right = helper(n - 1, l, i, hi, split, v, path_from_leaf)
    return Hash(left + right)

# 
def proof(key, root, l):
    l.sort() # sorts by first value of pair
    two_lists = [list(t) for t in zip(*l)]
    root = helper(n, two_lists[0], 0, len(l), 0, two_lists[1])
    

def insert(tree, k, v):
    return 0

def remove(tree, k, v):
    return 0

def empty_tree(n):
    return HStarEmpty(n)

usernames = ["ohemorange", "joebonneau", "edfelten", "bcrypt"]
hashed_usernames = [hex_to_int(Hash(user)) for user in usernames]
pks = [str(i) for i in [10,3,6,100]]
l = zip(hashed_usernames, pks)
print construct(256, l)

hashes_of_usernames = [100,3,2323123123,54345]
fake_pks = [101,31,23231231231,543451]
m = zip(hashes_of_usernames, fake_pks)
print construct(256, m)