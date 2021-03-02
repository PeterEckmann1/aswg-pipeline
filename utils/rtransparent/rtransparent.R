args <- commandArgs(TRUE)
results <- rtransparent::rt_all(args[1])
write.table(results, file=args[2])