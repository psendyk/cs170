import sys
from output_scorer import *

def run_scores(i):
	input_folder = "./all_inputs/small/"+str(i)
	output_file = "./outputs/small/"+str(i)+".out"
	score, msg =  score_output(input_folder, output_file)
	return msg, score

if __name__ == '__main__':
    summ = 0
    counter = 0
    for i in range(1,332):
    	if i in [22,39,80,106,139,142,153,162,178,181,188,231,258,273,287,302,304,312,321,322]:
        	continue
    	msg, score = run_scores(i)
    	print(msg)
    	if(score > 0.5):
    		print()
    		print(str(score)+" ABOVE 50% !!!")
    		print()
    	summ += score
    	counter += 1
    print()
    print("Average: " + str(summ / counter))
