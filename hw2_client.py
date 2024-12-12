import argparse
import logging
import time
import xmlrpc.client
import threading
import customtkinter

class ChatClient:
    def __init__(self, username, address):
        self.username = username
        self.address = address
        self.client = None

    def get_client_connection(self):
        if self.client is None:
            try:
                self.client = xmlrpc.client.ServerProxy(f"http://{self.address}")
            except Exception as e:
                logging.error(f"Error establishing connection with host: {e}")
                raise e
        return self.client

    def register(self, username, password):
        client = self.get_client_connection()
        try:
            reply = client.register(username, password)
            logging.info(f"Reply: {reply}")
            if "successfully" in reply:
                self.username = username
            return reply
        except Exception as e:
            logging.error(f"Error registering user: {e}")
            return str(e)
    
    def login(self, username, password):
        client = self.get_client_connection()
        try:
            reply=client.login(username, password)
            logging.info(f"Reply: {reply}")
            if "successfully" in reply:
                self.username = username
            return reply
        except Exception as e:
            logging.error(f"Error logging in user: {e}")
            return str(e)

    def check_messages(self):
        client = self.get_client_connection()
        while True:
            try:
                messages = client.check_messages(self.username)
                for message in messages:
                    logging.info(message)
            except Exception as e:
                logging.fatal("Chat has been shutdown. Goodbye.")
                break
            time.sleep(0.5)

    def list_topics(self):
        client = self.get_client_connection()
        try:
            topics = client.subject()  # 對應伺服器端的 subject() 方法
            if not topics:
                print("No topics.")
                return []
            else:
              for topic in topics:
                logging.info(topic)
                return topics
        except Exception as e:
            logging.error(f"Error listing topics: {e}")

    def create_topic(self, title, content):
        client = self.get_client_connection()
        try:
            reply = client.create(self.username, title, content)  # 對應伺服器端的 create() 方法
            logging.info(reply)
        except Exception as e:
            logging.error(f"Error creating topic: {e}")

    def reply_topic(self, topic_id, reply):
        client = self.get_client_connection()
        try:
            topic_info = client.discussion(topic_id)
            if not topic_info:
                print("No topics to reply.")
                return
            else:
                reply_message = client.reply(self.username, topic_id, reply)  # 對應伺服器端的 reply() 方法
                logging.info(reply_message)
                return reply_message
        except Exception as e:
            logging.error(f"Error replying to topic: {e}")

    def show_topic(self, topic_id):
        client = self.get_client_connection()
        try:
            topic_info = client.discussion(topic_id)  # 對應伺服器端的 discussion() 方法
            if not topic_info:
                print("Topic not found")
            else:
              logging.info(topic_info)
              return topic_info
        except Exception as e:
            logging.error(f"Error showing topic: {e}")

    def delete_topic(self, item_id):
        client = self.get_client_connection()
        try:
            reply = client.delete(self.username, item_id)  # 對應伺服器端的 delete() 方法
            if "not found" in reply.lower():
                return "Not found" 
            else:
                logging.info(reply)
                return reply
        except Exception as e:
            logging.error(f"Error deleting topic or reply: {e}")

    def history(self):
        client = self.get_client_connection()
        try:
            # 調用伺服器端的 get_user_actions 方法
            actions = client.get_user_actions(self.username)
            if not actions:
                print("No actions found.")
                return []
            else:
                for action in actions:
                    logging.info(action)
                return actions
        except Exception as e:
            logging.error(f"Error retrieving history: {e}")
            return []
          
    def logout(self):
        client = self.get_client_connection()
        try:
            client.logout(self.username)
        except Exception as e:
            logging.error(f"Error logging out: {e}")

def create_client_from_args():
    parser = argparse.ArgumentParser(description="Chat Client")
    parser.add_argument("--user", default=None, help="Your username")
    parser.add_argument("--host", default="localhost", help="The host you want to connect to")
    parser.add_argument("--port", default=3410, type=int, help="The port you want to connect to")

    args = parser.parse_args()

    address = f"{args.host}:{args.port}"
    return ChatClient(username=None, address=address)

def main_loop(client):
    while True:
      if not client.username:
        command = input("Enter command (register/login/exit/help): ").strip().lower()

        if command == "register":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            result = client.register(username, password)
            print(result)
            continue
        
        elif command =="login":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            result = client.login(username, password)
            print(result)
            if "successfully" in result.lower():
                break
            else:
                print("Login failed.Try again.")
                continue
            
        elif command == "help":
            print("""Available commands: 
- register: Register a new user.
- login: Log in to the chat system.
- exit: Exit the system.
- help: Display the available commands""")
            continue
        
        elif command == "exit":
            print("Exiting...")
            return
        
        else: 
            print("Invalid command. Please try again.")
            continue
        
    while True:
        try:
            line = input("Enter command: ").strip()
            params = line.split()
            command = params[0] if params else ""

            if command == "list_topics":
                client.list_topics()
            elif command == "create_topic":
                title = input("Enter topic title: ").strip()
                content = input("Enter topic content: ").strip()
                client.create_topic(title, content)
            elif command == "reply_topic":
                if len(params) < 2:
                    print("Please provide a topic ID.")
                    continue
                try:
                    topic_id = int(params[1])
                except ValueError:
                    print("Invalid topic ID. Please enter a number.")
                    continue
                reply = input("Enter your reply: ").strip()
                client.reply_topic(topic_id, reply)
            elif command == "show_topic":
                if len(params) < 2:
                    print("Please provide a topic ID.")
                    continue
                try:
                    topic_id = int(params[1])
                except ValueError:
                    print("Invalid topic ID. Please enter a number.")
                    continue
                client.show_topic(topic_id)
            elif command == "delete_topic":
                if len(params) < 2:
                    logging.warning("Please provide a topic ID or reply ID.")
                    continue
                try:
                    item_id = int(params[1])
                except ValueError:
                    print("Invalid ID. Please enter a number.")
                    continue
                client.delete_topic(item_id)
            elif command == "logout":
                client.logout()
                break
            elif command == "register":
                username = input("Enter username: ").strip()
                password = input("Enter password: ").strip()
                result = client.register(username, password)
            elif command == "help":
                print("""Available commands: 
                      register: Register a new user.
- login: Log in to the chat system.
- list_topics: List all available topics.
- create_topic: Create a new topic with a title and content.
- reply_topic [topic_id]: Reply to an existing topic.
- show_topic [topic_id]: Show the content and replies of a topic.
- delete_topic [topic_id]: Delete a topic or a reply by ID.
- logout: Log out of the system.
- help: Display this help message.""")
            else:
                logging.info("Unknown command. Type 'help' for a list of commands.")
        except (EOFError, KeyboardInterrupt):
            client.logout()
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Start by parsing any flags given to the program
    client = create_client_from_args()

    # Listen for messages in a background thread
    threading.Thread(target=client.check_messages, daemon=True).start()

    # Enter the main loop to process user input
    main_loop(client)
