from tkinter import *
from tkinter import filedialog
from tkinter import font
import nltk
from nltk.tokenize import word_tokenize, MWETokenizer
nltk.download('punkt')

#create a DFA that accept L(food)
class Food_Finder:
    def __init__(self, food_patterns):
        #the formal definition of dfa
        self.alphabet = sorted(set('abcdefghijklmnopqrstuvwxyz '))
        self.states = [0, ]
        self.start_state = 0
        self.trap_state = -1
        self.final_states = []
        self.accepted_list = []
        self.dfa = {0:{}, -1:{}}
        i = 0

        #create a dfa based on the patterns input
        for food in food_patterns:
            current_state = 0 #start state
            counter = 0 #detect the end of word
            for alpha in food:
                counter += 1 
                if (alpha not in self.dfa[current_state]):
                    i = i+1 #new state name
                    next_state = i #happen if new state addded
                    self.states.append(next_state) #append the new state into states[]
                    self.dfa[next_state] = {} #create a new state                
                    self.dfa[current_state][alpha] = next_state #draw a line to the new state

                next_state = self.dfa[current_state][alpha] #get the next state when input
                current_state = next_state #navigate to the next state

                if counter == len(food):
                    self.final_states.append(current_state)#store the final state

        #link the no transition alphabets to trap state
        for state in self.states:
            for alpha in self.alphabet:
                if alpha not in self.dfa[state]:
                    next_state = self.trap_state
                    self.dfa[state][alpha] = next_state

    #check if the input string is food
    def verify_food(self, input_text):
        current_state = 0
        #consumed every character of input string
        for alpha in input_text:
            if (alpha in self.dfa[current_state]):
                next_state = self.dfa[current_state][alpha]
                current_state = next_state
            else:
                return

        #store the accepted words
        if current_state in self.final_states and input_text not in self.accepted_list:
            self.accepted_list.append(input_text)
        
#create a window for visualization purpose
class Window:
    def __init__(self, master):
        self.master = master
        self.master.title("DFA Food Finder")
        self.master.geometry("800x400") #set window's starting size
        self.master.resizable(False, False) #size of window
        self.master.config(bg="lightgrey") #bg color

        #create three frames
        self.output_frame = Frame(self.master, bg="white", bd=2, relief=SOLID)
        self.output_frame.grid(row=0, rowspan=1, column=0, padx=10,  pady=10, sticky="nsew")

        self.text_frame = Frame(self.master, bg="white", bd=2, relief=SOLID)
        self.text_frame.grid(row=0, column=1, padx=10,  pady=10, sticky="nsew")

        #list of patterns and the output
        self.patterns_label=Label(self.output_frame, text="List of Food's Patterns ", bg="white")
        self.patterns_label.grid(row=0,  column=0,  padx=5,  pady=5, sticky="w")

        self.foods_pattern = Listbox(self.output_frame, height=5, width=40)
        self.foods_pattern.grid(row=1, column=0, padx=10)

        self.add_btn = Button(self.output_frame, text="Add", command=self.add_patterns)
        self.add_btn.grid(row=2, column=0, padx=15, pady=2, sticky='e')

        self.output_label=Label(self.output_frame, text="Output", bg="white")
        self.output_label.grid(row=3,  column=0,  padx=5,  pady=5, sticky="w")

        self.status_label=Label(self.output_frame, text="Status: ", bg="white")
        self.status_label.grid(row=4,  column=0,  padx=10, sticky="w")

        self.foods_found_label=Label(self.output_frame, text="Occurrence of Food Detected:", bg="white")
        self.foods_found_label.grid(row=5,  column=0,  padx=10, sticky="w")

        self.foods_found = Text(self.output_frame, height=8, width=30, state=DISABLED)
        self.foods_found.grid(row=6, column=0, padx=15)

        #the display of text file contents and output of detected foods in the text
        self.text_box = Text(self.text_frame, wrap="word", height=20, width=55, state=DISABLED)
        self.text_box.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.browse_btn = Button(self.text_frame, text="Browse File", command=self.browse_file)
        self.browse_btn.grid(row=1, column=0, padx=5, pady=2, sticky='w')

        self.detect_btn = Button(self.text_frame, text="Detect", command=self.dfa_detect)
        self.detect_btn.grid(row=1, column=2, padx=5, pady=2, sticky='e')

        self.patterns_list = []
        self.input_tokens = []

    #function to get the food pattern input
    def add_patterns(self):
        #get the file consists of list of food patterns
        pat_file_path = filedialog.askopenfilename()
        if pat_file_path:
            self.foods_pattern.delete(0, END)
            with open(pat_file_path, "r") as f:
                self.patterns_list = f.readlines()

            #insert the list of food patterns into listbox
            for i, item in enumerate(self.patterns_list):
                self.patterns_list[i] = item.replace("\n", "")
                self.foods_pattern.insert(END, item)

    #function to get the text file for demo            
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as f:
                file_contents = f.read() #read the input text

                #display the text file contents
                self.text_box.config(state=NORMAL)
                self.text_box.delete("1.0", END)
                self.text_box.insert("1.0", file_contents)
                self.text_box.config(state=DISABLED)

                #tokenize the text file into words
                tokenizer = MWETokenizer([], ' ')
                #tokenize multi words into single token
                for pattern in self.patterns_list:
                    if len(pattern.split()) > 1:
                        tokenizer.add_mwe(pattern.split())
                self.input_tokens = tokenizer.tokenize(word_tokenize(file_contents.lower()))

    #detect if the text file have foods that macth the food patterns 
    def dfa_detect(self):
        accepted_list = [] #store the accepted words in the text file
        status = "rejected" #declare the status of accept/reject
        self.foods_found.config(state=NORMAL)
        self.foods_found.delete("1.0", END)
        food_dfa = Food_Finder(self.patterns_list) #initialize a food finder object

        for word in self.input_tokens:
            food_dfa.verify_food(word) #verify each word is food or not
        
        accepted_list = food_dfa.accepted_list #get the list of foods detected
        if accepted_list:
            status = "accepted" #accept the text file

            #get the occurrence and position of each food found
            for food in accepted_list:
                #get the position of the food
                positions = self.find_all(food)

                #configure a tag for boldface
                bold_font = font.Font(font=self.text_box["font"])
                bold_font.configure(weight='bold')
                self.text_box.tag_configure("bold", font=bold_font)
                #bold the food
                for pos, end_pos in positions:
                    self.text_box.tag_add("bold", pos, end_pos)
                
                #get the occurrence of food
                occurrence = self.input_tokens.count(food)
                food_occ = food + "\t" + str(occurrence) + "\n" #display the occurrence with food
                self.foods_found.insert(END, food_occ)
                
        self.foods_found.config(state=DISABLED)
        self.status_label["text"] = "Status: " + status #display the status: accepted/rejected

    #function to find all the position of food
    def find_all(self, food):
        start = '1.0'
        positions = []
        while True:
            start = self.text_box.search(food, start, END, nocase=1)
            if not start:
                break
            end = '{}+{}c'.format(start, len(food))
            positions.append((start, end))
            start = end
        return positions

if __name__ == "__main__":
    root = Tk()
    app = Window(root)
    root.mainloop()