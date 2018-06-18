#!/usr/bin/env bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/hub.XXXXXXXX)
export PYTHONUNBUFFERED=1

WEBAPP="web_interface"
if [ "$1" != "" ]
then
    WEBAPP="$1"
fi

WEBAPP="$PWD/$WEBAPP"

echo $BASH_VERSION

if [ ! -f test/hub-email.conf ]
then
    read -t 0.1
    if [ $? -lt 128 ]
    then
        echo 'Are you using run-backend.sh?'
        echo 'Please start test/run-hub.sh once, because email configuration needs to be setup.'
        exit 1
    fi
fi

on_exit()
{
    rm -rf $TMPDIR
}

# whatever happens, call on_exit() at the end.
trap on_exit EXIT

# if there is no central db yet
if [ ! -f "$HOME/.sakura/hub.db" ]
then
    mkdir -p "$HOME/.sakura"
    # and a custom db skeleton is provided
    # in the 'test' directory
    if [ -f "test/hub.db" ]
    then
        # copy this db skeleton
        cp "test/hub.db" "$HOME/.sakura/hub.db"
    fi
fi

# prepare hub conf
if [ ! -f test/hub-email.conf ]
then
    echo 'Email config...'
    echo -n '* Mail server hostname or IP: '
    read host
    echo -n '* Mail server port number: '
    read port
    echo '* Mail server uses SSL:'
    select answer in 'yes' 'no'
    do
        case $answer$REPLY in
            'yes'|'yes1')
                ssl="true";;
            'no'|'no2')
                ssl="false";;
        esac
        [ "$ssl" != "" ] && break
        echo 'Invalid response.'
    done
    echo -n '* Login name/email used to authenticate on mail server: '
    read login
    passfile=$(mktemp)
    python3 sakura/common/password.py prompt "* Password: " 2>"$passfile"
    password=$(cat "$passfile"); rm "$passfile"
    echo -n '* Source of emails sent (e.g. sakura@your-domain.org): '
    read from

    cat > test/hub-email.conf << EOF
    "emailing": {
        "host": "$host",
        "port": $port,
        "ssl": $ssl,
        "login": "$login",
        "encoded-password": "$password",
        "source": "$from"
    }
EOF
    echo 'Email config saved in test/hub-email.conf.'
fi

if [ -f test/hub-debug.conf ]
then
    hub_debug_conf="$(cat << EOF
"mode": "debug",
$(cat test/hub-debug.conf),
EOF
)"
fi

cat > $TMPDIR/hub.conf << EOF
{
    "web-port": 8081,
    "hub-port": 10432,
    "work-dir": "$HOME/.sakura",
    $hub_debug_conf
$(cat test/hub-email.conf)
}
EOF

PYTHONPATH="$PWD" sakura/hub/hub.py -f $TMPDIR/hub.conf -d $WEBAPP
