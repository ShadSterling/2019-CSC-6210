import easygopigo3

class Robot():
    def __init__(self):
        self.__easy = easygopigo3.EasyGoPiGo3()
    def right(self):
        self.__easy.right()
    def stop(self):
        self.__easy.stop()
