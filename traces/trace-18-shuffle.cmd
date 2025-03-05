# The enter point for shuffle verification
option echo 0
log shuffle_xorshift_same2.log
show
# start shuffle * 4000000
source traces/shuffle_once.cmd 4000000
