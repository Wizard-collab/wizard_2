import random
import statistics

l = list(range(0, 1000))
percent_step = 100/len(l)
weights_list = []
for a in l:
	index = l.index(a)+1
	weight = 100-(percent_step*index)+percent_step/2
	weights_list.append(weight)
print(random.choices(l, weights=weights_list)[0])