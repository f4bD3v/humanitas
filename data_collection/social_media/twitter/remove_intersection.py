import os ; import sys ; import pickle

def main():
    num_partitions = 8
    old_users = {} ; new_users = {}
    print 'Merging...'
    for filename in os.listdir('old_files/'):
        if filename[filename.rfind('.')+1:] == 'pickle':
            f = open('old_files/' + filename, 'rb')
            users = pickle.load(f)
            f.close()
            print len(users)
            for user in users:
                old_users[user['screen_name']] = user

    for filename in os.listdir('new_files/'):
        if filename[filename.rfind('.')+1:] == 'pickle':
            f = open('new_files/' + filename, 'rb')
            users = pickle.load(f)
            f.close()
            for user in users:
                if not old_users.has_key(user['screen_name']):
                    new_users[user['screen_name']] = user
    
    print 'Unique users: %s'%(len(new_users))
    print 'Paritioning...'
    partition_size = len(new_users) / num_partitions
    for i in range(num_partitions):
        f_unique_users = open('outputs/%s.pickle'%(i), 'wb')
        pickle.dump(new_users.values()[i*partition_size:(i+1)*partition_size], f_unique_users)
        f_unique_users.close()
    
if __name__ == '__main__':
    main()
