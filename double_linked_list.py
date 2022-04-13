class Node:
    def __init__(self, data=None):
        self.prev = None
        self.data = data
        self.next = None

    def __str__(self):
        return str(self.data)


class NoSuchData(Exception):
    def __init__(self):
        super().__init__("ERROR: No such data")


class Cursor:
    def __init__(self, iterable):
        self.iterable = iterable
        self.pointer = None

    def first(self):
        self.pointer = self.iterable.head

    def has_next(self):
        return self.pointer is not None

    def get(self):
        return self.pointer.data

    def next(self):
        self.pointer = self.pointer.next


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def add_first(self, data):
        new_node = Node(data)
        new_node.next = self.head
        if self.head is None:
            self.tail = new_node
        else:
            self.head.prev = new_node
        self.head = new_node
        self.size += 1

    def add_last(self, data):
        if self.head is None:
            self.add_first(data)
        else:
            new_node = Node(data)
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            self.size += 1

    def find(self, data):
        node = self.head
        while node is not None:
            if data == node.data:
                return node
            node = node.next
        return None

    def delete(self, data):
        node_prev = None
        node_curr = self.head
        while node_curr is not None:
            if data == node_curr.data:
                self.size -= 1
                if node_prev is None:
                    self.head = self.head.next
                    if self.head is None:
                        self.tail = None
                    else:
                        self.head.prev = None
                elif node_curr.next is None:
                    node_prev.next = None
                    self.tail = node_prev
                else:
                    node_prev.next = node_curr.next
                    node_curr.next.prev = node_prev
                return
            else:
                node_prev = node_curr
                node_curr = node_curr.next

    def print_linked_list(self):
        print("--- DOUBLE LINKED LIST ---")
        if self.head is None:
            print("There are no elements in the current double linked list")
        else:
            node = self.head
            while node is not None:
                print(node.data)
                node = node.next
            print("--------------")

    @staticmethod
    def iterate_backwards(node):
        if node.next:
            DoubleLinkedList.iterate_backwards(node.next)
            print(node.data)
        else:
            print(node.data)
            return

    def print_linked_list_backwards_v2(self):
        if self.head is None:
            print("There are no elements in the current double linked list")
        else:
            node = self.tail
            while node is not None:
                print(node.data)
                node = node.prev

    def print_linked_list_backwards_v1(self):
        print("--- LINKED LIST BACKWARDS ---")
        if self.head is None:
            print("There are no elements in the current linked list")
        else:
            node_list = []
            node = self.head
            while not node is None:
                node_list.append(node)
                node = node.next
            for element in reversed(node_list):
                print(element.data)
            """for i in range(-1, -len(node_list) - 1, -1):
                print(node_list[i].data)"""

        print("-----------------------------")

    def length(self):
        return self.size

