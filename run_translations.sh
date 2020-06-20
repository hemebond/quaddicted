# Use this instead of "manage makemessages" because we need to exclude all the venv directories

./manage.py makemessages -l en -l ja --ignore=include/* --ignore=bin/* --ignore=lib/* --ignore=share/*
./manage.py compilemessages -l en -l ja --ignore=include/* --ignore=bin/* --ignore=lib/* --ignore=share/*
