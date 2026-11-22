class Node:
    def __init__(self, data):
        self.data = data  # Value stored in Node
        self.next = None # Pointer to the next Node in queue


class Queue:
    def __init__(self):
        self.front = None # First node in queue
        self.rear = None # Last node in queue
        self.size = 0 # Number of elements currently in the queue

    # Adds element to the end of queue
    def enqueue(self, data):
        new_node = Node(data) # Creates a new node for the data

        # If the queue is empty, the front and rear are set to the new node
        if self.rear is None:
            self.front = new_node
            self.rear = new_node

        else:
            # link new node at the end of the queue and update rear pointer
            self.rear.next = new_node
            self.rear = new_node

        self.size += 1 # Increases the size of queue

    # Removes and returns the element and the front of the queue
    def dequeue(self):
        if self.front is None:
            return None # Queue is empty, so nothing is removed

        removed_data = self.front.data # Store the data to return
        self.front = self.front.next # Moves the front pointer to next node

        # If the queue is now empty, rear pointer gets reset
        if self.front is None:
            self.rear = None

        self.size -= 1 # Decrease size of queue
        return removed_data # Returns the removed data

    # Returns the element at the front of the queue without removing it
    def peek(self):
        if self.front is None:
            return None # Queue is empty, so nothing returned
        return self.front.data

    # Checks if the queue is empty
    def is_empty(self):
        return self.front is None




