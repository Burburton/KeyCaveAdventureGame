# KeyCaveAdventureGame
A little game, which is named Key Cave Adventure, is designed by python3 with GUI maintaining model-view-controller (MVC) structure
## Instruction
The game can be modified into three mode (TASK ONE, TASK TWO and MASTER). TASK ONE is a simple version of GUI that represents various charactors with a unique color. TASK TWO import images as GUI componets that make the game more vivid. MASTER mode provides a recall button that allows player recall limited steps on the basis of TASK TWO.
## Charactors
* Wall: Dark grey
* Ibis (Player): Medium spring green
* Banana (MoveIncrease): Orange
* Trash (Key): Yellow
* Nest (Door): Red
The colors are only reflected in TASK ONE.
## Operations guide
Players are allowed to use 'wasd' on keyboard or keypad on the game window to control the Ibis go up, left, down and right. Every step would cost an energy. Ibis is forbidden to pass the walls. Ibis is required to gain the Trash(Key) and then arrive the Nest(Door) to win the game. During the period, if Ibis get Banana it will have move energy for step. If Ibis cannot get the Key and arrive Nest in the finite steps, it will lose the game. A timer would record the scores.
