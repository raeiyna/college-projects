# GROUP 5 - BENITEZ, PALACIOS, SANTOS, R.
# CPET5L
# LINKED LIST ACTIVITY #5

class CustomerNode:
    def __init__(self, customer_name):
        self.name = customer_name  
        self.next = None  

class CustomerQueue:
    def __init__(self):
        self.head = None  

    def add_customer(self, customer_name, position=None):
        new_customer = CustomerNode(customer_name)  
        if self.head is None or position == 0:
            
            new_customer.next = self.head
            self.head = new_customer
            print(f"Customer '{customer_name}' has been added at position 1.")  
        else:
            current = self.head
            current_position = 1  
            while current.next and (position is None or current_position < position):
                current = current.next  
                current_position += 1
            
            new_customer.next = current.next
            current.next = new_customer
            print(f"Customer '{customer_name}' has been added at position {current_position + 1}.")

    def remove_customer(self, customer_name):
        if self.head is None:
            print("\nThe queue is empty. No customer to remove.")
            return

        if self.head.name == customer_name:  
            self.head = self.head.next
            print(f"\nCustomer '{customer_name}' has been removed from the queue.")
            return

        current = self.head
        while current.next and current.next.name != customer_name:
            current = current.next  

        if current.next is None:
            print(f"\nCustomer '{customer_name}' is not in the queue.")
        else:
            current.next = current.next.next  
            print(f"\nCustomer '{customer_name}' has been removed from the queue.")

    def display_queue(self):
        if self.head is None:
            print("\nThe queue is currently empty.")
        else:
            current = self.head
            print("\nCustomer Queue:")
            position = 1  
            while current:
                print(f"{position}: {current.name}")
                current = current.next
                position += 1
            print()  

def main():
    print("Welcome to Swift Queue Assistant!")  
    print("Swift Queue Assistant's priority is for those with more urgent inquiries. Kindly get a priority queue number.\n")

    queue = CustomerQueue()
    
    
    initial_customers = ["Dona", "Reyna", "Vinze"]
    for customer in initial_customers:
        queue.add_customer(customer, 0)  

    while True:
        print("Swift Queue Assistant")
        print("1. Add a customer to the queue")
        print("2. Remove a customer from the queue")
        print("3. Display the current queue")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            customer_name = input("\nEnter the customer's name: ")
            position = input("Enter the position to insert the customer (0 for the start, leave empty for the end): ")
            if position == "":
                position = None  
            else:
                position = int(position)
            queue.add_customer(customer_name, position)
        elif choice == '2':
            customer_name = input("\nEnter the customer's name to remove: ")
            queue.remove_customer(customer_name)
        elif choice == '3':
            queue.display_queue()
        elif choice == '4':
            print("\nThank you for visiting, Swift Queue Assistant! Goodbye!")
            break
        else:
            print("\nInvalid choice, please try again.")

if __name__ == "__main__":
    main()
