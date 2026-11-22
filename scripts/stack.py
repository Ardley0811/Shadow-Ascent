class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None
        self._size = 0

    def push(self, item):
        # Adds item to the top of the stack
        new_node = Node(item)
        new_node.next = self.top
        self.top = new_node
        self._size += 1

    def pop(self):
        # Removes and returns top item from stack
        # Returns None is the stack is empty
        if self.top is None:
            return None
        popped_node = self.top
        self.top = self.top.next
        popped_node.next = None
        self._size  -= 1
        return popped_node.data

    def peek(self):
        # Return the top item of stack without removing it
        if self.top is None:
            return None
        return self.top.data

    def is_empty(self):
        # Checks if the stack is empty
        return self.top is None



    def clear(self):
        # Removes all items from the stack
        self.top = None
        self._size= 0

