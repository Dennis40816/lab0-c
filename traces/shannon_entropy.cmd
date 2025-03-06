# Test PRNG by shannon entropy
log shannon_entropy_compare.log
option entropy 1
option prng 0
option echo 0
source traces/random_once.cmd 10000
