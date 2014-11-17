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
