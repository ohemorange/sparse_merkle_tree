# extends http://www.links.org/files/RevocationTransparency.pdf
# usage:
# 
# construct
# builds an smt and returns the root, given a requested tree size
# and a list of (number, stringable) tuples
#
# proof
# returns a list of (hash, (start, finish)) tuples that can be
# used to reconstruct the tree's root, given a list of tuples, tree size,
# and a (k,v) in the list. empty subtrees are not indicated, since they
# can be easily inferred
#
# check_proof
# given the outputs of proof, tree size, and a (k,v) pair, determine
# the root of the smt

from hashlib import sha256
from bisect import bisect_left

def Hash(a):
    return sha256(a).hexdigest()

def hex_to_int(hex):
    return int("0x"+hex,16)

# a cache of hashes for empty trees of various lengths
hStarEmptyCache = [Hash('0')]

# return the hash of an empty branch of proper depth
# n is depth of tree
def HStarEmpty(n):
    if len(hStarEmptyCache) <= n:
        t = HStarEmpty(n - 1)
        t = Hash(t + t)
        assert len(hStarEmptyCache) == n
        hStarEmptyCache.append(t)
    return hStarEmptyCache[n]

def helper(n, l, lo, hi, offset, v, results=None, k=None):
    t = hi - lo
    if t == 0:
        return HStarEmpty(n)
    if n == 0:
        assert t == 1
        return Hash(str(v[lo]))
    split = (1 << (n - 1)) + offset # 2^(n-1) + offset
    i = bisect_left(l, split, lo, hi) # where should we insert 'split'
    left = helper(n - 1, l, lo, i, offset, v, results, k)
    right = helper(n - 1, l, i, hi, split, v, results, k)
    # if we also want a proof, we will have the extra args
    if results != None and k != None:
        # if one subtree contains k, append the other to the results
        to_append = None
        if lo <= k and k < i: # k in left
            to_append = right
        elif i <= k and k < hi:
            to_append = left
        if to_append != None:
            results.append(to_append)
    return Hash(left + right)

# construct a tree using a list l of (index, value) pairs
# return the root
# indices must be numbers, values can be any argument of str()
# n is the depth of the tree (= number of possible bits in the key)
def construct(n, l):
    if len(l) == 0:
        return ""
    l.sort() # sorts by first value of pair
    two_lists = [list(t) for t in zip(*l)]
    return helper(n, two_lists[0], 0, len(l), 0, two_lists[1])

def temp_index_of(l, k):
    i = 0
    for j in l:
        if j == k:
            return i
        i += 1
    return None

# currently returns all 256 hashes. some of these will be the hash of
# empty subtrees - this can be optimized for storage/transmission
def proof(l, n, k):
    if len(l) == 0:
        return ""
    l.sort() # sorts by first value of pair
    two_lists = [list(t) for t in zip(*l)]
    if k not in two_lists[0]:
        return None
    results = []
    index_of_k = temp_index_of(two_lists[0], k)
    root = helper(n, two_lists[0], 0, len(l), 0, two_lists[1], results, index_of_k)
    return results

def root_from_proof(k, v, n, proof_output):
    output = Hash(str(v))
    k1 = k
    for i in proof_output:
        if k1 % 2 == 0:
            output = Hash(output + i)
        else:
            output = Hash(i + output)
        k1 /= 2 # this will probably break in python 3...
    return output

def big_examples():
    usernames = ["ohemorange", "joebonneau", "edfelten", "bcrypt"]
    hashed_usernames = [hex_to_int(Hash(user)) for user in usernames]
    pks = [str(i) for i in [10,3,6,100]]
    l = zip(hashed_usernames, pks)
    result = construct(256, l)
    print audit_smt(l, 256, hex_to_int(Hash('ohemorange')), 10, result)

    hashes_of_usernames = [100,3,2323123123,54345]
    fake_pks = [101,31,23231231231,543451]
    m = zip(hashes_of_usernames, fake_pks)
    print construct(256, m)

'''
     /   \
    /     \
   /       \
  / \    /  \
 /\ /\  /\  /\
| | | | | | | |
  b   a       c
'''

# passing
def test_proof():
    keys = [3,1,7]
    vals = ["a", "b", "c"]
    l = zip(keys, vals)
    proof_output = proof(l, 3, 3)
    assert proof_output[0] == HStarEmpty(0)
    assert proof_output[1] == Hash(HStarEmpty(0)+Hash("b"))
    assert proof_output[2] == Hash(HStarEmpty(1)+Hash(HStarEmpty(0)+Hash("c")))

# passing
def test_root_from_proof():
    keys = [3,1,7]
    vals = ["a", "b", "c"]
    l = zip(keys, vals)
    proof_output = proof(l, 3, 3)
    right = Hash(HStarEmpty(1)+Hash(HStarEmpty(0)+Hash("c")))
    left = Hash(Hash(HStarEmpty(0)+Hash("b"))+Hash(HStarEmpty(0)+Hash("a")))
    correct_root = Hash(left + right)

    a = Hash("a")
    b = Hash(proof_output[0] + a)
    c = Hash(proof_output[1] + b)
    d = Hash(c + proof_output[2])

    assert correct_root == root_from_proof(3, "a", 3, proof_output)

# passing
def test_construct():
    keys = [3,1,7]
    vals = ["a", "b", "c"]
    l = zip(keys, vals)
    right = Hash(HStarEmpty(1)+Hash(HStarEmpty(0)+Hash("c")))
    left = Hash(Hash(HStarEmpty(0)+Hash("b"))+Hash(HStarEmpty(0)+Hash("a")))
    correct_root = Hash(left + right)
    assert correct_root == construct(3, l)

test_construct()
test_proof()
test_root_from_proof()

'''
Empty
0: 5fe...
1: 984...
2: 5de...
3: 77e...
'''