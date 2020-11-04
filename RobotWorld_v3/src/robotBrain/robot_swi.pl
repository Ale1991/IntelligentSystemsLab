% Robotics related example

% SENSOR READING
:- dynamic sensor_Left/1.
:- dynamic sensor_Forward/1.
:- dynamic sensor_Right/1.
:- dynamic direction/1.

:- dynamic stucked/1.

isStucked :- stucked(1).

% positive(X) :- X > 0.
% negative(Y) :- Y \==0, \+ positive(Y).

free_space_Left :- sensor_Left(A), A == " ".
free_space_Forward :- sensor_Forward(A), A == " ".
free_space_Right :- sensor_Right(A), A == " ".

free_space(left) :- free_space_Left.
free_space(forward) :- free_space_Forward.
free_space(right) :- free_space_Right.

energy_Left :- sensor_Left(A), A == " ".
energy_Forward :- sensor_Forward(A), A == " ".
energy_Right :- sensor_Right(A), A == " ".

energy(left) :- energy_Left.
energy(forward) :- energy_Forward.
energy(right) :- energy_Right.

wall_Left :- sensor_Left(A), A == "W".
wall_Forward :- sensor_Forward(A), A == "W".
wall_Right :- sensor_Right(A), A == "W".

wall(left) :- wall_Left.
wall(forward) :- wall_Forward.
wall(right) :- wall_Right.

robot_Left :- sensor_Left(A), A == "R".
robot_Forward :- sensor_Forward(A), A == "R".
robot_Right :- sensor_Right(A), A == "R".

robot(left) :- robot_Left.
robot(forward) :- robot_Forward.
robot(right) :- robot_Right.

direction_Nord :- direction(A), A == "NORD".
direction_Est :- direction(A), A == "EST".
direction_Sud :- direction(A), A == "SUD".
direction_Ovest :- direction(A), A == "OVEST".

direction(nord) :- direction_Nord.
direction(est) :- direction_Est.
direction(sud) :- direction_Sud.
direction(ovest) :- direction_Ovest.

% free_space :-  free_space_Left, free_space_Forward, free_space_Right.
trapped :- wall_Left, wall_Forward, wall_Right.

% PERCEPTIONS
step(left) :- (energy_Left ; free_space_Left ; (isStucked , robot_Left)) , \+ trapped.
step(forward) :- (energy_Forward ; free_space_Forward ; (isStucked , robot_Forward)) , \+ trapped.
step(right) :- (energy_Right ; free_space_Right ; (isStucked , robot_Right)) , \+ trapped.

% PLANNING RULE

% move(X) :- step(X).
move(X) :- template(X).



template(["Action.RS", "Action.STEP", "Action.RD", "Action.STEP"]) :- step(left).
template(["Action.STEP"]) :- step(forward).
template(["Action.RD", "Action.STEP", "Action.RS", "Action.STEP"]) :- step(right).
template(["Action.RD"]) :- trapped.