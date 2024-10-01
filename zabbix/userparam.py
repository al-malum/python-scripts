import argparse
import os


def arguments():
    parser = argparse.ArgumentParser(description='zabbix')
    parser.add_argument('-i', dest='argument', type=str)
    arg = parser.parse_args()
    listing = {'argument': arg.argument}
    return listing


def reporter(listing):
    argument = listing['argument']
    if argument == 1 or argument == '1':
        os.system('echo successful')
    elif argument == 2 or argument == '2':
        os.system('date')
    else:
        os.system('echo .!..')


if __name__ == '__main__':
    listing = arguments()
    reporter(listing)

