# The enter point for shuffle verification
option echo 0
new

log shuffle_getrandom1.log
ih RAND 10

# start shuffle * 4000000
source traces/shuffle_once.cmd 4000000
