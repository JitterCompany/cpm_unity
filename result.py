#!/usr/bin/env python

import sys
import os

class bcolors:
    HEADER = '\033[94m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if len(sys.argv) < 2:
    print(bcolors.FAIL + "syntax: "
            + sys.argv[0] + " <path/to/*.test.txt>" + bcolors.ENDC)
    exit(0)

result_folder = sys.argv[1]
if not result_folder.endswith('/'):
    result_folder+= '/'

try:
    files = os.listdir(result_folder)
except:
    print(bcolors.FAIL + "test result folder not found: '"
            + result_folder + "'" + bcolors.ENDC)
    exit(0)

files = [f for f in files if f.endswith(".test.txt")]
files.sort()

def result_color(fail_count, ignore_count):
    color = bcolors.OKGREEN;
    if fail_count:
        color = bcolors.FAIL
    elif ignore_count:
        color = bcolors.WARNING

    return color

class Result:
    def __init__(self, name):
        self.name = name
        self.passed = []
        self.ignores = []
        self.failures = []
        self.summary = ""
        self.print_prefix = '{:<40}'.format("[TEST] " + self.name + ": ")

    def count_passed(self):
        return len(self.passed)
    def count_ignores(self):
        return len(self.ignores)
    def count_failures(self):
        return len(self.failures)

    def print_passed(self):
        for ok in self.passed:
            print(bcolors.OKGREEN + self.print_prefix
                    + ok + bcolors.ENDC)
    def print_ignores(self):
        for ignore in self.ignores:
            print(bcolors.WARNING + self.print_prefix
                    + ignore + bcolors.ENDC)
    def print_failures(self):
        for fail in self.failures:
            print(bcolors.FAIL + self.print_prefix
                    + fail + bcolors.ENDC)
    def print_summary(self):

        color = result_color(self.count_failures(), self.count_ignores())
        print(color + self.print_prefix
                + self.summary + bcolors.ENDC)

def format_line(line):
    pos = line.index(':');
    path = line[:pos]
    line = os.path.basename(path) + line[pos:].strip()
    return line

def create_results(filename):
    with open(result_folder + filename) as f:
        result = Result(filename.replace('.txt',''))

        for line in f.readlines():
            # a test has failed
            if "FAIL" in line:
                result.failures.append(format_line(line))

            # a test is ignored
            elif "IGNORE" in line:
                result.ignores.append(format_line(line))

            # a test is passed
            elif "PASS" in line:
                result.passed.append(format_line(line))

            # test summary: end of the text file
            elif "Failures" in line:
                result.summary+= line.strip();
                break;

    return result


results = [create_results(f) for f in files]

# print header
print(bcolors.HEADER + "[TEST] ================" + bcolors.ENDC)
print(bcolors.HEADER + "[TEST] = Test Results =" + bcolors.ENDC)
print(bcolors.HEADER + "[TEST] ================" + bcolors.ENDC)

total_ignores = 0;
total_failures = 0;
total_passed = 0;

enable_print_passed = False

# print passed tests if they exist
for r in results:
    if r.count_passed():
        if enable_print_passed:
            print(bcolors.HEADER + "\n[TEST] Passed:" + bcolors.ENDC)
        break
for r in results:
    total_passed+= r.count_passed()
    total_ignores+= r.count_ignores()
    total_failures+= r.count_failures()

    if enable_print_passed:
        r.print_passed()

# print ignores if they exist
for r in results:
    if r.count_ignores():
        print(bcolors.HEADER + "\n[TEST] Ignores:" + bcolors.ENDC)
        break
for r in results:
    r.print_ignores()

# print failures if they exist
for r in results:
    if r.count_failures():
        print(bcolors.HEADER + "\n[TEST] Failures:" + bcolors.ENDC)
        break
for r in results:
    r.print_failures()

# print summary
print(bcolors.HEADER + "\n[TEST] Summary:" + bcolors.ENDC)
for r in results:
    r.print_summary()

print((bcolors.HEADER + "\n[TEST] Results: %d failed, %d ignored, %d passed" + bcolors.ENDC)
        % (total_failures, total_ignores, total_passed))
