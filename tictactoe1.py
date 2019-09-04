# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 13:53:32 2018

@author: sunil.dabbiru
"""
"""
Tic Tac Toe
"""
import random
def f_board():
    print("Board position legend :") 
    f_fill_board()
    
def f_reset_board():
    global game_state
    global l
    global a
    game_state = False
    a =''
    l =[]
    l = ['0','1','2','3','4','5','6','7','8','9']
    print("\033[H\033[J")  
    
def f_ask_player():
    while True:
        global a
        z = random.randint(0,1)
        #a = input("Choose (X) or (O)\n")
        if(z == 1):
            a = 'X'
            print("Player %s starts first"%a)
            break
        elif(z == 0):
            a = 'O'
            print("Player %s starts first"%a)
            break
        else:
            a = None
            print("\nInvalid entry ; Try again")
            
def f_fill_board():
    global l
    print(l[7]+" | "+l[8]+" | "+l[9])
    print("--|---|--")
    print(l[4]+" | "+l[5]+" | "+l[6])
    print("--|---|--")
    print(l[1]+" | "+l[2]+" | "+l[3])

def f_check_status():
    global game_state
    if ( (l[7] == 'X' and (l[7] == l[8] == l[9]  or l[7] == l[4] == l[1])) \
          or  (l[3] == 'X' and ( l[1] == l[2] == l[3] or l[3] == l[6] == l[9] )) \
          or (l[5] == 'X' and (l[4] == l[5] == l[6] or l[7] ==l[5] == l[3] or l[1] == l[5] == l[9] or l[8] == l[5] == l[2]))):
       print("\nPlayer X wins")
       game_state = False
    elif((l[7] == 'O' and (l[7] == l[8] == l[9]  or l[7] == l[4] == l[1])) \
          or  (l[3] == 'O' and ( l[1] == l[2] == l[3] or l[3] == l[6] == l[9] )) \
          or (l[5] == 'O' and (l[4] == l[5] == l[6] or l[7] ==l[5] == l[3] or l[1] == l[5] == l[9] or l[8] == l[5] == l[2]))):       
       print("\nPlayer O wins")
       game_state = False
    elif((l[1] == 'X' or l[1] == 'O') \
          and (l[2] == 'X' or l[2] == 'O') \
          and (l[3] == 'X' or l[3] == 'O') \
          and (l[4] == 'X' or l[4] == 'O') \
          and (l[5] == 'X' or l[5] == 'O') \
          and (l[6] == 'X' or l[6] == 'O') \
          and (l[7] == 'X' or l[7] == 'O') \
          and (l[8] == 'X' or l[8] == 'O') \
          and (l[9] == 'X' or l[9] == 'O')):
       print("\nDraw") 
       game_state = False
    else:
       game_state = True   
       
def f_play():
      global x
      global a
      global game_state
      game_state = True
      for i in range(1,10):
         if(a.upper()=='X' and game_state ==True):   
           print("\nPlayer "+a.upper()+" turn")
         elif(a.upper()=='O' and game_state ==True):  
           print("\nPlayer O turn")
         else:
           break  
         while True:   
           x =  int(input("Enter position :"))
           if(x > 0 and x < 10): 
            if(l[x] != 'X' and l[x] != 'O'):
             l.pop(x)   
             l.insert(x,a.upper())
             if a.upper() =='X':
                 a = 'O'
             else:
                 a = 'X' 
             break
            else:
             print("***Already used****")
           else:
            print("Invalid entry,Try again \n")
         f_fill_board()
         f_check_status()

##Call the functions 
f_reset_board()
f_board()
f_ask_player()
f_play()
  
  


    





             
    

    
    
