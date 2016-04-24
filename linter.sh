#!/usr/bin/env bash

###########################
# linter.sh
# -----
# looks through the current directory
# for all files ending in .yml
# and then passes them through yamllint
# which checks for valid yaml syntax
#
# YamlLint can be found at 
# https://pypi.python.org/pypi/yamllint
#
# Installed via pip with 
# $ pip install yamllint
#
#
###########################

for file in $(find . -name "*.yml")
do
    yamllint $file
    rc=$?
    if [ "$rc" -ne 0 ] ; then
        exit $rc
    fi
done

echo "Linting Passed"

exit 0