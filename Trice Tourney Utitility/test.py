def fun(a):
	return a+1

def test(val, function):
    return function(val)

if __name__ == "__main__":
    print(test(1,fun))