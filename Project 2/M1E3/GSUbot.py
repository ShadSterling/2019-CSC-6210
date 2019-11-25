import easygopigo3

class Robot():
    def __init__(self):
        self.__easy = easygopigo3.EasyGoPiGo3()
    def forward(self):
        self.__easy.forward()
    def left(self):
        self.__easy.left()
    def right(self):
        self.__easy.right()
    def backward(self):
        self.__easy.backward()
    def stop(self):
        self.__easy.stop()
