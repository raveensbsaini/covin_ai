#bin/bash 
export TESTING_DB=1
touch test.db
rm test.db
touch test.db
pytest -s
unset TESTING_DB
