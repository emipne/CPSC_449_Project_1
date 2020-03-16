# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
#
# if __name__ == '__main__':
#     app.run()

from configobj import ConfigObj
import os
import socket, subprocess, sys

SERVICE_DIR = ''
TEST_DIR = './tests'


def runtests():
    tests = os.listdir(TEST_DIR)
    print(tests)
    os.chdir(TEST_DIR)
    for file in tests:
        if (file.endswith('.yaml')):
            os.system('py.test ' + file)


if __name__ == '__main__':
    #python app.py test
    if sys.argv[1] == "test":
        runtests()
    else:
        print("Invalid arguments! Arguments accepted [test]")