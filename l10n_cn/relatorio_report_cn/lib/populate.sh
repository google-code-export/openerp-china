#!/bin/bash

test -f 'populate.sh' || exit

function install {
    test $2 || PYTHONPATH=. easy_install -a -Z -d . $1
}

install "PyYaml" "-d pyyaml"
install "pycha" "-d pycha"
install "genshi" "-d genshi"
install "lxml" "-d lxml"
install "relatorio" "-d relatorio"

for egg in *.egg
do
    if test -d $egg 
    then
        rm -rf $egg/EGG-INFO
        mv $egg/* .
        rm -rf $egg
    fi
done

rm -f site.*
rm -f easy-install.pth
