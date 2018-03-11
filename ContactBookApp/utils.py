import re

from .models import Contact

"""
Validate the entry passed to create a new contact
"""


class ContactValidator(object):

    def __init__(self, **kwargs):
        self.data = kwargs
        self.errors = dict()
        self.data['name'] = self.data.get('name', '').lower()
        self.data['email'] = self.data.get('email', '').lower()

    def clean_name(self):
        '''
        Check if name is blank or not
        '''
        if not self.data['name']:
            self.errors['name'] = 'Name cannot be blank'

    def clean_email(self):
        '''
        Check if valid email is provided
        '''
        if not re.match(r'[^@]+@[^@]+\.[^@]+', self.data['email']):
            self.errors['email'] = 'Provide a valid email address'
        if Contact.objects.filter(email__iexact=self.data['email']).exists():
            self.errors['email'] = 'This email ' + self.data['email'] + \
                ' is already saved in the Contact Book'

    def validate(self):
        self.clean_name()
        self.clean_email()


"""
emails as well as names associated are stored in their respective tries
EmailTrieNode: Nodes associated in the EmailTrie
NameTrieNode: NOdes associated in the NameTrie
"""


class EmailTrieNode(object):

    def __init__(self):
        self.children = [None] * 255
        self.value = 0
        self.name = ''

    def leafNode(self):
        '''
        Check if node is leaf node or not
        '''
        return self.value != 0

    def isItFreeNode(self):
        '''
        If node have no children then it is free
        If node have children return False else True
        '''
        for c in self.children:
            if c:
                return False
        return True


class EmailTrie(object):

    def __init__(self):
        self.root = self.getNode()
        self.count = 0

    def getNode(self):
        return EmailTrieNode()

    def getIndex(self, c):
        return ord(c)

    def dfs(self, curr, key, contacts):
        '''
        All possible contacts with `key` as the prefix email
        '''
        ind = 0
        for child in curr.children:
            if child is not None:
                self.dfs(child, key + chr(ind), contacts)
            ind += 1
        if curr.value != 0:
            contacts.append({'email': key, 'name': curr.name})

    def insert(self, key, name):
        length = len(key)
        curr = self.root
        self.count += 1

        for level in range(length):
            index = self.getIndex(key[level])

            if curr.children[index]:
                curr = curr.children[index]
            else:
                curr.children[index] = self.getNode()
                curr = curr.children[index]

        curr.value = self.count
        curr.name = name

    def search(self, key):
        length = len(key)
        curr = self.root
        for level in range(length):
            index = self.getIndex(key[level])
            if not curr.children[index]:
                return []
            curr = curr.children[index]

        res = curr != None
        contacts = []
        if res:
            (self.dfs(curr, key, contacts))
        return contacts

    def update(self, key, name):
        length = len(key)
        curr = self.root
        for level in range(length):
            index = self.getIndex(key[level])
            if not curr.children[index]:
                return []
            curr = curr.children[index]

        curr.name = name

    def _deleteHelper(self, pNode, key, level, length):
        '''
        Helper function for deleting key from trie
        '''
        if pNode:
            # Base case
            if level == length:
                if pNode.value:
                    # unmark leaf node
                    pNode.value = 0
                    pNode.name = ''

                # if empty, node to be deleted
                return pNode.isItFreeNode()

            # recursive case
            else:
                index = self.getIndex(key[level])
                if self._deleteHelper(pNode.children[index],
                                      key, level + 1, length):

                    # last node marked,delete it
                    del pNode.children[index]

                    # recursively climb up and delete
                    # eligible nodes
                    return (not pNode.leafNode() and
                            pNode.isItFreeNode())

        return False

    def deleteKey(self, key):
        '''
        Delete key from trie
        '''
        length = len(key)
        if length > 0:
            self._deleteHelper(self.root, key, 0, length)


class NameTrieNode(object):

    def __init__(self):
        self.children = [None] * 255
        self.value = 0
        self.emails = []

    def leafNode(self):
        '''
        Check if node is leaf node or not
        '''
        return self.value != 0

    def isItFreeNode(self):
        '''
        If node have no children then it is free
        If node have children return False else True
        '''
        for c in self.children:
            if c:
                return False
        if self.emails:
            return False
        return True


class NameTrie(object):

    def __init__(self):
        self.root = self.getNode()
        self.count = 0

    def getNode(self):
        return NameTrieNode()

    def getIndex(self, c):
        return ord(c)

    def dfs(self, curr, key, contacts):
        '''
        All possible contacts with `key` as the prefix name
        '''
        ind = 0
        for child in curr.children:
            if child is not None:
                self.dfs(child, key + chr(ind), contacts)
            ind += 1
        if curr.value != 0:
            for email in curr.emails:
                contacts.append({'name': key, 'email': email})

    def insert(self, key, email):
        length = len(key)
        curr = self.root
        self.count += 1

        for level in range(length):
            index = self.getIndex(key[level])

            if curr.children[index]:
                curr = curr.children[index]
            else:
                curr.children[index] = self.getNode()
                curr = curr.children[index]

        curr.value = self.count
        curr.emails.append(email)

    def search(self, key):
        length = len(key)
        curr = self.root
        for level in range(length):
            index = self.getIndex(key[level])
            if not curr.children[index]:
                return []
            curr = curr.children[index]

        res = curr != None
        contacts = []
        if res:
            (self.dfs(curr, key, contacts))
        return contacts

    def update(self, key, email):
        length = len(key)
        curr = self.root
        for level in range(length):
            index = self.getIndex(key[level])
            if not curr.children[index]:
                return []
            curr = curr.children[index]

        curr.emails.append(email)

    def _deleteHelper(self, pNode, key, level, length, email):
        '''
        Helper function for deleting key from trie
        '''
        if pNode:
            # Base case
            if level == length:
                if pNode.value:
                    # unmark leaf node
                    pNode.emails.remove(email)
                    if not pNode.emails:
                        pNode.value = 0

                # if empty, node to be deleted
                return pNode.isItFreeNode()

            # recursive case
            else:
                index = self.getIndex(key[level])
                if self._deleteHelper(pNode.children[index],
                                      key, level + 1, length, email):

                    del pNode.children[index]

                    return (not pNode.leafNode() and pNode.isItFreeNode())

        return False

    def deleteKey(self, key, email):
        '''
        Delete key from trie
        '''
        length = len(key)
        if length > 0:
            self._deleteHelper(self.root, key, 0, length, email)
