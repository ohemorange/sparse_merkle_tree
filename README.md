# Sparse Merkle Tree
Library and sample application

## Notes/todo
1. run new tests
2. figure out how to then implement consistency
- (later) batch changes for sending, and sign every batch - this is an epoch
- server that publishes and a client that checks
- what do normal changelogs have? are they timestamped?
- allow mapping from one username to multiple keys
- save things offline

### Ideas for auditing
- tweet the root/ chained sig of batch of roots
- github account that checks in the root
- use a service to publish it to the bitcoin blockchain

## Email about consistency proofs
I spent a lot of time thinking the past week about how to make updates efficient. I even dreamed up a pretty complicated scheme with Bloom filters and two levels of trees.

Turns out the answer is incredibly simple though: you only need to send a user Alice the full tree once, then for the next epoch only send the nodes in her path which have actually changed. This should be log(k) where k is the number of leaves of the tree which have changed, by the same argument that the proof should have N non-empty nodes for a tree with N non-zero leaves. This is exactly what we were hoping for, and it should be straightforward to implement.

I wrote a little script to estimate total proof sizes. Looks pretty promising-users would need to download 50-200kB per day depending on the total number of users and the security level.

Assuming of course the log N behavior holds. I have a proof outline for this: Consider Alice's path to the root (determined by her username hash). Any change to a random leaf in the tree has a probability 1/2 of changing the first sibling node in her proof, 1/4 of changing the second, and so on (counting up from the root). The last expected sibling node to change if N leaves change is O(lgN), and this bounds the length of the proof (even though some earlier siblings may not have changed). 