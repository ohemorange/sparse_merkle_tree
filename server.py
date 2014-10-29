# retains a list of (k,v) pairs, uses an smt to satisfy queries regarding
# said list.
from smt import *

# these two methods show how to use the smt library
def check_proof_against_root(k, v, n, proof_output, root):
    new_root = root_from_proof(k, v, n, proof_output)
    return new_root == root

def audit_smt(l, n, k, v, prev_root):
    proof_output = proof(l, n, k)
    return check_proof_against_root(k, v, n, proof_output, prev_root)

def list_example():
    usernames = ["ohemorange", "joebonneau", "edfelten", "bcrypt"]
    hashed_usernames = [hex_to_int(Hash(user)) for user in usernames]
    pks = [str(i) for i in [10,3,6,100]]
    l = zip(hashed_usernames, pks)
    result = construct(256, l)
    assert audit_smt(l, 256, hex_to_int(Hash('ohemorange')), 10, result)