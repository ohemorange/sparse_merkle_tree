# retains a list of (k,v) pairs, uses an smt to satisfy queries regarding
# said list.
import smt
import datetime

RUN_TESTS = True

USERNAME = "USERNAME"
HASH_OF_USERNAME = "HASH_OF_USERNAME" # hex string
PK_AS_INT = "PK_AS_INT"
ADDITION = "ADDITION"
DELETION = "DELETION"
PK_AS_HEX = "PK_AS_HEX"
TIMESTAMP = "TIMESTAMP"
CHANGE_TYPE = "CHANGE_TYPE"
TREE_SIZE = 256
EPOCH_SIZE = 16 # how many changes we make before signing and publishing

# TODO integrate with some offline store, git might actually
# work nicely.
data = []

data_changelog = []

roots_log = []

# maybe worry about the timestamps later
published_log = [] # a list of (timestamp, data) tuples

signed_head = ""

# type = ADDITION or DELETION
def register_change(user, change_type):
    # TODO this can maybe be done with a nice git repo or something
    data_changelog.append({USERNAME: user,
                           TIMESTAMP: datetime.datetime.now(),
                           CHANGE_TYPE: change_type})

def add_username_to_data(user, hex_pk):
    # TODO save offline
    d = {USERNAME: user,
         HASH_OF_USERNAME: smt.Hash(user),
         PK_AS_INT: smt.hex_to_int(hex_pk)}
    data.append(d)

def remove_username_from_data(user):
    # TODO save offline
    item_dict = filter(lambda item: item[USERNAME] == user, data)
    assert len(item_dict) == 1
    item = item_dict[0]
    data.remove(item)

def sign(string):
    # TODO lol
    return "Sig("+string+")"

def publish(head):
    # TODO publish to git or something
    published_log.append((datetime.datetime.now(),
        head))

def sign_and_publish_changes():
    global signed_head, roots_log
    signed_head = sign(signed_head + str(roots_log))
    publish(signed_head)
    roots_log = []

def append_root(root):
    roots_log.append(root)
    # TODO save offline in case the server goes down
    if len(roots_log) % EPOCH_SIZE == 0:
        sign_and_publish_changes()

# after any change to the tree, calculate and save the new root
def log_new_tree():
    l = [(smt.hex_to_int(item[HASH_OF_USERNAME]), item[PK_AS_INT]) \
         for item in data]
    new_root = smt.construct(TREE_SIZE, l)
    append_root(new_root)

def register_username(username, pk_as_hex):
    # register in changelog
    register_change(username, ADDITION)
    # add to data
    add_username_to_data(username,
                         pk_as_hex)
    # calculate and save new root
    log_new_tree()

def remove_username(username):
    # register in changelog
    register_change(username, DELETION)
    # remove from data
    remove_username_from_data(username)
    # calculate and save new root
    log_new_tree()

def update_pk(username, pk_as_hex):
    remove_username(username)
    register_username(username, pk_as_hex)

# the user sends in a username and a timestamp, and wants
# something since that time
def audit_username(username):
    # TODO

    # TODO send back to user
    return

def init():
    # load data
    # TODO wait for incoming requests
    # I need to look how to do this in python
    # also a switch...
    global data, data_changelog, roots_log, published_log, signed_head
    data = []
    data_changelog = []
    roots_log = []
    published_log = []
    signed_head = ""
    '''
    username = request.data[USERNAME]
    pk_as_hex = request.data[PK_AS_HEX]
    if request.type == "REGISTER_USERNAME":
        register_username(username, pk_as_hex)
    elif request.type == "REMOVE_USERNAME":
        remove_username(username)
    elif request.type == "UPDATE_PK":
        update_pk(username, pk_as_hex)
    elif request.type == "AUDIT_USERNAME":
        audit_username(username)
    '''

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

def test_register():
    username = "bugsbunny"
    pk_as_hex = "32"
    register_username(username, pk_as_hex)
    assert len(data_changelog) == 1
    assert data_changelog[0][USERNAME] == username
    assert data_changelog[0][CHANGE_TYPE] == ADDITION
    assert len(data) == 5
    assert roots_log == ['009baf8e939923d9496aaf0e3a322aa301fc410226492d301cdaa034451ca870']
    assert published_log == []

def test_remove():
    username = "bugsbunny"
    remove_username(username)
    assert len(data_changelog) == 2
    assert data_changelog[1][USERNAME] == username
    assert data_changelog[1][CHANGE_TYPE] == DELETION
    assert len(data) == 4
    assert roots_log[1] == "1cdc4584f1d62ddc5d296a225f4dc3a173cc2098a063249748ba5fba27d1cee2"
    assert published_log == []

def test_update():
    username = "ohemorange"
    pk_as_hex = "12"
    update_pk(username, pk_as_hex)
    assert data_changelog[2][USERNAME] == username
    assert data_changelog[2][CHANGE_TYPE] == DELETION
    assert data_changelog[3][USERNAME] == username
    assert data_changelog[3][CHANGE_TYPE] == ADDITION
    assert len(data) == 4
    assert roots_log[2] == "75f2cb60bfe14f4723de7aa0e4540d44928215bc9e19d499e5fffb500e5d20f1" 
    assert roots_log[3] == "5cc0fb65cda6d350bdb80cd28f5bf340a5972cfe7d357de05eec1751536b7abc"
    assert published_log == []

def test_root_consistency():
    username = "winniethepooh"
    pk_as_hex = "abc"
    register_username(username, pk_as_hex)
    remove_username(username)
    assert roots_log[3] == roots_log[5]

def test_publish_log():
    start = len(roots_log)
    end = EPOCH_SIZE
    for i in range(start, end - 1):
        register_username(str(i), str(i+1))
    assert published_log == []
    register_username(str(end-1), str(end))
    assert len(published_log) == 1

# just making sure nothing crashes here.
def test_start_from_clean():
    global data, data_changelog, roots_log, published_log, signed_head
    data = []
    data_changelog = []
    roots_log = []
    published_log = []
    signed_head = []
    username = "sofiathetrainterror"
    pk_as_hex = "bad"
    register_username(username, pk_as_hex)
    update_pk(username, "dab")
    remove_username(username)

def run_tests():
    global data, data_changelog, roots_log, published_log, signed_head
    data = [
        {USERNAME: "ohemorange", PK_AS_INT: 10},
        {USERNAME: "joebonneau", PK_AS_INT: 3},
        {USERNAME: "edfelten", PK_AS_INT: 6},
        {USERNAME: "bcrypt", PK_AS_INT: 100},
        ]
    for item in data:
        item[HASH_OF_USERNAME] = smt.Hash(item[USERNAME])
    data_changelog = []
    roots_log = []
    published_log = []
    signed_head = "abcdef"

    # don't change this order
    test_register()
    test_remove()
    test_update()
    test_root_consistency()
    test_publish_log()
    # test_audit()
    test_start_from_clean()
    init() # clear test data

if RUN_TESTS:
    run_tests()