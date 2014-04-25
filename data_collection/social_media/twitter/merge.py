import os ; import sys ; import pickle

def main():
    root = sys.argv[1]
    unique_users = {}
    for filename in os.listdir(root):
        if filename[filename.rfind('.')+1:] == 'pickle':
            f = open(filename, 'rb')
            users = pickle.load(f)
            f.close()
            for user in users:
                unique_users[user['screen_name']] = user
    f_unique_users = open('unique_users.pickle', 'wb')
    pickle.dump(unique_users.values(), f_unique_users)
    f_unique_users.close()

if __name__ == '__main__':
    main()
