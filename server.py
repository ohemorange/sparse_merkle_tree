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