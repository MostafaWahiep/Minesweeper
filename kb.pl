:- dynamic revealed/3, flagged/2, rows/1, cols/1.        %  row-col-number  /  flagged


valid_coord(X, Y) :-
    rows(R), cols(C),
    R1 is R - 1,
    C1 is C - 1,
    between(0, R1, X),
    between(0, C1, Y).

neighbor_offset(DR,DC) :-
    member(DR,[-1,0,1]),
    member(DC,[-1,0,1]),
    (DR \= 0 ; DC \= 0).

neighbor(R,C,NR,NC) :-
    neighbor_offset(DR,DC),
    NR is R+DR,
    NC is C+DC,
    valid_coord(NR,NC).

sum_flagged_neighbors(R, C, Count) :-
    ( setof([NR, NC], (neighbor(R, C, NR, NC), flagged(NR, NC)), L)
    -> length(L, Count)
    ;  Count = 0
    ).

unknown(R,C) :-
    valid_coord(R,C),
    \+ revealed(R,C,_),
    \+ flagged(R,C).

remaining_mines(R,C,Left) :-
    revealed(R,C,N),
    sum_flagged_neighbors(R,C,F),
    Left is N - F.

unknown_neighbours(R,C,Unks,Qty) :-
    setof([UR,UC],
            (neighbor(R,C,UR,UC), unknown(UR,UC)),
            Unks),
    length(Unks,Qty).


subset_sorted([], _).
subset_sorted([H|T], B) :- member(H, B), subset_sorted(T, B).

diff_sorted([], _, []).
diff_sorted([H|T], B, D) :-
    (   member(H, B) -> diff_sorted(T, B, D)
    ;   D = [H|Rest], diff_sorted(T, B, Rest)
    ).


single_sure_mine(R,C) :-
    unknown(R,C),
    neighbor(R,C,AR,AC),
    remaining_mines(AR,AC,L), L>0,
    unknown_neighbours(AR,AC,U,L),
    member([R,C], U).

single_can_reveal(R,C) :-
    unknown(R,C),
    neighbor(R,C,AR,AC),
    remaining_mines(AR,AC,0).


subset_mine(R,C) :-
    revealed(R1,C1,_), remaining_mines(R1,C1,L1), L1>0,
    unknown_neighbours(R1,C1,U1,_),
    revealed(R2,C2,_), (R1\=R2 ; C1\=C2),
    unknown_neighbours(R2,C2,U2,_),
    remaining_mines(R2,C2,L2), L2>0,
    subset_sorted(U1, U2),                   % U1 subset U2
    D is L2 - L1, D>0,                       % extra mines in U2
    diff_sorted(U2, U1, Diff), length(Diff,D),
    member([R,C], Diff).

subset_safe(R,C) :-
    revealed(R1,C1,_), remaining_mines(R1,C1,L),
    unknown_neighbours(R1,C1,U1,_),
    revealed(R2,C2,_), (R1\=R2 ; C1\=C2),
    unknown_neighbours(R2,C2,U2,_),
    remaining_mines(R2,C2,L),                % same mines-left
    subset_sorted(U1, U2),                   % U1 subset U2
    diff_sorted(U2, U1, SafeDiff),
    member([R,C], SafeDiff).


sure_mine(R,C) :- single_sure_mine(R,C) ; subset_mine(R,C).
can_reveal(R,C) :- single_can_reveal(R,C) ; subset_safe(R,C).